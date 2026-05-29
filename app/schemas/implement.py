from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ImplementBase(BaseModel):
    name: str = Field(..., max_length=100)


class ImplementCreate(ImplementBase):
    pass


class ImplementUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)


class ImplementRead(ImplementBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None
