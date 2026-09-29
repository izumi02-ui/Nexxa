import pytest

from app.config import Settings
from app.providers.registry import ProviderRegistry
from app.providers.spotify.factory import create_spotify_provider
from app.providers.spotify.provider import SpotifyProvider
from app.providers.types import ProviderName


def make_settings(
    client_id: str | None = "test-client-id",
    client_secret: str | None = "test-client-secret",
) -> Settings:
    return Settings(
        database_url=(
            "postgresql+psycopg://"
            "user:password@localhost:5432/nexxa"
        ),
        spotify_client_id=client_id,
        spotify_client_secret=client_secret,
    )


def test_spotify_factory_returns_none_without_client_id() -> None:
    settings = make_settings(
        client_id=None,
        client_secret="test-client-secret",
    )

    provider = create_spotify_provider(settings)

    assert provider is None


def test_spotify_factory_returns_none_without_client_secret() -> None:
    settings = make_settings(
        client_id="test-client-id",
        client_secret=None,
    )

    provider = create_spotify_provider(settings)

    assert provider is None


def test_spotify_factory_creates_provider() -> None:
    settings = make_settings()

    provider = create_spotify_provider(settings)

    assert provider is not None
    assert isinstance(provider, SpotifyProvider)
    assert provider.name is ProviderName.SPOTIFY


@pytest.mark.asyncio
async def test_spotify_provider_can_be_registered() -> None:
    settings = make_settings()

    provider = create_spotify_provider(settings)

    assert provider is not None

    registry = ProviderRegistry()

    registry.register(provider)

    registered = registry.get(ProviderName.SPOTIFY)

    assert registered is provider
    assert registered.name is ProviderName.SPOTIFY
