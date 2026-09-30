from collections import Counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.music.favorite_models import Favorite
from app.music.history_models import HistoryEntry
from app.music.models import Track


def get_recommendations(
    db: Session,
    user_id: int,
    limit: int = 20,
) -> list[Track]:
    if limit <= 0:
        return []

    history = list(
        db.scalars(
            select(HistoryEntry)
            .where(HistoryEntry.user_id == user_id)
            .order_by(
                HistoryEntry.played_at.desc(),
                HistoryEntry.id.desc(),
            )
        ).all()
    )

    favorites = list(
        db.scalars(
            select(Favorite)
            .where(Favorite.user_id == user_id)
            .order_by(
                Favorite.created_at.desc(),
                Favorite.id.desc(),
            )
        ).all()
    )

    source_track_ids = {
        entry.track_id
        for entry in history
    } | {
        favorite.track_id
        for favorite in favorites
    }

    if not source_track_ids:
        return (
            db.scalars(
                select(Track)
                .order_by(Track.id)
                .limit(limit)
            ).all()
        )

    source_tracks = list(
        db.scalars(
            select(Track).where(
                Track.id.in_(source_track_ids)
            )
        ).all()
    )

    artist_scores = Counter(
        track.artist_id
        for track in source_tracks
    )

    album_scores = Counter(
        track.album_id
        for track in source_tracks
        if track.album_id is not None
    )

    candidates = list(
        db.scalars(
            select(Track).where(
                ~Track.id.in_(source_track_ids)
            )
        ).all()
    )

    def score(track: Track) -> tuple[int, int, int]:
        artist_score = artist_scores.get(
            track.artist_id,
            0,
        )

        album_score = album_scores.get(
            track.album_id,
            0,
        )

        return (
            album_score * 3 + artist_score * 2,
            artist_score,
            -track.id,
        )

    candidates.sort(
        key=score,
        reverse=True,
    )

    return candidates[:limit]
