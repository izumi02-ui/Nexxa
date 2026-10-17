
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
from app.music.youtube_artist_stats_models import YouTubeArtistStats
from app.music.youtube_artist_stats_service import (
    get_youtube_channel_id,
    get_youtube_total_views,
    save_youtube_total_views,
)


def create_test_db() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return Session(engine)


def test_save_and_update_youtube_total_views() -> None:
    db = create_test_db()

    try:
        artist = Artist(name="YouTube Views Test Artist")
        db.add(artist)
        db.commit()
        db.refresh(artist)

        first = save_youtube_total_views(
            db=db,
            artist_id=artist.id,
            total_views=123456,
        )
        db.commit()

        assert first.total_views == 123456

        second = save_youtube_total_views(
            db=db,
            artist_id=artist.id,
            total_views=234567,
        )
        db.commit()

        assert second.id == first.id
        assert second.total_views == 234567

        saved = get_youtube_total_views(
            db=db,
            artist_id=artist.id,
        )
        assert saved is not None
        assert saved.total_views == 234567
    finally:
        db.close()


def test_save_youtube_total_views_rejects_negative_value() -> None:
    db = create_test_db()

    try:
        with pytest.raises(
            ValueError,
            match="cannot be negative",
        ):
            save_youtube_total_views(
                db=db,
                artist_id=1,
                total_views=-1,
            )
    finally:
        db.close()


def test_get_youtube_channel_id() -> None:
    db = create_test_db()

    try:
        artist = Artist(name="Mapped Artist")
        db.add(artist)
        db.commit()
        db.refresh(artist)

        db.add(
            ArtistProviderProfile(
                artist_id=artist.id,
                provider="youtube",
                external_id="UC_test_channel",
                external_url="https://www.youtube.com/channel/UC_test_channel",
            )
        )
        db.commit()

        assert get_youtube_channel_id(
            db=db,
            artist_id=artist.id,
        ) == "UC_test_channel"

        assert get_youtube_channel_id(
            db=db,
            artist_id=999999,
        ) is None
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
        artist = Artist(name="Endpoint Test Artist")
        db.add(artist)
        db.commit()
        db.refresh(artist)

        db.add(
            ArtistProviderProfile(
                artist_id=artist.id,
                provider="youtube",
                external_id="UC_endpoint_test",
                external_url="https://www.youtube.com/channel/UC_endpoint_test",
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
            total_views = 987654

        class FakeYouTubeClient:
            def __init__(self, api_key: str) -> None:
                assert api_key == "test-api-key"

            async def get_channel(self, channel_id: str):
                assert channel_id == "UC_endpoint_test"
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


def test_refresh_youtube_total_views_endpoint(
    test_app: FastAPI,
) -> None:
    with TestClient(test_app) as client:
        response = client.get(
            f"/api/v1/artists/{test_app.state.artist_id}/youtube/total-views",
        )

        assert response.status_code == 200
        assert response.json() == {
            "artist_id": test_app.state.artist_id,
            "total_views": 987654,
        }

        # A subsequent request persists/updates the same artist row.
        response_again = client.get(
            f"/api/v1/artists/{test_app.state.artist_id}/youtube/total-views",
        )
        assert response_again.status_code == 200
        assert response_again.json()["total_views"] == 987654
