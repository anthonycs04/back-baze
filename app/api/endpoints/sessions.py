from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.session import (
    CompleteRoutineSessionRequest,
    RegisterExerciseCompletionRequest,
    RoutineSessionExerciseLogRead,
    RoutineSessionWithLogs,
    StartRoutineSessionRequest,
)
from app.services.session_service import (
    complete_routine_session,
    get_session_with_logs,
    register_exercise_completion,
    start_routine_session,
)


router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/start", response_model=RoutineSessionWithLogs, status_code=status.HTTP_201_CREATED)
def start_session(
    payload: StartRoutineSessionRequest,
    db: Session = Depends(get_db),
) -> RoutineSessionWithLogs:
    session = start_routine_session(db, payload)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Athlete or active routine not found for this date",
        )
    return session


@router.get("/{session_id}", response_model=RoutineSessionWithLogs)
def get_session(session_id: UUID, db: Session = Depends(get_db)) -> RoutineSessionWithLogs:
    session = get_session_with_logs(db, session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session


@router.patch(
    "/{session_id}/exercise-logs/{log_id}",
    response_model=RoutineSessionExerciseLogRead,
)
def register_completed_exercise(
    session_id: UUID,
    log_id: UUID,
    payload: RegisterExerciseCompletionRequest,
    db: Session = Depends(get_db),
) -> RoutineSessionExerciseLogRead:
    log = register_exercise_completion(db, session_id, log_id, payload)
    if log is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session exercise log not found",
        )
    return log


@router.post("/{session_id}/complete", response_model=RoutineSessionWithLogs)
def complete_session(
    session_id: UUID,
    payload: CompleteRoutineSessionRequest | None = None,
    db: Session = Depends(get_db),
) -> RoutineSessionWithLogs:
    session = complete_routine_session(
        db,
        session_id,
        payload or CompleteRoutineSessionRequest(),
    )
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session
