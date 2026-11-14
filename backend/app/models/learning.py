import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class LearningResource(Base):
    __tablename__ = "learning_resources"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    skill_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("skills.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    url: Mapped[str | None] = mapped_column(String(500))
    difficulty: Mapped[str | None] = mapped_column(String(50))
    estimated_duration_hours: Mapped[float | None] = mapped_column(Float)
    description: Mapped[str | None] = mapped_column(Text)
    provider: Mapped[str | None] = mapped_column(String(200))
    is_free: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    skill: Mapped["Skill"] = relationship(back_populates="learning_resources", lazy="selectin")


class LearningRoadmap(Base):
    __tablename__ = "learning_roadmaps"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    learner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("learner_profiles.id"), nullable=False)
    career_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("career_roles.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    total_estimated_hours: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(50), default="active")
    generated_by: Mapped[str] = mapped_column(String(50), default="ai")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    learner: Mapped["LearnerProfile"] = relationship(back_populates="roadmaps")
    career: Mapped["CareerRole"] = relationship(lazy="selectin")
    tasks: Mapped[list["RoadmapTask"]] = relationship(back_populates="roadmap", lazy="selectin", order_by="RoadmapTask.order_index")


class RoadmapTask(Base):
    __tablename__ = "roadmap_tasks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    roadmap_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("learning_roadmaps.id"), nullable=False)
    skill_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("skills.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    topic: Mapped[str | None] = mapped_column(String(200))
    difficulty: Mapped[str | None] = mapped_column(String(50))
    estimated_hours: Mapped[float | None] = mapped_column(Float)
    learning_objective: Mapped[str | None] = mapped_column(Text)
    recommended_resource: Mapped[str | None] = mapped_column(Text)
    practical_exercise: Mapped[str | None] = mapped_column(Text)
    completion_criteria: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    week_number: Mapped[int | None] = mapped_column(Integer)
    order_index: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    roadmap: Mapped["LearningRoadmap"] = relationship(back_populates="tasks", lazy="selectin")
    skill: Mapped["Skill"] = relationship(lazy="selectin")
