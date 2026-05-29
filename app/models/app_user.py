from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Index, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import UserRole, pg_enum


class AppUser(Base):
    __tablename__ = "app_users"
    __table_args__ = (
        UniqueConstraint("dni", name="app_users_dni_key"),
        Index("idx_app_users_dni", "dni"),
        Index("idx_app_users_role", "role"),
    )

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    dni: Mapped[str] = mapped_column(String(20), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        pg_enum(UserRole, "user_role"),
        nullable=False,
        server_default=text("'athlete'::user_role"),
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

    routines: Mapped[list[Routine]] = relationship(back_populates="athlete")
    routine_sessions: Mapped[list[RoutineSession]] = relationship(back_populates="athlete")
