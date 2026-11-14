from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class MentorChatRequest(BaseModel):
    message: str
    context: Optional[str] = "general"


class MentorChatResponse(BaseModel):
    message: str
    suggestions: Optional[list] = None
    resources: Optional[list] = None
