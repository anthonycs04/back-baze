from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import RoutineSection, pg_enum


class RoutineDayPlanExercise(Base):
    __tablename__ = "routine_day_plan_exercises"
    __table_args__ = (
        UniqueConstraint(
            "routine_day_plan_id",
            "section",
            "order_number",
            name="routine_day_plan_exercises_routine_day_plan_id_section_orde_key",
        ),
        Index("idx_routine_day_plan_exercises_plan_id", "routine_day_plan_id"),
        Index("idx_routine_day_plan_exercises_exercise_id", "exercise_id"),
    )

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    routine_day_plan_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("routine_day_plans.id", ondelete="CASCADE"),
        nullable=False,
    )
    exercise_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("exercises.id"),
        nullable=False,
    )
    section: Mapped[RoutineSection] = mapped_column(
        pg_enum(RoutineSection, "routine_section"),
        nullable=False,
        server_default=text("'main'::routine_section"),
    )
    order_number: Mapped[int] = mapped_column(Integer, nullable=False)
    sets: Mapped[int | None] = mapped_column(Integer)
    reps: Mapped[str | None] = mapped_column(String(50))
    implement_id: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("implements.id"),
    )
    load_value: Mapped[str | None] = mapped_column(String(80))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        server_default=text("now()"),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        server_default=text("now()"),
    )

    day_plan: Mapped[RoutineDayPlan] = relationship(back_populates="exercises")
    exercise: Mapped[Exercise] = relationship(back_populates="routine_day_plan_exercises")
    implement: Mapped[Implement | None] = relationship(back_populates="routine_day_plan_exercises")
    exercise_logs: Mapped[list[RoutineSessionExerciseLog]] = relationship(
        back_populates="routine_day_plan_exercise",
    )
