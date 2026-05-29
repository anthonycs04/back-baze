from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Exercise, Implement
from app.schemas.exercise import ExerciseRead, ExerciseUpdate
from app.services.storage_service import (
    StorageConfigurationError,
    StorageUploadError,
    is_video_upload,
    upload_exercise_video,
)


router = APIRouter(prefix="/exercises", tags=["exercises"])


def _get_exercise_or_404(exercise_id: UUID, db: Session) -> Exercise:
    exercise = db.get(Exercise, exercise_id)
    if exercise is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    return exercise


def _ensure_implement_exists(implement_id: UUID | None, db: Session) -> None:
    if implement_id is not None and db.get(Implement, implement_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Default implement not found",
        )


def _parse_optional_uuid(value: str | None) -> UUID | None:
    if value is None or value.strip() == "":
        return None

    try:
        return UUID(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="default_implement_id must be a valid UUID",
        ) from exc


@router.post("", response_model=ExerciseRead, status_code=status.HTTP_201_CREATED)
def create_exercise(
    name: str = Form(..., max_length=150),
    description: str | None = Form(default=None),
    default_implement_id: str | None = Form(default=None),
    video_file: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
) -> Exercise:
    implement_id = _parse_optional_uuid(default_implement_id)
    _ensure_implement_exists(implement_id, db)

    video_url = None
    if video_file is not None and video_file.filename:
        if not is_video_upload(video_file):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="video_file must be a video file",
            )

        try:
            video_url = upload_exercise_video(video_file)
        except StorageConfigurationError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Supabase Storage is not configured",
            ) from exc
        except StorageUploadError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(exc),
            ) from exc

    exercise = Exercise(
        name=name,
        description=description,
        video_url=video_url,
        default_implement_id=implement_id,
        is_active=True,
    )
    db.add(exercise)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Exercise creation violates a database constraint",
        ) from exc

    db.refresh(exercise)
    return exercise


@router.get("", response_model=list[ExerciseRead])
def list_exercises(
    db: Session = Depends(get_db),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[Exercise]:
    return list(db.scalars(select(Exercise).offset(skip).limit(limit)).all())


@router.get("/{exercise_id}", response_model=ExerciseRead)
def get_exercise(exercise_id: UUID, db: Session = Depends(get_db)) -> Exercise:
    return _get_exercise_or_404(exercise_id, db)


@router.patch("/{exercise_id}", response_model=ExerciseRead)
def update_exercise(
    exercise_id: UUID,
    payload: ExerciseUpdate,
    db: Session = Depends(get_db),
) -> Exercise:
    exercise = _get_exercise_or_404(exercise_id, db)
    update_data = payload.model_dump(exclude_unset=True)

    if "default_implement_id" in update_data:
        _ensure_implement_exists(update_data["default_implement_id"], db)

    for field, value in update_data.items():
        setattr(exercise, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Exercise update violates a database constraint",
        ) from exc

    db.refresh(exercise)
    return exercise


@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(exercise_id: UUID, db: Session = Depends(get_db)) -> Response:
    exercise = _get_exercise_or_404(exercise_id, db)
    db.delete(exercise)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
