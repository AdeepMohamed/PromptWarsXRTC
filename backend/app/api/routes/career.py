import uuid
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.career import CareerAnalyzeRequest, CareerSimulateRequest, CareerGoalRequest
from app.services.career_service import (
    list_careers, analyze_career, simulate_careers, set_career_goal
)
from app.agents.orchestrator import CentralOrchestrator

router = APIRouter(prefix="", tags=["Careers"])
orchestrator = CentralOrchestrator()


@router.get("/careers")
async def get_careers(db: AsyncSession = Depends(get_db)):
    careers = await list_careers(db)
    return {"careers": careers}


@router.post("/career/analyze")
async def analyze(
    data: CareerAnalyzeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    analysis = await analyze_career(db, user, data.career_id)
    return {"analysis": analysis}


@router.post("/career/simulate")
async def simulate(
    data: CareerSimulateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    simulations = await simulate_careers(db, user, data.career_ids)
    return {"simulations": simulations}


@router.put("/career/goal")
async def set_goal(
    data: CareerGoalRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.models.learner import LearnerProfile
    from sqlalchemy import select
    profile = (await db.execute(select(LearnerProfile).where(LearnerProfile.user_id == user.id))).scalar_one_or_none()
    
    if profile:
        result = await orchestrator.career_change(profile.id, data.career_id, db)
        return result
    else:
        return await set_career_goal(db, user, data.career_id)
