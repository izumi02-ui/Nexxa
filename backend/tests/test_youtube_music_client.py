import pytest

from app.providers.youtube.client import YouTubeVideo
from app.providers.youtube_music.client import YouTubeMusicClient


class FakeYouTubeClient:
    def __init__(self) -> None:
        self.search_calls: list[tuple[str, int, str | None]] = []

    async def search_videos(
        self,
        query: str,
        limit: int = 20,
        page_token: str | None = None,
    ) -> tuple[list[YouTubeVideo], str | None]:
        self.search_calls.append(
            (query, limit, page_token),
        )

        if page_token is None:
            return (
                [
                    YouTubeVideo(
                        video_id="video-1",
                        title="Test Song 1",
                        channel_name="Test Artist 1",
                        description="Test description",
                        thumbnail_url="https://example.com/1.jpg",
                        duration="PT3M30S",
                        url="https://www.youtube.com/watch?v=video-1",
                    )
                ],
                "page-2",
            )

        return (
            [
                YouTubeVideo(
                    video_id="video-2",
                    title="Test Song 2",
                    channel_name="Test Artist 2",
                    description="Test description",
                    thumbnail_url="https://example.com/2.jpg",
                    duration="PT4M",
                    url="https://www.youtube.com/watch?v=video-2",
                )
            ],
            None,
        )

    async def get_video(
        self,
        external_id: str,
    ) -> YouTubeVideo | None:
        if external_id != "video-1":
            return None

        return YouTubeVideo(
            video_id="video-1",
            title="Test Song",
            channel_name="Test Artist",
            description="Test description",
            thumbnail_url="https://example.com/thumb.jpg",
            duration="PT3M30S",
            url="https://www.youtube.com/watch?v=video-1",
        )


@pytest.mark.asyncio
async def test_search_tracks_uses_youtube_data_api_client() -> None:
    youtube_client = FakeYouTubeClient()

    client = YouTubeMusicClient(
        youtube_client=youtube_client,
    )

    results = await client.search_tracks(
        query="Test Song",
        limit=10,
    )

    assert len(results) == 2
    assert results[0]["external_id"] == "video-1"
    assert results[0]["title"] == "Test Song 1"
    assert results[0]["artist_name"] == "Test Artist 1"
    assert results[0]["album_name"] is None
    assert results[0]["duration_ms"] is None
    assert results[0]["artwork_url"] == "https://example.com/1.jpg"
    assert results[0]["external_url"] == (
        "https://www.youtube.com/watch?v=video-1"
    )

    assert results[1]["external_id"] == "video-2"
    assert results[1]["title"] == "Test Song 2"
    assert results[1]["artist_name"] == "Test Artist 2"

    assert youtube_client.search_calls == [
        ("Test Song", 10, None),
        ("Test Song", 9, "page-2"),
    ]


@pytest.mark.asyncio
async def test_search_tracks_stops_at_requested_limit() -> None:
    youtube_client = FakeYouTubeClient()

    client = YouTubeMusicClient(
        youtube_client=youtube_client,
    )

    results = await client.search_tracks(
        query="Test Song",
        limit=1,
    )

    assert len(results) == 1
    assert results[0]["external_id"] == "video-1"

    assert youtube_client.search_calls == [
        ("Test Song", 1, None),
    ]


@pytest.mark.asyncio
async def test_search_tracks_returns_empty_for_zero_limit() -> None:
    youtube_client = FakeYouTubeClient()

    client = YouTubeMusicClient(
        youtube_client=youtube_client,
    )

    results = await client.search_tracks(
        query="Test Song",
        limit=0,
    )

    assert results == []
    assert youtube_client.search_calls == []


@pytest.mark.asyncio
async def test_get_track_uses_youtube_data_api_client() -> None:
    client = YouTubeMusicClient(
        youtube_client=FakeYouTubeClient(),
    )

    result = await client.get_track("video-1")

    assert result is not None
    assert result["external_id"] == "video-1"
    assert result["title"] == "Test Song"
    assert result["artist_name"] == "Test Artist"
    assert result["album_name"] is None
    assert result["duration_ms"] == 210000
    assert result["artwork_url"] == "https://example.com/thumb.jpg"
    assert result["external_url"] == (
        "https://www.youtube.com/watch?v=video-1"
    )


@pytest.mark.asyncio
async def test_get_track_returns_none_when_video_is_missing() -> None:
    client = YouTubeMusicClient(
        youtube_client=FakeYouTubeClient(),
    )

    result = await client.get_track("missing-video")

    assert result is None


def test_duration_to_ms() -> None:
    assert YouTubeMusicClient._duration_to_ms("PT3M30S") == 210000
    assert YouTubeMusicClient._duration_to_ms("PT1H2M3S") == 3723000
    assert YouTubeMusicClient._duration_to_ms("PT45S") == 45000


def test_duration_to_ms_invalid_values() -> None:
    assert YouTubeMusicClient._duration_to_ms(None) is None
    assert YouTubeMusicClient._duration_to_ms("") is None
    assert YouTubeMusicClient._duration_to_ms("invalid") is None
    assert YouTubeMusicClient._duration_to_ms("PT3") is None
