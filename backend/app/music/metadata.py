from dataclasses import dataclass

from app.providers.types import ProviderName, ProviderTrack


@dataclass(frozen=True)
class NormalizedTrackMetadata:
    """Provider-independent normalized track metadata."""

    title: str
    artist_name: str
    album_name: str | None
    duration_ms: int | None
    artwork_url: str | None
    provider: ProviderName
    external_id: str
    external_url: str | None


class MetadataNormalizationError(ValueError):
    """Raised when provider metadata cannot be normalized."""


def normalize_track_metadata(
    track: ProviderTrack,
) -> NormalizedTrackMetadata:
    title = track.title.strip()
    artist_name = track.artist_name.strip()

    if not title:
        raise MetadataNormalizationError(
            "Track title cannot be empty."
        )

    if not artist_name:
        raise MetadataNormalizationError(
            "Track artist cannot be empty."
        )

    external_id = track.external_id.strip()

    if not external_id:
        raise MetadataNormalizationError(
            "Track external ID cannot be empty."
        )

    if track.duration_ms is not None and track.duration_ms < 0:
        raise MetadataNormalizationError(
            "Track duration cannot be negative."
        )

    album_name = (
        track.album_name.strip()
        if track.album_name and track.album_name.strip()
        else None
    )

    artwork_url = (
        track.artwork_url.strip()
        if track.artwork_url and track.artwork_url.strip()
        else None
    )

    external_url = (
        track.external_url.strip()
        if track.external_url and track.external_url.strip()
        else None
    )

    return NormalizedTrackMetadata(
        title=title,
        artist_name=artist_name,
        album_name=album_name,
        duration_ms=track.duration_ms,
        artwork_url=artwork_url,
        provider=track.provider,
        external_id=external_id,
        external_url=external_url,
    )
