from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.user import User
from app.models.learner import LearnerProfile, LearnerSkill
from app.models.skill import Skill
from app.schemas.learner import LearnerProfileUpdate, LearnerSkillItem, AddSkillsRequest
from fastapi import HTTPException
import uuid


async def get_learner_profile(db: AsyncSession, user: User) -> dict:
    result = await db.execute(
        select(LearnerProfile).where(LearnerProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Learner profile not found")

    # Get skills
    skills_result = await db.execute(
        select(LearnerSkill).where(LearnerSkill.learner_id == profile.id)
    )
    learner_skills = skills_result.scalars().all()

    skills_list = []
    for ls in learner_skills:
        skill_result = await db.execute(select(Skill).where(Skill.id == ls.skill_id))
        skill = skill_result.scalar_one_or_none()
        skills_list.append(LearnerSkillItem(
            skill_id=ls.skill_id,
            name=skill.name if skill else None,
            proficiency=ls.proficiency,
            confidence=ls.confidence,
            source=ls.source,
        ))

    target_career = None
    if profile.target_career_id:
        from app.models.career import CareerRole
        cr = await db.execute(select(CareerRole).where(CareerRole.id == profile.target_career_id))
        career = cr.scalar_one_or_none()
        if career:
            target_career = {"id": str(career.id), "title": career.title, "slug": career.slug}

    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "target_career": target_career,
        "bio": profile.bio,
        "education_level": profile.education_level,
        "years_experience": profile.years_experience,
        "academic_background": profile.academic_background,
        "certifications": profile.certifications,
        "career_readiness_score": profile.career_readiness_score,
        "skills": skills_list,
    }


async def update_learner_profile(db: AsyncSession, user: User, data: LearnerProfileUpdate) -> dict:
    result = await db.execute(
        select(LearnerProfile).where(LearnerProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Learner profile not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)

    await db.flush()
    return await get_learner_profile(db, user)


async def add_learner_skills(db: AsyncSession, user: User, data: AddSkillsRequest) -> list:
    result = await db.execute(
        select(LearnerProfile).where(LearnerProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Learner profile not found")

    added_skills = []
    for skill_input in data.skills:
        # Check skill exists
        skill_result = await db.execute(select(Skill).where(Skill.id == skill_input.skill_id))
        skill = skill_result.scalar_one_or_none()
        if not skill:
            continue

        # Upsert learner skill
        existing = await db.execute(
            select(LearnerSkill).where(
                LearnerSkill.learner_id == profile.id,
                LearnerSkill.skill_id == skill_input.skill_id,
            )
        )
        ls = existing.scalar_one_or_none()
        if ls:
            ls.proficiency = skill_input.proficiency
        else:
            ls = LearnerSkill(
                learner_id=profile.id,
                skill_id=skill_input.skill_id,
                proficiency=skill_input.proficiency,
            )
            db.add(ls)

        await db.flush()
        added_skills.append(LearnerSkillItem(
            skill_id=ls.skill_id,
            name=skill.name,
            proficiency=ls.proficiency,
            confidence=ls.confidence,
            source=ls.source,
        ))

    return added_skills
