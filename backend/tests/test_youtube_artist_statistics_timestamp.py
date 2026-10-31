from collections.abc import Generator
from datetime import datetime, timezone

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
    get_youtube_statistics_timestamp,
    save_youtube_public_video_count,
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


def test_save_youtube_total_views_sets_statistics_timestamp() -> None:
    db = create_test_db()

    try:
        artist = Artist(name="YouTube Timestamp Views Artist")
        db.add(artist)
        db.commit()
        db.refresh(artist)

        stats = save_youtube_total_views(
            db=db,
            artist_id=artist.id,
            total_views=123456,
        )
        db.commit()

        assert stats.statistics_fetched_at is not None
        assert stats.statistics_fetched_at.tzinfo is not None

    finally:
        db.close()


def test_save_youtube_public_video_count_sets_statistics_timestamp() -> None:
    db = create_test_db()

    try:
        artist = Artist(name="YouTube Timestamp Videos Artist")
        db.add(artist)
        db.commit()
        db.refresh(artist)

        stats = save_youtube_public_video_count(
            db=db,
            artist_id=artist.id,
            public_video_count=150,
        )
        db.commit()

        assert stats.statistics_fetched_at is not None
        assert stats.statistics_fetched_at.tzinfo is not None

    finally:
        db.close()


def test_get_youtube_statistics_timestamp_returns_saved_value() -> None:
    db = create_test_db()

    try:
        artist = Artist(name="YouTube Saved Timestamp Artist")
        db.add(artist)
        db.commit()
        db.refresh(artist)

        expected_timestamp = datetime(
            2026, 10, 31, 10, 30, tzinfo=timezone.utc
        )

        db.add(
            YouTubeArtistStats(
                artist_id=artist.id,
                total_views=5000,
                statistics_fetched_at=expected_timestamp,
            )
        )
        db.commit()

        timestamp = get_youtube_statistics_timestamp(
            db=db,
            artist_id=artist.id,
        )

        assert timestamp is not None
        assert timestamp.replace(tzinfo=timezone.utc) == expected_timestamp

    finally:
        db.close()


def test_get_youtube_statistics_timestamp_returns_none_without_stats() -> None:
    db = create_test_db()

    try:
        artist = Artist(name="YouTube Missing Timestamp Artist")
        db.add(artist)
        db.commit()
        db.refresh(artist)

        assert get_youtube_statistics_timestamp(
            db=db,
            artist_id=artist.id,
        ) is None

    finally:
        db.close()


def test_youtube_statistics_timestamp_endpoint() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        artist = Artist(name="YouTube Timestamp Endpoint Artist")
        db.add(artist)
        db.commit()
        db.refresh(artist)

        db.add(
            ArtistProviderProfile(
                artist_id=artist.id,
                provider="youtube",
                external_id="UC_timestamp_test",
                external_url=(
                    "https://www.youtube.com/channel/UC_timestamp_test"
                ),
            )
        )

        expected_timestamp = datetime.now(timezone.utc)

        db.add(
            YouTubeArtistStats(
                artist_id=artist.id,
                total_views=1000,
                statistics_fetched_at=expected_timestamp,
            )
        )
        db.commit()

        app = FastAPI()
        app.include_router(api_router)

        def override_get_db() -> Generator[Session, None, None]:
            yield db

        app.dependency_overrides[get_db] = override_get_db

        try:
            with TestClient(app) as client:
                response = client.get(
                    f"/api/v1/artists/{artist.id}"
                    "/youtube/statistics-timestamp"
                )

            assert response.status_code == 200

            data = response.json()

            assert data["artist_id"] == artist.id
            assert data["channel_id"] == "UC_timestamp_test"
            assert data["statistics_fetched_at"] is not None

        finally:
            app.dependency_overrides.clear()