
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database.session import get_db
from app.music.artist_models import Artist
from app.music.youtube_artist_stats_schemas import (
    YouTubeTotalViewsResponse,
)
from app.music.youtube_artist_stats_service import (
    get_youtube_channel_id,
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
    description=(
        "Fetch the channel's current total views and save them "
        "against the canonical NEXXA artist."
    ),
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
