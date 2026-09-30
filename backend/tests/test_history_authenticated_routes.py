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
            email="history-route@example.com",
            username="historyrouteuser",
            is_active=True,
        )

        other_user = User(
            email="history-other@example.com",
            username="historyotheruser",
            is_active=True,
        )

        artist = Artist(
            name="History Test Artist",
        )

        db.add_all(
            [
                user,
                other_user,
                artist,
            ]
        )

        db.commit()

        db.refresh(user)
        db.refresh(other_user)
        db.refresh(artist)

        track = Track(
            title="History Test Track",
            artist_id=artist.id,
        )

        db.add(track)
        db.commit()
        db.refresh(track)

        app = FastAPI()
        app.include_router(api_router)

        app.state.test_user_id = user.id
        app.state.other_user_id = other_user.id
        app.state.test_track_id = track.id

        def override_get_db() -> Generator[Session, None, None]:
            yield db

        app.dependency_overrides[get_db] = override_get_db

        try:
            yield app
        finally:
            app.dependency_overrides.clear()


def test_authenticated_user_can_create_history(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        token = create_access_token(
            user_id=test_app.state.test_user_id,
        )

        response = client.post(
            "/api/v1/history",
            json={
                "track_id": test_app.state.test_track_id,
                "position_ms": 30_000,
                "duration_ms": 240_000,
            },
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert response.status_code == 201

        body = response.json()

        assert body["user_id"] == test_app.state.test_user_id
        assert body["track_id"] == test_app.state.test_track_id
        assert body["position_ms"] == 30_000
        assert body["duration_ms"] == 240_000


def test_authenticated_user_can_list_own_history(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        token = create_access_token(
            user_id=test_app.state.test_user_id,
        )

        create_response = client.post(
            "/api/v1/history",
            json={
                "track_id": test_app.state.test_track_id,
            },
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert create_response.status_code == 201

        list_response = client.get(
            "/api/v1/history",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert list_response.status_code == 200

        history = list_response.json()

        assert len(history) == 1
        assert history[0]["user_id"] == test_app.state.test_user_id
        assert history[0]["track_id"] == test_app.state.test_track_id


def test_authenticated_users_have_isolated_history(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        first_token = create_access_token(
            user_id=test_app.state.test_user_id,
        )

        second_token = create_access_token(
            user_id=test_app.state.other_user_id,
        )

        create_response = client.post(
            "/api/v1/history",
            json={
                "track_id": test_app.state.test_track_id,
            },
            headers={
                "Authorization": f"Bearer {first_token}",
            },
        )

        assert create_response.status_code == 201

        first_list = client.get(
            "/api/v1/history",
            headers={
                "Authorization": f"Bearer {first_token}",
            },
        )

        second_list = client.get(
            "/api/v1/history",
            headers={
                "Authorization": f"Bearer {second_token}",
            },
        )

        assert first_list.status_code == 200
        assert second_list.status_code == 200

        assert len(first_list.json()) == 1
        assert second_list.json() == []


def test_authenticated_user_cannot_delete_another_users_history(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        first_token = create_access_token(
            user_id=test_app.state.test_user_id,
        )

        second_token = create_access_token(
            user_id=test_app.state.other_user_id,
        )

        create_response = client.post(
            "/api/v1/history",
            json={
                "track_id": test_app.state.test_track_id,
            },
            headers={
                "Authorization": f"Bearer {first_token}",
            },
        )

        assert create_response.status_code == 201

        history_id = create_response.json()["id"]

        delete_response = client.delete(
            f"/api/v1/history/{history_id}",
            headers={
                "Authorization": f"Bearer {second_token}",
            },
        )

        assert delete_response.status_code == 404

        owner_history = client.get(
            "/api/v1/history",
            headers={
                "Authorization": f"Bearer {first_token}",
            },
        )

        assert owner_history.status_code == 200
        assert len(owner_history.json()) == 1
        assert owner_history.json()[0]["id"] == history_id


def test_authenticated_user_can_delete_own_history(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        token = create_access_token(
            user_id=test_app.state.test_user_id,
        )

        create_response = client.post(
            "/api/v1/history",
            json={
                "track_id": test_app.state.test_track_id,
            },
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert create_response.status_code == 201

        history_id = create_response.json()["id"]

        delete_response = client.delete(
            f"/api/v1/history/{history_id}",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert delete_response.status_code == 204

        list_response = client.get(
            "/api/v1/history",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert list_response.status_code == 200
        assert list_response.json() == []


def test_authenticated_user_can_clear_own_history(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        token = create_access_token(
            user_id=test_app.state.test_user_id,
        )

        for _ in range(3):
            response = client.post(
                "/api/v1/history",
                json={
                    "track_id": test_app.state.test_track_id,
                },
                headers={
                    "Authorization": f"Bearer {token}",
                },
            )

            assert response.status_code == 201

        delete_response = client.delete(
            "/api/v1/history",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert delete_response.status_code == 204

        list_response = client.get(
            "/api/v1/history",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert list_response.status_code == 200
        assert list_response.json() == []


def test_clear_history_does_not_delete_another_users_history(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        first_token = create_access_token(
            user_id=test_app.state.test_user_id,
        )

        second_token = create_access_token(
            user_id=test_app.state.other_user_id,
        )

        first_create = client.post(
            "/api/v1/history",
            json={
                "track_id": test_app.state.test_track_id,
            },
            headers={
                "Authorization": f"Bearer {first_token}",
            },
        )

        assert first_create.status_code == 201

        second_create = client.post(
            "/api/v1/history",
            json={
                "track_id": test_app.state.test_track_id,
            },
            headers={
                "Authorization": f"Bearer {second_token}",
            },
        )

        assert second_create.status_code == 201

        clear_response = client.delete(
            "/api/v1/history",
            headers={
                "Authorization": f"Bearer {first_token}",
            },
        )

        assert clear_response.status_code == 204

        first_history = client.get(
            "/api/v1/history",
            headers={
                "Authorization": f"Bearer {first_token}",
            },
        )

        second_history = client.get(
            "/api/v1/history",
            headers={
                "Authorization": f"Bearer {second_token}",
            },
        )

        assert first_history.status_code == 200
        assert second_history.status_code == 200

        assert first_history.json() == []
        assert len(second_history.json()) == 1


def test_history_requires_authentication(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        list_response = client.get(
            "/api/v1/history",
        )

        create_response = client.post(
            "/api/v1/history",
            json={
                "track_id": test_app.state.test_track_id,
            },
        )

        assert list_response.status_code == 401
        assert create_response.status_code == 401
