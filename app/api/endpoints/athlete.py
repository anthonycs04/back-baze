from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.athlete import AthleteRoutineDayRead, AthleteRoutineWeekRead
from app.schemas.session import (
    RoutineSessionWithLogs,
    StartAthleteRoutineSessionRequest,
    StartRoutineSessionRequest,
)
from app.services.routine_service import (
    get_athlete,
    get_routine_for_day,
    get_routine_for_week,
)
from app.services.session_service import start_routine_session


router = APIRouter(prefix="/athlete", tags=["athlete"])


@router.get("/{user_id}/routine/today", response_model=AthleteRoutineDayRead)
def get_today_routine(
    user_id: UUID,
    target_date: date | None = Query(default=None, alias="date"),
    db: Session = Depends(get_db),
) -> AthleteRoutineDayRead:
    if get_athlete(db, user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found")

    routine_day = get_routine_for_day(db, user_id, target_date or date.today())
    if routine_day is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No routine found for this date",
        )

    return routine_day


@router.get("/{user_id}/routine/week", response_model=AthleteRoutineWeekRead)
def get_week_routine(
    user_id: UUID,
    target_date: date | None = Query(default=None, alias="date"),
    db: Session = Depends(get_db),
) -> AthleteRoutineWeekRead:
    if get_athlete(db, user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found")

    return get_routine_for_week(db, user_id, target_date or date.today())


@router.post(
    "/{user_id}/routine/start",
    response_model=RoutineSessionWithLogs,
    status_code=status.HTTP_201_CREATED,
)
def start_today_routine(
    user_id: UUID,
    payload: StartAthleteRoutineSessionRequest | None = None,
    db: Session = Depends(get_db),
) -> RoutineSessionWithLogs:
    session = start_routine_session(
        db,
        StartRoutineSessionRequest(
            user_id=user_id,
            training_date=payload.training_date if payload else None,
            notes=payload.notes if payload else None,
        ),
    )
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Athlete or active routine not found for this date",
        )
    return session
