import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.skill import Skill
from app.models.learner import LearnerProfile
from app.services.career_service import get_skill_gaps
from app.agents.orchestrator import CentralOrchestrator

router = APIRouter(prefix="/skills", tags=["Skills"])
orchestrator = CentralOrchestrator()


@router.get("")
async def list_skills(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Skill).where(Skill.is_active == True)
    if category:
        query = query.where(Skill.category == category)
    result = await db.execute(query)
    skills = result.scalars().all()
    return {"skills": [{"id": str(s.id), "name": s.name, "category": s.category, "description": s.description} for s in skills]}


@router.post("/analyze")
async def analyze_skills(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = (await db.execute(select(LearnerProfile).where(LearnerProfile.user_id == user.id))).scalar_one_or_none()
    if not profile:
        return {"error": "Learner profile not found"}
    result = await orchestrator.initial_analysis(profile.id, profile.target_career_id, db)
    return {"skill_analysis": result.get("skill_analysis", {})}


@router.get("/gaps")
async def skill_gaps(
    career_id: Optional[uuid.UUID] = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = (await db.execute(select(LearnerProfile).where(LearnerProfile.user_id == user.id))).scalar_one_or_none()
    target_id = career_id or (profile.target_career_id if profile else None)
    if not target_id:
        return {"gaps": []}
    gaps = await get_skill_gaps(db, user, target_id)
    return {"gaps": gaps}
