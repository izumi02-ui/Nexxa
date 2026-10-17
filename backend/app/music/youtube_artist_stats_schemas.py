
from pydantic import BaseModel, ConfigDict, Field


class YouTubeTotalViewsResponse(BaseModel):
    """Response containing an artist's saved YouTube channel views."""

    model_config = ConfigDict(from_attributes=True)

    artist_id: int = Field(gt=0)
    total_views: int | None = Field(default=None, ge=0)
