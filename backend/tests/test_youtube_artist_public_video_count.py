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
from app.music.artist_provider_models import ArtistProviderProfile
from app.music.youtube_artist_stats_service import (
    get_youtube_public_video_count,
    save_youtube_public_video_count,
)


def create_test_db() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return Session(engine)


def test_save_and_update_youtube_public_video_count() -> None:
    db = create_test_db()

    try:
        artist = Artist(name="YouTube Video Count Test Artist")
        db.add(artist)
        db.commit()
        db.refresh(artist)

        first = save_youtube_public_video_count(
            db=db,
            artist_id=artist.id,
            public_video_count=125,
        )
        db.commit()

        assert first.public_video_count == 125

        second = save_youtube_public_video_count(
            db=db,
            artist_id=artist.id,
            public_video_count=150,
        )
        db.commit()

        assert second.id == first.id
        assert second.public_video_count == 150

        saved = get_youtube_public_video_count(
            db=db,
            artist_id=artist.id,
        )

        assert saved is not None
        assert saved.public_video_count == 150
    finally:
        db.close()


def test_save_youtube_public_video_count_rejects_negative_value() -> None:
    db = create_test_db()

    try:
        with pytest.raises(
            ValueError,
            match="cannot be negative",
        ):
            save_youtube_public_video_count(
                db=db,
                artist_id=1,
                public_video_count=-1,
            )
    finally:
        db.close()


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
        artist = Artist(name="Public Video Count Endpoint Artist")
        db.add(artist)
        db.commit()
        db.refresh(artist)

        db.add(
            ArtistProviderProfile(
                artist_id=artist.id,
                provider="youtube",
                external_id="UC_video_count_test",
                external_url=(
                    "https://www.youtube.com/channel/UC_video_count_test"
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

        class FakeChannel:
            public_video_count = 321

        class FakeYouTubeClient:
            def __init__(self, api_key: str) -> None:
                assert api_key == "test-api-key"

            async def get_channel(self, channel_id: str):
                assert channel_id == "UC_video_count_test"
                return FakeChannel()

        monkeypatch.setattr(
            "app.music.youtube_artist_stats_routes.get_settings",
            lambda: type(
                "Settings",
                (),
                {"youtube_api_key": "test-api-key"},
            )(),
        )
        monkeypatch.setattr(
            "app.music.youtube_artist_stats_routes.YouTubeClient",
            FakeYouTubeClient,
        )

        try:
            yield app
        finally:
            app.dependency_overrides.clear()


def test_refresh_youtube_public_video_count_endpoint(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        response = client.get(
            f"/api/v1/artists/{test_app.state.artist_id}"
            "/youtube/public-video-count",
        )

        assert response.status_code == 200
        assert response.json() == {
            "artist_id": test_app.state.artist_id,
            "public_video_count": 321,
        }

        response_again = client.get(
            f"/api/v1/artists/{test_app.state.artist_id}"
            "/youtube/public-video-count",
        )

        assert response_again.status_code == 200
        assert response_again.json()["public_video_count"] == 321