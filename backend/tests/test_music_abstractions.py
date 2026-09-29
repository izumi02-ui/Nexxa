from app.music.metadata import (
    MetadataNormalizationError,
    normalize_track_metadata,
)
from app.music.source_resolution import (
    SourceResolutionError,
    SourceResolver,
)
from app.providers.types import ProviderName, ProviderTrack


def make_provider_track(
    *,
    artwork_url: str | None = "https://example.com/artwork.jpg",
    external_url: str | None = "https://example.com/track",
    duration_ms: int | None = 180000,
) -> ProviderTrack:
    return ProviderTrack(
        provider=ProviderName.SPOTIFY,
        external_id="track-123",
        title="Test Track",
        artist_name="Test Artist",
        album_name="Test Album",
        duration_ms=duration_ms,
        artwork_url=artwork_url,
        external_url=external_url,
    )


def test_metadata_normalization_preserves_provider_metadata() -> None:
    track = make_provider_track()

    normalized = normalize_track_metadata(track)

    assert normalized.title == "Test Track"
    assert normalized.artist_name == "Test Artist"
    assert normalized.album_name == "Test Album"
    assert normalized.duration_ms == 180000
    assert normalized.artwork_url == "https://example.com/artwork.jpg"
    assert normalized.provider == ProviderName.SPOTIFY
    assert normalized.external_id == "track-123"
    assert normalized.external_url == "https://example.com/track"


def test_metadata_normalization_strips_text_fields() -> None:
    track = ProviderTrack(
        provider=ProviderName.SPOTIFY,
        external_id="  track-123  ",
        title="  Test Track  ",
        artist_name="  Test Artist  ",
        album_name="  Test Album  ",
        duration_ms=180000,
        artwork_url="  https://example.com/artwork.jpg  ",
        external_url="  https://example.com/track  ",
    )

    normalized = normalize_track_metadata(track)

    assert normalized.external_id == "track-123"
    assert normalized.title == "Test Track"
    assert normalized.artist_name == "Test Artist"
    assert normalized.album_name == "Test Album"
    assert normalized.artwork_url == "https://example.com/artwork.jpg"
    assert normalized.external_url == "https://example.com/track"


def test_metadata_normalization_allows_optional_fields_to_be_none() -> None:
    track = make_provider_track(
        artwork_url=None,
        external_url=None,
        duration_ms=None,
    )

    normalized = normalize_track_metadata(track)

    assert normalized.album_name == "Test Album"
    assert normalized.duration_ms is None
    assert normalized.artwork_url is None
    assert normalized.external_url is None


def test_metadata_normalization_converts_blank_optional_fields_to_none() -> None:
    track = ProviderTrack(
        provider=ProviderName.SPOTIFY,
        external_id="track-123",
        title="Test Track",
        artist_name="Test Artist",
        album_name="   ",
        duration_ms=180000,
        artwork_url="   ",
        external_url="   ",
    )

    normalized = normalize_track_metadata(track)

    assert normalized.album_name is None
    assert normalized.artwork_url is None
    assert normalized.external_url is None


def test_metadata_normalization_rejects_empty_title() -> None:
    track = ProviderTrack(
        provider=ProviderName.SPOTIFY,
        external_id="track-123",
        title="   ",
        artist_name="Test Artist",
        album_name=None,
        duration_ms=None,
        artwork_url=None,
        external_url=None,
    )

    try:
        normalize_track_metadata(track)
    except MetadataNormalizationError as exc:
        assert str(exc) == "Track title cannot be empty."
    else:
        raise AssertionError("Expected MetadataNormalizationError")


def test_metadata_normalization_rejects_empty_artist() -> None:
    track = ProviderTrack(
        provider=ProviderName.SPOTIFY,
        external_id="track-123",
        title="Test Track",
        artist_name="   ",
        album_name=None,
        duration_ms=None,
        artwork_url=None,
        external_url=None,
    )

    try:
        normalize_track_metadata(track)
    except MetadataNormalizationError as exc:
        assert str(exc) == "Track artist cannot be empty."
    else:
        raise AssertionError("Expected MetadataNormalizationError")


def test_metadata_normalization_rejects_empty_external_id() -> None:
    track = ProviderTrack(
        provider=ProviderName.SPOTIFY,
        external_id="   ",
        title="Test Track",
        artist_name="Test Artist",
        album_name=None,
        duration_ms=None,
        artwork_url=None,
        external_url=None,
    )

    try:
        normalize_track_metadata(track)
    except MetadataNormalizationError as exc:
        assert str(exc) == "Track external ID cannot be empty."
    else:
        raise AssertionError("Expected MetadataNormalizationError")


def test_metadata_normalization_rejects_negative_duration() -> None:
    track = make_provider_track(
        duration_ms=-1,
    )

    try:
        normalize_track_metadata(track)
    except MetadataNormalizationError as exc:
        assert str(exc) == "Track duration cannot be negative."
    else:
        raise AssertionError("Expected MetadataNormalizationError")


def test_source_resolution_returns_provider_source() -> None:
    track = make_provider_track()

    resolved = SourceResolver().resolve(track)

    assert resolved.provider == ProviderName.SPOTIFY
    assert resolved.external_id == "track-123"
    assert resolved.url == "https://example.com/track"


def test_source_resolution_rejects_empty_external_id() -> None:
    track = ProviderTrack(
        provider=ProviderName.SPOTIFY,
        external_id="   ",
        title="Test Track",
        artist_name="Test Artist",
        album_name=None,
        duration_ms=None,
        artwork_url=None,
        external_url="https://example.com/track",
    )

    try:
        SourceResolver().resolve(track)
    except SourceResolutionError as exc:
        assert str(exc) == "Provider track does not contain an external ID."
    else:
        raise AssertionError("Expected SourceResolutionError")


def test_source_resolution_rejects_missing_external_url() -> None:
    track = make_provider_track(
        external_url=None,
    )

    try:
        SourceResolver().resolve(track)
    except SourceResolutionError as exc:
        assert str(exc) == (
            "Provider track does not contain a playable external URL."
        )
    else:
        raise AssertionError("Expected SourceResolutionError")
