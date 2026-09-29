from app.config import Settings
from app.providers.youtube.client import YouTubeClient
from app.providers.youtube.provider import YouTubeProvider


def create_youtube_provider(settings: Settings) -> YouTubeProvider | None:
    """Create YouTube when the API key is configured."""
    if not settings.youtube_api_key:
        return None

    client = YouTubeClient(
        api_key=settings.youtube_api_key,
    )

    return YouTubeProvider(client=client)
