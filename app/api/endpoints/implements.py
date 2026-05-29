from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Implement
from app.schemas.implement import ImplementCreate, ImplementRead, ImplementUpdate


router = APIRouter(prefix="/implements", tags=["implements"])


def _get_implement_or_404(implement_id: UUID, db: Session) -> Implement:
    implement = db.get(Implement, implement_id)
    if implement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Implement not found")
    return implement


@router.post("", response_model=ImplementRead, status_code=status.HTTP_201_CREATED)
def create_implement(payload: ImplementCreate, db: Session = Depends(get_db)) -> Implement:
    implement = Implement(**payload.model_dump())
    db.add(implement)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Implement name already exists",
        ) from exc

    db.refresh(implement)
    return implement


@router.get("", response_model=list[ImplementRead])
def list_implements(
    db: Session = Depends(get_db),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[Implement]:
    return list(db.scalars(select(Implement).offset(skip).limit(limit)).all())


@router.get("/{implement_id}", response_model=ImplementRead)
def get_implement(implement_id: UUID, db: Session = Depends(get_db)) -> Implement:
    return _get_implement_or_404(implement_id, db)


@router.patch("/{implement_id}", response_model=ImplementRead)
def update_implement(
    implement_id: UUID,
    payload: ImplementUpdate,
    db: Session = Depends(get_db),
) -> Implement:
    implement = _get_implement_or_404(implement_id, db)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(implement, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Implement update violates a database constraint",
        ) from exc

    db.refresh(implement)
    return implement


@router.delete("/{implement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_implement(implement_id: UUID, db: Session = Depends(get_db)) -> Response:
    implement = _get_implement_or_404(implement_id, db)
    db.delete(implement)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
