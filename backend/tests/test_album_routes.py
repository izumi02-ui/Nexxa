from collections.abc import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.router import api_router
from app.database.base import Base
from app.database.session import get_db
from app.music.artist_models import Artist


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
        artist = Artist(
            name="Album Test Artist",
        )

        db.add(artist)
        db.commit()
        db.refresh(artist)

        app = FastAPI()
        app.include_router(api_router)

        app.state.artist_id = artist.id

        def override_get_db() -> Generator[Session, None, None]:
            yield db

        app.dependency_overrides[get_db] = override_get_db

        try:
            yield app
        finally:
            app.dependency_overrides.clear()


def test_create_album(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        response = client.post(
            "/api/v1/albums",
            json={
                "title": "Test Album",
                "artist_id": test_app.state.artist_id,
            },
        )

        assert response.status_code == 201

        body = response.json()

        assert body["id"] >= 1
        assert body["title"] == "Test Album"
        assert body["artist_id"] == test_app.state.artist_id
        assert body["artwork_url"] is None
        assert body["release_date"] is None


def test_get_album(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        create_response = client.post(
            "/api/v1/albums",
            json={
                "title": "Get Test Album",
                "artist_id": test_app.state.artist_id,
            },
        )

        assert create_response.status_code == 201

        album_id = create_response.json()["id"]

        response = client.get(
            f"/api/v1/albums/{album_id}",
        )

        assert response.status_code == 200

        body = response.json()

        assert body["id"] == album_id
        assert body["title"] == "Get Test Album"
        assert body["artist_id"] == test_app.state.artist_id
        assert body["artwork_url"] is None
        assert body["release_date"] is None


def test_get_missing_album_returns_404(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        response = client.get(
            "/api/v1/albums/999999",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Album not found"


def test_list_albums(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        first = client.post(
            "/api/v1/albums",
            json={
                "title": "Zeta Album",
                "artist_id": test_app.state.artist_id,
            },
        )

        second = client.post(
            "/api/v1/albums",
            json={
                "title": "Alpha Album",
                "artist_id": test_app.state.artist_id,
            },
        )

        assert first.status_code == 201
        assert second.status_code == 201

        response = client.get("/api/v1/albums")

        assert response.status_code == 200

        body = response.json()

        assert isinstance(body, list)
        assert len(body) == 2

        assert body[0]["title"] == "Alpha Album"
        assert body[1]["title"] == "Zeta Album"
