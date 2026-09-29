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
            email="route@example.com",
            username="routeuser",
            is_active=True,
        )

        other_user = User(
            email="other@example.com",
            username="otheruser",
            is_active=True,
        )

        artist = Artist(
            name="Test Artist",
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
            title="Test Track",
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


def test_authenticated_user_can_list_empty_favorites(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        token = create_access_token(
            user_id=test_app.state.test_user_id,
        )

        response = client.get(
            "/api/v1/favorites",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert response.status_code == 200
        assert response.json() == []


def test_authenticated_user_can_add_favorite(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        token = create_access_token(
            user_id=test_app.state.test_user_id,
        )

        response = client.post(
            "/api/v1/favorites",
            json={
                "track_id": test_app.state.test_track_id,
            },
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert response.status_code == 201
        assert response.json()["user_id"] == test_app.state.test_user_id
        assert response.json()["track_id"] == test_app.state.test_track_id


def test_authenticated_user_can_list_own_favorites(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        token = create_access_token(
            user_id=test_app.state.test_user_id,
        )

        create_response = client.post(
            "/api/v1/favorites",
            json={
                "track_id": test_app.state.test_track_id,
            },
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert create_response.status_code == 201

        list_response = client.get(
            "/api/v1/favorites",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert list_response.status_code == 200
        assert len(list_response.json()) == 1
        assert (
            list_response.json()[0]["track_id"]
            == test_app.state.test_track_id
        )
        assert (
            list_response.json()[0]["user_id"]
            == test_app.state.test_user_id
        )


def test_authenticated_users_have_isolated_favorites(
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
            "/api/v1/favorites",
            json={
                "track_id": test_app.state.test_track_id,
            },
            headers={
                "Authorization": f"Bearer {first_token}",
            },
        )

        assert create_response.status_code == 201

        first_list = client.get(
            "/api/v1/favorites",
            headers={
                "Authorization": f"Bearer {first_token}",
            },
        )

        second_list = client.get(
            "/api/v1/favorites",
            headers={
                "Authorization": f"Bearer {second_token}",
            },
        )

        assert first_list.status_code == 200
        assert second_list.status_code == 200

        assert len(first_list.json()) == 1
        assert second_list.json() == []


def test_authenticated_user_can_delete_favorite(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        token = create_access_token(
            user_id=test_app.state.test_user_id,
        )

        create_response = client.post(
            "/api/v1/favorites",
            json={
                "track_id": test_app.state.test_track_id,
            },
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert create_response.status_code == 201

        delete_response = client.delete(
            f"/api/v1/favorites/{test_app.state.test_track_id}",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert delete_response.status_code == 204


def test_authenticated_user_cannot_delete_another_users_favorite(
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
            "/api/v1/favorites",
            json={
                "track_id": test_app.state.test_track_id,
            },
            headers={
                "Authorization": f"Bearer {first_token}",
            },
        )

        assert create_response.status_code == 201

        delete_response = client.delete(
            f"/api/v1/favorites/{test_app.state.test_track_id}",
            headers={
                "Authorization": f"Bearer {second_token}",
            },
        )

        assert delete_response.status_code == 404
