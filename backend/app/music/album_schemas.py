from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class AlbumCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=500,
    )
    artist_id: int = Field(
        gt=0,
    )
    artwork_url: str | None = None
    release_date: date | None = None


class AlbumResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    title: str
    artist_id: int
    artwork_url: str | None
    release_date: date | None
