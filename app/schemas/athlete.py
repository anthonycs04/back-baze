from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.routine import RoutineDayPlanWithExercises, RoutineRead


class AthleteRoutineDayRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: date
    day_of_week: int = Field(..., ge=1, le=7)
    routine: RoutineRead
    day_plan: RoutineDayPlanWithExercises


class AthleteRoutineWeekDayRead(BaseModel):
    date: date
    day_of_week: int = Field(..., ge=1, le=5)
    routine: RoutineRead | None = None
    day_plan: RoutineDayPlanWithExercises | None = None


class AthleteRoutineWeekRead(BaseModel):
    user_id: UUID
    week_start: date
    week_end: date
    days: list[AthleteRoutineWeekDayRead]
