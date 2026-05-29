from datetime import date, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import RoutineDayPlanExercise, RoutineSession, RoutineSessionExerciseLog
from app.models.enums import RoutineSection, RoutineSessionStatus
from app.schemas.session import (
    CompleteRoutineSessionRequest,
    RegisterExerciseCompletionRequest,
    StartRoutineSessionRequest,
)
from app.services.routine_service import get_active_day_plan, get_athlete


SECTION_ORDER = {
    RoutineSection.WARMUP.value: 0,
    RoutineSection.MAIN.value: 1,
}


def get_section_order(section: RoutineSection | str) -> int:
    section_value = section.value if isinstance(section, RoutineSection) else section
    return SECTION_ORDER.get(section_value, 99)


def get_planned_exercise_sort_key(planned_exercise: RoutineDayPlanExercise) -> tuple[int, int]:
    return (
        get_section_order(planned_exercise.section),
        planned_exercise.order_number,
    )


def get_log_sort_key(log: RoutineSessionExerciseLog) -> tuple[int, int]:
    planned_exercise = log.routine_day_plan_exercise
    if planned_exercise is None:
        return (99, 0)
    return get_planned_exercise_sort_key(planned_exercise)


def get_session_with_logs(db: Session, session_id: UUID) -> RoutineSession | None:
    session = db.scalar(
        select(RoutineSession)
        .where(RoutineSession.id == session_id)
        .options(
            selectinload(RoutineSession.exercise_logs).selectinload(
                RoutineSessionExerciseLog.exercise
            ),
            selectinload(RoutineSession.exercise_logs).selectinload(
                RoutineSessionExerciseLog.routine_day_plan_exercise
            ),
        )
    )
    if session is not None:
        session.exercise_logs.sort(key=get_log_sort_key)
    return session


def start_routine_session(
    db: Session,
    payload: StartRoutineSessionRequest,
) -> RoutineSession | None:
    if get_athlete(db, payload.user_id) is None:
        return None

    training_date = payload.training_date or date.today()
    day_plan = get_active_day_plan(db, payload.user_id, training_date)
    if day_plan is None:
        return None

    session = RoutineSession(
        user_id=payload.user_id,
        routine_id=day_plan.routine_id,
        routine_day_plan_id=day_plan.id,
        training_date=training_date,
        status=RoutineSessionStatus.STARTED,
        notes=payload.notes,
    )
    db.add(session)
    db.flush()

    for planned_exercise in sorted(day_plan.exercises, key=get_planned_exercise_sort_key):
        db.add(
            RoutineSessionExerciseLog(
                session_id=session.id,
                routine_day_plan_exercise_id=planned_exercise.id,
                exercise_id=planned_exercise.exercise_id,
                planned_sets=planned_exercise.sets,
                planned_reps=planned_exercise.reps,
                planned_load_value=planned_exercise.load_value,
                is_completed=False,
            )
        )

    db.commit()
    return get_session_with_logs(db, session.id)


def register_exercise_completion(
    db: Session,
    session_id: UUID,
    log_id: UUID,
    payload: RegisterExerciseCompletionRequest,
) -> RoutineSessionExerciseLog | None:
    session = db.get(RoutineSession, session_id)
    if session is None:
        return None

    log = db.scalar(
        select(RoutineSessionExerciseLog).where(
            RoutineSessionExerciseLog.id == log_id,
            RoutineSessionExerciseLog.session_id == session_id,
        )
    )
    if log is None:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(log, field, value)

    if payload.is_completed and log.completed_at is None:
        log.completed_at = datetime.now()

    db.commit()
    db.refresh(log)
    return log


def complete_routine_session(
    db: Session,
    session_id: UUID,
    payload: CompleteRoutineSessionRequest,
) -> RoutineSession | None:
    session = get_session_with_logs(db, session_id)
    if session is None:
        return None

    session.status = RoutineSessionStatus.COMPLETED
    session.completed_at = payload.completed_at or datetime.now()
    if payload.notes is not None:
        session.notes = payload.notes

    db.commit()
    return get_session_with_logs(db, session_id)
