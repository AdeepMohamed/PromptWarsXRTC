import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class ProjectSubmission(Base):
    __tablename__ = "project_submissions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    learner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("learner_profiles.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    technologies: Mapped[dict | None] = mapped_column(JSON)
    github_url: Mapped[str | None] = mapped_column(String(500))
    outcomes: Mapped[str | None] = mapped_column(Text)
    demonstrated_skills: Mapped[dict | None] = mapped_column(JSON)
    ai_analysis: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="submitted")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    learner: Mapped["LearnerProfile"] = relationship(back_populates="project_submissions")
