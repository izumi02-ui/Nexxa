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
        artist = Artist(
            name="API Test Artist",
        )

        db.add(artist)
        db.commit()
        db.refresh(artist)

        app = FastAPI()
        app.include_router(api_router)

        app.state.artist_id = artist.id
        app.state.db = db

        def override_get_db() -> Generator[Session, None, None]:
            yield db

        app.dependency_overrides[get_db] = override_get_db

        try:
            yield app
        finally:
            app.dependency_overrides.clear()


def test_create_album_api(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        response = client.post(
            "/api/v1/albums",
            json={
                "title": "API Album",
                "artist_id": test_app.state.artist_id,
            },
        )

        assert response.status_code == 201

        body = response.json()

        assert body["title"] == "API Album"
        assert body["artist_id"] == test_app.state.artist_id


def test_get_album_api(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        create_response = client.post(
            "/api/v1/albums",
            json={
                "title": "Get API Album",
                "artist_id": test_app.state.artist_id,
            },
        )

        assert create_response.status_code == 201

        album_id = create_response.json()["id"]

        response = client.get(
            f"/api/v1/albums/{album_id}",
        )

        assert response.status_code == 200
        assert response.json()["id"] == album_id


def test_list_albums_api(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        for title in (
            "First API Album",
            "Second API Album",
        ):
            response = client.post(
                "/api/v1/albums",
                json={
                    "title": title,
                    "artist_id": test_app.state.artist_id,
                },
            )

            assert response.status_code == 201

        response = client.get("/api/v1/albums")

        assert response.status_code == 200
        assert len(response.json()) == 2


def test_album_tracks_api(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        create_response = client.post(
            "/api/v1/albums",
            json={
                "title": "Tracks API Album",
                "artist_id": test_app.state.artist_id,
            },
        )

        assert create_response.status_code == 201

        album_id = create_response.json()["id"]

        db: Session = test_app.state.db

        track = Track(
            title="API Track",
            artist_id=test_app.state.artist_id,
            album_id=album_id,
        )

        db.add(track)
        db.commit()
        db.refresh(track)

        response = client.get(
            f"/api/v1/albums/{album_id}/tracks",
        )

        assert response.status_code == 200

        body = response.json()

        assert len(body) == 1
        assert body[0]["title"] == "API Track"
        assert body[0]["album_id"] == album_id


def test_missing_album_api(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        response = client.get(
            "/api/v1/albums/999999",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Album not found"
