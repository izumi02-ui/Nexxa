from fastapi import FastAPI

from app.config import get_settings


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Backend API for NEXXA, a cross-platform music application.",
    version=settings.app_version,
)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
    }