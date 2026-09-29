from app.config import Settings
from app.providers.youtube_music.client import YouTubeMusicClient
from app.providers.youtube_music.provider import YouTubeMusicProvider


def create_youtube_music_provider(
    settings: Settings,
) -> YouTubeMusicProvider | None:
    """Create YouTube Music when its documented integration is configured."""
    if not getattr(settings, "youtube_music_api_key", None):
        return None

    client = YouTubeMusicClient()

    return YouTubeMusicProvider(
        client=client,
    )
