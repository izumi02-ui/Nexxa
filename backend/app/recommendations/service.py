from collections import Counter
from collections.abc import Iterable

from sqlalchemy.orm import Session

from app.music.models import Track


def get_recommendations(
    db: Session,
    track_ids: Iterable[int] | None = None,
    limit: int = 20,
) -> list[Track]:
    """
    Return deterministic track recommendations based on the user's
    existing track selections.

    Tracks sharing an artist or album with the supplied tracks are
    preferred. Already supplied tracks are excluded.
    """
    if limit <= 0:
        return []

    source_ids = {
        track_id
        for track_id in (track_ids or [])
        if isinstance(track_id, int) and track_id > 0
    }

    if not source_ids:
        return (
            db.query(Track)
            .order_by(Track.id)
            .limit(limit)
            .all()
        )

    source_tracks = (
        db.query(Track)
        .filter(Track.id.in_(source_ids))
        .all()
    )

    if not source_tracks:
        return (
            db.query(Track)
            .order_by(Track.id)
            .limit(limit)
            .all()
        )

    artist_ids = {
        track.artist_id
        for track in source_tracks
        if track.artist_id is not None
    }

    album_ids = {
        track.album_id
        for track in source_tracks
        if track.album_id is not None
    }

    candidates = (
        db.query(Track)
        .filter(~Track.id.in_(source_ids))
        .all()
    )

    source_artist_counts = Counter(
        track.artist_id
        for track in source_tracks
        if track.artist_id is not None
    )

    source_album_counts = Counter(
        track.album_id
        for track in source_tracks
        if track.album_id is not None
    )

    def score(track: Track) -> tuple[int, int]:
        artist_score = (
            source_artist_counts.get(track.artist_id, 0)
            if track.artist_id in artist_ids
            else 0
        )

        album_score = (
            source_album_counts.get(track.album_id, 0)
            if track.album_id in album_ids
            else 0
        )

        return (
            album_score * 3 + artist_score * 2,
            -track.id,
        )

    candidates.sort(key=score, reverse=True)

    return candidates[:limit]
