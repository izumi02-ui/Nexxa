import pytest

from app.providers.types import ProviderName
from app.providers.youtube.client import YouTubeVideo
from app.providers.youtube.provider import YouTubeProvider


class FakeYouTubeClient:
    def __init__(self) -> None:
        self.search_calls: list[tuple[str, int]] = []
        self.video_calls: list[str] = []

    async def search_videos(
        self,
        query: str,
        limit: int = 10,
        page_token: str | None = None,
    ) -> tuple[list[YouTubeVideo], str | None]:
        self.search_calls.append((query, limit))

        return [
            YouTubeVideo(
                video_id="video-1",
                title="Test Song",
                channel_name="Test Artist",
                description="Test description",
                thumbnail_url="https://example.com/thumb.jpg",
                duration=None,
                url="https://www.youtube.com/watch?v=video-1",
            )
        ], None

    async def get_video(
        self,
        external_id: str,
    ) -> YouTubeVideo | None:
        self.video_calls.append(external_id)

        if external_id == "missing":
            return None

        return YouTubeVideo(
            video_id=external_id,
            title="Test Song",
            channel_name="Test Artist",
            description="Test description",
            thumbnail_url="https://example.com/thumb.jpg",
            duration="PT3M30S",
            url=f"https://www.youtube.com/watch?v={external_id}",
        )


@pytest.mark.asyncio
async def test_provider_name() -> None:
    client = FakeYouTubeClient()
    provider = YouTubeProvider(client=client)

    assert provider.name == ProviderName.YOUTUBE


@pytest.mark.asyncio
async def test_search_tracks_normalizes_results() -> None:
    client = FakeYouTubeClient()
    provider = YouTubeProvider(client=client)

    results = await provider.search_tracks(
        query="test song",
        limit=10,
    )

    assert len(results) == 1

    track = results[0]

    assert track.provider == ProviderName.YOUTUBE
    assert track.external_id == "video-1"
    assert track.title == "Test Song"
    assert track.artist_name == "Test Artist"
    assert track.album_name is None
    assert track.duration_ms is None
    assert track.artwork_url == "https://example.com/thumb.jpg"
    assert track.external_url == (
        "https://www.youtube.com/watch?v=video-1"
    )

    assert client.search_calls == [("test song", 10)]


@pytest.mark.asyncio
async def test_get_track_normalizes_duration() -> None:
    client = FakeYouTubeClient()
    provider = YouTubeProvider(client=client)

    track = await provider.get_track("video-1")

    assert track is not None
    assert track.provider == ProviderName.YOUTUBE
    assert track.external_id == "video-1"
    assert track.title == "Test Song"
    assert track.artist_name == "Test Artist"
    assert track.duration_ms == 210_000
    assert track.artwork_url == "https://example.com/thumb.jpg"
    assert track.external_url == (
        "https://www.youtube.com/watch?v=video-1"
    )

    assert client.video_calls == ["video-1"]


@pytest.mark.asyncio
async def test_get_track_returns_none_when_video_is_missing() -> None:
    client = FakeYouTubeClient()
    provider = YouTubeProvider(client=client)

    track = await provider.get_track("missing")

    assert track is None
    assert client.video_calls == ["missing"]


def test_duration_to_ms() -> None:
    assert YouTubeProvider._duration_to_ms("PT3M30S") == 210_000
    assert YouTubeProvider._duration_to_ms("PT1H2M3S") == 3_723_000
    assert YouTubeProvider._duration_to_ms("PT45S") == 45_000
    assert YouTubeProvider._duration_to_ms(None) is None
    assert YouTubeProvider._duration_to_ms("") is None
