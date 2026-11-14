import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.learner import LearnerProfile
from app.schemas.roadmap import TaskUpdate
from app.services.roadmap_service import generate_roadmap, get_roadmap as get_active_roadmap, update_task as update_task_status
from app.agents.orchestrator import CentralOrchestrator

router = APIRouter(prefix="/roadmap", tags=["Roadmap"])
orchestrator = CentralOrchestrator()


@router.post("/generate")
async def create_roadmap(
    career_id: Optional[uuid.UUID] = Body(None, embed=True),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = (await db.execute(select(LearnerProfile).where(LearnerProfile.user_id == user.id))).scalar_one_or_none()
    if not profile:
        return {"error": "Profile not found"}
    result = await orchestrator.initial_analysis(profile.id, career_id or profile.target_career_id, db)
    return {"roadmap": result.get("roadmap", {})}


@router.get("")
async def get_roadmap(
    career_id: Optional[uuid.UUID] = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    roadmap = await get_active_roadmap(db, user, career_id)
    return {"roadmap": roadmap}


@router.put("/tasks/{task_id}")
async def update_task(
    task_id: uuid.UUID,
    data: TaskUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await update_task_status(db, user, task_id, data.status)
    return {"task": task}
