from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, Index, Text, text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import RoutineSessionStatus, pg_enum


class RoutineSession(Base):
    __tablename__ = "routine_sessions"
    __table_args__ = (
        Index("idx_routine_sessions_user_id", "user_id"),
        Index("idx_routine_sessions_training_date", "training_date"),
    )

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("app_users.id", ondelete="CASCADE"),
        nullable=False,
    )
    routine_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("routines.id", ondelete="CASCADE"),
        nullable=False,
    )
    routine_day_plan_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("routine_day_plans.id", ondelete="CASCADE"),
        nullable=False,
    )
    training_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=text("CURRENT_DATE"),
    )
    status: Mapped[RoutineSessionStatus] = mapped_column(
        pg_enum(RoutineSessionStatus, "routine_session_status"),
        nullable=False,
        server_default=text("'started'::routine_session_status"),
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        server_default=text("now()"),
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        server_default=text("now()"),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        server_default=text("now()"),
    )

    athlete: Mapped[AppUser] = relationship(back_populates="routine_sessions")
    routine: Mapped[Routine] = relationship(back_populates="sessions")
    day_plan: Mapped[RoutineDayPlan] = relationship(back_populates="sessions")
    exercise_logs: Mapped[list[RoutineSessionExerciseLog]] = relationship(
        back_populates="routine_session",
    )
