from collections.abc import Generator
from types import SimpleNamespace

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


def test_get_channel_topics(monkeypatch) -> None:
    from app.providers.youtube.client import YouTubeClient

    class FakeResponse:
        def json(self):
            return {
                "items": [
                    {
                        "id": "UC_topics_test",
                        "topicDetails": {
                            "topicCategories": [
                                "https://en.wikipedia.org/wiki/Pop_music",
                                "https://en.wikipedia.org/wiki/Rock_music",
                            ],
                        },
                    },
                ],
            }

    async def fake_request(self, endpoint, params):
        assert endpoint == "channels"
        assert params["part"] == "topicDetails"
        assert params["id"] == "UC_topics_test"
        return FakeResponse()

    monkeypatch.setattr(
        YouTubeClient,
        "_request",
        fake_request,
    )

    import asyncio

    client = YouTubeClient(api_key="test-api-key")

    categories = asyncio.run(
        client.get_channel_topics("UC_topics_test")
    )

    assert categories == [
        "https://en.wikipedia.org/wiki/Pop_music",
        "https://en.wikipedia.org/wiki/Rock_music",
    ]


def test_get_channel_topics_returns_empty_list_when_unavailable(
    monkeypatch,
) -> None:
    from app.providers.youtube.client import YouTubeClient

    class FakeResponse:
        def json(self):
            return {
                "items": [
                    {
                        "id": "UC_topics_test",
                        "topicDetails": {},
                    },
                ],
            }

    async def fake_request(self, endpoint, params):
        return FakeResponse()

    monkeypatch.setattr(
        YouTubeClient,
        "_request",
        fake_request,
    )

    import asyncio

    client = YouTubeClient(api_key="test-api-key")

    categories = asyncio.run(
        client.get_channel_topics("UC_topics_test")
    )

    assert categories == []


def test_get_channel_topics_returns_none_when_channel_not_found(
    monkeypatch,
) -> None:
    from app.providers.youtube.client import YouTubeClient

    class FakeResponse:
        def json(self):
            return {"items": []}

    async def fake_request(self, endpoint, params):
        return FakeResponse()

    monkeypatch.setattr(
        YouTubeClient,
        "_request",
        fake_request,
    )

    import asyncio

    client = YouTubeClient(api_key="test-api-key")

    assert asyncio.run(
        client.get_channel_topics("UC_missing")
    ) is None


def test_youtube_artist_topics_endpoint(monkeypatch) -> None:
    import app.music.youtube_artist_stats_routes as routes

    db = create_test_db()

    try:
        artist = Artist(name="YouTube Topics Test Artist")
        db.add(artist)
        db.commit()
        db.refresh(artist)

        db.add(
            ArtistProviderProfile(
                artist_id=artist.id,
                provider="youtube",
                external_id="UC_topics_endpoint",
                external_url=(
                    "https://www.youtube.com/channel/UC_topics_endpoint"
                ),
            )
        )
        db.commit()

        class FakeYouTubeClient:
            def __init__(self, api_key: str) -> None:
                assert api_key == "test-api-key"

            async def get_channel_topics(self, channel_id: str):
                assert channel_id == "UC_topics_endpoint"
                return [
                    "https://en.wikipedia.org/wiki/Pop_music",
                ]

        monkeypatch.setattr(
            routes,
            "get_settings",
            lambda: SimpleNamespace(
                youtube_api_key="test-api-key",
            ),
        )
        monkeypatch.setattr(
            routes,
            "YouTubeClient",
            FakeYouTubeClient,
        )

        app = FastAPI()
        app.include_router(api_router)

        def override_get_db() -> Generator[Session, None, None]:
            yield db

        app.dependency_overrides[get_db] = override_get_db

        with TestClient(app) as client:
            response = client.get(
                f"/api/v1/artists/{artist.id}/youtube/topics"
            )

        assert response.status_code == 200
        assert response.json() == {
            "artist_id": artist.id,
            "channel_id": "UC_topics_endpoint",
            "topic_categories": [
                "https://en.wikipedia.org/wiki/Pop_music",
            ],
        }

    finally:
        db.close()