import time

import jwt
import pytest

from app.auth.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    decode_access_token,
)
from app.config import get_settings


def test_create_and_decode_access_token() -> None:
    token = create_access_token(user_id=123)

    assert isinstance(token, str)
    assert token

    user_id = decode_access_token(token)

    assert user_id == 123


def test_access_token_contains_required_claims() -> None:
    settings = get_settings()

    token = create_access_token(user_id=123)

    payload = jwt.decode(
        token,
        settings.auth_secret_key,
        algorithms=["HS256"],
    )

    assert payload["sub"] == "123"
    assert "iat" in payload
    assert "exp" in payload
    assert payload["exp"] > payload["iat"]
    assert (
        payload["exp"] - payload["iat"]
        == ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


def test_decode_access_token_rejects_invalid_token() -> None:
    with pytest.raises(Exception):
        decode_access_token("invalid-token")


def test_decode_access_token_rejects_token_without_subject() -> None:
    settings = get_settings()

    token = jwt.encode(
        {},
        settings.auth_secret_key,
        algorithm="HS256",
    )

    with pytest.raises(ValueError, match="missing subject"):
        decode_access_token(token)


def test_decode_access_token_rejects_invalid_subject() -> None:
    settings = get_settings()

    token = jwt.encode(
        {"sub": "not-an-integer"},
        settings.auth_secret_key,
        algorithm="HS256",
    )

    with pytest.raises(ValueError, match="invalid subject"):
        decode_access_token(token)


def test_decode_access_token_rejects_expired_token() -> None:
    settings = get_settings()

    token = jwt.encode(
        {
            "sub": "123",
            "iat": int(time.time()) - 120,
            "exp": int(time.time()) - 60,
        },
        settings.auth_secret_key,
        algorithm="HS256",
    )

    with pytest.raises(Exception):
        decode_access_token(token)
