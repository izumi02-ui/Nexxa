import pytest

from app.providers.youtube_music.client import (
    YouTubeMusicClient,
    YouTubeMusicUnsupportedError,
)


@pytest.mark.asyncio
async def test_search_tracks_raises_unsupported_error() -> None:
    client = YouTubeMusicClient()

    with pytest.raises(YouTubeMusicUnsupportedError):
        await client.search_tracks("test")


@pytest.mark.asyncio
async def test_get_track_raises_unsupported_error() -> None:
    client = YouTubeMusicClient()

    with pytest.raises(YouTubeMusicUnsupportedError):
        await client.get_track("test-track")
