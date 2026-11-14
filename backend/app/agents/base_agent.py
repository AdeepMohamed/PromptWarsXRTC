"""
Abstract base class for all COGNIFY AI agents.

Provides the AgentInput / AgentOutput Pydantic models, the abstract execute()
contract, and a shared log_activity() helper that writes to
``agent_activity_logs``.
"""

from __future__ import annotations

import logging
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pydantic I/O models
# ---------------------------------------------------------------------------

class AgentInput(BaseModel):
    """Standard input envelope for every agent."""

    learner_id: uuid.UUID
    data: dict[str, Any] = Field(default_factory=dict)


class AgentOutput(BaseModel):
    """Standard output envelope returned by every agent."""

    agent_name: str
    status: str = "completed"  # "completed" | "failed"
    result: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
    processing_duration_ms: int = 0


# ---------------------------------------------------------------------------
# Base agent
# ---------------------------------------------------------------------------

class BaseAgent(ABC):
    """Abstract base for all COGNIFY agents."""

    name: str = "base_agent"
    description: str = ""

    # ------------------------------------------------------------------
    # execute — subclasses must implement
    # ------------------------------------------------------------------

    @abstractmethod
    async def execute(self, input_data: AgentInput, db) -> AgentOutput:
        """Run the agent's logic and return an ``AgentOutput``."""
        ...

    # ------------------------------------------------------------------
    # safe_execute — wraps execute with timing + error handling
    # ------------------------------------------------------------------

    async def safe_execute(self, input_data: AgentInput, db) -> AgentOutput:
        """Call *execute* with timing, logging, and error handling."""

        start = time.perf_counter_ns()
        try:
            output = await self.execute(input_data, db)
            elapsed_ms = int((time.perf_counter_ns() - start) / 1_000_000)
            output.processing_duration_ms = elapsed_ms

            await self.log_activity(
                db,
                learner_id=input_data.learner_id,
                task=f"{self.name}.execute",
                input_summary=str(input_data.data)[:500],
                output_summary=str(output.result)[:500],
                status=output.status,
                duration_ms=elapsed_ms,
            )
            return output

        except Exception as exc:
            elapsed_ms = int((time.perf_counter_ns() - start) / 1_000_000)
            logger.exception("%s failed: %s", self.name, exc)
            await self.log_activity(
                db,
                learner_id=input_data.learner_id,
                task=f"{self.name}.execute",
                input_summary=str(input_data.data)[:500],
                output_summary="",
                status="failed",
                duration_ms=elapsed_ms,
                error=str(exc),
            )
            return AgentOutput(
                agent_name=self.name,
                status="failed",
                result={},
                errors=[str(exc)],
                processing_duration_ms=elapsed_ms,
            )

    # ------------------------------------------------------------------
    # log_activity — writes a row to agent_activity_logs
    # ------------------------------------------------------------------

    async def log_activity(
        self,
        db,
        learner_id: uuid.UUID,
        task: str,
        input_summary: str,
        output_summary: str,
        status: str,
        duration_ms: int,
        error: str | None = None,
    ) -> None:
        """Persist an ``AgentActivityLog`` row."""

        try:
            from app.models import AgentActivityLog
        except ImportError:
            try:
                from app.models.agent import AgentActivityLog
            except ImportError:
                logger.warning("AgentActivityLog model not available – skipping log write")
                return

        now = datetime.now(timezone.utc)
        log_entry = AgentActivityLog(
            id=uuid.uuid4(),
            learner_id=learner_id,
            agent_name=self.name,
            task=task,
            input_summary=input_summary,
            output_summary=output_summary,
            status=status,
            error_message=error,
            processing_duration_ms=duration_ms,
            started_at=now,
            completed_at=now if status in ("completed", "failed") else None,
            created_at=now,
        )
        db.add(log_entry)
        try:
            await db.flush()
        except Exception:
            logger.warning("Failed to flush agent activity log – will rely on session commit")
