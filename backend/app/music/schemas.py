from pydantic import Field

from app.validation.common import NEXXABaseModel


class TrackCreate(NEXXABaseModel):
    """Validated data required to create a track."""

    title: str = Field(
        min_length=1,
        max_length=500,
    )

    artist_id: int = Field(
        ge=1,
    )

    album_id: int | None = Field(
        default=None,
        ge=1,
    )

    duration_ms: int | None = Field(
        default=None,
        ge=0,
    )

    artwork_url: str | None = None


class TrackResponse(NEXXABaseModel):
    """API representation of a normalized track."""

    id: int
    title: str
    artist_id: int
    album_id: int | None
    duration_ms: int | None
    artwork_url: str | None