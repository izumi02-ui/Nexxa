from pydantic import Field

from app.validation.common import NEXXABaseModel


class QueueItemCreate(NEXXABaseModel):
    """Validated data for adding a track to the queue."""

    track_id: int = Field(
        ge=1,
    )

    position: int = Field(
        ge=0,
    )


class QueueItemResponse(NEXXABaseModel):
    """API representation of a queue item."""

    id: int
    user_id: int
    track_id: int
    position: int