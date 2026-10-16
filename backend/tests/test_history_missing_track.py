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
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    with Session(engine) as db:
        user = User(
            email="history-missing-track-route@example.com",
            username="historymissingtrack",
            is_active=True,
        )
        artist = Artist(name="History Route Test Artist")

        db.add_all([user, artist])
        db.flush()

        track = Track(
            title="Existing Test Track",
            artist_id=artist.id,
        )
        db.add(track)
        db.commit()
        db.refresh(user)
        db.refresh(track)

        app = FastAPI()
        app.include_router(api_router)
        app.state.test_user_id = user.id
        app.state.test_track_id = track.id

        def override_get_db() -> Generator[Session, None, None]:
            yield db

        app.dependency_overrides[get_db] = override_get_db

        try:
            yield app
        finally:
            app.dependency_overrides.clear()

    engine.dispose()


def test_missing_track_returns_404_without_creating_history(
    test_app: FastAPI,
) -> None:
    token = create_access_token(
        user_id=test_app.state.test_user_id,
    )
    headers = {"Authorization": f"Bearer {token}"}

    with TestClient(test_app) as client:
        response = client.post(
            "/api/v1/history",
            json={"track_id": 999999},
            headers=headers,
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Track not found"

        history_response = client.get(
            "/api/v1/history",
            headers=headers,
        )

        assert history_response.status_code == 200
        assert history_response.json() == []


def test_existing_track_can_still_be_added_to_history(
    test_app: FastAPI,
) -> None:
    token = create_access_token(
        user_id=test_app.state.test_user_id,
    )

    with TestClient(test_app) as client:
        response = client.post(
            "/api/v1/history",
            json={"track_id": test_app.state.test_track_id},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        assert response.json()["track_id"] == test_app.state.test_track_id