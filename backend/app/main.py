from fastapi import FastAPI

from app.config import get_settings
from app.environment import get_environment


settings = get_settings()
environment = get_environment(settings)

app = FastAPI(
    title=settings.app_name,
    description="Backend API for NEXXA, a cross-platform music application.",
    version=settings.app_version,
    debug=environment.debug,
)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": environment.name,
    }