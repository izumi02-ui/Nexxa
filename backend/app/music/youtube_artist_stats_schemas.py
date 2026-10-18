from pydantic import BaseModel, ConfigDict, Field


class YouTubeTotalViewsResponse(BaseModel):
    """Response containing an artist's saved YouTube channel views."""

    model_config = ConfigDict(from_attributes=True)

    artist_id: int = Field(gt=0)
    total_views: int | None = Field(default=None, ge=0)


class YouTubePublicVideoCountResponse(BaseModel):
    """Response containing an artist's YouTube public video count."""

    model_config = ConfigDict(from_attributes=True)

    artist_id: int = Field(gt=0)
    public_video_count: int | None = Field(default=None, ge=0)