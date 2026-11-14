"""
Central Agent Orchestrator for COGNIFY AI.

Coordinates the 5 specialized AI agents:
1. Skill Agent
2. Career Agent
3. Learning Agent
4. Performance Agent
5. Mentor Agent

Implements the three core adaptive workflows:
- initial_analysis
- assessment_update
- career_change
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.agents.base_agent import AgentInput, AgentOutput
from app.agents.career_agent import CareerAgent
from app.agents.learning_agent import LearningAgent
from app.agents.mentor_agent import MentorAgent
from app.agents.performance_agent import PerformanceAgent
from app.agents.skill_agent import SkillAgent

from app.models.agent import AgentActivityLog
from app.models.analytics import CareerGoalHistory, LearningActivity
from app.models.assessment import Assessment, AssessmentQuestion, AssessmentResult
from app.models.career import CareerRequirement, CareerRole
from app.models.learner import LearnerProfile, LearnerSkill
from app.models.learning import LearningResource, LearningRoadmap, RoadmapTask
from app.models.skill import Skill

logger = logging.getLogger(__name__)


class CentralOrchestrator:
    """Coordinates multi-agent workflows and manages adaptive transitions."""

    def __init__(self):
        self.skill_agent = SkillAgent()
        self.career_agent = CareerAgent()
        self.learning_agent = LearningAgent()
        self.performance_agent = PerformanceAgent()
        self.mentor_agent = MentorAgent()

    # -----------------------------------------------------------------------
    # WORKFLOW 1: INITIAL ANALYSIS
    # -----------------------------------------------------------------------
    async def initial_analysis(
        self,
        learner_id: uuid.UUID,
        career_id: uuid.UUID | None,
        db,
    ) -> dict[str, Any]:
        """Execute end-to-end multi-agent skill & career readiness pipeline."""

        # 1. Fetch learner profile
        stmt = (
            select(LearnerProfile)
            .where(LearnerProfile.id == learner_id)
            .options(
                selectinload(LearnerProfile.skills).selectinload(LearnerSkill.skill),
                selectinload(LearnerProfile.target_career),
                selectinload(LearnerProfile.project_submissions),
                selectinload(LearnerProfile.assessment_results),
            )
        )
        res = await db.execute(stmt)
        profile = res.scalar_one_or_none()
        if not profile:
            raise ValueError(f"LearnerProfile {learner_id} not found")

        # Set target career if supplied
        if career_id:
            profile.target_career_id = career_id
            await db.flush()

        effective_career_id = profile.target_career_id
        if not effective_career_id:
            # Fallback to default Full Stack Developer if none set
            career_stmt = select(CareerRole).where(CareerRole.slug == "full-stack-developer")
            c_res = await db.execute(career_stmt)
            default_career = c_res.scalar_one_or_none()
            if default_career:
                effective_career_id = default_career.id
                profile.target_career_id = default_career.id
                await db.flush()

        # Fetch Career details
        career_obj = None
        if effective_career_id:
            c_stmt = select(CareerRole).where(CareerRole.id == effective_career_id)
            c_res = await db.execute(c_stmt)
            career_obj = c_res.scalar_one_or_none()

        # Build agent payload
        existing_skills_map = {
            ls.skill.name: ls.proficiency for ls in profile.skills if ls.skill
        }

        # Step A: Skill Agent
        skill_input = AgentInput(
            learner_id=learner_id,
            data={
                "profile": {
                    "bio": profile.bio,
                    "education_level": profile.education_level,
                    "years_experience": profile.years_experience,
                    "certifications": profile.certifications or [],
                },
                "skills": [
                    {"name": ls.skill.name, "proficiency": ls.proficiency, "confidence": ls.confidence}
                    for ls in profile.skills if ls.skill
                ],
                "assessments": [
                    {"percentage": ar.percentage, "score": ar.score}
                    for ar in profile.assessment_results
                ],
                "projects": [
                    {"title": p.title, "technologies": p.technologies or []}
                    for p in profile.project_submissions
                ],
            },
        )
        skill_output = await self.skill_agent.safe_execute(skill_input, db)

        # Step B: Career Agent
        req_stmt = select(CareerRequirement).where(CareerRequirement.career_id == effective_career_id).options(selectinload(CareerRequirement.skill))
        req_res = await db.execute(req_stmt)
        req_rows = req_res.scalars().all()

        career_reqs = [
            {
                "skill_name": r.skill.name if r.skill else "Unknown",
                "importance": r.importance,
                "min_proficiency": r.min_proficiency,
                "is_critical": r.is_critical,
                "description": r.description,
            }
            for r in req_rows
        ]

        career_input = AgentInput(
            learner_id=learner_id,
            data={
                "career_id": str(effective_career_id),
                "target_career": {
                    "id": str(career_obj.id) if career_obj else "",
                    "title": career_obj.title if career_obj else "Target Role",
                },
                "career_requirements": career_reqs,
                "learner_skills": existing_skills_map,
            },
        )
        career_output = await self.career_agent.safe_execute(career_input, db)

        # Update readiness on profile
        readiness_score = float(career_output.result.get("career", {}).get("readiness_score", 0.0))
        profile.career_readiness_score = readiness_score
        profile.last_analysis_at = datetime.now(timezone.utc)

        # Step C: Learning Agent
        # Fetch available resources
        res_stmt = select(LearningResource).options(selectinload(LearningResource.skill))
        res_rows = (await db.execute(res_stmt)).scalars().all()
        db_resources = [
            {
                "skill_name": r.skill.name if r.skill else "",
                "title": r.title,
                "difficulty": r.difficulty,
                "estimated_duration_hours": r.estimated_duration_hours,
                "provider": r.provider,
                "url": r.url,
                "is_free": r.is_free,
            }
            for r in res_rows
        ]

        learning_input = AgentInput(
            learner_id=learner_id,
            data={
                "career_id": str(effective_career_id),
                "career_title": career_obj.title if career_obj else "Target Role",
                "skill_gaps": career_output.result.get("missing_skills", []),
                "critical_gaps": career_output.result.get("critical_gaps", []),
                "learning_resources": db_resources,
            },
        )
        learning_output = await self.learning_agent.safe_execute(learning_input, db)

        # Save Roadmap to Neon DB
        # First archive any existing active roadmaps for this career
        old_roadmaps = (
            await db.execute(
                select(LearningRoadmap)
                .where(LearningRoadmap.learner_id == learner_id, LearningRoadmap.status == "active")
            )
        ).scalars().all()
        for r in old_roadmaps:
            r.status = "archived"

        roadmap_data = learning_output.result.get("roadmap", {})
        new_roadmap = LearningRoadmap(
            id=uuid.uuid4(),
            learner_id=learner_id,
            career_id=effective_career_id,
            title=roadmap_data.get("title", f"{career_obj.title if career_obj else 'Career'} Roadmap"),
            description=f"Personalized 6-week curriculum generated by COGNIFY AI Learning Agent.",
            total_estimated_hours=roadmap_data.get("total_hours", 0.0),
            status="active",
            generated_by="ai",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(new_roadmap)
        await db.flush()

        # Skill lookup map
        all_skills_stmt = select(Skill)
        all_skills = {s.name.lower(): s.id for s in (await db.execute(all_skills_stmt)).scalars().all()}

        # Create Roadmap Tasks
        tasks_created = []
        for t in roadmap_data.get("tasks", []):
            skill_name = t.get("skill", "General")
            s_id = all_skills.get(skill_name.lower())
            if not s_id and all_skills:
                s_id = next(iter(all_skills.values()))

            task_obj = RoadmapTask(
                id=uuid.uuid4(),
                roadmap_id=new_roadmap.id,
                skill_id=s_id,
                title=t.get("topic") or t.get("description") or f"Learn {skill_name}",
                description=t.get("description"),
                topic=t.get("topic"),
                difficulty=t.get("difficulty", "beginner"),
                estimated_hours=float(t.get("estimated_hours", 4.0)),
                learning_objective=t.get("learning_objective"),
                recommended_resource=t.get("recommended_resource"),
                practical_exercise=t.get("practical_exercise"),
                completion_criteria=t.get("completion_criteria"),
                priority=int(t.get("priority", 1)),
                week_number=int(t.get("week_number", 1)),
                order_index=int(t.get("order_index", 1)),
                status="pending",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(task_obj)
            tasks_created.append(task_obj)

        # Activity log
        activity = LearningActivity(
            id=uuid.uuid4(),
            learner_id=learner_id,
            activity_type="skill_update",
            description=f"Completed initial AI analysis for {career_obj.title if career_obj else 'Career'}. Readiness: {readiness_score}%.",
            activity_metadata={
                "readiness": readiness_score,
                "career": career_obj.title if career_obj else "",
                "tasks_count": len(tasks_created),
            },
            created_at=datetime.now(timezone.utc),
        )
        db.add(activity)
        await db.commit()

        return {
            "learner_id": str(learner_id),
            "career": career_output.result.get("career", {}),
            "skill_analysis": skill_output.result,
            "career_analysis": career_output.result,
            "roadmap": {
                "id": str(new_roadmap.id),
                "title": new_roadmap.title,
                "total_hours": new_roadmap.total_estimated_hours,
                "tasks_count": len(tasks_created),
            },
            "agent_activities": [
                {"agent": skill_output.agent_name, "status": skill_output.status, "duration_ms": skill_output.processing_duration_ms},
                {"agent": career_output.agent_name, "status": career_output.status, "duration_ms": career_output.processing_duration_ms},
                {"agent": learning_output.agent_name, "status": learning_output.status, "duration_ms": learning_output.processing_duration_ms},
            ],
        }

    # -----------------------------------------------------------------------
    # WORKFLOW 2: ADAPTIVE ASSESSMENT UPDATE
    # -----------------------------------------------------------------------
    async def assessment_update(
        self,
        learner_id: uuid.UUID,
        assessment_result_id: uuid.UUID,
        db,
    ) -> dict[str, Any]:
        """Evaluate assessment, update proficiency, adapt roadmap, and engage Mentor Agent."""

        # Fetch assessment result
        res_stmt = (
            select(AssessmentResult)
            .where(AssessmentResult.id == assessment_result_id)
            .options(selectinload(AssessmentResult.assessment).selectinload(Assessment.skill))
        )
        res_row = (await db.execute(res_stmt)).scalar_one_or_none()
        if not res_row:
            raise ValueError(f"AssessmentResult {assessment_result_id} not found")

        assessment = res_row.assessment
        skill_name = assessment.skill.name if assessment and assessment.skill else "General"

        # Fetch questions
        q_stmt = select(AssessmentQuestion).where(AssessmentQuestion.assessment_id == assessment.id)
        questions = (await db.execute(q_stmt)).scalars().all()
        q_dicts = [
            {
                "id": str(q.id),
                "question_text": q.question_text,
                "topic": q.topic,
                "correct_answer": q.correct_answer,
                "points": q.points,
            }
            for q in questions
        ]

        # Fetch learner current skills
        ls_stmt = (
            select(LearnerSkill)
            .where(LearnerSkill.learner_id == learner_id)
            .options(selectinload(LearnerSkill.skill))
        )
        existing_ls = (await db.execute(ls_stmt)).scalars().all()
        skills_map = {ls.skill.name: ls.proficiency for ls in existing_ls if ls.skill}

        # Step A: Performance Agent
        perf_input = AgentInput(
            learner_id=learner_id,
            data={
                "assessment": {
                    "title": assessment.title,
                    "skill_name": skill_name,
                    "passing_score": assessment.passing_score,
                },
                "result": {
                    "score": res_row.score,
                    "max_score": res_row.max_score,
                    "percentage": res_row.percentage,
                    "answers": res_row.answers or {},
                },
                "questions": q_dicts,
                "skills": skills_map,
            },
        )
        perf_output = await self.performance_agent.safe_execute(perf_input, db)
        perf_res = perf_output.result

        # Update weak_topics in AssessmentResult
        res_row.weak_topics = perf_res.get("weak_topics", [])

        # Update LearnerSkill table
        updated_prof = 0.0
        for up in perf_res.get("proficiency_updates", []):
            target_skill_name = up.get("skill")
            new_prof = float(up.get("new", 0.0))
            updated_prof = new_prof

            # Find matching LearnerSkill row
            matched = False
            for ls in existing_ls:
                if ls.skill and ls.skill.name.lower() == target_skill_name.lower():
                    ls.proficiency = new_prof
                    ls.confidence = "assessed"
                    ls.source = "assessment"
                    ls.last_assessed_at = datetime.now(timezone.utc)
                    matched = True
                    break

            if not matched:
                # Skill didn't exist in profile yet, create row
                skill_obj_stmt = select(Skill).where(Skill.name.ilike(target_skill_name))
                skill_obj = (await db.execute(skill_obj_stmt)).scalar_one_or_none()
                if skill_obj:
                    new_ls = LearnerSkill(
                        id=uuid.uuid4(),
                        learner_id=learner_id,
                        skill_id=skill_obj.id,
                        proficiency=new_prof,
                        confidence="assessed",
                        source="assessment",
                        last_assessed_at=datetime.now(timezone.utc),
                        created_at=datetime.now(timezone.utc),
                        updated_at=datetime.now(timezone.utc),
                    )
                    db.add(new_ls)

        # Step B: Recalculate Career Readiness
        profile = (await db.execute(select(LearnerProfile).where(LearnerProfile.id == learner_id))).scalar_one()
        if profile.target_career_id:
            req_stmt = (
                select(CareerRequirement)
                .where(CareerRequirement.career_id == profile.target_career_id)
                .options(selectinload(CareerRequirement.skill))
            )
            reqs = (await db.execute(req_stmt)).scalars().all()
            total_weighted = 0.0
            total_weight = 0.0
            updated_skills_map = {**skills_map, skill_name: updated_prof}

            for r in reqs:
                s_name = r.skill.name if r.skill else ""
                prof = updated_skills_map.get(s_name, 0.0)
                total_weighted += (prof * r.importance)
                total_weight += (r.importance * 100.0)

            if total_weight > 0:
                profile.career_readiness_score = round((total_weighted / total_weight) * 100, 2)

        # Step C: If Poor Performance or Interventions triggered -> Inject tasks into active roadmap
        injected_tasks = []
        is_poor = perf_res.get("is_poor_performance", False)
        active_roadmap_stmt = (
            select(LearningRoadmap)
            .where(LearningRoadmap.learner_id == learner_id, LearningRoadmap.status == "active")
        )
        active_roadmap = (await db.execute(active_roadmap_stmt)).scalar_one_or_none()

        if active_roadmap and (is_poor or perf_res.get("roadmap_modifications")):
            skill_obj = (await db.execute(select(Skill).where(Skill.name.ilike(skill_name)))).scalar_one_or_none()
            for mod in perf_res.get("roadmap_modifications", []):
                new_task = RoadmapTask(
                    id=uuid.uuid4(),
                    roadmap_id=active_roadmap.id,
                    skill_id=skill_obj.id if skill_obj else assessment.skill_id,
                    title=f"[Intervention] {mod.get('topic')}",
                    description=mod.get("reason"),
                    topic=mod.get("topic"),
                    difficulty="beginner" if is_poor else "intermediate",
                    estimated_hours=3.5,
                    learning_objective=f"Reinforce core concept: {mod.get('topic')}",
                    recommended_resource="Interactive Remedial Sandbox & Documentation",
                    practical_exercise=f"Solve 5 deliberate practice exercises focusing on {mod.get('topic')}",
                    completion_criteria="Complete code challenges and achieve 80%+ on retry diagnostic",
                    priority=1,
                    week_number=1,  # immediate priority
                    order_index=0,
                    status="pending",
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                db.add(new_task)
                injected_tasks.append(new_task.title)

        # Step D: Mentor Agent Briefing
        mentor_input = AgentInput(
            learner_id=learner_id,
            data={
                "message": f"I just completed my {skill_name} assessment and scored {res_row.percentage}%. What should I do next?",
                "context": "assessment",
                "learner_info": {
                    "profile": {"education": profile.education_level},
                    "target_career": "Target Career",
                    "career_readiness_score": profile.career_readiness_score,
                    "skills": [{"name": k, "proficiency": v} for k, v in skills_map.items()],
                    "recent_assessment": {
                        "skill": skill_name,
                        "percentage": res_row.percentage,
                        "weak_topics": perf_res.get("weak_topics", []),
                    },
                },
            },
        )
        mentor_output = await self.mentor_agent.safe_execute(mentor_input, db)

        # Record activity
        activity = LearningActivity(
            id=uuid.uuid4(),
            learner_id=learner_id,
            activity_type="assessment",
            description=f"Submitted {skill_name} Assessment with score {res_row.percentage}%. System triggered {'Remedial Intervention' if is_poor else 'Competency Advancement'}.",
            activity_metadata={
                "score": res_row.score,
                "percentage": res_row.percentage,
                "is_poor": is_poor,
                "injected_tasks": injected_tasks,
            },
            created_at=datetime.now(timezone.utc),
        )
        db.add(activity)
        await db.commit()

        return {
            "assessment_id": str(assessment.id),
            "score": res_row.score,
            "percentage": res_row.percentage,
            "performance_evaluation": perf_res,
            "new_career_readiness": profile.career_readiness_score,
            "adapted_tasks": injected_tasks,
            "mentor_feedback": mentor_output.result,
        }

    # -----------------------------------------------------------------------
    # WORKFLOW 3: CAREER GOAL CHANGE
    # -----------------------------------------------------------------------
    async def career_change(
        self,
        learner_id: uuid.UUID,
        new_career_id: uuid.UUID,
        db,
        reason: str = "Learner changed career aspiration",
    ) -> dict[str, Any]:
        """Detect career change, preserve transferable competencies, and adapt roadmap."""

        profile = (await db.execute(select(LearnerProfile).where(LearnerProfile.id == learner_id))).scalar_one_or_none()
        if not profile:
            raise ValueError(f"LearnerProfile {learner_id} not found")

        old_career_id = profile.target_career_id
        old_readiness = profile.career_readiness_score

        # Record career goal history
        history_entry = CareerGoalHistory(
            id=uuid.uuid4(),
            learner_id=learner_id,
            previous_career_id=old_career_id,
            new_career_id=new_career_id,
            readiness_at_change=old_readiness,
            reason=reason,
            created_at=datetime.now(timezone.utc),
        )
        db.add(history_entry)

        # Archive active roadmaps
        active_roadmaps = (
            await db.execute(
                select(LearningRoadmap)
                .where(LearningRoadmap.learner_id == learner_id, LearningRoadmap.status == "active")
            )
        ).scalars().all()
        for r in active_roadmaps:
            r.status = "archived"

        # Update profile career
        profile.target_career_id = new_career_id
        await db.flush()

        # Re-run initial analysis for new career
        analysis_result = await self.initial_analysis(learner_id, new_career_id, db)

        # Log career change activity
        activity = LearningActivity(
            id=uuid.uuid4(),
            learner_id=learner_id,
            activity_type="career_change",
            description=f"Switched target career path. Regenerated personalized roadmap while preserving demonstrated skills.",
            activity_metadata={
                "previous_career_id": str(old_career_id) if old_career_id else None,
                "new_career_id": str(new_career_id),
                "new_readiness": profile.career_readiness_score,
            },
            created_at=datetime.now(timezone.utc),
        )
        db.add(activity)
        await db.commit()

        return {
            "status": "career_switched",
            "previous_readiness": old_readiness,
            "new_readiness": profile.career_readiness_score,
            "analysis": analysis_result,
        }
