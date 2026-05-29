from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import RoutineStatus, pg_enum


class Routine(Base):
    __tablename__ = "routines"
    __table_args__ = (
        Index("idx_routines_user_id", "user_id"),
        Index("idx_routines_status", "status"),
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
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    status: Mapped[RoutineStatus] = mapped_column(
        pg_enum(RoutineStatus, "routine_status"),
        nullable=False,
        server_default=text("'active'::routine_status"),
    )
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        server_default=text("now()"),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        server_default=text("now()"),
    )

    athlete: Mapped[AppUser] = relationship(back_populates="routines")
    day_plans: Mapped[list[RoutineDayPlan]] = relationship(back_populates="routine")
    sessions: Mapped[list[RoutineSession]] = relationship(back_populates="routine")
