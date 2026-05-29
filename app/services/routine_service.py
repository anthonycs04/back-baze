from datetime import date, timedelta
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models import AppUser, Routine, RoutineDayPlan, RoutineDayPlanExercise
from app.models.enums import RoutineStatus, UserRole
from app.schemas.athlete import (
    AthleteRoutineDayRead,
    AthleteRoutineWeekDayRead,
    AthleteRoutineWeekRead,
)


def get_athlete(db: Session, user_id: UUID) -> AppUser | None:
    user = db.get(AppUser, user_id)
    if user is None or not user.is_active or user.role != UserRole.ATHLETE:
        return None
    return user


def get_week_start(target_date: date) -> date:
    return target_date - timedelta(days=target_date.weekday())


def get_active_day_plan(
    db: Session,
    user_id: UUID,
    target_date: date,
) -> RoutineDayPlan | None:
    day_of_week = target_date.weekday() + 1
    if day_of_week > 5:
        return None

    statement = (
        select(RoutineDayPlan)
        .join(Routine)
        .where(
            Routine.user_id == user_id,
            Routine.status == RoutineStatus.ACTIVE,
            or_(Routine.start_date.is_(None), Routine.start_date <= target_date),
            or_(Routine.end_date.is_(None), Routine.end_date >= target_date),
            RoutineDayPlan.day_of_week == day_of_week,
            RoutineDayPlan.effective_from <= target_date,
            or_(
                RoutineDayPlan.effective_to.is_(None),
                RoutineDayPlan.effective_to >= target_date,
            ),
        )
        .options(
            joinedload(RoutineDayPlan.routine),
            selectinload(RoutineDayPlan.exercises).joinedload(RoutineDayPlanExercise.exercise),
            selectinload(RoutineDayPlan.exercises).joinedload(RoutineDayPlanExercise.implement),
        )
        .order_by(
            RoutineDayPlan.priority.desc(),
            RoutineDayPlan.effective_from.desc(),
            RoutineDayPlan.created_at.desc().nullslast(),
        )
        .limit(1)
    )
    return db.scalar(statement)


def build_day_response(target_date: date, day_plan: RoutineDayPlan) -> AthleteRoutineDayRead:
    section_order = {"warmup": 0, "main": 1}
    exercises = sorted(
        day_plan.exercises,
        key=lambda item: (section_order[item.section.value], item.order_number),
    )
    day_plan_payload = {
        "id": day_plan.id,
        "routine_id": day_plan.routine_id,
        "day_of_week": day_plan.day_of_week,
        "title": day_plan.title,
        "plan_type": day_plan.plan_type,
        "effective_from": day_plan.effective_from,
        "effective_to": day_plan.effective_to,
        "priority": day_plan.priority,
        "change_reason": day_plan.change_reason,
        "created_at": day_plan.created_at,
        "updated_at": day_plan.updated_at,
        "exercises": exercises,
    }

    return AthleteRoutineDayRead.model_validate(
        {
            "date": target_date,
            "day_of_week": target_date.weekday() + 1,
            "routine": day_plan.routine,
            "day_plan": day_plan_payload,
        }
    )


def get_routine_for_day(
    db: Session,
    user_id: UUID,
    target_date: date,
) -> AthleteRoutineDayRead | None:
    day_plan = get_active_day_plan(db, user_id, target_date)
    if day_plan is None:
        return None
    return build_day_response(target_date, day_plan)


def get_routine_for_week(
    db: Session,
    user_id: UUID,
    target_date: date,
) -> AthleteRoutineWeekRead:
    week_start = get_week_start(target_date)
    week_days = [week_start + timedelta(days=offset) for offset in range(5)]
    days: list[AthleteRoutineWeekDayRead] = []

    for current_date in week_days:
        routine_day = get_routine_for_day(db, user_id, current_date)
        if routine_day is None:
            days.append(
                AthleteRoutineWeekDayRead(
                    date=current_date,
                    day_of_week=current_date.weekday() + 1,
                )
            )
            continue

        days.append(
            AthleteRoutineWeekDayRead(
                date=current_date,
                day_of_week=routine_day.day_of_week,
                routine=routine_day.routine,
                day_plan=routine_day.day_plan,
            )
        )

    return AthleteRoutineWeekRead(
        user_id=user_id,
        week_start=week_start,
        week_end=week_days[-1],
        days=days,
    )
