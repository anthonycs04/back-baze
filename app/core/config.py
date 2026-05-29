import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Baze Fitness API"
    app_version: str = "0.1.0"
    environment: str = "local"
    database_url: str | None = None
    sql_echo: bool = False
    supabase_url: str | None = None
    supabase_storage_bucket: str | None = None
    supabase_service_role_key: str | None = None
    backend_cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@lru_cache
def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        app_name=os.getenv("APP_NAME", "Baze Fitness API"),
        app_version=os.getenv("APP_VERSION", "0.1.0"),
        environment=os.getenv("ENVIRONMENT", "local"),
        database_url=os.getenv("DATABASE_URL"),
        sql_echo=_to_bool(os.getenv("SQL_ECHO")),
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_storage_bucket=os.getenv("SUPABASE_STORAGE_BUCKET"),
        supabase_service_role_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
        backend_cors_origins=[
            origin.strip()
            for origin in os.getenv(
                "BACKEND_CORS_ORIGINS",
                "http://localhost:5173,http://127.0.0.1:5173",
            ).split(",")
            if origin.strip()
        ],
    )


settings = get_settings()
