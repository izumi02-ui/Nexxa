from pydantic import Field

from app.validation.common import NEXXABaseModel


class ArtistCreate(NEXXABaseModel):
    """Validated data required to create an artist."""

    name: str = Field(
        min_length=1,
        max_length=500,
    )

    image_url: str | None = None


class ArtistResponse(NEXXABaseModel):
    """API representation of an artist."""

    id: int
    name: str
    image_url: str | None