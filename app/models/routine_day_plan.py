from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, SmallInteger, String, Text, text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import RoutineDayPlanType, pg_enum


class RoutineDayPlan(Base):
    __tablename__ = "routine_day_plans"
    __table_args__ = (
        CheckConstraint("day_of_week >= 1 AND day_of_week <= 5", name="routine_day_plans_day_of_week_check"),
        CheckConstraint("effective_to IS NULL OR effective_to >= effective_from", name="routine_day_plans_check"),
        Index("idx_routine_day_plans_routine_id", "routine_id"),
        Index("idx_routine_day_plans_day_of_week", "day_of_week"),
        Index("idx_routine_day_plans_effective_dates", "effective_from", "effective_to"),
    )

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    routine_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("routines.id", ondelete="CASCADE"),
        nullable=False,
    )
    day_of_week: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    title: Mapped[str | None] = mapped_column(String(120))
    plan_type: Mapped[RoutineDayPlanType] = mapped_column(
        pg_enum(RoutineDayPlanType, "routine_day_plan_type"),
        nullable=False,
        server_default=text("'base'::routine_day_plan_type"),
    )
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date)
    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )
    change_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        server_default=text("now()"),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        server_default=text("now()"),
    )

    routine: Mapped[Routine] = relationship(back_populates="day_plans")
    exercises: Mapped[list[RoutineDayPlanExercise]] = relationship(back_populates="day_plan")
    sessions: Mapped[list[RoutineSession]] = relationship(back_populates="day_plan")
