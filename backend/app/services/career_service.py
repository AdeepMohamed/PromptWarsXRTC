from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.learner import LearnerProfile, LearnerSkill
from app.models.career import CareerRole, CareerRequirement
from app.models.skill import Skill
from app.models.analytics import CareerGoalHistory
from app.schemas.career import (
    CareerResponse, CareerAnalysisResponse, SimulationResult, SkillGapResponse
)
from fastapi import HTTPException


async def list_careers(db: AsyncSession) -> list:
    result = await db.execute(select(CareerRole).where(CareerRole.is_active == True))
    careers = result.scalars().all()
    return [CareerResponse.model_validate(c) for c in careers]


async def analyze_career(db: AsyncSession, user: User, career_id) -> dict:
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

    # Get requirements with joined Skill names in a single query (eliminating N+1 query loop)
    reqs = await db.execute(
        select(CareerRequirement, Skill.name)
        .join(Skill, CareerRequirement.skill_id == Skill.id)
        .where(CareerRequirement.career_id == career_id)
    )
    requirements_data = reqs.all()

    # Get learner skills
    ls_result = await db.execute(
        select(LearnerSkill).where(LearnerSkill.learner_id == profile.id)
    )
    learner_skills = {ls.skill_id: ls.proficiency for ls in ls_result.scalars().all()}

    strong = []
    missing = []
    critical_gaps = []
    total_score = 0
    total_weight = 0

    for req, skill_name in requirements_data:
        current = learner_skills.get(req.skill_id, 0)
        gap = max(0, req.min_proficiency - current)

        weighted = min(current / req.min_proficiency, 1.0) * req.importance if req.min_proficiency > 0 else req.importance
        total_score += weighted
        total_weight += req.importance

        entry = {"skill": skill_name, "current": current, "required": req.min_proficiency, "importance": req.importance, "gap": gap}

        if current >= req.min_proficiency:
            strong.append(entry)
        else:
            missing.append(entry)
            if req.is_critical:
                critical_gaps.append(entry)

    readiness = (total_score / total_weight * 100) if total_weight > 0 else 0

    recommendations = []
    for m in sorted(missing, key=lambda x: x["importance"], reverse=True)[:5]:
        recommendations.append(f"Focus on improving {m['skill']} (gap: {m['gap']:.0f} points)")

    return {
        "career": CareerResponse.model_validate(career),
        "readiness_score": round(readiness, 1),
        "strong_skills": strong,
        "missing_skills": missing,
        "critical_gaps": critical_gaps,
        "recommendations": recommendations,
    }


async def simulate_careers(db: AsyncSession, user: User, career_ids: list) -> list:
    results = []
    for cid in career_ids:
        analysis = await analyze_career(db, user, cid)
        effort = sum(m["gap"] * 0.5 for m in analysis["missing_skills"])
        results.append(SimulationResult(
            career=analysis["career"],
            readiness=analysis["readiness_score"],
            required_skills=[s["skill"] for s in analysis["strong_skills"] + analysis["missing_skills"]],
            missing_skills=[s["skill"] for s in analysis["missing_skills"]],
            effort_hours=round(effort, 1),
            transferable_skills=[s["skill"] for s in analysis["strong_skills"]],
        ))
    return results


async def set_career_goal(db: AsyncSession, user: User, career_id) -> dict:
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

    # Record history
    history = CareerGoalHistory(
        learner_id=profile.id,
        previous_career_id=profile.target_career_id,
        new_career_id=career_id,
        readiness_at_change=profile.career_readiness_score,
    )
    db.add(history)

    profile.target_career_id = career_id
    await db.flush()

    analysis = await analyze_career(db, user, career_id)

    return {
        "profile": {"target_career_id": str(career_id)},
        "gap_analysis": analysis,
    }


async def get_skill_gaps(db: AsyncSession, user: User, career_id) -> list:
    profile_result = await db.execute(
        select(LearnerProfile).where(LearnerProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    reqs = await db.execute(
        select(CareerRequirement, Skill.name)
        .join(Skill, CareerRequirement.skill_id == Skill.id)
        .where(CareerRequirement.career_id == career_id)
    )
    requirements_data = reqs.all()

    ls_result = await db.execute(
        select(LearnerSkill).where(LearnerSkill.learner_id == profile.id)
    )
    learner_skills = {ls.skill_id: ls.proficiency for ls in ls_result.scalars().all()}

    gaps = []
    for req, skill_name in requirements_data:
        current = learner_skills.get(req.skill_id, 0)
        gap_val = max(0, req.min_proficiency - current)
        gaps.append(SkillGapResponse(
            skill=skill_name or "Unknown",
            current_proficiency=current,
            required_proficiency=req.min_proficiency,
            importance=req.importance,
            gap=gap_val,
            is_critical=req.is_critical,
        ))

    return gaps


async def analyze_skills(db: AsyncSession, user: User) -> dict:
    profile_result = await db.execute(
        select(LearnerProfile).where(LearnerProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    ls_result = await db.execute(
        select(LearnerSkill, Skill)
        .join(Skill, LearnerSkill.skill_id == Skill.id)
        .where(LearnerSkill.learner_id == profile.id)
    )
    learner_skills_data = ls_result.all()

    technical = []
    soft = []
    strengths = []
    weaknesses = []
    categories = {}

    for ls, skill in learner_skills_data:
        if not skill:
            continue

        entry = {"name": skill.name, "proficiency": ls.proficiency, "category": skill.category}

        if skill.category == "technical" or skill.category == "tool":
            technical.append(entry)
        else:
            soft.append(entry)

        if ls.proficiency >= 60:
            strengths.append(entry)
        elif ls.proficiency < 40:
            weaknesses.append(entry)

        cat = skill.category
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(entry)

    return {
        "technical_skills": technical,
        "soft_skills": soft,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "skill_dna": {"categories": categories},
    }
