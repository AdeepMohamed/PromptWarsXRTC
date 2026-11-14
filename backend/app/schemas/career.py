from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID


class CareerResponse(BaseModel):
    id: UUID
    title: str
    slug: str
    description: Optional[str] = None
    category: Optional[str] = None
    demand_level: Optional[str] = None

    model_config = {"from_attributes": True}


class CareerAnalyzeRequest(BaseModel):
    career_id: UUID


class SkillGap(BaseModel):
    skill: str
    current_proficiency: float
    required_proficiency: float
    importance: float
    gap: float
    is_critical: bool


class CareerAnalysisResponse(BaseModel):
    career: CareerResponse
    readiness_score: float
    strong_skills: list = []
    missing_skills: list = []
    critical_gaps: list = []
    recommendations: list = []
    agent_activity: Optional[dict] = None


class CareerSimulateRequest(BaseModel):
    career_ids: List[UUID]


class SimulationResult(BaseModel):
    career: CareerResponse
    readiness: float
    required_skills: list = []
    missing_skills: list = []
    effort_hours: float = 0
    transferable_skills: list = []


class CareerGoalRequest(BaseModel):
    career_id: UUID


class SkillAnalysisResponse(BaseModel):
    technical_skills: list = []
    soft_skills: list = []
    strengths: list = []
    weaknesses: list = []
    skill_dna: dict = {}


class SkillGapResponse(BaseModel):
    skill: str
    current_proficiency: float
    required_proficiency: float
    importance: float
    gap: float
    is_critical: bool
