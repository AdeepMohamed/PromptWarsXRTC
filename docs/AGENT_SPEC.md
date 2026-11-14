# COGNIFY AI — Agent Architecture Specification

## Python command
Use `python3.11` (located at `C:\Users\ASUS\.local\bin\python3.11.exe`) for ALL Python commands.

## Overview
5 specialized agents + 1 central orchestrator, all in `backend/app/agents/`.

## File Structure
```
backend/app/agents/
├── __init__.py
├── base_agent.py          # Abstract base class for all agents
├── grok_client.py         # Grok API client wrapper
├── orchestrator.py        # Central agent orchestrator
├── skill_agent.py         # Agent 1: Skill analysis
├── career_agent.py        # Agent 2: Career matching
├── learning_agent.py      # Agent 3: Learning roadmap
├── performance_agent.py   # Agent 4: Assessment evaluation
└── mentor_agent.py        # Agent 5: AI mentor
```

## Base Agent (base_agent.py)
```python
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime
import uuid

class AgentInput(BaseModel):
    learner_id: uuid.UUID
    data: dict

class AgentOutput(BaseModel):
    agent_name: str
    status: str  # "completed" or "failed"
    result: dict
    errors: list[str] = []
    processing_duration_ms: int = 0

class BaseAgent(ABC):
    name: str
    description: str
    
    @abstractmethod
    async def execute(self, input_data: AgentInput, db_session) -> AgentOutput:
        pass
    
    async def log_activity(self, db_session, learner_id, task, input_summary, 
                           output_summary, status, duration_ms, error=None):
        # Log to agent_activity_logs table
        pass
```

## Grok Client (grok_client.py)
- Uses GROK_API_KEY from env
- Base URL: https://api.x.ai/v1/chat/completions
- Model: grok-3-mini-fast  
- Structured JSON output via system prompts
- Retry logic (3 attempts, exponential backoff)
- Timeout: 30s per request
- Returns parsed JSON or raises GrokAPIError

## Agent 1: Skill Agent (skill_agent.py)
Input: learner profile, skills, certifications, projects, assessment history
Output:
```json
{
  "technical_skills": [{"name": "Python", "proficiency": 85, "confidence": "assessed"}],
  "soft_skills": [{"name": "Problem Solving", "proficiency": 70, "confidence": "claimed"}],
  "strengths": ["Python programming", "SQL databases"],
  "weaknesses": ["Frontend development", "Version control"],
  "skill_dna": {
    "programming": 75,
    "analytical_thinking": 70,
    "problem_solving": 65,
    "communication": 50,
    "technical_proficiency": 60,
    "project_experience": 40
  },
  "recommendations": ["Focus on JavaScript fundamentals"]
}
```

## Agent 2: Career Agent (career_agent.py)
Input: learner skills, target career
Output:
```json
{
  "career": {"title": "Full Stack Developer", "readiness_score": 35.5},
  "required_skills": [{"name": "JavaScript", "importance": 9, "min_proficiency": 70}],
  "strong_skills": [{"name": "Python", "current": 85, "required": 60, "status": "exceeds"}],
  "missing_skills": [{"name": "React", "importance": 9, "gap": 70, "reason": "Core frontend framework"}],
  "critical_gaps": [{"name": "JavaScript", "importance": 10, "urgency": "high"}],
  "readiness_formula": "sum(current * importance) / sum(importance)"
}
```

## Agent 3: Learning Agent (learning_agent.py)
Input: skill gaps, career requirements, assessment history
Output:
```json
{
  "roadmap": {
    "title": "Full Stack Developer Roadmap",
    "total_weeks": 6,
    "total_hours": 120,
    "tasks": [
      {
        "skill": "JavaScript",
        "topic": "Variables and Data Types",
        "description": "Learn JavaScript fundamentals",
        "difficulty": "beginner",
        "estimated_hours": 4,
        "learning_objective": "Understand JS variables, types, operators",
        "recommended_resource": "MDN JavaScript Guide",
        "practical_exercise": "Build a calculator",
        "completion_criteria": "Complete calculator project",
        "priority": 1,
        "week_number": 1,
        "order_index": 1
      }
    ]
  }
}
```

## Agent 4: Performance Agent (performance_agent.py)
Input: assessment results, learner skills, history
Output:
```json
{
  "score_analysis": {"score": 25, "max": 100, "percentage": 25},
  "weak_topics": ["Functions", "Arrays", "Objects"],
  "proficiency_updates": [{"skill": "JavaScript", "old": 0, "new": 15}],
  "is_poor_performance": true,
  "stagnation_detected": false,
  "interventions": [
    {"type": "remedial", "skill": "JavaScript", "topic": "Functions", "action": "Generate practice exercises"}
  ],
  "roadmap_modifications": [
    {"action": "add_task", "skill": "JavaScript", "topic": "Functions Deep Dive", "reason": "Repeated weakness"}
  ]
}
```

## Agent 5: Mentor Agent (mentor_agent.py)
Input: learner context (profile, skills, gaps, progress), user message
Output:
```json
{
  "message": "Based on your assessment results...",
  "suggestions": ["Practice array methods daily", "Try building a todo app"],
  "resources": [{"title": "JavaScript Arrays", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array"}]
}
```

## Orchestrator (orchestrator.py)
Manages three workflows:

### 1. Initial Analysis Workflow
```
receive_profile → skill_agent → career_agent → calculate_gaps → learning_agent → save_to_db → notify_mentor → log_history
```

### 2. Assessment Update Workflow
```
receive_results → performance_agent → update_proficiency → recalculate_readiness → learning_agent(partial) → save_to_db → notify_mentor → log_history
```

### 3. Career Change Workflow
```
detect_change → career_agent(new) → identify_transferable → calculate_new_gaps → learning_agent(new) → archive_old → save_to_db → notify_mentor → log_history
```

## Fallback Logic
When Grok API is unavailable:
- Skill Agent: Use raw proficiency values from DB
- Career Agent: Calculate readiness from career_requirements table directly
- Learning Agent: Generate roadmap from learning_resources in DB, ordered by difficulty
- Performance Agent: Calculate gaps purely from score data
- Mentor Agent: Return template responses with learner data filled in

## Important Implementation Notes
- Each agent MUST use the DB models from `app.models` — import them
- Each agent MUST log activity via `agent_activity_logs` table
- Use async/await throughout
- Validate all AI outputs with Pydantic before using
- Never expose raw AI output to users without validation
