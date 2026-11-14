import uuid
from typing import Optional, Any
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.learner import LearnerProfile
from app.models.agent import AgentActivityLog
from app.agents.orchestrator import CentralOrchestrator

router = APIRouter(prefix="/agents", tags=["Agent System"])
orchestrator = CentralOrchestrator()


@router.post("/orchestrate")
async def orchestrate(
    workflow: str = Body(..., embed=True),
    params: dict[str, Any] = Body(default_factory=dict, embed=True),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = (await db.execute(select(LearnerProfile).where(LearnerProfile.user_id == user.id))).scalar_one_or_none()
    if not profile:
        return {"error": "Learner profile not found"}

    learner_id = profile.id

    if workflow == "initial_analysis":
        career_id = params.get("career_id")
        career_uuid = uuid.UUID(career_id) if career_id else profile.target_career_id
        res = await orchestrator.initial_analysis(learner_id, career_uuid, db)
        return {"result": res}

    elif workflow == "assessment_update":
        res_id = params.get("assessment_result_id")
        if not res_id:
            return {"error": "assessment_result_id required"}
        res = await orchestrator.assessment_update(learner_id, uuid.UUID(str(res_id)), db)
        return {"result": res}

    elif workflow == "career_change":
        new_career_id = params.get("new_career_id")
        if not new_career_id:
            return {"error": "new_career_id required"}
        reason = params.get("reason", "Learner changed career aspiration")
        res = await orchestrator.career_change(learner_id, uuid.UUID(str(new_career_id)), db, reason)
        return {"result": res}

    return {"error": f"Unknown workflow: {workflow}"}


@router.get("/activity")
async def get_activity(
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = (await db.execute(select(LearnerProfile).where(LearnerProfile.user_id == user.id))).scalar_one_or_none()
    
    query = select(AgentActivityLog).order_by(desc(AgentActivityLog.created_at)).limit(limit)
    if profile:
        # Show this learner's activities or system activities
        query = query.where((AgentActivityLog.learner_id == profile.id) | (AgentActivityLog.learner_id == None))

    rows = (await db.execute(query)).scalars().all()

    return {
        "activities": [
            {
                "id": str(r.id),
                "agent_name": r.agent_name,
                "task": r.task,
                "status": r.status,
                "input_summary": r.input_summary,
                "output_summary": r.output_summary,
                "error_message": r.error_message,
                "duration_ms": r.processing_duration_ms,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            }
            for r in rows
        ]
    }
