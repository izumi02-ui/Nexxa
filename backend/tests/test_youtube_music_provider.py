import pytest

from app.providers.types import ProviderName
from app.providers.youtube_music.client import (
    YouTubeMusicClient,
    YouTubeMusicUnsupportedError,
)
from app.providers.youtube_music.provider import YouTubeMusicProvider


def test_youtube_music_provider_name() -> None:
    provider = YouTubeMusicProvider(
        client=YouTubeMusicClient(),
    )

    assert provider.name == ProviderName.YOUTUBE_MUSIC


@pytest.mark.asyncio
async def test_youtube_music_search_isolated_when_unsupported() -> None:
    provider = YouTubeMusicProvider(
        client=YouTubeMusicClient(),
    )

    with pytest.raises(YouTubeMusicUnsupportedError):
        await provider.search_tracks("test", limit=10)


@pytest.mark.asyncio
async def test_youtube_music_get_track_isolated_when_unsupported() -> None:
    provider = YouTubeMusicProvider(
        client=YouTubeMusicClient(),
    )

    with pytest.raises(YouTubeMusicUnsupportedError):
        await provider.get_track("test-track")
