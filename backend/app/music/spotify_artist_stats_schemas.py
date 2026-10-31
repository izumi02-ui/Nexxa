from datetime import datetime

from pydantic import Field

from app.validation.common import NEXXABaseModel


class SpotifyArtistReleaseResponse(NEXXABaseModel):
    """One Spotify artist album or single."""

    id: str
    name: str
    album_type: str | None = None
    release_date: str | None = None
    total_tracks: int | None = Field(default=None, ge=0)
    image_url: str | None = None
    external_url: str | None = None


class SpotifyArtistTopTrackResponse(NEXXABaseModel):
    """One popular Spotify track by an artist."""

    id: str
    name: str
    album_name: str | None = None
    duration_ms: int | None = Field(default=None, ge=0)
    explicit: bool | None = None
    popularity: int | None = Field(default=None, ge=0, le=100)
    image_url: str | None = None
    external_url: str | None = None


class SpotifyArtistStatsResponse(NEXXABaseModel):
    """Saved Spotify artist statistics and profile data."""

    artist_id: int = Field(gt=0)
    spotify_artist_id: str | None = None
    spotify_url: str | None = None
    followers: int | None = Field(default=None, ge=0)
    popularity: int | None = Field(default=None, ge=0, le=100)

    # Not provided by Spotify's standard Web API.
    monthly_listeners: int | None = Field(default=None, ge=0)

    genres: list[str] = Field(default_factory=list)
    albums: list[SpotifyArtistReleaseResponse] = Field(
        default_factory=list
    )
    singles: list[SpotifyArtistReleaseResponse] = Field(
        default_factory=list
    )
    top_tracks: list[SpotifyArtistTopTrackResponse] = Field(
        default_factory=list
    )

    statistics_available: bool
    statistics_fetched_at: datetime
    updated_at: datetime


class SpotifyArtistRefreshResponse(NEXXABaseModel):
    """Result of refreshing Spotify artist statistics."""

    artist_id: int = Field(gt=0)
    refreshed: bool
    message: str
    statistics: SpotifyArtistStatsResponse | None = None