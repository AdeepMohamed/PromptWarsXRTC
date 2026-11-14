import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.learner import LearnerProfile
from app.schemas.assessment import AssessmentSubmitRequest
from app.services.assessment_service import (
    list_assessments, get_assessment, submit_assessment, get_results as get_assessment_results
)
from app.agents.orchestrator import CentralOrchestrator

router = APIRouter(prefix="/assessments", tags=["Assessments"])
orchestrator = CentralOrchestrator()


@router.get("")
async def get_assessments(
    skill_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    assessments = await list_assessments(db, skill_id)
    return {"assessments": assessments}


@router.get("/results")
async def get_results_list(
    skill_id: Optional[uuid.UUID] = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    results = await get_assessment_results(db, user, skill_id)
    return {"results": results}


@router.get("/{assessment_id}")
async def get_assessment_detail(
    assessment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    assessment = await get_assessment(db, assessment_id)
    return {"assessment": assessment}


@router.post("/submit")
async def submit(
    data: AssessmentSubmitRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = (await db.execute(select(LearnerProfile).where(LearnerProfile.user_id == user.id))).scalar_one_or_none()
    if not profile:
        return {"error": "Profile not found"}

    # Grade and persist
    submission_res = await submit_assessment(
        db, user, data.assessment_id, data.answers, data.time_taken_seconds
    )
    
    # Trigger multi-agent adaptive workflow
    adaptation_res = await orchestrator.assessment_update(profile.id, submission_res["result_id"], db)

    return {
        "result": {
            **submission_res,
            "adaptation": adaptation_res,
        }
    }
