from app.config import Settings
from app.providers.youtube.client import YouTubeClient
from app.providers.youtube_music.provider import YouTubeMusicProvider


def create_youtube_music_provider(
    settings: Settings,
) -> YouTubeMusicProvider | None:
    """Create the YouTube Music provider using the YouTube Data API key."""

    if not settings.youtube_api_key:
        return None

    client = YouTubeClient(
        api_key=settings.youtube_api_key,
    )

    return YouTubeMusicProvider(
        client=client,
    )
