from app.config import Settings
from app.providers.youtube.factory import create_youtube_provider
from app.providers.youtube.provider import YouTubeProvider


def test_create_youtube_provider_when_configured() -> None:
    settings = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        youtube_api_key="test-api-key",
    )

    provider = create_youtube_provider(settings)

    assert isinstance(provider, YouTubeProvider)


def test_create_youtube_provider_without_api_key() -> None:
    settings = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
    )

    provider = create_youtube_provider(settings)

    assert provider is None
