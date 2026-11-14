import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UniqueConstraint
from app.core.database import Base


class CareerRole(Base):
    __tablename__ = "career_roles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(100))
    avg_salary_range: Mapped[str | None] = mapped_column(String(100))
    demand_level: Mapped[str | None] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    requirements: Mapped[list["CareerRequirement"]] = relationship(back_populates="career", lazy="selectin")


class CareerRequirement(Base):
    __tablename__ = "career_requirements"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    career_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("career_roles.id"), nullable=False)
    skill_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("skills.id"), nullable=False)
    importance: Mapped[float] = mapped_column(Float, nullable=False)
    min_proficiency: Mapped[float] = mapped_column(Float, nullable=False)
    is_critical: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    career: Mapped["CareerRole"] = relationship(back_populates="requirements", lazy="selectin")
    skill: Mapped["Skill"] = relationship(back_populates="career_requirements", lazy="selectin")

    __table_args__ = (UniqueConstraint("career_id", "skill_id", name="uq_career_skill"),)
