from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.learner import LearnerProfileUpdate, AddSkillsRequest
from app.services.learner_service import get_learner_profile, update_learner_profile, add_learner_skills

router = APIRouter(prefix="/learner", tags=["Learner"])


@router.get("/profile")
async def get_profile(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await get_learner_profile(db, user)
    return {"profile": profile}


@router.put("/profile")
async def update_profile(
    data: LearnerProfileUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    updated = await update_learner_profile(db, user, data)
    return {"profile": updated}


@router.post("/skills")
async def add_skills(
    data: AddSkillsRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    skills = await add_learner_skills(db, user, data)
    return {"skills": skills}
