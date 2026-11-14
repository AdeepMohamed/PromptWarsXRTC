from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.learner import LearnerProfile
from app.models.project import ProjectSubmission
from app.schemas.project import ProjectSubmitRequest, ProjectResponse
from fastapi import HTTPException


async def submit_project(db: AsyncSession, user: User, data: ProjectSubmitRequest) -> dict:
    profile_result = await db.execute(
        select(LearnerProfile).where(LearnerProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    project = ProjectSubmission(
        learner_id=profile.id,
        title=data.title,
        description=data.description,
        technologies=data.technologies,
        github_url=data.github_url,
        outcomes=data.outcomes,
        demonstrated_skills=[],
        ai_analysis="Project submitted successfully. AI analysis pending.",
    )
    db.add(project)
    await db.flush()

    return ProjectResponse.model_validate(project).model_dump()


async def list_projects(db: AsyncSession, user: User) -> list:
    profile_result = await db.execute(
        select(LearnerProfile).where(LearnerProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    result = await db.execute(
        select(ProjectSubmission)
        .where(ProjectSubmission.learner_id == profile.id)
        .order_by(ProjectSubmission.created_at.desc())
    )
    projects = result.scalars().all()
    return [ProjectResponse.model_validate(p).model_dump() for p in projects]
