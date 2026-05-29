from datetime import date, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models import (
    AppUser,
    Exercise,
    Implement,
    Routine,
    RoutineDayPlan,
    RoutineDayPlanExercise,
)
from app.models.enums import RoutineDayPlanType, RoutineStatus, UserRole
from app.schemas.routine import AdminRoutineDaySaveRequest


def get_week_start(target_date: date) -> date:
    return target_date - timedelta(days=target_date.weekday())


def get_athlete_user(db: Session, user_id: UUID) -> AppUser | None:
    user = db.get(AppUser, user_id)
    if user is None or user.role != UserRole.ATHLETE:
        return None
    return user


def load_day_plan(db: Session, day_plan_id: UUID) -> RoutineDayPlan | None:
    return db.scalar(
        select(RoutineDayPlan)
        .where(RoutineDayPlan.id == day_plan_id)
        .options(
            joinedload(RoutineDayPlan.routine),
            selectinload(RoutineDayPlan.exercises).joinedload(RoutineDayPlanExercise.exercise),
            selectinload(RoutineDayPlan.exercises).joinedload(RoutineDayPlanExercise.implement),
        )
    )


def get_or_create_active_routine(
    db: Session,
    athlete: AppUser,
    payload: AdminRoutineDaySaveRequest,
) -> Routine | None:
    if payload.routine_id is not None:
        return db.scalar(
            select(Routine).where(
                Routine.id == payload.routine_id,
                Routine.user_id == athlete.id,
            )
        )

    routine = db.scalar(
        select(Routine)
        .where(Routine.user_id == athlete.id, Routine.status == RoutineStatus.ACTIVE)
        .order_by(Routine.created_at.desc().nullslast())
        .limit(1)
    )
    if routine is not None:
        return routine

    routine = Routine(
        user_id=athlete.id,
        name=payload.routine_name or f"Rutina de {athlete.full_name}",
        status=RoutineStatus.ACTIVE,
    )
    db.add(routine)
    db.flush()
    return routine


def validate_references(db: Session, payload: AdminRoutineDaySaveRequest) -> bool:
    exercise_ids = {item.exercise_id for item in payload.exercises}
    implement_ids = {item.implement_id for item in payload.exercises if item.implement_id is not None}

    if exercise_ids:
        found_exercises = set(
            db.scalars(select(Exercise.id).where(Exercise.id.in_(exercise_ids))).all()
        )
        if found_exercises != exercise_ids:
            return False

    if implement_ids:
        found_implements = set(
            db.scalars(select(Implement.id).where(Implement.id.in_(implement_ids))).all()
        )
        if found_implements != implement_ids:
            return False

    return True


def save_admin_routine_day(
    db: Session,
    user_id: UUID,
    payload: AdminRoutineDaySaveRequest,
) -> RoutineDayPlan | None:
    athlete = get_athlete_user(db, user_id)
    if athlete is None:
        return None

    if not validate_references(db, payload):
        return None

    routine = get_or_create_active_routine(db, athlete, payload)
    if routine is None:
        return None

    effective_from = payload.effective_from or get_week_start(date.today())

    next_priority = payload.priority
    if next_priority is None:
        current_priority = db.scalar(
            select(func.max(RoutineDayPlan.priority)).where(
                RoutineDayPlan.routine_id == routine.id,
                RoutineDayPlan.day_of_week == payload.day_of_week,
            )
        )
        next_priority = (current_priority or 0) + 1

    day_plan = RoutineDayPlan(
        routine_id=routine.id,
        day_of_week=payload.day_of_week,
        title=payload.title,
        plan_type=RoutineDayPlanType.BASE,
        effective_from=effective_from,
        effective_to=payload.effective_to,
        priority=next_priority,
        change_reason=payload.change_reason,
    )
    db.add(day_plan)
    db.flush()

    for item in payload.exercises:
        db.add(
            RoutineDayPlanExercise(
                routine_day_plan_id=day_plan.id,
                exercise_id=item.exercise_id,
                section=item.section,
                order_number=item.order_number,
                sets=item.sets,
                reps=item.reps,
                implement_id=item.implement_id,
                load_value=item.load_value,
                notes=item.notes,
            )
        )

    db.commit()
    return load_day_plan(db, day_plan.id)
