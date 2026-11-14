import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class LearningActivity(Base):
    __tablename__ = "learning_activity"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    learner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("learner_profiles.id"), nullable=False)
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    activity_metadata: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    learner: Mapped["LearnerProfile"] = relationship(back_populates="activities")


class CareerGoalHistory(Base):
    __tablename__ = "career_goal_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    learner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("learner_profiles.id"), nullable=False)
    previous_career_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("career_roles.id"), nullable=True)
    new_career_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("career_roles.id"), nullable=False)
    readiness_at_change: Mapped[float | None] = mapped_column(Float)
    reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    learner: Mapped["LearnerProfile"] = relationship(back_populates="goal_history")
    previous_career: Mapped["CareerRole"] = relationship(foreign_keys=[previous_career_id], lazy="selectin")
    new_career: Mapped["CareerRole"] = relationship(foreign_keys=[new_career_id], lazy="selectin")
