from pathlib import Path
from uuid import uuid4
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from fastapi import UploadFile

from app.core.config import settings


class StorageConfigurationError(Exception):
    pass


class StorageUploadError(Exception):
    pass


def is_video_upload(file: UploadFile) -> bool:
    content_type = file.content_type or ""
    return content_type.startswith("video/")


def upload_exercise_video(file: UploadFile) -> str:
    if not settings.supabase_url:
        raise StorageConfigurationError("SUPABASE_URL is not configured")
    if not settings.supabase_storage_bucket:
        raise StorageConfigurationError("SUPABASE_STORAGE_BUCKET is not configured")
    if not settings.supabase_service_role_key:
        raise StorageConfigurationError("SUPABASE_SERVICE_ROLE_KEY is not configured")

    file.file.seek(0)
    content = file.file.read()
    if not content:
        raise StorageUploadError("Video file is empty")

    extension = Path(file.filename or "").suffix.lower() or ".mp4"
    object_path = f"exercises/{uuid4()}{extension}"
    base_url = settings.supabase_url.rstrip("/")
    bucket = quote(settings.supabase_storage_bucket, safe="")
    quoted_path = quote(object_path, safe="/")
    upload_url = f"{base_url}/storage/v1/object/{bucket}/{quoted_path}"

    request = Request(
        upload_url,
        data=content,
        method="POST",
        headers={
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
            "apikey": settings.supabase_service_role_key,
            "Content-Type": file.content_type or "application/octet-stream",
            "Cache-Control": "3600",
            "x-upsert": "false",
        },
    )

    try:
        with urlopen(request, timeout=30):
            pass
    except HTTPError as exc:
        raise StorageUploadError(f"Supabase Storage upload failed with status {exc.code}") from exc
    except URLError as exc:
        raise StorageUploadError("Supabase Storage is unavailable") from exc

    return f"{base_url}/storage/v1/object/public/{bucket}/{quoted_path}"
