from app.config import Settings
from app.providers.registry import ProviderRegistry
from app.providers.spotify.factory import create_spotify_provider
from app.providers.youtube.factory import create_youtube_provider
from app.providers.youtube_music.factory import create_youtube_music_provider


async def create_provider_registry(settings: Settings) -> ProviderRegistry:
    """Create and configure the NEXXA provider registry."""
    registry = ProviderRegistry()

    spotify = create_spotify_provider(settings)
    if spotify is not None:
        registry.register(spotify)

    youtube = create_youtube_provider(settings)
    if youtube is not None:
        registry.register(youtube)

    youtube_music = create_youtube_music_provider(settings)
    if youtube_music is not None:
        registry.register(youtube_music)

    return registry
