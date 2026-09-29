import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.auth.security import create_access_token
from app.database.base import Base


@pytest.fixture
def db() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


def test_get_current_user_requires_credentials(
    db: Session,
) -> None:
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(
            credentials=None,
            db=db,
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authentication required"


def test_get_current_user_rejects_invalid_token(
    db: Session,
) -> None:
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="invalid-token",
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(
            credentials=credentials,
            db=db,
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid authentication credentials"


def test_get_current_user_rejects_unknown_user(
    db: Session,
) -> None:
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=create_access_token(user_id=999),
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(
            credentials=credentials,
            db=db,
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid authentication credentials"


def test_get_current_user_returns_active_user(
    db: Session,
) -> None:
    user = User(
        email="active@example.com",
        username="activeuser",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=create_access_token(user_id=user.id),
    )

    current_user = get_current_user(
        credentials=credentials,
        db=db,
    )

    assert current_user.id == user.id
    assert current_user.email == "active@example.com"
    assert current_user.is_active is True


def test_get_current_user_rejects_inactive_user(
    db: Session,
) -> None:
    user = User(
        email="inactive@example.com",
        username="inactiveuser",
        is_active=False,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=create_access_token(user_id=user.id),
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(
            credentials=credentials,
            db=db,
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "User account is inactive"
