from pydantic import Field

from app.validation.common import NEXXABaseModel


class AlbumCreate(NEXXABaseModel):
    """Validated data required to create an album."""

    title: str = Field(
        min_length=1,
        max_length=500,
    )

    artist_id: int | None = Field(
        default=None,
        ge=1,
    )

    artwork_url: str | None = None

    release_date: str | None = Field(
        default=None,
        max_length=50,
    )


class AlbumResponse(NEXXABaseModel):
    """API representation of an album."""

    id: int
    title: str
    artist_id: int | None
    artwork_url: str | None
    release_date: str | None