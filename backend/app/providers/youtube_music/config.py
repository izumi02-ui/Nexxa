from pydantic_settings import BaseSettings, SettingsConfigDict


class YouTubeMusicSettings(BaseSettings):
    """Server-side YouTube Music provider configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
