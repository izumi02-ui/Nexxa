from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database.session import get_db
from app.music.artist_models import Artist
from app.music.youtube_artist_stats_schemas import (
    YouTubeArtistProfileResponse,
    YouTubeLatestVideosResponse,
    YouTubeMostLikedVideosResponse,
    YouTubeMostViewedVideosResponse,
    YouTubePublicVideoCountResponse,
    YouTubeTotalViewsResponse,
    YouTubeVideoCommentCountResponse,
    YouTubeVideoLikeCountResponse,
    YouTubeChannelTopicsResponse,
    YouTubeStatisticsTimestampResponse,
    YouTubeVideoViewCountResponse,
)
from app.music.youtube_artist_stats_service import (
    get_youtube_channel_id,
    get_youtube_channel_profile,
    get_youtube_statistics_timestamp,
    save_youtube_public_video_count,
    save_youtube_total_views,
)
from app.providers.youtube.client import (
    YouTubeAPIError,
    YouTubeClient,
)

router = APIRouter(
    prefix="/artists",
    tags=["artist YouTube statistics"],
)


@router.get(
    "/{artist_id}/youtube/total-views",
    response_model=YouTubeTotalViewsResponse,
    summary="Refresh YouTube channel total views",
    responses={
        404: {"description": "Artist or YouTube channel mapping not found"},
        502: {"description": "YouTube API request failed"},
        503: {"description": "YouTube API key is not configured"},
    },
)
async def refresh_youtube_total_views(
    artist_id: int,
    db: Session = Depends(get_db),
) -> YouTubeTotalViewsResponse:
    artist = db.get(Artist, artist_id)

    if artist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found",
        )

    channel_id = get_youtube_channel_id(db=db, artist_id=artist_id)

    if channel_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="YouTube channel mapping not found",
        )

    api_key = get_settings().youtube_api_key

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="YouTube API key is not configured",
        )

    client = YouTubeClient(api_key=api_key)

    try:
        channel = await client.get_channel(channel_id)
    except YouTubeAPIError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to retrieve YouTube channel statistics",
        ) from exc

    if channel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="YouTube channel was not found",
        )

    stats = save_youtube_total_views(
        db=db,
        artist_id=artist_id,
        total_views=channel.total_views,
    )

    db.commit()
    db.refresh(stats)

    return YouTubeTotalViewsResponse(
        artist_id=artist_id,
        total_views=stats.total_views,
    )


@router.get(
    "/{artist_id}/youtube/public-video-count",
    response_model=YouTubePublicVideoCountResponse,
    summary="Refresh YouTube public video count",
    responses={
        404: {"description": "Artist or YouTube channel mapping not found"},
        502: {"description": "YouTube API request failed"},
        503: {"description": "YouTube API key is not configured"},
    },
)
async def refresh_youtube_public_video_count(
    artist_id: int,
    db: Session = Depends(get_db),
) -> YouTubePublicVideoCountResponse:
    artist = db.get(Artist, artist_id)

    if artist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found",
        )

    channel_id = get_youtube_channel_id(db=db, artist_id=artist_id)

    if channel_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="YouTube channel mapping not found",
        )

    api_key = get_settings().youtube_api_key

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="YouTube API key is not configured",
        )

    client = YouTubeClient(api_key=api_key)

    try:
        channel = await client.get_channel(channel_id)
    except YouTubeAPIError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to retrieve YouTube channel statistics",
        ) from exc

    if channel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="YouTube channel was not found",
        )

    stats = save_youtube_public_video_count(
        db=db,
        artist_id=artist_id,
        public_video_count=channel.public_video_count,
    )

    db.commit()
    db.refresh(stats)

    return YouTubePublicVideoCountResponse(
        artist_id=artist_id,
        public_video_count=stats.public_video_count,
    )


@router.get(
    "/{artist_id}/youtube/most-viewed-videos",
    response_model=YouTubeMostViewedVideosResponse,
    summary="Get an artist's most-viewed YouTube videos",
    responses={
        404: {"description": "Artist or YouTube channel mapping not found"},
        502: {"description": "YouTube API request failed"},
        503: {"description": "YouTube API key is not configured"},
    },
)
async def get_youtube_most_viewed_videos(
    artist_id: int,
    limit: int = 10,
    page_token: str | None = None,
    db: Session = Depends(get_db),
) -> YouTubeMostViewedVideosResponse:
    if limit < 1 or limit > 50:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Limit must be between 1 and 50",
        )

    artist = db.get(Artist, artist_id)

    if artist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found",
        )

    channel_id = get_youtube_channel_id(db=db, artist_id=artist_id)

    if channel_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="YouTube channel mapping not found",
        )

    api_key = get_settings().youtube_api_key

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="YouTube API key is not configured",
        )

    client = YouTubeClient(api_key=api_key)

    try:
        videos, next_page_token = await client.get_channel_videos_by_views(
            channel_id=channel_id,
            limit=limit,
            page_token=page_token,
        )
    except YouTubeAPIError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to retrieve YouTube videos",
        ) from exc

    return YouTubeMostViewedVideosResponse(
        artist_id=artist_id,
        channel_id=channel_id,
        videos=videos,
        next_page_token=next_page_token,
    )


@router.get(
    "/{artist_id}/youtube/most-liked-videos",
    response_model=YouTubeMostLikedVideosResponse,
    summary="Get an artist's videos sorted by public like count",
    responses={
        404: {"description": "Artist or YouTube channel mapping not found"},
        502: {"description": "YouTube API request failed"},
        503: {"description": "YouTube API key is not configured"},
    },
)
async def get_youtube_most_liked_videos(
    artist_id: int,
    limit: int = 10,
    page_token: str | None = None,
    db: Session = Depends(get_db),
) -> YouTubeMostLikedVideosResponse:
    if limit < 1 or limit > 50:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Limit must be between 1 and 50",
        )

    artist = db.get(Artist, artist_id)

    if artist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found",
        )

    channel_id = get_youtube_channel_id(db=db, artist_id=artist_id)

    if channel_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="YouTube channel mapping not found",
        )

    api_key = get_settings().youtube_api_key

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="YouTube API key is not configured",
        )

    client = YouTubeClient(api_key=api_key)

    try:
        videos, next_page_token = await client.get_channel_videos_by_likes(
            channel_id=channel_id,
            limit=limit,
            page_token=page_token,
        )
    except YouTubeAPIError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to retrieve YouTube videos",
        ) from exc

    return YouTubeMostLikedVideosResponse(
        artist_id=artist_id,
        channel_id=channel_id,
        videos=videos,
        next_page_token=next_page_token,
    )


@router.get(
    "/{artist_id}/youtube/latest-videos",
    response_model=YouTubeLatestVideosResponse,
    summary="Get an artist's latest YouTube videos",
    responses={
        404: {"description": "Artist or YouTube channel mapping not found"},
        502: {"description": "YouTube API request failed"},
        503: {"description": "YouTube API key is not configured"},
    },
)
async def get_youtube_latest_videos(
    artist_id: int,
    limit: int = 10,
    page_token: str | None = None,
    db: Session = Depends(get_db),
) -> YouTubeLatestVideosResponse:
    if limit < 1 or limit > 50:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Limit must be between 1 and 50",
        )

    artist = db.get(Artist, artist_id)

    if artist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found",
        )

    channel_id = get_youtube_channel_id(db=db, artist_id=artist_id)

    if channel_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="YouTube channel mapping not found",
        )

    api_key = get_settings().youtube_api_key

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="YouTube API key is not configured",
        )

    client = YouTubeClient(api_key=api_key)

    try:
        videos, next_page_token = await client.get_channel_latest_videos(
            channel_id=channel_id,
            limit=limit,
            page_token=page_token,
        )
    except YouTubeAPIError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to retrieve latest YouTube videos",
        ) from exc

    return YouTubeLatestVideosResponse(
        artist_id=artist_id,
        channel_id=channel_id,
        videos=videos,
        next_page_token=next_page_token,
    )


@router.get(
    "/{artist_id}/youtube/videos/{video_id}/view-count",
    response_model=YouTubeVideoViewCountResponse,
    summary="Get the public view count for one artist video",
    responses={
        404: {"description": "Artist, channel, or video not found"},
        502: {"description": "YouTube API request failed"},
        503: {"description": "YouTube API key is not configured"},
    },
)
async def get_youtube_video_view_count(
    artist_id: int,
    video_id: str,
    db: Session = Depends(get_db),
) -> YouTubeVideoViewCountResponse:
    artist = db.get(Artist, artist_id)

    if artist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found",
        )

    channel_id = get_youtube_channel_id(db=db, artist_id=artist_id)

    if channel_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="YouTube channel mapping not found",
        )

    api_key = get_settings().youtube_api_key

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="YouTube API key is not configured",
        )

    client = YouTubeClient(api_key=api_key)

    try:
        video = await client.get_channel_video_view_count(
            channel_id=channel_id,
            video_id=video_id,
        )
    except YouTubeAPIError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to retrieve YouTube video statistics",
        ) from exc

    if video is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found for this artist's YouTube channel",
        )

    return YouTubeVideoViewCountResponse(
        artist_id=artist_id,
        channel_id=channel_id,
        video_id=video["video_id"],
        title=video["title"],
        view_count=video["view_count"],
    )

@router.get(
    "/{artist_id}/youtube/videos/{video_id}/like-count",
    response_model=YouTubeVideoLikeCountResponse,
    summary="Get the public like count for one artist video",
    responses={
        404: {"description": "Artist, channel, or video not found"},
        502: {"description": "YouTube API request failed"},
        503: {"description": "YouTube API key is not configured"},
    },
)
async def get_youtube_video_like_count(
    artist_id: int,
    video_id: str,
    db: Session = Depends(get_db),
) -> YouTubeVideoLikeCountResponse:
    artist = db.get(Artist, artist_id)

    if artist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found",
        )

    channel_id = get_youtube_channel_id(db=db, artist_id=artist_id)

    if channel_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="YouTube channel mapping not found",
        )

    api_key = get_settings().youtube_api_key

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="YouTube API key is not configured",
        )

    client = YouTubeClient(api_key=api_key)

    try:
        video = await client.get_channel_video_like_count(
            channel_id=channel_id,
            video_id=video_id,
        )
    except YouTubeAPIError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to retrieve YouTube video statistics",
        ) from exc

    if video is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found for this artist's YouTube channel",
        )

    return YouTubeVideoLikeCountResponse(
        artist_id=artist_id,
        channel_id=channel_id,
        video_id=video["video_id"],
        title=video["title"],
        like_count=video["like_count"],
    )

@router.get(
    "/{artist_id}/youtube/videos/{video_id}/comment-count",
    response_model=YouTubeVideoCommentCountResponse,
    summary="Get the public comment count for one artist video",
    responses={
        404: {"description": "Artist, channel, or video not found"},
        502: {"description": "YouTube API request failed"},
        503: {"description": "YouTube API key is not configured"},
    },
)
async def get_youtube_video_comment_count(
    artist_id: int,
    video_id: str,
    db: Session = Depends(get_db),
) -> YouTubeVideoCommentCountResponse:
    artist = db.get(Artist, artist_id)

    if artist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found",
        )

    channel_id = get_youtube_channel_id(db=db, artist_id=artist_id)

    if channel_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="YouTube channel mapping not found",
        )

    api_key = get_settings().youtube_api_key

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="YouTube API key is not configured",
        )

    client = YouTubeClient(api_key=api_key)

    try:
        video = await client.get_channel_video_comment_count(
            channel_id=channel_id,
            video_id=video_id,
        )
    except YouTubeAPIError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to retrieve YouTube video statistics",
        ) from exc

    if video is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found for this artist's YouTube channel",
        )

    return YouTubeVideoCommentCountResponse(
        artist_id=artist_id,
        channel_id=channel_id,
        video_id=video["video_id"],
        title=video["title"],
        comment_count=video["comment_count"],
    )

@router.get(
    "/{artist_id}/youtube/profile",
    response_model=YouTubeArtistProfileResponse,
    summary="Get an artist's external YouTube profile",
    responses={
        404: {"description": "Artist or YouTube channel mapping not found"},
    },
)
async def get_youtube_artist_profile(
    artist_id: int,
    db: Session = Depends(get_db),
) -> YouTubeArtistProfileResponse:
    profile = get_youtube_channel_profile(
        db=db,
        artist_id=artist_id,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist or YouTube channel mapping not found",
        )

    return YouTubeArtistProfileResponse(
        artist_id=artist_id,
        channel_id=profile["channel_id"],
        external_url=profile["external_url"],
    )

@router.get(
    "/{artist_id}/youtube/topics",
    response_model=YouTubeChannelTopicsResponse,
    summary="Get an artist's YouTube channel topic categories",
    responses={
        404: {"description": "Artist or YouTube channel not found"},
        502: {"description": "YouTube API request failed"},
        503: {"description": "YouTube API key is not configured"},
    },
)
async def get_youtube_artist_topics(
    artist_id: int,
    db: Session = Depends(get_db),
) -> YouTubeChannelTopicsResponse:
    artist = db.get(Artist, artist_id)

    if artist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found",
        )

    channel_id = get_youtube_channel_id(
        db=db,
        artist_id=artist_id,
    )

    if channel_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="YouTube channel mapping not found",
        )

    api_key = get_settings().youtube_api_key

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="YouTube API key is not configured",
        )

    client = YouTubeClient(api_key=api_key)

    try:
        categories = await client.get_channel_topics(
            channel_id=channel_id,
        )
    except YouTubeAPIError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to retrieve YouTube channel topics",
        ) from exc

    if categories is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="YouTube channel was not found",
        )

    return YouTubeChannelTopicsResponse(
        artist_id=artist_id,
        channel_id=channel_id,
        topic_categories=categories,
    )