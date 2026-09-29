from datetime import datetime

from pydantic import Field

from app.validation.common import NEXXABaseModel


class HistoryCreate(NEXXABaseModel):
    track_id: int = Field(ge=1)
    position_ms: int | None = Field(default=None, ge=0)
    duration_ms: int | None = Field(default=None, ge=0)


class HistoryResponse(NEXXABaseModel):
    id: int
    user_id: int
    track_id: int
    played_at: datetime
    position_ms: int | None
    duration_ms: int | None
