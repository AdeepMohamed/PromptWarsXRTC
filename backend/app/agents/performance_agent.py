"""
Agent 4 — Performance Analysis Agent.

Evaluates learner assessments, detects weak concepts, updates skill proficiency,
flags poor performance and stagnation, and generates targeted learning interventions.

Fallback: Derives evaluations deterministically from question answers, topic scoring,
and historical assessment records.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Optional

from pydantic import BaseModel, Field
from sqlalchemy import select

from app.agents.base_agent import AgentInput, AgentOutput, BaseAgent
from app.agents.grok_client import GrokAPIError, grok_chat

logger = logging.getLogger(__name__)


class ProficiencyUpdate(BaseModel):
    skill: str
    old: float
    new: float


class Intervention(BaseModel):
    type: str  # "remedial" | "reinforcement" | "advanced"
    skill: str
    topic: str
    action: str


class RoadmapModification(BaseModel):
    action: str  # "add_task" | "prioritize" | "review"
    skill: str
    topic: str
    reason: str


class PerformanceReport(BaseModel):
    score_analysis: dict[str, Any]
    weak_topics: list[str] = Field(default_factory=list)
    proficiency_updates: list[dict[str, Any]] = Field(default_factory=list)
    is_poor_performance: bool = False
    stagnation_detected: bool = False
    interventions: list[dict[str, Any]] = Field(default_factory=list)
    roadmap_modifications: list[dict[str, Any]] = Field(default_factory=list)


class PerformanceAgent(BaseAgent):
    name: str = "performance_agent"
    description: str = (
        "Evaluates assessments, identifies weak concepts, updates skill proficiency, "
        "detects learning stagnation, and initiates adaptive interventions."
    )

    async def execute(self, input_data: AgentInput, db) -> AgentOutput:
        data = input_data.data
        assessment_data = data.get("assessment", {})
        result_data = data.get("result", {})
        questions = data.get("questions", [])
        answers = result_data.get("answers", {})
        current_skills = data.get("skills", {})
        history = data.get("history", [])

        # Try Grok AI evaluation first
        try:
            ai_result = await self._run_grok(assessment_data, result_data, questions, answers, current_skills)
            validated = PerformanceReport(**ai_result)
            return AgentOutput(
                agent_name=self.name,
                status="completed",
                result=validated.model_dump(),
            )
        except Exception as exc:
            logger.info("Falling back to deterministic performance evaluation: %s", exc)
            fallback = self._deterministic_evaluation(
                assessment_data, result_data, questions, answers, current_skills, history
            )
            return AgentOutput(
                agent_name=self.name,
                status="completed",
                result=fallback,
            )

    async def _run_grok(
        self,
        assessment: dict[str, Any],
        result: dict[str, Any],
        questions: list[dict[str, Any]],
        answers: dict[str, Any],
        current_skills: dict[str, Any],
    ) -> dict[str, Any]:
        system_prompt = (
            "You are COGNIFY AI's Performance Agent. Evaluate the learner's assessment results. "
            "Analyze incorrect questions to identify weak concepts. Update proficiency realistically "
            "(a low score drops or establishes a low proficiency; a high score boosts it). "
            "Detect if score is poor (<50%) and recommend concrete remedial interventions.\n\n"
            "Return valid JSON strictly adhering to this schema:\n"
            "{\n"
            '  "score_analysis": {"score": float, "max": float, "percentage": float},\n'
            '  "weak_topics": ["topic1", "topic2"],\n'
            '  "proficiency_updates": [{"skill": "SkillName", "old": float, "new": float}],\n'
            '  "is_poor_performance": bool,\n'
            '  "stagnation_detected": bool,\n'
            '  "interventions": [{"type": "remedial", "skill": "SkillName", "topic": "Topic", "action": "Action"}],\n'
            '  "roadmap_modifications": [{"action": "add_task", "skill": "SkillName", "topic": "Topic", "reason": "Reason"}]\n'
            "}"
        )

        user_prompt = (
            f"Assessment: {assessment}\n"
            f"Score Summary: {result}\n"
            f"Questions & Keys: {questions}\n"
            f"Learner Answers: {answers}\n"
            f"Current Skills: {current_skills}\n"
        )

        return await grok_chat(system_prompt, user_prompt, temperature=0.2)

    def _deterministic_evaluation(
        self,
        assessment: dict[str, Any],
        result: dict[str, Any],
        questions: list[dict[str, Any]],
        answers: dict[str, Any],
        current_skills: dict[str, Any],
        history: list[dict[str, Any]],
    ) -> dict[str, Any]:
        skill_name = assessment.get("skill_name") or assessment.get("title") or "Technical"
        score = float(result.get("score", 0.0))
        max_score = float(result.get("max_score", 100.0))
        if max_score <= 0:
            max_score = 100.0
        percentage = round((score / max_score) * 100, 2)
        if "percentage" in result:
            percentage = round(float(result["percentage"]), 2)

        is_poor = percentage < 50.0

        # Topic breakdown
        topic_scores: dict[str, dict[str, int]] = {}
        for q in questions:
            qid = str(q.get("id"))
            topic = q.get("topic") or "General Fundamentals"
            correct = str(q.get("correct_answer", "")).strip()
            user_ans = str(answers.get(qid, "")).strip()

            if topic not in topic_scores:
                topic_scores[topic] = {"correct": 0, "total": 0}
            topic_scores[topic]["total"] += 1
            if user_ans and user_ans.lower() == correct.lower():
                topic_scores[topic]["correct"] += 1

        weak_topics: list[str] = []
        for topic, stats in topic_scores.items():
            if stats["total"] > 0 and (stats["correct"] / stats["total"]) < 0.6:
                weak_topics.append(topic)

        if not weak_topics and is_poor:
            # Fallback topics from assessment if any were wrong
            for q in questions:
                topic = q.get("topic")
                if topic and topic not in weak_topics:
                    weak_topics.append(topic)

        # Proficiency update calculation
        # New proficiency blends existing claimed/assessed proficiency with this test score
        old_prof = float(current_skills.get(skill_name, 0.0))
        if old_prof == 0:
            # Initial assessment establishes baseline
            new_prof = round(percentage * 0.85, 1) if percentage >= 50 else round(percentage * 0.6, 1)
        else:
            # 60% historical + 40% new performance
            new_prof = round(old_prof * 0.6 + percentage * 0.4, 1)

        new_prof = max(0.0, min(100.0, new_prof))

        proficiency_updates = [{
            "skill": skill_name,
            "old": old_prof,
            "new": new_prof,
        }]

        # Check for stagnation: 3 or more assessments in a row with < 5% delta
        stagnation_detected = False
        if len(history) >= 2:
            recent_percentages = [float(h.get("percentage", 0)) for h in history[-2:]]
            if all(abs(p - percentage) < 6 for p in recent_percentages) and percentage < 65:
                stagnation_detected = True

        # Interventions
        interventions: list[dict[str, Any]] = []
        roadmap_modifications: list[dict[str, Any]] = []

        if is_poor:
            for wt in (weak_topics[:3] or ["Core Fundamentals"]):
                interventions.append({
                    "type": "remedial",
                    "skill": skill_name,
                    "topic": wt,
                    "action": f"Assign focused remedial practice module on {wt}",
                })
                roadmap_modifications.append({
                    "action": "add_task",
                    "skill": skill_name,
                    "topic": f"{wt} Intensive Practice",
                    "reason": f"Remedial intervention: score {percentage}% identified key gaps in {wt}",
                })
        elif percentage >= 80:
            interventions.append({
                "type": "advanced",
                "skill": skill_name,
                "topic": "Advanced Mastery",
                "action": f"Unlock practical advanced portfolio project in {skill_name}",
            })
            roadmap_modifications.append({
                "action": "prioritize",
                "skill": skill_name,
                "topic": f"Advanced {skill_name} Application",
                "reason": f"High score {percentage}% demonstrates competency; fast-tracking to advanced topics",
            })

        return {
            "score_analysis": {
                "score": score,
                "max": max_score,
                "percentage": percentage,
            },
            "weak_topics": weak_topics,
            "proficiency_updates": proficiency_updates,
            "is_poor_performance": is_poor,
            "stagnation_detected": stagnation_detected,
            "interventions": interventions,
            "roadmap_modifications": roadmap_modifications,
        }
