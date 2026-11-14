"""
Agent 3 — Learning Roadmap Agent.

Generates a personalised, structured roadmap of tasks based on a learner's
skill gaps, career requirements, and available resources.

Fallback: builds the roadmap directly from `learning_resources` +
`career_requirements`, ordered by importance DESC then difficulty ASC.
"""

from __future__ import annotations

import json
import logging
import math
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

class RoadmapTask(BaseModel):
    skill: str
    topic: str
    description: str = ""
    difficulty: str = "beginner"
    estimated_hours: float = 4.0
    learning_objective: str = ""
    recommended_resource: str = ""
    practical_exercise: str = ""
    completion_criteria: str = ""
    priority: int = 0
    week_number: int = 1
    order_index: int = 1


class RoadmapResult(BaseModel):
    title: str = "Learning Roadmap"
    total_weeks: int = 1
    total_hours: float = 0.0
    tasks: list[RoadmapTask] = Field(default_factory=list)


class LearningAgentResult(BaseModel):
    roadmap: RoadmapResult = Field(default_factory=RoadmapResult)


# ---------------------------------------------------------------------------
# Learning Agent
# ---------------------------------------------------------------------------

DIFFICULTY_ORDER = {"beginner": 0, "intermediate": 1, "advanced": 2}
HOURS_PER_WEEK = 20  # for week assignment heuristic


class LearningAgent(BaseAgent):
    name: str = "learning_agent"
    description: str = "Generates personalised learning roadmaps from skill gaps."

    async def execute(self, input_data: AgentInput, db) -> AgentOutput:
        gaps = input_data.data.get("gaps") or input_data.data.get("skill_gaps", [])
        career_title = input_data.data.get("career_title", "Career Goal")
        career_id = input_data.data.get("career_id")

        db_data = await self._load_resources(gaps, career_id, db)
        db_data["gaps"] = gaps
        db_data["career_title"] = career_title

        try:
            result = await self._ai_analysis(db_data)
        except (GrokAPIError, Exception) as exc:
            logger.warning("Grok unavailable for roadmap generation – fallback: %s", exc)
            result = self._fallback(db_data)

        validated = LearningAgentResult.model_validate({"roadmap": result})
        return AgentOutput(agent_name=self.name, status="completed", result=validated.model_dump())

    # ------------------------------------------------------------------
    # DB loader
    # ------------------------------------------------------------------

    async def _load_resources(self, gaps: list[dict], career_id: str | None, db) -> dict:
        from app.models import LearningResource, Skill, CareerRequirement

        # Gather skill names from gaps
        gap_skill_names: set[str] = {g.get("name", g.get("skill", "")) for g in gaps}

        # Resolve skill ids
        stmt = select(Skill).where(Skill.name.in_(gap_skill_names)) if gap_skill_names else select(Skill).limit(0)
        rows = await db.execute(stmt)
        skill_map: dict[str, uuid.UUID] = {}
        for sk in rows.scalars().all():
            skill_map[sk.name] = sk.id

        # Resources for those skills
        resources: list[dict] = []
        if skill_map:
            stmt = (
                select(LearningResource, Skill)
                .join(Skill, LearningResource.skill_id == Skill.id)
                .where(LearningResource.skill_id.in_(list(skill_map.values())))
            )
            for lr, sk in (await db.execute(stmt)).all():
                resources.append({
                    "skill": sk.name,
                    "title": lr.title,
                    "resource_type": lr.resource_type,
                    "url": lr.url or "",
                    "difficulty": lr.difficulty or "beginner",
                    "hours": lr.estimated_duration_hours or 2,
                    "description": lr.description or "",
                    "provider": lr.provider or "",
                })

        # Career requirements for ordering
        requirements: list[dict] = []
        if career_id:
            cid = uuid.UUID(str(career_id))
            stmt = (
                select(CareerRequirement, Skill)
                .join(Skill, CareerRequirement.skill_id == Skill.id)
                .where(CareerRequirement.career_id == cid)
            )
            for cr, sk in (await db.execute(stmt)).all():
                requirements.append({
                    "skill": sk.name,
                    "importance": cr.importance,
                    "min_proficiency": cr.min_proficiency,
                })

        return {"resources": resources, "requirements": requirements}

    # ------------------------------------------------------------------
    # AI path
    # ------------------------------------------------------------------

    async def _ai_analysis(self, db_data: dict) -> dict:
        system = (
            "You are COGNIFY's Learning Roadmap AI. Create a structured roadmap "
            "for the learner based on their skill gaps. Return ONLY valid JSON:\n"
            "  title: string\n"
            "  total_weeks: int\n"
            "  total_hours: float\n"
            "  tasks: [{skill, topic, description, difficulty (beginner/intermediate/advanced), "
            "estimated_hours, learning_objective, recommended_resource, practical_exercise, "
            "completion_criteria, priority (lower=higher), week_number, order_index}]\n"
            "Order tasks by importance (critical gaps first) then difficulty (easier first). "
            "Assign week_number so that each week has ≤ 20 hours."
        )
        return await grok_chat(system, json.dumps(db_data, default=str))

    # ------------------------------------------------------------------
    # Deterministic fallback
    # ------------------------------------------------------------------

    def _fallback(self, db_data: dict) -> dict:
        gaps = db_data.get("gaps", [])
        resources = db_data.get("resources", [])
        requirements = db_data.get("requirements", [])
        career_title = db_data.get("career_title", "Learning Roadmap")

        # Build importance map from requirements
        importance_map: dict[str, float] = {r["skill"]: r["importance"] for r in requirements}

        # Build resource map keyed by skill
        resource_map: dict[str, list[dict]] = {}
        for r in resources:
            resource_map.setdefault(r["skill"], []).append(r)

        # Sort gaps by importance desc, then by gap size desc
        sorted_gaps = sorted(
            gaps,
            key=lambda g: (importance_map.get(g.get("name", g.get("skill", "")), 5), g.get("gap", g.get("importance", 5))),
            reverse=True,
        )

        tasks: list[dict] = []
        order = 1
        week = 1
        week_hours = 0.0

        for gap in sorted_gaps:
            skill_name = gap.get("name", gap.get("skill", "Unknown"))
            gap_size = gap.get("gap", gap.get("min_proficiency", 50))
            importance = importance_map.get(skill_name, 5)

            # Determine difficulty from gap size
            if gap_size > 60:
                difficulty = "beginner"
            elif gap_size > 30:
                difficulty = "intermediate"
            else:
                difficulty = "advanced"

            # Find matching resources (sorted easiest first)
            skill_resources = sorted(
                resource_map.get(skill_name, []),
                key=lambda r: DIFFICULTY_ORDER.get(r.get("difficulty", "beginner"), 0),
            )

            # If we have resources, create a task per resource; otherwise a generic task
            if skill_resources:
                for res in skill_resources:
                    hours = res.get("hours", 4.0)
                    if week_hours + hours > HOURS_PER_WEEK:
                        week += 1
                        week_hours = 0.0
                    week_hours += hours
                    tasks.append({
                        "skill": skill_name,
                        "topic": res.get("title", skill_name),
                        "description": res.get("description", f"Learn {skill_name}"),
                        "difficulty": res.get("difficulty", difficulty),
                        "estimated_hours": hours,
                        "learning_objective": f"Improve {skill_name} proficiency",
                        "recommended_resource": res.get("url") or res.get("title", ""),
                        "practical_exercise": f"Complete exercises for {res.get('title', skill_name)}",
                        "completion_criteria": f"Demonstrate understanding of {res.get('title', skill_name)}",
                        "priority": order,
                        "week_number": week,
                        "order_index": order,
                    })
                    order += 1
            else:
                hours = max(4.0, gap_size / 10)
                if week_hours + hours > HOURS_PER_WEEK:
                    week += 1
                    week_hours = 0.0
                week_hours += hours
                tasks.append({
                    "skill": skill_name,
                    "topic": f"{skill_name} Fundamentals",
                    "description": f"Study {skill_name} to close the skill gap",
                    "difficulty": difficulty,
                    "estimated_hours": hours,
                    "learning_objective": f"Build proficiency in {skill_name}",
                    "recommended_resource": f"Search for {skill_name} tutorials",
                    "practical_exercise": f"Build a small project using {skill_name}",
                    "completion_criteria": f"Complete a {skill_name} practice project",
                    "priority": order,
                    "week_number": week,
                    "order_index": order,
                })
                order += 1

        total_hours = sum(t["estimated_hours"] for t in tasks)

        return {
            "title": f"{career_title} Roadmap",
            "total_weeks": week,
            "total_hours": round(total_hours, 1),
            "tasks": tasks,
        }
