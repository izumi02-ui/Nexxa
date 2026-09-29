import pytest

from app.config import Settings
from app.providers.bootstrap import create_provider_registry
from app.providers.registry import ProviderRegistry
from app.providers.spotify.provider import SpotifyProvider
from app.providers.types import ProviderName


def make_settings(
    client_id: str | None = "test-client-id",
    client_secret: str | None = "test-client-secret",
) -> Settings:
    return Settings(
        database_url=(
            "postgresql+psycopg://user:password@localhost:5432/nexxa"
        ),
        spotify_client_id=client_id,
        spotify_client_secret=client_secret,
    )


@pytest.mark.asyncio
async def test_provider_registry_starts_with_spotify() -> None:
    settings = make_settings()

    registry = await create_provider_registry(settings)

    assert isinstance(registry, ProviderRegistry)

    spotify = registry.get(ProviderName.SPOTIFY)

    assert isinstance(spotify, SpotifyProvider)


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
async def test_provider_registry_skips_youtube_music_without_documented_api_key() -> None:
    settings = make_settings()

    registry = await create_provider_registry(settings)

    assert registry.get(ProviderName.YOUTUBE_MUSIC) is None
