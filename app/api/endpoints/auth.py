from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import AppUser
from app.schemas.auth import LoginDniRequest, LoginDniResponse


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login-dni", response_model=LoginDniResponse)
def login_dni(payload: LoginDniRequest, db: Session = Depends(get_db)) -> AppUser:
    user = db.scalar(select(AppUser).where(AppUser.dni == payload.dni))

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid DNI",
        )

    return user
