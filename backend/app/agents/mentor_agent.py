"""
Agent 5 — Mentor Agent.

Personalized AI career mentor using authentic learner data:
profile, target career, skill inventory, gaps, recent assessments, and roadmap progress.
Avoids generic boilerplate answers; tailors technical explanations and career strategy.

Fallback: Context-aware template engine loaded with real learner metrics.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from pydantic import BaseModel, Field

from app.agents.base_agent import AgentInput, AgentOutput, BaseAgent
from app.agents.grok_client import GrokAPIError, grok_chat

logger = logging.getLogger(__name__)


class MentorResource(BaseModel):
    title: str
    url: str


class MentorResponse(BaseModel):
    message: str
    suggestions: list[str] = Field(default_factory=list)
    resources: list[dict[str, str]] = Field(default_factory=list)


class MentorAgent(BaseAgent):
    name: str = "mentor_agent"
    description: str = (
        "Personalized AI Career Mentor providing context-specific guidance, "
        "remedial advice, technical explanations, and interview preparation."
    )

    async def execute(self, input_data: AgentInput, db) -> AgentOutput:
        data = input_data.data
        user_message = data.get("message", "")
        context_type = data.get("context", "general")
        learner_info = data.get("learner_info", {})

        # Try Grok AI mentor first
        try:
            ai_result = await self._run_grok(user_message, context_type, learner_info)
            validated = MentorResponse(**ai_result)
            return AgentOutput(
                agent_name=self.name,
                status="completed",
                result=validated.model_dump(),
            )
        except Exception as exc:
            logger.info("Falling back to deterministic mentor reasoning: %s", exc)
            fallback = self._deterministic_mentor(user_message, context_type, learner_info)
            return AgentOutput(
                agent_name=self.name,
                status="completed",
                result=fallback,
            )

    async def _run_grok(
        self,
        message: str,
        context_type: str,
        learner_info: dict[str, Any],
    ) -> dict[str, Any]:
        system_prompt = (
            "You are COGNIFY AI's Personalized Career Mentor. You are speaking directly to a learner. "
            "Use their authentic profile, target career, skill levels, recent assessments, and gaps. "
            "Never give generic motivational fluff. Provide concrete technical guidance, code mental models, "
            "interview tips, and actionable next steps.\n\n"
            "Return valid JSON matching this schema:\n"
            "{\n"
            '  "message": "Direct, empathetic, highly technical or career-strategic response...",\n'
            '  "suggestions": ["Action item 1", "Action item 2"],\n'
            '  "resources": [{"title": "Resource Name", "url": "https://..."}]\n'
            "}"
        )

        user_prompt = (
            f"Context Mode: {context_type}\n"
            f"Learner Profile: {learner_info.get('profile', {})}\n"
            f"Target Career: {learner_info.get('target_career', 'Not selected')}\n"
            f"Career Readiness: {learner_info.get('career_readiness_score', 0)}%\n"
            f"Skill Proficiencies: {learner_info.get('skills', [])}\n"
            f"Skill Gaps: {learner_info.get('gaps', [])}\n"
            f"Recent Assessment: {learner_info.get('recent_assessment', {})}\n"
            f"User Question/Prompt: {message}\n"
        )

        return await grok_chat(system_prompt, user_prompt, temperature=0.4)

    def _deterministic_mentor(
        self,
        message: str,
        context_type: str,
        learner_info: dict[str, Any],
    ) -> dict[str, Any]:
        target_career = learner_info.get("target_career") or "Full Stack Developer"
        readiness = learner_info.get("career_readiness_score", 0.0)
        skills = learner_info.get("skills", [])
        gaps = learner_info.get("gaps", [])
        recent_assessment = learner_info.get("recent_assessment")

        msg_lower = message.lower()

        # Handle specific common questions or assessment follow-ups
        if recent_assessment and ("assessment" in msg_lower or "score" in msg_lower or recent_assessment.get("percentage", 100) < 50):
            score = recent_assessment.get("percentage", 0)
            skill = recent_assessment.get("skill", "JavaScript")
            weak = recent_assessment.get("weak_topics", ["Fundamentals", "Functions"])
            weak_str = ", ".join(weak) if isinstance(weak, list) else str(weak)

            response_msg = (
                f"I reviewed your recent {skill} assessment ({score}%). While this score flagged critical gaps in {weak_str}, "
                f"this is exactly where targeted growth happens. Our Performance Agent has already adjusted your roadmap to inject "
                f"foundational exercises on these topics before moving to complex frameworks. "
                f"Focus on writing small functions by hand and tracing scope on paper before returning to the IDE."
            )
            suggestions = [
                f"Review {weak_str} documentation and syntax mental models",
                f"Complete 3 targeted coding exercises on {skill}",
                "Retake the diagnostic assessment after 48 hours of practice",
            ]
            resources = [
                {"title": f"{skill} MDN Web Docs", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript"},
                {"title": "JavaScript.info — The Modern JavaScript Tutorial", "url": "https://javascript.info"},
            ]
        elif "career" in msg_lower or "readiness" in msg_lower or context_type == "career":
            missing_names = [g.get("name", "") for g in gaps[:3]]
            response_msg = (
                f"Your current estimated readiness for {target_career} is {readiness}%. "
                f"Your primary strengths give you a solid analytical foundation, but the critical bottleneck "
                f"is bridging: {', '.join(missing_names) if missing_names else 'core frontend technologies'}. "
                f"Closing these gaps will move your readiness past the 75% benchmark where interview invitations accelerate."
            )
            suggestions = [
                f"Prioritize High-Urgency gap: {missing_names[0] if missing_names else 'Core tech'}",
                "Build one end-to-end portfolio project verifying both frontend and backend skills",
                "Simulate alternative career paths in the Career Simulator to see transferable strengths",
            ]
            resources = [
                {"title": f"Roadmap.sh — {target_career} Roadmap", "url": "https://roadmap.sh"},
                {"title": "Full Stack Open — Deep Dive Into Modern Web Development", "url": "https://fullstackopen.com/en/"},
            ]
        else:
            response_msg = (
                f"Welcome! As your AI Career Mentor for {target_career}, I track your real-time skill DNA and assessment history. "
                f"You are currently at {readiness}% career readiness. Feel free to ask me to explain any difficult concept, "
                f"break down why a specific skill gap matters for hiring managers, or walk you through an assessment mistake."
            )
            suggestions = [
                "Ask: 'Why did I struggle on my last assessment?'",
                f"Ask: 'What are the top 3 interview questions for {target_career}?'",
                "Ask: 'How does Python transfer to Machine Learning vs Full Stack?'",
            ]
            resources = [
                {"title": "COGNIFY AI Career Documentation", "url": "https://github.com"},
                {"title": "System Design Primer", "url": "https://github.com/donnemartin/system-design-primer"},
            ]

        return {
            "message": response_msg,
            "suggestions": suggestions,
            "resources": resources,
        }
