from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import RoutineDayPlanType, RoutineSection, RoutineStatus
from app.schemas.exercise import ExerciseRead
from app.schemas.implement import ImplementRead


class RoutineBase(BaseModel):
    user_id: UUID
    name: str = Field(..., max_length=150)
    status: RoutineStatus = RoutineStatus.ACTIVE
    start_date: date | None = None
    end_date: date | None = None
    notes: str | None = None


class RoutineCreate(RoutineBase):
    pass


class RoutineUpdate(BaseModel):
    user_id: UUID | None = None
    name: str | None = Field(default=None, max_length=150)
    status: RoutineStatus | None = None
    start_date: date | None = None
    end_date: date | None = None
    notes: str | None = None


class RoutineRead(RoutineBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None


class RoutineDayPlanBase(BaseModel):
    routine_id: UUID
    day_of_week: int = Field(..., ge=1, le=5)
    title: str | None = Field(default=None, max_length=120)
    plan_type: RoutineDayPlanType = RoutineDayPlanType.BASE
    effective_from: date
    effective_to: date | None = None
    priority: int = 0
    change_reason: str | None = None


class RoutineDayPlanCreate(RoutineDayPlanBase):
    pass


class RoutineDayPlanUpdate(BaseModel):
    routine_id: UUID | None = None
    day_of_week: int | None = Field(default=None, ge=1, le=5)
    title: str | None = Field(default=None, max_length=120)
    plan_type: RoutineDayPlanType | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    priority: int | None = None
    change_reason: str | None = None


class RoutineDayPlanRead(RoutineDayPlanBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None


class RoutineDayPlanExerciseBase(BaseModel):
    routine_day_plan_id: UUID
    exercise_id: UUID
    section: RoutineSection = RoutineSection.MAIN
    order_number: int = Field(..., ge=1)
    sets: int | None = Field(default=None, ge=0)
    reps: str | None = Field(default=None, max_length=50)
    implement_id: UUID | None = None
    load_value: str | None = Field(default=None, max_length=80)
    notes: str | None = None


class RoutineDayPlanExerciseCreate(RoutineDayPlanExerciseBase):
    pass


class RoutineDayPlanExerciseUpdate(BaseModel):
    routine_day_plan_id: UUID | None = None
    exercise_id: UUID | None = None
    section: RoutineSection | None = None
    order_number: int | None = Field(default=None, ge=1)
    sets: int | None = Field(default=None, ge=0)
    reps: str | None = Field(default=None, max_length=50)
    implement_id: UUID | None = None
    load_value: str | None = Field(default=None, max_length=80)
    notes: str | None = None


class RoutineDayPlanExerciseRead(RoutineDayPlanExerciseBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None
    exercise: ExerciseRead | None = None
    implement: ImplementRead | None = None


class RoutineDayPlanWithExercises(RoutineDayPlanRead):
    exercises: list[RoutineDayPlanExerciseRead] = Field(default_factory=list)


class RoutineWithDayPlans(RoutineRead):
    day_plans: list[RoutineDayPlanWithExercises] = Field(default_factory=list)


class AdminRoutineDayExerciseInput(BaseModel):
    exercise_id: UUID
    section: RoutineSection = RoutineSection.MAIN
    order_number: int = Field(..., ge=1)
    sets: int | None = Field(default=None, ge=0)
    reps: str | None = Field(default=None, max_length=50)
    implement_id: UUID | None = None
    load_value: str | None = Field(default=None, max_length=80)
    notes: str | None = None


class AdminRoutineDaySaveRequest(BaseModel):
    routine_id: UUID | None = None
    routine_name: str | None = Field(default=None, max_length=150)
    day_of_week: int = Field(..., ge=1, le=5)
    title: str | None = Field(default=None, max_length=120)
    effective_from: date | None = None
    effective_to: date | None = None
    priority: int | None = None
    change_reason: str | None = None
    exercises: list[AdminRoutineDayExerciseInput] = Field(default_factory=list)


class AdminRoutineDaySaveResponse(BaseModel):
    routine: RoutineRead
    day_plan: RoutineDayPlanWithExercises
