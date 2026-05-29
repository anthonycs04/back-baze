from fastapi import APIRouter

from app.api.endpoints import admin_routines, athlete, auth, exercises, health, implements, sessions, users


api_router = APIRouter()
api_router.include_router(admin_routines.router)
api_router.include_router(athlete.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(exercises.router)
api_router.include_router(implements.router)
api_router.include_router(sessions.router)
api_router.include_router(health.router)
