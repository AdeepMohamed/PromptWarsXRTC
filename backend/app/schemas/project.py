from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class ProjectSubmitRequest(BaseModel):
    title: str = Field(..., max_length=300)
    description: Optional[str] = None
    technologies: Optional[list] = None
    github_url: Optional[str] = None
    outcomes: Optional[str] = None


class ProjectResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    technologies: Optional[list | dict | str] = None
    github_url: Optional[str] = None
    outcomes: Optional[str] = None
    demonstrated_skills: Optional[list | dict | str] = None
    ai_analysis: Optional[str] = None
    status: str = "submitted"
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
