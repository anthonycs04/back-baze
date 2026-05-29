from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import UserRole


class UserBase(BaseModel):
    full_name: str = Field(..., max_length=120)
    dni: str = Field(..., max_length=20)
    role: UserRole = UserRole.ATHLETE
    is_active: bool = True


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=120)
    dni: str | None = Field(default=None, max_length=20)
    role: UserRole | None = None
    is_active: bool | None = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None
