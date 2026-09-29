from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SpotifySettings(BaseSettings):
    """Server-side Spotify configuration."""

    spotify_client_id: str = Field(
        min_length=1,
    )

    spotify_client_secret: str = Field(
        min_length=1,
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )