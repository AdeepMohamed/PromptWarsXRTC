import pytest
from app.agents.skill_agent import SkillAgent
from app.agents.career_agent import CareerAgent
from app.agents.learning_agent import LearningAgent
from app.agents.performance_agent import PerformanceAgent
from app.agents.mentor_agent import MentorAgent
from app.agents.orchestrator import CentralOrchestrator


def test_agent_initialization():
    """Verify all 5 independent AI agents and orchestrator initialize cleanly."""
    skill_agent = SkillAgent()
    career_agent = CareerAgent()
    learning_agent = LearningAgent()
    perf_agent = PerformanceAgent()
    mentor_agent = MentorAgent()
    orchestrator = CentralOrchestrator()

    assert skill_agent.name == "skill_agent"
    assert career_agent.name == "career_agent"
    assert learning_agent.name == "learning_agent"
    assert perf_agent.name == "performance_agent"
    assert mentor_agent.name == "mentor_agent"
    assert orchestrator is not None


def test_skill_agent_fallback_dna():
    """Test Skill Agent deterministic fallback competency vector synthesis."""
    agent = SkillAgent()
    learner_data = {
        "skills": [
            {"name": "Python", "proficiency": 85.0, "confidence": "demonstrated", "category": "technical"},
            {"name": "SQL", "proficiency": 75.0, "confidence": "assessed", "category": "technical"},
            {"name": "HTML", "proficiency": 60.0, "confidence": "assessed", "category": "technical"},
        ],
        "projects": [{"title": "Portfolio Website"}],
        "assessments": [{"percentage": 85.0}],
    }
    analysis = agent._fallback_analysis(learner_data)
    assert "skill_dna" in analysis
    assert "technical_skills" in analysis
    assert len(analysis["technical_skills"]) > 0
    assert "strengths" in analysis


def test_career_agent_readiness_calculation():
    """Test Career Agent mathematical vector readiness scoring."""
    agent = CareerAgent()
    db_data = {
        "career_title": "Full Stack Developer",
        "requirements": [
            {"skill_name": "Python", "importance": 1.0, "min_proficiency": 70, "is_critical": False, "description": ""},
            {"skill_name": "SQL", "importance": 1.0, "min_proficiency": 60, "is_critical": False, "description": ""},
            {"skill_name": "React", "importance": 1.5, "min_proficiency": 80, "is_critical": True, "description": ""},
        ],
        "learner_skills": {
            "Python": {"proficiency": 80.0},
            "SQL": {"proficiency": 70.0},
        }
    }
    analysis = agent._fallback_analysis(db_data)
    assert "career" in analysis
    assert "readiness_score" in analysis["career"]
    assert 0 <= analysis["career"]["readiness_score"] <= 100
    assert "critical_gaps" in analysis
    assert any("React" in g["name"] for g in analysis["critical_gaps"])


def test_learning_agent_roadmap_synthesis():
    """Test Learning Agent fallback 6-week curriculum synthesis."""
    agent = LearningAgent()
    db_data = {
        "career_title": "Full Stack Developer",
        "requirements": [{"skill": "React", "importance": 1.5}],
        "resources": [],
        "gaps": [{"skill": "React", "gap": 65}],
    }

    roadmap = agent._fallback(db_data)
    assert "tasks" in roadmap
    assert len(roadmap["tasks"]) > 0
