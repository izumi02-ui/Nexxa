import jwt

from app.config import get_settings


def create_access_token(user_id: int) -> str:
    """Create a signed access token for an authenticated user."""

    settings = get_settings()

    payload = {
        "sub": str(user_id),
    }

    return jwt.encode(
        payload,
        settings.auth_secret_key,
        algorithm="HS256",
    )


def decode_access_token(token: str) -> int:
    """Decode and validate an access token."""

    settings = get_settings()

    payload = jwt.decode(
        token,
        settings.auth_secret_key,
        algorithms=["HS256"],
    )

    user_id = payload.get("sub")

    if user_id is None:
        raise ValueError("Access token is missing subject")

    try:
        return int(user_id)
    except (TypeError, ValueError) as exc:
        raise ValueError("Access token contains invalid subject") from exc
