from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.learner import LearnerProfile, LearnerSkill
from app.models.skill import Skill
from app.models.assessment import Assessment, AssessmentQuestion, AssessmentResult
from app.schemas.assessment import (
    AssessmentListItem, AssessmentDetailResponse, QuestionResponse,
    AssessmentResultResponse, AssessmentResultItem
)
from fastapi import HTTPException
from datetime import datetime, timezone
import uuid


async def list_assessments(db: AsyncSession, skill_id=None) -> list:
    query = select(Assessment).where(Assessment.is_active == True)
    if skill_id:
        query = query.where(Assessment.skill_id == skill_id)

    result = await db.execute(query)
    assessments = result.scalars().all()

    items = []
    for a in assessments:
        q_count = await db.execute(
            select(AssessmentQuestion).where(AssessmentQuestion.assessment_id == a.id)
        )
        questions = q_count.scalars().all()
        skill_result = await db.execute(select(Skill).where(Skill.id == a.skill_id))
        skill = skill_result.scalar_one_or_none()
        items.append(AssessmentListItem(
            id=a.id,
            title=a.title,
            skill=skill.name if skill else None,
            skill_id=a.skill_id,
            difficulty=a.difficulty,
            time_limit=a.time_limit_minutes,
            question_count=len(questions),
        ))

    return items


async def get_assessment(db: AsyncSession, assessment_id) -> dict:
    result = await db.execute(select(Assessment).where(Assessment.id == assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    q_result = await db.execute(
        select(AssessmentQuestion)
        .where(AssessmentQuestion.assessment_id == assessment_id)
        .order_by(AssessmentQuestion.order_index)
    )
    questions = q_result.scalars().all()

    return {
        "id": assessment.id,
        "title": assessment.title,
        "description": assessment.description,
        "difficulty": assessment.difficulty,
        "time_limit_minutes": assessment.time_limit_minutes,
        "questions": [QuestionResponse(
            id=q.id,
            question_text=q.question_text,
            question_type=q.question_type,
            options=q.options,
            topic=q.topic,
            difficulty=q.difficulty,
            points=q.points,
        ) for q in questions],
    }


async def submit_assessment(db: AsyncSession, user: User, assessment_id, answers: dict, time_taken: int = None) -> dict:
    profile_result = await db.execute(
        select(LearnerProfile).where(LearnerProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    assessment_result = await db.execute(select(Assessment).where(Assessment.id == assessment_id))
    assessment = assessment_result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Get questions
    q_result = await db.execute(
        select(AssessmentQuestion).where(AssessmentQuestion.assessment_id == assessment_id)
    )
    questions = q_result.scalars().all()

    # Grade
    score = 0
    max_score = 0
    weak_topics = []
    topic_scores = {}

    for q in questions:
        max_score += q.points
        q_id_str = str(q.id)
        user_answer = answers.get(q_id_str, "")
        if user_answer.strip().lower() == q.correct_answer.strip().lower():
            score += q.points
            if q.topic:
                topic_scores.setdefault(q.topic, []).append(True)
        else:
            if q.topic:
                topic_scores.setdefault(q.topic, []).append(False)

    percentage = (score / max_score * 100) if max_score > 0 else 0

    for topic, results in topic_scores.items():
        correct_ratio = sum(1 for r in results if r) / len(results)
        if correct_ratio < 0.5:
            weak_topics.append(topic)

    # Save result
    ar = AssessmentResult(
        learner_id=profile.id,
        assessment_id=assessment_id,
        score=score,
        max_score=max_score,
        percentage=percentage,
        answers=answers,
        weak_topics=weak_topics,
        time_taken_seconds=time_taken,
        completed_at=datetime.now(timezone.utc),
    )
    db.add(ar)

    # Update learner skill proficiency
    existing = await db.execute(
        select(LearnerSkill).where(
            LearnerSkill.learner_id == profile.id,
            LearnerSkill.skill_id == assessment.skill_id,
        )
    )
    ls = existing.scalar_one_or_none()
    proficiency_updates = []
    if ls:
        old_prof = ls.proficiency
        ls.proficiency = percentage
        ls.confidence = "assessed"
        ls.source = "assessment"
        ls.last_assessed_at = datetime.now(timezone.utc)
        proficiency_updates.append({"skill_id": str(assessment.skill_id), "old": old_prof, "new": percentage})
    else:
        ls = LearnerSkill(
            learner_id=profile.id,
            skill_id=assessment.skill_id,
            proficiency=percentage,
            confidence="assessed",
            source="assessment",
            last_assessed_at=datetime.now(timezone.utc),
        )
        db.add(ls)
        proficiency_updates.append({"skill_id": str(assessment.skill_id), "old": 0, "new": percentage})

    await db.flush()

    return {
        "result_id": ar.id,
        "score": score,
        "max_score": max_score,
        "percentage": round(percentage, 1),
        "weak_topics": weak_topics,
        "improvements": [f"Focus on: {t}" for t in weak_topics],
        "proficiency_updates": proficiency_updates,
        "roadmap_changes": [],
    }


async def get_results(db: AsyncSession, user: User, skill_id=None) -> list:
    profile_result = await db.execute(
        select(LearnerProfile).where(LearnerProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    query = select(AssessmentResult).where(AssessmentResult.learner_id == profile.id)
    if skill_id:
        # Filter by skill through assessment
        query = query.join(Assessment).where(Assessment.skill_id == skill_id)

    result = await db.execute(query.order_by(AssessmentResult.completed_at.desc()))
    results = result.scalars().all()

    return [AssessmentResultItem(
        id=r.id,
        assessment_id=r.assessment_id,
        score=r.score,
        max_score=r.max_score,
        percentage=r.percentage,
        weak_topics=r.weak_topics,
        time_taken_seconds=r.time_taken_seconds,
        completed_at=r.completed_at,
    ) for r in results]
