from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class DashboardResponse(BaseModel):
    career_readiness: float = 0.0
    current_career_goal: str = "Full Stack Developer"
    skills_mastered: int = 0
    total_skills: int = 0
    missing_skills: list = []
    learning_progress: float = 0.0
    recent_assessments: list = []
    upcoming_tasks: list = []
    weekly_activity: list = []
    recent_agent_decisions: list = []
    recommendations: list = []


class ProgressResponse(BaseModel):
    skill_improvements: list = []
    assessment_scores: list = []
    readiness_history: list = []
    activities_by_type: dict = {}
