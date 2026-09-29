from datetime import datetime

from pydantic import Field

from app.validation.common import NEXXABaseModel


class PlaylistCreate(NEXXABaseModel):
    """Validated data required to create a playlist."""

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    description: str | None = None

    artwork_url: str | None = None

    is_public: bool = False


class PlaylistResponse(NEXXABaseModel):
    """API representation of a playlist."""

    id: int
    user_id: int
    name: str
    description: str | None
    artwork_url: str | None
    is_public: bool
    created_at: datetime
    updated_at: datetime


class PlaylistTrackCreate(NEXXABaseModel):
    """Validated data for adding a track to a playlist."""

    track_id: int = Field(
        ge=1,
    )

    position: int = Field(
        ge=0,
    )


class PlaylistTrackResponse(NEXXABaseModel):
    """API representation of a playlist track."""

    id: int
    playlist_id: int
    track_id: int
    position: int
    added_at: datetime
