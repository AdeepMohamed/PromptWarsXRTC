"""
Agent 1 — Skill Analysis Agent.

Analyses a learner's skills from profile data, certifications, projects, and
assessment results.  Produces a Skill-DNA radar and actionable recommendations.

Fallback: when Grok is unavailable the agent derives every output directly
from the DB rows (learner_skills, assessment_results, project_submissions).
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.agents.base_agent import AgentInput, AgentOutput, BaseAgent
from app.agents.grok_client import GrokAPIError, grok_chat

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pydantic sub-models for validated output
# ---------------------------------------------------------------------------

class SkillEntry(BaseModel):
    name: str
    proficiency: float
    confidence: str = "claimed"


class SkillDNA(BaseModel):
    programming: float = 0.0
    analytical_thinking: float = 0.0
    problem_solving: float = 0.0
    communication: float = 0.0
    technical_proficiency: float = 0.0
    project_experience: float = 0.0


class SkillAnalysisResult(BaseModel):
    technical_skills: list[SkillEntry] = Field(default_factory=list)
    soft_skills: list[SkillEntry] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    skill_dna: SkillDNA = Field(default_factory=SkillDNA)
    recommendations: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Skill Agent
# ---------------------------------------------------------------------------

class SkillAgent(BaseAgent):
    name: str = "skill_agent"
    description: str = "Analyses learner skills, certifications and projects to produce a skill-DNA profile."

    # ------------------------------------------------------------------
    # execute
    # ------------------------------------------------------------------

    async def execute(self, input_data: AgentInput, db) -> AgentOutput:
        # 1. Load data from DB
        learner_data = await self._load_learner_data(input_data.learner_id, db)

        # 2. Try AI-powered analysis
        try:
            result = await self._ai_analysis(learner_data)
        except (GrokAPIError, Exception) as exc:
            logger.warning("Grok unavailable for skill analysis – falling back: %s", exc)
            result = self._fallback_analysis(learner_data)

        validated = SkillAnalysisResult.model_validate(result)
        return AgentOutput(
            agent_name=self.name,
            status="completed",
            result=validated.model_dump(),
        )

    # ------------------------------------------------------------------
    # DB loader
    # ------------------------------------------------------------------

    async def _load_learner_data(self, learner_id: uuid.UUID, db) -> dict[str, Any]:
        from app.models import LearnerProfile, LearnerSkill, Skill, AssessmentResult, ProjectSubmission

        # Profile
        stmt = select(LearnerProfile).where((LearnerProfile.id == learner_id) | (LearnerProfile.user_id == learner_id))
        res = await db.execute(stmt)
        profile = res.scalar_one_or_none()

        profile_dict: dict[str, Any] = {}
        profile_id: uuid.UUID | None = None
        if profile:
            profile_id = profile.id
            profile_dict = {
                "bio": profile.bio or "",
                "education_level": profile.education_level or "",
                "years_experience": profile.years_experience or 0,
                "academic_background": profile.academic_background or "",
                "certifications": profile.certifications or [],
            }

        # Skills
        skills_list: list[dict] = []
        if profile_id:
            stmt = (
                select(LearnerSkill, Skill)
                .join(Skill, LearnerSkill.skill_id == Skill.id)
                .where(LearnerSkill.learner_id == profile_id)
            )
            rows = await db.execute(stmt)
            for ls, sk in rows.all():
                skills_list.append({
                    "name": sk.name,
                    "category": sk.category,
                    "proficiency": ls.proficiency,
                    "confidence": ls.confidence,
                    "source": ls.source,
                })

        # Assessment history
        assessments: list[dict] = []
        if profile_id:
            stmt = select(AssessmentResult).where(AssessmentResult.learner_id == profile_id).order_by(AssessmentResult.completed_at.desc()).limit(20)
            rows = await db.execute(stmt)
            for ar in rows.scalars().all():
                assessments.append({
                    "score": ar.score,
                    "max_score": ar.max_score,
                    "percentage": ar.percentage,
                    "weak_topics": ar.weak_topics or [],
                })

        # Projects
        projects: list[dict] = []
        if profile_id:
            stmt = select(ProjectSubmission).where(ProjectSubmission.learner_id == profile_id).limit(20)
            rows = await db.execute(stmt)
            for ps in rows.scalars().all():
                projects.append({
                    "title": ps.title,
                    "technologies": ps.technologies or [],
                    "demonstrated_skills": ps.demonstrated_skills or [],
                })

        return {
            "profile": profile_dict,
            "profile_id": str(profile_id) if profile_id else None,
            "skills": skills_list,
            "assessments": assessments,
            "projects": projects,
        }

    # ------------------------------------------------------------------
    # AI path
    # ------------------------------------------------------------------

    async def _ai_analysis(self, learner_data: dict) -> dict:
        system = (
            "You are COGNIFY's Skill Analysis AI. Analyse the learner data and "
            "return ONLY valid JSON (no markdown fences) with these keys:\n"
            "  technical_skills: [{name, proficiency (0-100), confidence}]\n"
            "  soft_skills: [{name, proficiency (0-100), confidence}]\n"
            "  strengths: [string]\n"
            "  weaknesses: [string]\n"
            "  skill_dna: {programming, analytical_thinking, problem_solving, "
            "communication, technical_proficiency, project_experience} each 0-100\n"
            "  recommendations: [string]\n"
            "Base your analysis on the learner's skills, assessment scores, "
            "projects, certifications and profile."
        )
        import json
        user = json.dumps(learner_data, default=str)
        return await grok_chat(system, user)

    # ------------------------------------------------------------------
    # Deterministic fallback
    # ------------------------------------------------------------------

    def _fallback_analysis(self, learner_data: dict) -> dict:
        skills = learner_data.get("skills", [])
        assessments = learner_data.get("assessments", [])
        projects = learner_data.get("projects", [])
        profile = learner_data.get("profile", {})

        technical: list[dict] = []
        soft: list[dict] = []
        for s in skills:
            entry = {"name": s["name"], "proficiency": s["proficiency"], "confidence": s["confidence"]}
            if s.get("category") in ("technical", "tool"):
                technical.append(entry)
            else:
                soft.append(entry)

        # Strengths = skills ≥ 60, weaknesses < 40
        strengths = [s["name"] for s in skills if s["proficiency"] >= 60]
        weaknesses = [s["name"] for s in skills if s["proficiency"] < 40]

        # Weak topics from assessments
        weak_topics_set: set[str] = set()
        for a in assessments:
            for t in (a.get("weak_topics") or []):
                weak_topics_set.add(t)
        if weak_topics_set:
            weaknesses = list(set(weaknesses) | weak_topics_set)

        # Skill DNA – averages by rough category heuristics
        tech_profs = [s["proficiency"] for s in skills if s.get("category") in ("technical", "tool")]
        soft_profs = [s["proficiency"] for s in skills if s.get("category") == "soft"]
        avg_assessment = (sum(a["percentage"] for a in assessments) / len(assessments)) if assessments else 0
        project_score = min(len(projects) * 20, 100)

        skill_dna = {
            "programming": (sum(tech_profs) / len(tech_profs)) if tech_profs else 0,
            "analytical_thinking": avg_assessment * 0.8 if assessments else 0,
            "problem_solving": avg_assessment * 0.7 if assessments else 0,
            "communication": (sum(soft_profs) / len(soft_profs)) if soft_profs else 0,
            "technical_proficiency": (sum(tech_profs) / len(tech_profs)) if tech_profs else 0,
            "project_experience": project_score,
        }

        # Recommendations
        recommendations: list[str] = []
        if weaknesses:
            recommendations.append(f"Focus on improving: {', '.join(weaknesses[:3])}")
        if not projects:
            recommendations.append("Build portfolio projects to demonstrate skills")
        if not (profile.get("certifications")):
            recommendations.append("Consider earning industry certifications")
        if avg_assessment < 50 and assessments:
            recommendations.append("Review assessment weak topics and practice regularly")

        return {
            "technical_skills": technical,
            "soft_skills": soft,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "skill_dna": skill_dna,
            "recommendations": recommendations,
        }
