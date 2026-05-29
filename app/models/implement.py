from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Implement(Base):
    __tablename__ = "implements"
    __table_args__ = (UniqueConstraint("name", name="implements_name_key"),)

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        server_default=text("now()"),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        server_default=text("now()"),
    )

    exercises: Mapped[list[Exercise]] = relationship(back_populates="default_implement")
    routine_day_plan_exercises: Mapped[list[RoutineDayPlanExercise]] = relationship(
        back_populates="implement",
    )
