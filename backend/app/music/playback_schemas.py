from pydantic import Field

from app.validation.common import NEXXABaseModel


class PlaybackStateUpdate(NEXXABaseModel):
    """Validated playback-state update."""

    track_id: int | None = Field(
        default=None,
        ge=1,
    )

    position_ms: int = Field(
        default=0,
        ge=0,
    )

    is_playing: bool = False


class PlaybackStateResponse(NEXXABaseModel):
    """API representation of playback state."""

    user_id: int
    track_id: int | None
    position_ms: int
    is_playing: bool