from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class SkillResponse(BaseModel):
    id: UUID
    name: str
    category: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}
