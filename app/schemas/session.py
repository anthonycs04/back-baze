from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import RoutineSection, RoutineSessionStatus
from app.schemas.exercise import ExerciseRead


class RoutineSessionBase(BaseModel):
    user_id: UUID
    routine_id: UUID
    routine_day_plan_id: UUID
    training_date: date | None = None
    status: RoutineSessionStatus = RoutineSessionStatus.STARTED
    started_at: datetime | None = None
    completed_at: datetime | None = None
    notes: str | None = None


class RoutineSessionCreate(RoutineSessionBase):
    pass


class RoutineSessionUpdate(BaseModel):
    user_id: UUID | None = None
    routine_id: UUID | None = None
    routine_day_plan_id: UUID | None = None
    training_date: date | None = None
    status: RoutineSessionStatus | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    notes: str | None = None


class RoutineSessionRead(RoutineSessionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    training_date: date
    created_at: datetime | None = None
    updated_at: datetime | None = None


class RoutineSessionExerciseLogBase(BaseModel):
    session_id: UUID
    routine_day_plan_exercise_id: UUID
    exercise_id: UUID
    planned_sets: int | None = Field(default=None, ge=0)
    planned_reps: str | None = Field(default=None, max_length=50)
    planned_load_value: str | None = Field(default=None, max_length=80)
    actual_sets: int | None = Field(default=None, ge=0)
    actual_reps: str | None = Field(default=None, max_length=50)
    actual_load_value: str | None = Field(default=None, max_length=80)
    is_completed: bool = False
    feedback: str | None = None
    completed_at: datetime | None = None


class RoutineSessionExerciseLogCreate(RoutineSessionExerciseLogBase):
    pass


class RoutineSessionExerciseLogUpdate(BaseModel):
    session_id: UUID | None = None
    routine_day_plan_exercise_id: UUID | None = None
    exercise_id: UUID | None = None
    planned_sets: int | None = Field(default=None, ge=0)
    planned_reps: str | None = Field(default=None, max_length=50)
    planned_load_value: str | None = Field(default=None, max_length=80)
    actual_sets: int | None = Field(default=None, ge=0)
    actual_reps: str | None = Field(default=None, max_length=50)
    actual_load_value: str | None = Field(default=None, max_length=80)
    is_completed: bool | None = None
    feedback: str | None = None
    completed_at: datetime | None = None


class RoutineSessionExerciseLogRead(RoutineSessionExerciseLogBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None
    section: RoutineSection | None = None
    order_number: int | None = None
    exercise: ExerciseRead | None = None


class RoutineSessionWithLogs(RoutineSessionRead):
    exercise_logs: list[RoutineSessionExerciseLogRead] = Field(default_factory=list)


class StartRoutineSessionRequest(BaseModel):
    user_id: UUID
    training_date: date | None = None
    notes: str | None = None


class StartAthleteRoutineSessionRequest(BaseModel):
    training_date: date | None = None
    notes: str | None = None


class RegisterExerciseCompletionRequest(BaseModel):
    actual_sets: int | None = Field(default=None, ge=0)
    actual_reps: str | None = Field(default=None, max_length=50)
    actual_load_value: str | None = Field(default=None, max_length=80)
    feedback: str | None = None
    is_completed: bool = True
    completed_at: datetime | None = None


class CompleteRoutineSessionRequest(BaseModel):
    notes: str | None = None
    completed_at: datetime | None = None
