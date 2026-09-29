from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class YouTubeMusicSettings(BaseSettings):
    """Server-side YouTube Music configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    youtube_music_api_key: str = Field(
        min_length=1,
    )
