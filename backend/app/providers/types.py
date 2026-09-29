from dataclasses import dataclass
from enum import Enum


class ProviderName(str, Enum):
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    YOUTUBE_MUSIC = "youtube_music"
    JIOSAAVN = "jiosaavn"


@dataclass(frozen=True)
class ProviderTrack:
    provider: ProviderName
    external_id: str
    title: str
    artist_name: str
    album_name: str | None = None
    duration_ms: int | None = None
    external_url: str | None = None