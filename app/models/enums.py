from enum import Enum

from sqlalchemy.dialects.postgresql import ENUM as PgEnum


class UserRole(str, Enum):
    ADMIN = "admin"
    ATHLETE = "athlete"


class RoutineStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class RoutineSection(str, Enum):
    WARMUP = "warmup"
    MAIN = "main"


class RoutineDayPlanType(str, Enum):
    BASE = "base"
    PERMANENT_CHANGE = "permanent_change"
    TEMPORARY_OVERRIDE = "temporary_override"


class RoutineSessionStatus(str, Enum):
    STARTED = "started"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


def pg_enum(enum_class: type[Enum], name: str) -> PgEnum:
    return PgEnum(
        enum_class,
        name=name,
        values_callable=lambda values: [item.value for item in values],
        create_type=False,
    )
