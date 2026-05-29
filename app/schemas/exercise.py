from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ExerciseBase(BaseModel):
    name: str = Field(..., max_length=150)
    description: str | None = None
    video_url: str | None = None
    default_implement_id: UUID | None = None
    is_active: bool = True


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=150)
    description: str | None = None
    video_url: str | None = None
    default_implement_id: UUID | None = None
    is_active: bool | None = None


class ExerciseRead(ExerciseBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None
