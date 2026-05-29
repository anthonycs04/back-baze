from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import UserRole
from app.schemas.user import UserRead


class LoginDniRequest(BaseModel):
    dni: str = Field(..., max_length=20)


class LoginDniResponse(UserRead):
    model_config = ConfigDict(from_attributes=True)

    role: UserRole
