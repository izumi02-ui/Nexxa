from fastapi import APIRouter

from app.config import get_settings


router = APIRouter()

settings = get_settings()


@router.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "nexxa-api",
        "version": settings.app_version,
    }