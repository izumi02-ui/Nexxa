from collections.abc import Generator

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


def create_test_db() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return Session(engine)


def test_get_youtube_channel_profile() -> None:
    from app.music.youtube_artist_stats_service import (
        get_youtube_channel_profile,
    )

    db = create_test_db()

    try:
        artist = Artist(name="YouTube Profile Test Artist")
        db.add(artist)
        db.commit()
        db.refresh(artist)

        db.add(
            ArtistProviderProfile(
                artist_id=artist.id,
                provider="youtube",
                external_id="UC_test_channel",
                external_url=(
                    "https://www.youtube.com/channel/UC_test_channel"
                ),
            )
        )
        db.commit()

        profile = get_youtube_channel_profile(
            db=db,
            artist_id=artist.id,
        )

        assert profile == {
            "channel_id": "UC_test_channel",
            "external_url": (
                "https://www.youtube.com/channel/UC_test_channel"
            ),
        }

        assert get_youtube_channel_profile(
            db=db,
            artist_id=999999,
        ) is None
    finally:
        db.close()


def test_get_youtube_channel_profile_uses_canonical_url_if_missing() -> None:
    from app.music.youtube_artist_stats_service import (
        get_youtube_channel_profile,
    )

    db = create_test_db()

    try:
        artist = Artist(name="YouTube URL Fallback Test Artist")
        db.add(artist)
        db.commit()
        db.refresh(artist)

        db.add(
            ArtistProviderProfile(
                artist_id=artist.id,
                provider="youtube",
                external_id="UC_fallback_test",
                external_url=None,
            )
        )
        db.commit()

        profile = get_youtube_channel_profile(
            db=db,
            artist_id=artist.id,
        )

        assert profile == {
            "channel_id": "UC_fallback_test",
            "external_url": (
                "https://www.youtube.com/channel/UC_fallback_test"
            ),
        }
    finally:
        db.close()


def test_get_youtube_channel_profile_returns_none_without_mapping() -> None:
    from app.music.youtube_artist_stats_service import (
        get_youtube_channel_profile,
    )

    db = create_test_db()

    try:
        artist = Artist(name="Unmapped YouTube Artist")
        db.add(artist)
        db.commit()
        db.refresh(artist)

        assert get_youtube_channel_profile(
            db=db,
            artist_id=artist.id,
        ) is None
    finally:
        db.close()


def test_youtube_artist_profile_endpoint() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        artist = Artist(name="YouTube Endpoint Test Artist")
        db.add(artist)
        db.commit()
        db.refresh(artist)

        db.add(
            ArtistProviderProfile(
                artist_id=artist.id,
                provider="youtube",
                external_id="UC_endpoint_test",
                external_url=(
                    "https://www.youtube.com/channel/UC_endpoint_test"
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

        try:
            with TestClient(app) as client:
                response = client.get(
                    f"/api/v1/artists/{artist.id}/youtube/profile"
                )

                assert response.status_code == 200
                assert response.json() == {
                    "artist_id": artist.id,
                    "channel_id": "UC_endpoint_test",
                    "external_url": (
                        "https://www.youtube.com/channel/UC_endpoint_test"
                    ),
                }
        finally:
            app.dependency_overrides.clear()