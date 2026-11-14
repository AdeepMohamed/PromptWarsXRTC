import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    learner_skills: Mapped[list["LearnerSkill"]] = relationship(back_populates="skill", lazy="selectin")
    career_requirements: Mapped[list["CareerRequirement"]] = relationship(back_populates="skill", lazy="selectin")
    learning_resources: Mapped[list["LearningResource"]] = relationship(back_populates="skill", lazy="selectin")
    assessments: Mapped[list["Assessment"]] = relationship(back_populates="skill", lazy="selectin")
