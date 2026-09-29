from collections.abc import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.router import api_router
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.auth.security import create_access_token
from app.database.base import Base
from app.database.session import get_db


@pytest.fixture
def test_app() -> Generator[FastAPI, None, None]:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        user = User(
            email="route@example.com",
            username="routeuser",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        def override_get_db() -> Generator[Session, None, None]:
            yield db

        app = FastAPI()
        app.include_router(api_router)

        app.dependency_overrides[get_db] = override_get_db

        try:
            yield app
        finally:
            app.dependency_overrides.clear()


def test_authenticated_user_can_list_empty_favorites(
    test_app: FastAPI,
) -> None:
    with Session(create_engine("sqlite:///:memory:")):
        pass

    with TestClient(test_app) as client:
        token = create_access_token(user_id=1)

        response = client.get(
            "/api/v1/favorites",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json() == []


def test_authenticated_user_can_add_favorite(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        token = create_access_token(user_id=1)

        response = client.post(
            "/api/v1/favorites",
            json={"track_id": 42},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        assert response.json()["user_id"] == 1
        assert response.json()["track_id"] == 42


def test_authenticated_user_can_delete_favorite(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        token = create_access_token(user_id=1)

        create_response = client.post(
            "/api/v1/favorites",
            json={"track_id": 55},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert create_response.status_code == 201

        delete_response = client.delete(
            "/api/v1/favorites/55",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert delete_response.status_code == 204
