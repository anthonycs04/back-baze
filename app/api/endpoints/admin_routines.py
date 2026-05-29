from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.routine import AdminRoutineDaySaveRequest, AdminRoutineDaySaveResponse
from app.services.admin_routine_service import save_admin_routine_day


router = APIRouter(prefix="/admin", tags=["admin-routines"])


@router.put(
    "/athletes/{user_id}/routine/day",
    response_model=AdminRoutineDaySaveResponse,
)
def save_athlete_routine_day(
    user_id: UUID,
    payload: AdminRoutineDaySaveRequest,
    db: Session = Depends(get_db),
) -> AdminRoutineDaySaveResponse:
    day_plan = save_admin_routine_day(db, user_id, payload)
    if day_plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Athlete, routine, exercise or implement not found",
        )

    return AdminRoutineDaySaveResponse(routine=day_plan.routine, day_plan=day_plan)
