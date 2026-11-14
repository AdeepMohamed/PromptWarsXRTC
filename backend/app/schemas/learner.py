from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class LearnerSkillItem(BaseModel):
    skill_id: UUID
    name: Optional[str] = None
    proficiency: float = 0.0
    confidence: Optional[str] = "claimed"
    source: Optional[str] = "self_reported"

    model_config = {"from_attributes": True}


class LearnerProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    target_career: Optional[dict] = None
    bio: Optional[str] = None
    education_level: Optional[str] = None
    years_experience: int = 0
    academic_background: Optional[str] = None
    certifications: Optional[list] = None
    career_readiness_score: float = 0.0
    skills: List[LearnerSkillItem] = []

    model_config = {"from_attributes": True}


class LearnerProfileUpdate(BaseModel):
    bio: Optional[str] = None
    education_level: Optional[str] = None
    years_experience: Optional[int] = None
    academic_background: Optional[str] = None
    certifications: Optional[list] = None


class SkillInput(BaseModel):
    skill_id: UUID
    proficiency: float = Field(..., ge=0, le=100)


class AddSkillsRequest(BaseModel):
    skills: List[SkillInput]
