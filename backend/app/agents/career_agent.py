"""
Agent 2 — Career Matching Agent.

Compares a learner's current skill profile against the requirements of a
target career role.  Produces a readiness score, lists strong / missing /
critical skills, and gap analysis.

Fallback: pure DB calculation.
  readiness = Σ(current_prof × importance) / Σ(importance × 100) × 100
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import select

from app.agents.base_agent import AgentInput, AgentOutput, BaseAgent
from app.agents.grok_client import GrokAPIError, grok_chat

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pydantic sub-models
# ---------------------------------------------------------------------------

class CareerInfo(BaseModel):
    title: str = ""
    readiness_score: float = 0.0


class RequiredSkill(BaseModel):
    name: str
    importance: float
    min_proficiency: float


class StrongSkill(BaseModel):
    name: str
    current: float
    required: float
    status: str = "exceeds"


class MissingSkill(BaseModel):
    name: str
    importance: float
    gap: float
    reason: str = ""


class CriticalGap(BaseModel):
    name: str
    importance: float
    urgency: str = "high"


class CareerAnalysisResult(BaseModel):
    career: CareerInfo = Field(default_factory=CareerInfo)
    required_skills: list[RequiredSkill] = Field(default_factory=list)
    strong_skills: list[StrongSkill] = Field(default_factory=list)
    missing_skills: list[MissingSkill] = Field(default_factory=list)
    critical_gaps: list[CriticalGap] = Field(default_factory=list)
    readiness_formula: str = "sum(current * importance) / sum(importance * 100) * 100"


# ---------------------------------------------------------------------------
# Career Agent
# ---------------------------------------------------------------------------

class CareerAgent(BaseAgent):
    name: str = "career_agent"
    description: str = "Compares learner skills against career requirements and computes readiness."

    async def execute(self, input_data: AgentInput, db) -> AgentOutput:
        career_id = input_data.data.get("career_id") or (input_data.data.get("target_career", {}).get("id") if isinstance(input_data.data.get("target_career"), dict) else None)
        if not career_id:
            return AgentOutput(agent_name=self.name, status="failed", errors=["career_id missing from input data"])

        career_id = uuid.UUID(str(career_id))
        db_data = await self._load_data(input_data.learner_id, career_id, db)

        try:
            result = await self._ai_analysis(db_data)
        except (GrokAPIError, Exception) as exc:
            logger.warning("Grok unavailable for career analysis – fallback: %s", exc)
            result = self._fallback_analysis(db_data)

        validated = CareerAnalysisResult.model_validate(result)
        return AgentOutput(agent_name=self.name, status="completed", result=validated.model_dump())

    # ------------------------------------------------------------------
    # DB loader
    # ------------------------------------------------------------------

    async def _load_data(self, learner_id: uuid.UUID, career_id: uuid.UUID, db) -> dict[str, Any]:
        from app.models import LearnerProfile, LearnerSkill, Skill, CareerRole, CareerRequirement

        # Career
        stmt = select(CareerRole).where(CareerRole.id == career_id)
        career = (await db.execute(stmt)).scalar_one_or_none()
        career_title = career.title if career else "Unknown"

        # Profile
        stmt = select(LearnerProfile).where((LearnerProfile.id == learner_id) | (LearnerProfile.user_id == learner_id))
        profile = (await db.execute(stmt)).scalar_one_or_none()
        profile_id = profile.id if profile else None

        # Requirements
        stmt = (
            select(CareerRequirement, Skill)
            .join(Skill, CareerRequirement.skill_id == Skill.id)
            .where(CareerRequirement.career_id == career_id)
        )
        req_rows = (await db.execute(stmt)).all()

        requirements: list[dict] = []
        for cr, sk in req_rows:
            requirements.append({
                "skill_name": sk.name,
                "skill_id": str(sk.id),
                "importance": cr.importance,
                "min_proficiency": cr.min_proficiency,
                "is_critical": cr.is_critical,
                "description": cr.description or "",
            })

        # Learner skills
        learner_skills: dict[str, dict] = {}
        if profile_id:
            stmt = (
                select(LearnerSkill, Skill)
                .join(Skill, LearnerSkill.skill_id == Skill.id)
                .where(LearnerSkill.learner_id == profile_id)
            )
            for ls, sk in (await db.execute(stmt)).all():
                learner_skills[sk.name] = {
                    "proficiency": ls.proficiency,
                    "confidence": ls.confidence,
                }

        return {
            "career_title": career_title,
            "career_id": str(career_id),
            "requirements": requirements,
            "learner_skills": learner_skills,
        }

    # ------------------------------------------------------------------
    # AI path
    # ------------------------------------------------------------------

    async def _ai_analysis(self, db_data: dict) -> dict:
        system = (
            "You are COGNIFY's Career Readiness AI. Compare the learner's skills "
            "to the career requirements and return ONLY valid JSON:\n"
            "  career: {title, readiness_score (0-100)}\n"
            "  required_skills: [{name, importance, min_proficiency}]\n"
            "  strong_skills: [{name, current, required, status}]\n"
            "  missing_skills: [{name, importance, gap, reason}]\n"
            "  critical_gaps: [{name, importance, urgency}]\n"
            "  readiness_formula: string explaining the formula used\n"
            "Use readiness = sum(min(current,100) * importance) / sum(importance * 100) * 100"
        )
        return await grok_chat(system, json.dumps(db_data, default=str))

    # ------------------------------------------------------------------
    # Deterministic fallback
    # ------------------------------------------------------------------

    def _fallback_analysis(self, db_data: dict) -> dict:
        career_title = db_data["career_title"]
        requirements = db_data["requirements"]
        learner_skills = db_data["learner_skills"]

        required: list[dict] = []
        strong: list[dict] = []
        missing: list[dict] = []
        critical: list[dict] = []

        weighted_sum = 0.0
        max_sum = 0.0

        for req in requirements:
            name = req["skill_name"]
            importance = req["importance"]
            min_prof = req["min_proficiency"]
            is_crit = req["is_critical"]

            required.append({"name": name, "importance": importance, "min_proficiency": min_prof})

            current = learner_skills.get(name, {}).get("proficiency", 0.0)
            weighted_sum += current * importance
            max_sum += 100.0 * importance

            if current >= min_prof:
                strong.append({"name": name, "current": current, "required": min_prof, "status": "exceeds" if current > min_prof else "meets"})
            else:
                gap = min_prof - current
                missing.append({"name": name, "importance": importance, "gap": gap, "reason": req.get("description") or f"Required for {career_title}"})
                if is_crit:
                    urgency = "high" if gap > 50 else "medium"
                    critical.append({"name": name, "importance": importance, "urgency": urgency})

        readiness = (weighted_sum / max_sum * 100) if max_sum > 0 else 0.0

        return {
            "career": {"title": career_title, "readiness_score": round(readiness, 2)},
            "required_skills": required,
            "strong_skills": strong,
            "missing_skills": sorted(missing, key=lambda m: m["importance"], reverse=True),
            "critical_gaps": critical,
            "readiness_formula": "sum(current * importance) / sum(importance * 100) * 100",
        }
