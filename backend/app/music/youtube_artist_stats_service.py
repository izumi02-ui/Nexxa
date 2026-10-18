from sqlalchemy import select
from sqlalchemy.orm import Session

from app.music.artist_models import Artist
from app.music.artist_provider_models import ArtistProviderProfile
from app.music.youtube_artist_stats_models import YouTubeArtistStats


def get_youtube_channel_id(
    db: Session,
    artist_id: int,
) -> str | None:
    """Return the mapped YouTube channel ID for an existing artist."""

    artist = db.get(Artist, artist_id)

    if artist is None:
        return None

    profile = db.scalar(
        select(ArtistProviderProfile).where(
            ArtistProviderProfile.artist_id == artist_id,
            ArtistProviderProfile.provider == "youtube",
        )
    )

    if profile is None:
        return None

    return profile.external_id


def save_youtube_total_views(
    db: Session,
    artist_id: int,
    total_views: int | None,
) -> YouTubeArtistStats:
    """Insert or update the saved total channel view count."""

    if total_views is not None and total_views < 0:
        raise ValueError("YouTube total views cannot be negative.")

    stats = db.scalar(
        select(YouTubeArtistStats).where(
            YouTubeArtistStats.artist_id == artist_id,
        )
    )

    if stats is None:
        stats = YouTubeArtistStats(
            artist_id=artist_id,
            total_views=total_views,
        )
        db.add(stats)
    else:
        stats.total_views = total_views

    db.flush()
    return stats


def get_youtube_total_views(
    db: Session,
    artist_id: int,
) -> YouTubeArtistStats | None:
    """Return the saved YouTube total views, if available."""

    return db.scalar(
        select(YouTubeArtistStats).where(
            YouTubeArtistStats.artist_id == artist_id,
        )
    )


def save_youtube_public_video_count(
    db: Session,
    artist_id: int,
    public_video_count: int | None,
) -> YouTubeArtistStats:
    """Insert or update the saved public video count."""

    if public_video_count is not None and public_video_count < 0:
        raise ValueError(
            "YouTube public video count cannot be negative."
        )

    stats = db.scalar(
        select(YouTubeArtistStats).where(
            YouTubeArtistStats.artist_id == artist_id,
        )
    )

    if stats is None:
        stats = YouTubeArtistStats(
            artist_id=artist_id,
            public_video_count=public_video_count,
        )
        db.add(stats)
    else:
        stats.public_video_count = public_video_count

    db.flush()
    return stats


def get_youtube_public_video_count(
    db: Session,
    artist_id: int,
) -> YouTubeArtistStats | None:
    """Return the saved YouTube public video count, if available."""

    return db.scalar(
        select(YouTubeArtistStats).where(
            YouTubeArtistStats.artist_id == artist_id,
        )
    )