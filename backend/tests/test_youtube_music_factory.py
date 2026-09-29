from app.config import Settings
from app.providers.youtube_music.factory import create_youtube_music_provider
from app.providers.youtube_music.provider import YouTubeMusicProvider


def test_create_youtube_music_provider_without_documented_api_key() -> None:
    settings = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
    )

    provider = create_youtube_music_provider(settings)

    assert provider is None
