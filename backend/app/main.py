from fastapi import FastAPI

from app.api.router import api_router
from app.config import get_settings
from app.environment import get_environment
from app.errors.exceptions import NEXXAError
from app.errors.handlers import nexxa_error_handler
from app.logging_config import configure_logging, get_logger


configure_logging()

logger = get_logger(__name__)

settings = get_settings()
environment = get_environment(settings)

app = FastAPI(
    title=settings.app_name,
    description="Backend API for NEXXA, a cross-platform music application.",
    version=settings.app_version,
    debug=environment.debug,
)

app.add_exception_handler(
    NEXXAError,
    nexxa_error_handler,
)

app.include_router(api_router)


@app.get("/")
async def root() -> dict[str, str]:
    logger.info("Root endpoint requested")

    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": environment.name,
    }