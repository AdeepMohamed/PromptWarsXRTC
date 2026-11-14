import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Float, Integer, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class LearnerProfile(Base):
    __tablename__ = "learner_profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    target_career_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("career_roles.id"), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text)
    education_level: Mapped[str | None] = mapped_column(String(100))
    years_experience: Mapped[int] = mapped_column(Integer, default=0)
    academic_background: Mapped[str | None] = mapped_column(Text)
    certifications: Mapped[dict | None] = mapped_column(JSON, default=list)
    career_readiness_score: Mapped[float] = mapped_column(Float, default=0.0)
    last_analysis_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship(back_populates="learner_profile", lazy="selectin")
    target_career: Mapped[Optional["CareerRole"]] = relationship(lazy="selectin")
    skills: Mapped[list["LearnerSkill"]] = relationship(back_populates="learner", lazy="selectin")
    roadmaps: Mapped[list["LearningRoadmap"]] = relationship(back_populates="learner", lazy="selectin")
    assessment_results: Mapped[list["AssessmentResult"]] = relationship(back_populates="learner", lazy="selectin")
    project_submissions: Mapped[list["ProjectSubmission"]] = relationship(back_populates="learner", lazy="selectin")
    activities: Mapped[list["LearningActivity"]] = relationship(back_populates="learner", lazy="selectin")
    goal_history: Mapped[list["CareerGoalHistory"]] = relationship(back_populates="learner", lazy="selectin")
    agent_logs: Mapped[list["AgentActivityLog"]] = relationship(back_populates="learner", lazy="selectin")


class LearnerSkill(Base):
    __tablename__ = "learner_skills"
    __table_args__ = ({"sqlite_autoincrement": True},)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    learner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("learner_profiles.id"), nullable=False)
    skill_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("skills.id"), nullable=False)
    proficiency: Mapped[float] = mapped_column(Float, default=0.0)
    confidence: Mapped[str] = mapped_column(String(50), default="claimed")
    source: Mapped[str] = mapped_column(String(50), default="self_reported")
    last_assessed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    learner: Mapped["LearnerProfile"] = relationship(back_populates="skills", lazy="selectin")
    skill: Mapped["Skill"] = relationship(back_populates="learner_skills", lazy="selectin")

    from sqlalchemy import UniqueConstraint
    __table_args__ = (UniqueConstraint("learner_id", "skill_id", name="uq_learner_skill"),)
