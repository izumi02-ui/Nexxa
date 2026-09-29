from pydantic import Field

from app.validation.common import NEXXABaseModel


class TrackCreate(NEXXABaseModel):
    """Validated data required to create a track."""

    title: str = Field(
        min_length=1,
        max_length=500,
    )

    artist_name: str = Field(
        min_length=1,
        max_length=500,
    )

    album_name: str | None = Field(
        default=None,
        max_length=500,
    )

    duration_ms: int | None = Field(
        default=None,
        ge=0,
    )

    artwork_url: str | None = None


class TrackResponse(NEXXABaseModel):
    """API representation of a track."""

    id: int
    title: str
    artist_name: str
    album_name: str | None
    duration_ms: int | None
    artwork_url: str | None