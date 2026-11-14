from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class AgentOrchestrationRequest(BaseModel):
    workflow: str
    params: dict = {}


class AgentActivityResponse(BaseModel):
    id: UUID
    agent_name: str
    task: str
    status: str
    input_summary: Optional[str] = None
    output_summary: Optional[str] = None
    duration_ms: Optional[int] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
