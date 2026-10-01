from collections import Counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.music.favorite_models import Favorite
from app.music.history_models import HistoryEntry
from app.music.models import Track
from app.music.playlist_models import Playlist, PlaylistTrack


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

    playlists = list(
        db.scalars(
            select(Playlist)
            .where(Playlist.user_id == user_id)
            .order_by(
                Playlist.updated_at.desc(),
                Playlist.id.desc(),
            )
        ).all()
    )

    playlist_ids = {playlist.id for playlist in playlists}

    playlist_tracks = []

    if playlist_ids:
        playlist_tracks = list(
            db.scalars(
                select(PlaylistTrack)
                .where(
                    PlaylistTrack.playlist_id.in_(playlist_ids)
                )
                .order_by(
                    PlaylistTrack.added_at.desc(),
                    PlaylistTrack.id.desc(),
                )
            ).all()
        )

    source_track_ids = {
        entry.track_id
        for entry in history
    }

    source_track_ids |= {
        favorite.track_id
        for favorite in favorites
    }

    source_track_ids |= {
        playlist_track.track_id
        for playlist_track in playlist_tracks
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

    playlist_track_counts = Counter(
        playlist_track.track_id
        for playlist_track in playlist_tracks
    )

    candidates = list(
        db.scalars(
            select(Track).where(
                ~Track.id.in_(source_track_ids)
            )
        ).all()
    )

    def score(track: Track) -> tuple[int, int, int, int]:
        artist_score = artist_scores.get(
            track.artist_id,
            0,
        )

        album_score = album_scores.get(
            track.album_id,
            0,
        )

        playlist_score = playlist_track_counts.get(
            track.id,
            0,
        )

        total_score = (
            album_score * 3
            + artist_score * 2
            + playlist_score * 4
        )

        return (
            total_score,
            playlist_score,
            artist_score,
            -track.id,
        )

    candidates.sort(
        key=score,
        reverse=True,
    )

    return candidates[:limit]
