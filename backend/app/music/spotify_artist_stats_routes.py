from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database.session import get_db
from app.music.artist_models import Artist
from app.music.spotify_artist_stats_schemas import (
    SpotifyArtistRefreshResponse,
    SpotifyArtistStatsResponse,
)
from app.music.spotify_artist_stats_service import (
    get_spotify_artist_id,
    get_spotify_artist_stats,
    refresh_spotify_artist_stats,
)
from app.providers.spotify.client import (
    SpotifyAPIError,
    SpotifyClient,
)


router = APIRouter(
    prefix="/artists",
    tags=["artist Spotify statistics"],
)


@router.get(
    "/{artist_id}/spotify/statistics",
    response_model=SpotifyArtistStatsResponse,
    summary="Get saved Spotify artist statistics",
    responses={
        404: {"description": "Artist or Spotify statistics not found"},
    },
)
def get_artist_spotify_statistics(
    artist_id: int,
    db: Session = Depends(get_db),
) -> SpotifyArtistStatsResponse:
    artist = db.get(Artist, artist_id)

    if artist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found",
        )

    stats = get_spotify_artist_stats(
        db=db,
        artist_id=artist_id,
    )

    if stats is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spotify artist statistics not found",
        )

    return stats


@router.post(
    "/{artist_id}/spotify/statistics/refresh",
    response_model=SpotifyArtistRefreshResponse,
    summary="Refresh Spotify artist statistics",
    responses={
        404: {"description": "Artist or Spotify artist mapping not found"},
        502: {"description": "Spotify API request failed"},
        503: {"description": "Spotify credentials are not configured"},
    },
)
async def refresh_artist_spotify_statistics(
    artist_id: int,
    db: Session = Depends(get_db),
) -> SpotifyArtistRefreshResponse:
    artist = db.get(Artist, artist_id)

    if artist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found",
        )

    spotify_artist_id = get_spotify_artist_id(
        db=db,
        artist_id=artist_id,
    )

    if spotify_artist_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spotify artist mapping not found",
        )

    settings = get_settings()

    if (
        not settings.spotify_client_id
        or not settings.spotify_client_secret
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Spotify credentials are not configured",
        )

    client = SpotifyClient(
        client_id=settings.spotify_client_id,
        client_secret=settings.spotify_client_secret,
    )

    try:
        stats = await refresh_spotify_artist_stats(
            db=db,
            artist_id=artist_id,
            client=client,
        )
    except SpotifyAPIError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to retrieve Spotify artist statistics",
        ) from exc
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Spotify returned invalid artist data",
        ) from exc

    if stats is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spotify artist mapping not found",
        )

    db.commit()
    db.refresh(stats)

    return SpotifyArtistRefreshResponse(
        artist_id=artist_id,
        refreshed=True,
        message="Spotify artist statistics refreshed successfully",
        statistics=stats,
    )