from fastapi import Request
from fastapi.responses import JSONResponse

from app.errors.exceptions import NEXXAError


async def nexxa_error_handler(
    request: Request,
    exc: NEXXAError,
) -> JSONResponse:
    return JSONResponse(
        status_code=_status_code_for_error(exc.code),
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        },
    )


def _status_code_for_error(code: str) -> int:
    return {
        "NOT_FOUND": 404,
        "VALIDATION_ERROR": 400,
        "AUTHENTICATION_REQUIRED": 401,
        "FORBIDDEN": 403,
        "PROVIDER_UNAVAILABLE": 503,
    }.get(code, 400)
