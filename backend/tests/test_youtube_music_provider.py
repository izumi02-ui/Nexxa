import pytest

from app.providers.types import ProviderName
from app.providers.youtube.client import YouTubeVideo
from app.providers.youtube_music.client import YouTubeMusicClient
from app.providers.youtube_music.provider import YouTubeMusicProvider


class FakeYouTubeClient:
    async def search_videos(
        self,
        query: str,
        limit: int = 20,
        page_token: str | None = None,
    ) -> tuple[list[YouTubeVideo], str | None]:
        return (
            [
                YouTubeVideo(
                    video_id="video-1",
                    title="Test Song",
                    channel_name="Test Artist",
                    description="Test description",
                    thumbnail_url="https://example.com/thumb.jpg",
                    duration="PT3M30S",
                    url="https://www.youtube.com/watch?v=video-1",
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


def create_provider() -> YouTubeMusicProvider:
    return YouTubeMusicProvider(
        client=YouTubeMusicClient(
            youtube_client=FakeYouTubeClient(),
        ),
    )


def test_youtube_music_provider_name() -> None:
    provider = create_provider()

    assert provider.name == ProviderName.YOUTUBE_MUSIC


@pytest.mark.asyncio
async def test_search_tracks_normalizes_provider_tracks() -> None:
    provider = create_provider()

    results = await provider.search_tracks(
        query="Test Song",
        limit=10,
    )

    assert len(results) == 1

    track = results[0]

    assert track.provider == ProviderName.YOUTUBE_MUSIC
    assert track.external_id == "video-1"
    assert track.title == "Test Song"
    assert track.artist_name == "Test Artist"
    assert track.album_name is None
    assert track.duration_ms is None
    assert track.artwork_url == "https://example.com/thumb.jpg"
    assert track.external_url == (
        "https://www.youtube.com/watch?v=video-1"
    )


@pytest.mark.asyncio
async def test_get_track_normalizes_provider_track() -> None:
    provider = create_provider()

    track = await provider.get_track("video-1")

    assert track is not None
    assert track.provider == ProviderName.YOUTUBE_MUSIC
    assert track.external_id == "video-1"
    assert track.title == "Test Song"
    assert track.artist_name == "Test Artist"
    assert track.album_name is None
    assert track.duration_ms == 210000
    assert track.artwork_url == "https://example.com/thumb.jpg"
    assert track.external_url == (
        "https://www.youtube.com/watch?v=video-1"
    )


@pytest.mark.asyncio
async def test_get_track_returns_none_when_missing() -> None:
    provider = create_provider()

    track = await provider.get_track("missing-video")

    assert track is None
