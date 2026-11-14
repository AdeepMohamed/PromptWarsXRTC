from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class RoadmapTaskResponse(BaseModel):
    id: UUID
    skill_id: UUID
    title: str
    description: Optional[str] = None
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_hours: Optional[float] = None
    learning_objective: Optional[str] = None
    recommended_resource: Optional[str] = None
    practical_exercise: Optional[str] = None
    completion_criteria: Optional[str] = None
    priority: int = 0
    week_number: Optional[int] = None
    order_index: Optional[int] = None
    status: str = "pending"
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class RoadmapResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    total_estimated_hours: float = 0
    status: str = "active"
    tasks: List[RoadmapTaskResponse] = []
    weeks: Optional[int] = None

    model_config = {"from_attributes": True}


class RoadmapGenerateRequest(BaseModel):
    career_id: UUID


class TaskUpdateRequest(BaseModel):
    status: str = Field(..., pattern="^(completed|in_progress|skipped|pending)$")

TaskUpdate = TaskUpdateRequest
