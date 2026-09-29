from dataclasses import dataclass
from enum import Enum


class ProviderName(str, Enum):
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    YOUTUBE_MUSIC = "youtube_music"
    JIOSAAVN = "jiosaavn"


@dataclass(frozen=True)
class ProviderTrack:
    """Normalized track representation shared by all providers."""

    provider: ProviderName
    external_id: str
    title: str
    artist_name: str
    album_name: str | None
    duration_ms: int | None
    artwork_url: str | None
    external_url: str | None
