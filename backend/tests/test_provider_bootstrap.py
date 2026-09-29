import pytest

from app.config import Settings
from app.providers.bootstrap import create_provider_registry
from app.providers.registry import ProviderRegistry
from app.providers.spotify.provider import SpotifyProvider
from app.providers.types import ProviderName
from app.providers.youtube.provider import YouTubeProvider
from app.providers.youtube_music.provider import YouTubeMusicProvider


def make_settings(
    client_id: str | None = "test-client-id",
    client_secret: str | None = "test-client-secret",
    youtube_api_key: str | None = "test-youtube-api-key",
) -> Settings:
    return Settings(
        database_url=(
            "postgresql+psycopg://user:password@localhost:5432/nexxa"
        ),
        spotify_client_id=client_id,
        spotify_client_secret=client_secret,
        youtube_api_key=youtube_api_key,
    )


@pytest.mark.asyncio
async def test_provider_registry_starts_with_configured_providers() -> None:
    settings = make_settings()

    registry = await create_provider_registry(settings)

    assert isinstance(registry, ProviderRegistry)

    spotify = registry.get(ProviderName.SPOTIFY)
    youtube = registry.get(ProviderName.YOUTUBE)
    youtube_music = registry.get(ProviderName.YOUTUBE_MUSIC)

    assert isinstance(spotify, SpotifyProvider)
    assert isinstance(youtube, YouTubeProvider)
    assert isinstance(youtube_music, YouTubeMusicProvider)


@pytest.mark.asyncio
async def test_provider_registry_skips_spotify_without_credentials() -> None:
    settings = make_settings(
        client_id=None,
        client_secret=None,
    )

    registry = await create_provider_registry(settings)

    assert registry.get(ProviderName.SPOTIFY) is None


@pytest.mark.asyncio
async def test_provider_registry_skips_spotify_without_client_id() -> None:
    settings = make_settings(
        client_id=None,
        client_secret="test-client-secret",
    )

    registry = await create_provider_registry(settings)

    assert registry.get(ProviderName.SPOTIFY) is None


@pytest.mark.asyncio
async def test_provider_registry_skips_spotify_without_client_secret() -> None:
    settings = make_settings(
        client_id="test-client-id",
        client_secret=None,
    )

    registry = await create_provider_registry(settings)

    assert registry.get(ProviderName.SPOTIFY) is None


@pytest.mark.asyncio
async def test_provider_registry_skips_youtube_without_api_key() -> None:
    settings = make_settings(
        youtube_api_key=None,
    )

    registry = await create_provider_registry(settings)

    assert registry.get(ProviderName.YOUTUBE) is None
    assert registry.get(ProviderName.YOUTUBE_MUSIC) is None
