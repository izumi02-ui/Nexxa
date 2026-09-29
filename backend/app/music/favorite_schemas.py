from datetime import datetime

from pydantic import Field

from app.validation.common import NEXXABaseModel


class FavoriteCreate(NEXXABaseModel):
    """Validated data required to favorite a track."""

    track_id: int = Field(
        ge=1,
    )


class FavoriteResponse(NEXXABaseModel):
    """API representation of a favorite track."""

    id: int
    user_id: int
    track_id: int
    created_at: datetime
