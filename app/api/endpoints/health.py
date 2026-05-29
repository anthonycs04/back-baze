from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.database import check_database_connection


router = APIRouter(tags=["health"])


@router.get("/health", response_model=None)
def health_check(check_db: bool = Query(default=False)) -> dict[str, str] | JSONResponse:
    payload = {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
    }

    if not check_db:
        return payload

    database_ok = check_database_connection()
    payload["database"] = "ok" if database_ok else "unavailable"

    if not database_ok:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=payload,
        )

    return payload
