from dataclasses import dataclass

from app.providers.types import ProviderName, ProviderTrack


@dataclass(frozen=True)
class NormalizedTrackMetadata:
    """Provider-independent canonical track metadata."""

    title: str
    artist_name: str
    album_name: str | None
    duration_ms: int | None
    artwork_url: str | None
    provider: ProviderName
    external_id: str
    external_url: str | None


class MetadataNormalizer:
    """Converts provider metadata into the NEXXA canonical format."""

    def normalize(
        self,
        track: ProviderTrack,
        artwork_url: str | None = None,
    ) -> NormalizedTrackMetadata:
        return NormalizedTrackMetadata(
            title=track.title.strip(),
            artist_name=track.artist_name.strip(),
            album_name=(
                track.album_name.strip()
                if track.album_name
                else None
            ),
            duration_ms=track.duration_ms,
            artwork_url=artwork_url,
            provider=track.provider,
            external_id=track.external_id,
            external_url=track.external_url,
        )