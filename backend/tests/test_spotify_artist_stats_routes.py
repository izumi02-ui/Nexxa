from collections.abc import Generator
from datetime import datetime, timezone
from types import SimpleNamespace

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
from app.music.artist_provider_models import ArtistProviderProfile
from app.music.spotify_artist_stats_models import SpotifyArtistStats


@pytest.fixture
def test_app(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[FastAPI, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        artist = Artist(name="Spotify Route Test Artist")
        db.add(artist)
        db.commit()
        db.refresh(artist)

        db.add(
            ArtistProviderProfile(
                artist_id=artist.id,
                provider="spotify",
                external_id="spotify_test_artist",
                external_url=(
                    "https://open.spotify.com/artist/"
                    "spotify_test_artist"
                ),
            )
        )
        db.commit()

        app = FastAPI()
        app.include_router(api_router)
        app.state.artist_id = artist.id

        def override_get_db() -> Generator[Session, None, None]:
            yield db

        app.dependency_overrides[get_db] = override_get_db

        monkeypatch.setattr(
            "app.music.spotify_artist_stats_routes.get_settings",
            lambda: SimpleNamespace(
                spotify_client_id="test-client-id",
                spotify_client_secret="test-client-secret",
            ),
        )

        try:
            yield app
        finally:
            app.dependency_overrides.clear()


def test_get_spotify_artist_statistics_returns_saved_data(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        response = client.get(
            f"/api/v1/artists/{test_app.state.artist_id}"
            "/spotify/statistics"
        )

    assert response.status_code == 404


def test_get_spotify_artist_statistics_returns_404_for_unknown_artist(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        response = client.get(
            "/api/v1/artists/999999/spotify/statistics"
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Artist not found"


def test_refresh_spotify_artist_statistics(
    test_app: FastAPI,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.music.spotify_artist_stats_routes as routes

    class FakeSpotifyClient:
        def __init__(
            self,
            client_id: str,
            client_secret: str,
        ) -> None:
            assert client_id == "test-client-id"
            assert client_secret == "test-client-secret"

    async def fake_refresh(
        db: Session,
        artist_id: int,
        client: FakeSpotifyClient,
    ) -> SpotifyArtistStats:
        stats = SpotifyArtistStats(
            artist_id=artist_id,
            spotify_artist_id="spotify_test_artist",
            spotify_url=(
                "https://open.spotify.com/artist/"
                "spotify_test_artist"
            ),
            followers=12345,
            popularity=80,
            monthly_listeners=None,
            genres=["pop"],
            albums=[],
            singles=[],
            top_tracks=[],
            statistics_available=True,
            statistics_fetched_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(stats)
        db.flush()
        return stats

    monkeypatch.setattr(
        routes,
        "SpotifyClient",
        FakeSpotifyClient,
    )
    monkeypatch.setattr(
        routes,
        "refresh_spotify_artist_stats",
        fake_refresh,
    )

    with TestClient(test_app) as client:
        response = client.post(
            f"/api/v1/artists/{test_app.state.artist_id}"
            "/spotify/statistics/refresh"
        )

    assert response.status_code == 200

    payload = response.json()
    assert payload["artist_id"] == test_app.state.artist_id
    assert payload["refreshed"] is True
    assert payload["statistics"]["spotify_artist_id"] == (
        "spotify_test_artist"
    )
    assert payload["statistics"]["followers"] == 12345
    assert payload["statistics"]["popularity"] == 80


def test_refresh_spotify_artist_statistics_requires_mapping(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        response = client.post(
            "/api/v1/artists/999999/spotify/statistics/refresh"
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Artist not found"