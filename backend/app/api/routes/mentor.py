from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.learner import LearnerProfile, LearnerSkill
from app.models.career import CareerRole, CareerRequirement
from app.schemas.mentor import MentorChatRequest
from app.agents.base_agent import AgentInput
from app.agents.mentor_agent import MentorAgent

router = APIRouter(prefix="/mentor", tags=["AI Mentor"])
mentor_agent = MentorAgent()


@router.post("/chat")
async def mentor_chat(
    data: MentorChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = (
        await db.execute(
            select(LearnerProfile)
            .where(LearnerProfile.user_id == user.id)
            .options(
                selectinload(LearnerProfile.skills).selectinload(LearnerSkill.skill),
                selectinload(LearnerProfile.target_career),
                selectinload(LearnerProfile.assessment_results),
            )
        )
    ).scalar_one_or_none()

    if not profile:
        return {"response": {"message": "Learner profile not found.", "suggestions": [], "resources": []}}

    # Gaps and recent assessment
    gaps = []
    if profile.target_career_id:
        reqs = (
            await db.execute(
                select(CareerRequirement)
                .where(CareerRequirement.career_id == profile.target_career_id)
                .options(selectinload(CareerRequirement.skill))
            )
        ).scalars().all()
        skills_map = {ls.skill.name.lower(): ls.proficiency for ls in profile.skills if ls.skill}
        for r in reqs:
            s_name = r.skill.name if r.skill else ""
            cur = skills_map.get(s_name.lower(), 0.0)
            if cur < r.min_proficiency:
                gaps.append({"name": s_name, "gap": r.min_proficiency - cur})

    recent_ar = profile.assessment_results[-1] if profile.assessment_results else None

    learner_info = {
        "profile": {
            "bio": profile.bio,
            "education": profile.education_level,
            "experience": profile.years_experience,
        },
        "target_career": profile.target_career.title if profile.target_career else "General",
        "career_readiness_score": profile.career_readiness_score,
        "skills": [{"name": ls.skill.name, "proficiency": ls.proficiency} for ls in profile.skills if ls.skill],
        "gaps": gaps,
        "recent_assessment": {
            "score": recent_ar.score if recent_ar else 0,
            "percentage": recent_ar.percentage if recent_ar else 0,
            "weak_topics": recent_ar.weak_topics if recent_ar else [],
        } if recent_ar else None,
    }

    agent_input = AgentInput(
        learner_id=profile.id,
        data={
            "message": data.message,
            "context": data.context or "general",
            "learner_info": learner_info,
        },
    )

    output = await mentor_agent.safe_execute(agent_input, db)
    await db.commit()
    return {"response": output.result}
