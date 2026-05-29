from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    video_url: Mapped[str | None] = mapped_column(Text)
    default_implement_id: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("implements.id"),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        server_default=text("now()"),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        server_default=text("now()"),
    )

    default_implement: Mapped[Implement | None] = relationship(back_populates="exercises")
    routine_day_plan_exercises: Mapped[list[RoutineDayPlanExercise]] = relationship(
        back_populates="exercise",
    )
    routine_session_exercise_logs: Mapped[list[RoutineSessionExerciseLog]] = relationship(
        back_populates="exercise",
    )
