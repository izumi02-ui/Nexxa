from collections.abc import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.router import api_router
from app.auth.models import User
from app.auth.security import create_access_token
from app.database.base import Base
from app.database.session import get_db
from app.music.artist_models import Artist
from app.music.models import Track


@pytest.fixture
def test_app() -> Generator[FastAPI, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    with Session(engine) as db:
        user = User(
            email="history-validation@example.com",
            username="historyvalidation",
            password_hash="hashed-password",
            is_active=True,
        )

        artist = Artist(
            name="Validation Test Artist",
        )

        db.add_all([user, artist])
        db.flush()

        track = Track(
            title="Validation Test Track",
            artist_id=artist.id,
        )

        db.add(track)
        db.commit()

        db.refresh(user)
        db.refresh(track)

        app = FastAPI()
        app.include_router(api_router)

        app.state.user_id = user.id
        app.state.track_id = track.id

        def override_get_db() -> Generator[Session, None, None]:
            yield db

        app.dependency_overrides[get_db] = override_get_db

        try:
            yield app
        finally:
            app.dependency_overrides.clear()


def get_auth_headers(test_app: FastAPI) -> dict[str, str]:
    token = create_access_token(
        user_id=test_app.state.user_id,
    )

    return {
        "Authorization": f"Bearer {token}",
    }


def test_history_rejects_zero_track_id(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        response = client.post(
            "/api/v1/history",
            json={
                "track_id": 0,
            },
            headers=get_auth_headers(test_app),
        )

        assert response.status_code == 422


def test_history_rejects_negative_track_id(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        response = client.post(
            "/api/v1/history",
            json={
                "track_id": -1,
            },
            headers=get_auth_headers(test_app),
        )

        assert response.status_code == 422


def test_history_rejects_missing_track_id(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        response = client.post(
            "/api/v1/history",
            json={},
            headers=get_auth_headers(test_app),
        )

        assert response.status_code == 422


def test_history_rejects_negative_position(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        response = client.post(
            "/api/v1/history",
            json={
                "track_id": test_app.state.track_id,
                "position_ms": -1,
            },
            headers=get_auth_headers(test_app),
        )

        assert response.status_code == 422


def test_history_rejects_negative_duration(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        response = client.post(
            "/api/v1/history",
            json={
                "track_id": test_app.state.track_id,
                "duration_ms": -1,
            },
            headers=get_auth_headers(test_app),
        )

        assert response.status_code == 422


def test_history_accepts_zero_position(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        response = client.post(
            "/api/v1/history",
            json={
                "track_id": test_app.state.track_id,
                "position_ms": 0,
            },
            headers=get_auth_headers(test_app),
        )

        assert response.status_code == 201

        body = response.json()

        assert body["position_ms"] == 0


def test_history_accepts_zero_duration(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        response = client.post(
            "/api/v1/history",
            json={
                "track_id": test_app.state.track_id,
                "duration_ms": 0,
            },
            headers=get_auth_headers(test_app),
        )

        assert response.status_code == 201

        body = response.json()

        assert body["duration_ms"] == 0


def test_history_accepts_track_without_optional_fields(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        response = client.post(
            "/api/v1/history",
            json={
                "track_id": test_app.state.track_id,
            },
            headers=get_auth_headers(test_app),
        )

        assert response.status_code == 201

        body = response.json()

        assert body["track_id"] == test_app.state.track_id
        assert body["position_ms"] is None
        assert body["duration_ms"] is None


def test_history_rejects_string_track_id(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        response = client.post(
            "/api/v1/history",
            json={
                "track_id": "not-a-track",
            },
            headers=get_auth_headers(test_app),
        )

        assert response.status_code == 422


def test_history_rejects_string_position(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        response = client.post(
            "/api/v1/history",
            json={
                "track_id": test_app.state.track_id,
                "position_ms": "invalid",
            },
            headers=get_auth_headers(test_app),
        )

        assert response.status_code == 422


def test_history_rejects_string_duration(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        response = client.post(
            "/api/v1/history",
            json={
                "track_id": test_app.state.track_id,
                "duration_ms": "invalid",
            },
            headers=get_auth_headers(test_app),
        )

        assert response.status_code == 422
