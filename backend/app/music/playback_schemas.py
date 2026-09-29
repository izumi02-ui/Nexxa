from datetime import datetime

from pydantic import Field

from app.validation.common import NEXXABaseModel


class PlaybackStateUpdate(NEXXABaseModel):
    """Validated playback-state update."""

    current_track_id: int | None = Field(
        default=None,
        ge=1,
    )

    position_ms: int = Field(
        default=0,
        ge=0,
    )

    volume: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    is_playing: bool = False


class PlaybackStateResponse(NEXXABaseModel):
    """API representation of playback state."""

    id: int
    user_id: int
    current_track_id: int | None
    position_ms: int
    volume: float
    is_playing: bool
    updated_at: datetime