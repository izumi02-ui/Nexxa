import pytest

from app.music.metadata import (
    MetadataNormalizationError,
    normalize_track_metadata,
)
from app.music.source_resolution import (
    SourceResolutionError,
    SourceResolver,
)
from app.providers.types import ProviderName, ProviderTrack


def make_track(
    *,
    title: str = "Test Track",
    artist_name: str = "Test Artist",
    album_name: str | None = "Test Album",
    external_url: str | None = "https://example.com/track",
) -> ProviderTrack:
    return ProviderTrack(
        provider=ProviderName.YOUTUBE,
        external_id="track-123",
        title=title,
        artist_name=artist_name,
        album_name=album_name,
        duration_ms=180000,
        external_url=external_url,
    )


def test_metadata_normalization_strips_text() -> None:
    result = normalize_track_metadata(
        make_track(
            title="  Test Track  ",
            artist_name="  Test Artist  ",
        )
    )

    assert result.title == "Test Track"
    assert result.artist_name == "Test Artist"
    assert result.album_name == "Test Album"


def test_metadata_normalization_rejects_empty_title() -> None:
    with pytest.raises(MetadataNormalizationError):
        normalize_track_metadata(
            make_track(title="   ")
        )


def test_metadata_normalization_rejects_empty_artist() -> None:
    with pytest.raises(MetadataNormalizationError):
        normalize_track_metadata(
            make_track(artist_name="   ")
        )


def test_source_resolution_returns_provider_source() -> None:
    result = SourceResolver().resolve(
        make_track()
    )

    assert result.provider == ProviderName.YOUTUBE
    assert result.external_id == "track-123"
    assert result.url == "https://example.com/track"


def test_source_resolution_rejects_missing_url() -> None:
    with pytest.raises(SourceResolutionError):
        SourceResolver().resolve(
            make_track(external_url=None)
        )