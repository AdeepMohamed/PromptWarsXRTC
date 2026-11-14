from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.user import User
from app.models.learner import LearnerProfile, LearnerSkill
from app.models.skill import Skill
from app.models.assessment import AssessmentResult
from app.models.learning import LearningRoadmap, RoadmapTask
from app.models.analytics import LearningActivity
from app.models.agent import AgentActivityLog
from app.schemas.analytics import DashboardResponse, ProgressResponse
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone


async def get_dashboard(db: AsyncSession, user: User) -> dict:
    profile_result = await db.execute(
        select(LearnerProfile).where(LearnerProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # 1. Fetch skills with joined skill name in 1 query
    skills_res = await db.execute(
        select(LearnerSkill, Skill.name)
        .join(Skill, LearnerSkill.skill_id == Skill.id)
        .where(LearnerSkill.learner_id == profile.id)
    )
    skill_rows = skills_res.all()
    total_skills = len(skill_rows)
    skills_mastered = sum(1 for ls, _ in skill_rows if ls.proficiency >= 70)

    recommendations = []
    for ls, sname in skill_rows:
        if ls.proficiency < 30:
            recommendations.append(f"Start learning {sname} — currently at {ls.proficiency:.0f}%")
            if len(recommendations) >= 3:
                break

    # 2. Fetch all roadmap tasks in 1 query
    tasks_res = await db.execute(
        select(RoadmapTask)
        .join(LearningRoadmap, RoadmapTask.roadmap_id == LearningRoadmap.id)
        .where(LearningRoadmap.learner_id == profile.id)
    )
    tasks = tasks_res.scalars().all()
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.status == "completed")
    upcoming = [
        {"id": str(t.id), "title": t.title, "status": t.status, "week": t.week_number}
        for t in tasks if t.status in ("pending", "in_progress")
    ]
    learning_progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    # 3. Recent assessments
    assess_result = await db.execute(
        select(AssessmentResult)
        .where(AssessmentResult.learner_id == profile.id)
        .order_by(AssessmentResult.completed_at.desc())
        .limit(5)
    )
    recent_assessments = [
        {"id": str(r.id), "score": r.percentage, "completed_at": r.completed_at.isoformat() if r.completed_at else None}
        for r in assess_result.scalars().all()
    ]

    # 4. Recent agent decisions
    agent_result = await db.execute(
        select(AgentActivityLog)
        .where(AgentActivityLog.learner_id == profile.id)
        .order_by(AgentActivityLog.created_at.desc())
        .limit(5)
    )
    agent_decisions = [
        {"agent": a.agent_name, "task": a.task, "status": a.status}
        for a in agent_result.scalars().all()
    ]

    # 5. Weekly activity
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    activity_result = await db.execute(
        select(LearningActivity)
        .where(LearningActivity.learner_id == profile.id, LearningActivity.created_at >= week_ago)
    )
    weekly = [
        {"type": a.activity_type, "description": a.description, "date": a.created_at.isoformat() if a.created_at else None}
        for a in activity_result.scalars().all()
    ]

    return DashboardResponse(
        career_readiness=profile.career_readiness_score,
        skills_mastered=skills_mastered,
        total_skills=total_skills,
        learning_progress=round(learning_progress, 1),
        recent_assessments=recent_assessments,
        upcoming_tasks=upcoming[:5],
        weekly_activity=weekly,
        recent_agent_decisions=agent_decisions,
        recommendations=recommendations,
    ).model_dump()


async def get_progress(db: AsyncSession, user: User, period: str = "30d") -> dict:
    profile_result = await db.execute(
        select(LearnerProfile).where(LearnerProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    days = int(period.replace("d", "")) if "d" in period else 30
    since = datetime.now(timezone.utc) - timedelta(days=days)

    # Assessment scores
    assess_result = await db.execute(
        select(AssessmentResult)
        .where(AssessmentResult.learner_id == profile.id, AssessmentResult.completed_at >= since)
        .order_by(AssessmentResult.completed_at)
    )
    assessment_scores = [
        {"score": r.percentage, "date": r.completed_at.isoformat() if r.completed_at else None}
        for r in assess_result.scalars().all()
    ]

    # Activities by type
    activity_result = await db.execute(
        select(LearningActivity)
        .where(LearningActivity.learner_id == profile.id, LearningActivity.created_at >= since)
    )
    activities = activity_result.scalars().all()
    by_type = {}
    for a in activities:
        by_type[a.activity_type] = by_type.get(a.activity_type, 0) + 1

    return ProgressResponse(
        skill_improvements=[],
        assessment_scores=assessment_scores,
        readiness_history=[],
        activities_by_type=by_type,
    ).model_dump()
