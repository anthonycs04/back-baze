from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RoutineSessionExerciseLog(Base):
    __tablename__ = "routine_session_exercise_logs"
    __table_args__ = (Index("idx_routine_session_exercise_logs_session_id", "session_id"),)

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    session_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("routine_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    routine_day_plan_exercise_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("routine_day_plan_exercises.id", ondelete="CASCADE"),
        nullable=False,
    )
    exercise_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("exercises.id"),
        nullable=False,
    )
    planned_sets: Mapped[int | None] = mapped_column(Integer)
    planned_reps: Mapped[str | None] = mapped_column(String(50))
    planned_load_value: Mapped[str | None] = mapped_column(String(80))
    actual_sets: Mapped[int | None] = mapped_column(Integer)
    actual_reps: Mapped[str | None] = mapped_column(String(50))
    actual_load_value: Mapped[str | None] = mapped_column(String(80))
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    feedback: Mapped[str | None] = mapped_column(Text)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        server_default=text("now()"),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        server_default=text("now()"),
    )

    routine_session: Mapped[RoutineSession] = relationship(back_populates="exercise_logs")
    routine_day_plan_exercise: Mapped[RoutineDayPlanExercise] = relationship(
        back_populates="exercise_logs",
    )
    exercise: Mapped[Exercise] = relationship(back_populates="routine_session_exercise_logs")

    @property
    def section(self):
        return self.routine_day_plan_exercise.section if self.routine_day_plan_exercise else None

    @property
    def order_number(self):
        return self.routine_day_plan_exercise.order_number if self.routine_day_plan_exercise else None
