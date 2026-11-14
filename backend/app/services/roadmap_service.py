from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.learner import LearnerProfile, LearnerSkill
from app.models.career import CareerRole, CareerRequirement
from app.models.skill import Skill
from app.models.learning import LearningRoadmap, RoadmapTask
from app.schemas.roadmap import RoadmapResponse, RoadmapTaskResponse
from fastapi import HTTPException
import uuid


async def generate_roadmap(db: AsyncSession, user: User, career_id) -> dict:
    profile_result = await db.execute(
        select(LearnerProfile).where(LearnerProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    career_result = await db.execute(select(CareerRole).where(CareerRole.id == career_id))
    career = career_result.scalar_one_or_none()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")

    # Get gaps
    reqs = await db.execute(
        select(CareerRequirement).where(CareerRequirement.career_id == career_id)
    )
    requirements = reqs.scalars().all()

    ls_result = await db.execute(
        select(LearnerSkill).where(LearnerSkill.learner_id == profile.id)
    )
    learner_skills = {ls.skill_id: ls.proficiency for ls in ls_result.scalars().all()}

    # Create roadmap
    roadmap = LearningRoadmap(
        learner_id=profile.id,
        career_id=career_id,
        title=f"Roadmap to {career.title}",
        description=f"Personalized learning path to become a {career.title}",
    )
    db.add(roadmap)
    await db.flush()

    tasks = []
    order = 0
    week = 1
    total_hours = 0

    sorted_reqs = sorted(requirements, key=lambda r: (not r.is_critical, -r.importance))

    for req in sorted_reqs:
        current = learner_skills.get(req.skill_id, 0)
        gap = req.min_proficiency - current
        if gap <= 0:
            continue

        skill_result = await db.execute(select(Skill).where(Skill.id == req.skill_id))
        skill = skill_result.scalar_one_or_none()
        if not skill:
            continue

        hours = round(gap * 0.4, 1)
        difficulty = "beginner" if current < 30 else ("intermediate" if current < 60 else "advanced")

        task = RoadmapTask(
            roadmap_id=roadmap.id,
            skill_id=req.skill_id,
            title=f"Learn {skill.name}" if current < 20 else f"Improve {skill.name}",
            description=f"Bridge the gap from {current:.0f} to {req.min_proficiency:.0f} proficiency in {skill.name}",
            topic=skill.name,
            difficulty=difficulty,
            estimated_hours=hours,
            learning_objective=f"Achieve {req.min_proficiency:.0f}% proficiency in {skill.name}",
            recommended_resource=f"Practice {skill.name} through projects and tutorials",
            practical_exercise=f"Build a small project using {skill.name}",
            completion_criteria=f"Score {req.min_proficiency:.0f}% on {skill.name} assessment",
            priority=1 if req.is_critical else 0,
            week_number=week,
            order_index=order,
        )
        db.add(task)
        tasks.append(task)
        total_hours += hours
        order += 1
        if order % 3 == 0:
            week += 1

    roadmap.total_estimated_hours = total_hours
    await db.flush()

    task_responses = [RoadmapTaskResponse.model_validate(t) for t in tasks]

    return {
        "id": roadmap.id,
        "title": roadmap.title,
        "description": roadmap.description,
        "total_estimated_hours": total_hours,
        "status": roadmap.status,
        "tasks": task_responses,
        "weeks": week,
    }


async def get_roadmap(db: AsyncSession, user: User, career_id=None) -> dict:
    profile_result = await db.execute(
        select(LearnerProfile).where(LearnerProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    query = select(LearningRoadmap).where(LearningRoadmap.learner_id == profile.id)
    if career_id:
        query = query.where(LearningRoadmap.career_id == career_id)
    query = query.order_by(LearningRoadmap.created_at.desc())

    result = await db.execute(query)
    roadmap = result.scalar_one_or_none()
    if not roadmap:
        raise HTTPException(status_code=404, detail="No roadmap found")

    tasks_result = await db.execute(
        select(RoadmapTask).where(RoadmapTask.roadmap_id == roadmap.id).order_by(RoadmapTask.order_index)
    )
    tasks = tasks_result.scalars().all()

    max_week = max((t.week_number or 0 for t in tasks), default=0)

    return {
        "id": roadmap.id,
        "title": roadmap.title,
        "description": roadmap.description,
        "total_estimated_hours": roadmap.total_estimated_hours,
        "status": roadmap.status,
        "tasks": [RoadmapTaskResponse.model_validate(t) for t in tasks],
        "weeks": max_week,
    }


async def update_task(db: AsyncSession, user: User, task_id, status: str) -> dict:
    from datetime import datetime, timezone

    profile_result = await db.execute(
        select(LearnerProfile).where(LearnerProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    task_result = await db.execute(select(RoadmapTask).where(RoadmapTask.id == task_id))
    task = task_result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify ownership
    roadmap_result = await db.execute(
        select(LearningRoadmap).where(LearningRoadmap.id == task.roadmap_id)
    )
    roadmap = roadmap_result.scalar_one_or_none()
    if not roadmap or roadmap.learner_id != profile.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    task.status = status
    if status == "completed":
        task.completed_at = datetime.now(timezone.utc)
    await db.flush()

    return RoadmapTaskResponse.model_validate(task).model_dump()
