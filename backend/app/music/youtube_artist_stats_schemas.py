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


class YouTubeMostViewedVideo(BaseModel):
    """A YouTube video with its public view count."""

    video_id: str
    title: str
    channel_name: str
    description: str
    thumbnail_url: str | None = None
    duration: str | None = None
    url: str
    view_count: int | None = Field(default=None, ge=0)


class YouTubeMostViewedVideosResponse(BaseModel):
    """Most-viewed videos for a mapped YouTube artist channel."""

    model_config = ConfigDict(from_attributes=True)

    artist_id: int = Field(gt=0)
    channel_id: str
    videos: list[YouTubeMostViewedVideo]
    next_page_token: str | None = None