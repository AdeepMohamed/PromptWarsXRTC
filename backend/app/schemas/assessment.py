from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime


class QuestionResponse(BaseModel):
    id: UUID
    question_text: str
    question_type: str
    options: Optional[list] = None
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    points: float = 1.0

    model_config = {"from_attributes": True}


class AssessmentListItem(BaseModel):
    id: UUID
    title: str
    skill: Optional[str] = None
    skill_id: Optional[UUID] = None
    difficulty: Optional[str] = None
    time_limit: Optional[int] = None
    question_count: int = 0

    model_config = {"from_attributes": True}


class AssessmentDetailResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    difficulty: Optional[str] = None
    time_limit_minutes: int = 30
    questions: List[QuestionResponse] = []

    model_config = {"from_attributes": True}


class AssessmentSubmitRequest(BaseModel):
    assessment_id: UUID
    answers: Dict[str, str]
    time_taken_seconds: Optional[int] = None


class AssessmentResultResponse(BaseModel):
    score: float
    max_score: float
    percentage: float
    weak_topics: Optional[list] = None
    improvements: list = []
    proficiency_updates: list = []
    roadmap_changes: list = []

    model_config = {"from_attributes": True}


class AssessmentResultItem(BaseModel):
    id: UUID
    assessment_id: UUID
    score: float
    max_score: float
    percentage: float
    weak_topics: Optional[list] = None
    time_taken_seconds: Optional[int] = None
    completed_at: datetime

    model_config = {"from_attributes": True}
