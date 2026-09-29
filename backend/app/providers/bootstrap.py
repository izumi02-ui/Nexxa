from app.config import Settings
from app.providers.registry import ProviderRegistry
from app.providers.spotify.factory import create_spotify_provider


async def create_provider_registry(
    settings: Settings,
) -> ProviderRegistry:
    """Create and configure the NEXXA provider registry."""

    registry = ProviderRegistry()

    spotify = await create_spotify_provider(settings)

    if spotify is not None:
        registry.register(spotify)

    return registry