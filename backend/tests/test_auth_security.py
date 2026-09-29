import pytest

from app.auth.security import (
    create_access_token,
    decode_access_token,
)


def test_create_and_decode_access_token() -> None:
    token = create_access_token(user_id=123)

    assert isinstance(token, str)
    assert token

    user_id = decode_access_token(token)

    assert user_id == 123


def test_decode_access_token_rejects_invalid_token() -> None:
    with pytest.raises(Exception):
        decode_access_token("invalid-token")


def test_decode_access_token_rejects_token_without_subject() -> None:
    import jwt

    from app.config import get_settings

    settings = get_settings()

    token = jwt.encode(
        {},
        settings.auth_secret_key,
        algorithm="HS256",
    )

    with pytest.raises(ValueError, match="missing subject"):
        decode_access_token(token)


def test_decode_access_token_rejects_invalid_subject() -> None:
    import jwt

    from app.config import get_settings

    settings = get_settings()

    token = jwt.encode(
        {"sub": "not-an-integer"},
        settings.auth_secret_key,
        algorithm="HS256",
    )

    with pytest.raises(ValueError, match="invalid subject"):
        decode_access_token(token)
