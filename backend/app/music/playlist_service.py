from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.music.playlist_models import Playlist, PlaylistTrack


def create_playlist(
    db: Session,
    user_id: int,
    name: str,
    description: str | None = None,
    artwork_url: str | None = None,
    is_public: bool = False,
) -> Playlist:
    """Create a playlist owned by a user."""

    playlist = Playlist(
        user_id=user_id,
        name=name,
        description=description,
        artwork_url=artwork_url,
        is_public=is_public,
    )

    db.add(playlist)
    db.flush()

    return playlist


def get_playlist(
    db: Session,
    user_id: int,
    playlist_id: int,
) -> Playlist | None:
    """Return a playlist owned by a user."""

    return db.scalar(
        select(Playlist).where(
            Playlist.id == playlist_id,
            Playlist.user_id == user_id,
        )
    )


def list_playlists(
    db: Session,
    user_id: int,
) -> list[Playlist]:
    """Return all playlists belonging to a user."""

    return list(
        db.scalars(
            select(Playlist)
            .where(Playlist.user_id == user_id)
            .order_by(
                Playlist.created_at.desc(),
                Playlist.id.desc(),
            )
        ).all()
    )


def update_playlist(
    db: Session,
    user_id: int,
    playlist_id: int,
    name: str | None = None,
    description: str | None = None,
    artwork_url: str | None = None,
    is_public: bool | None = None,
) -> Playlist | None:
    """Update a playlist owned by a user."""

    playlist = get_playlist(
        db=db,
        user_id=user_id,
        playlist_id=playlist_id,
    )

    if playlist is None:
        return None

    if name is not None:
        playlist.name = name

    if description is not None:
        playlist.description = description

    if artwork_url is not None:
        playlist.artwork_url = artwork_url

    if is_public is not None:
        playlist.is_public = is_public

    db.flush()

    return playlist


def delete_playlist(
    db: Session,
    user_id: int,
    playlist_id: int,
) -> bool:
    """Delete a playlist owned by a user."""

    playlist = get_playlist(
        db=db,
        user_id=user_id,
        playlist_id=playlist_id,
    )

    if playlist is None:
        return False

    db.execute(
        delete(PlaylistTrack).where(
            PlaylistTrack.playlist_id == playlist_id,
        )
    )

    db.delete(playlist)
    db.flush()

    return True


def add_track_to_playlist(
    db: Session,
    user_id: int,
    playlist_id: int,
    track_id: int,
    position: int,
) -> PlaylistTrack | None:
    """Add a track to a playlist owned by a user."""

    playlist = get_playlist(
        db=db,
        user_id=user_id,
        playlist_id=playlist_id,
    )

    if playlist is None:
        return None

    playlist_track = PlaylistTrack(
        playlist_id=playlist_id,
        track_id=track_id,
        position=position,
    )

    db.add(playlist_track)
    db.flush()

    return playlist_track


def remove_track_from_playlist(
    db: Session,
    user_id: int,
    playlist_id: int,
    track_id: int,
) -> bool:
    """Remove a track from a playlist owned by a user."""

    playlist = get_playlist(
        db=db,
        user_id=user_id,
        playlist_id=playlist_id,
    )

    if playlist is None:
        return False

    playlist_track = db.scalar(
        select(PlaylistTrack).where(
            PlaylistTrack.playlist_id == playlist_id,
            PlaylistTrack.track_id == track_id,
        )
    )

    if playlist_track is None:
        return False

    db.delete(playlist_track)
    db.flush()

    return True


def get_playlist_tracks(
    db: Session,
    user_id: int,
    playlist_id: int,
) -> list[PlaylistTrack] | None:
    """Return playlist tracks in their current order."""

    playlist = get_playlist(
        db=db,
        user_id=user_id,
        playlist_id=playlist_id,
    )

    if playlist is None:
        return None

    return list(
        db.scalars(
            select(PlaylistTrack)
            .where(
                PlaylistTrack.playlist_id == playlist_id,
            )
            .order_by(
                PlaylistTrack.position.asc(),
                PlaylistTrack.id.asc(),
            )
        ).all()
    )


def update_playlist_track_position(
    db: Session,
    user_id: int,
    playlist_id: int,
    track_id: int,
    position: int,
) -> PlaylistTrack | None:
    """Move a playlist track to a new zero-based position."""

    if position < 0:
        raise ValueError("Playlist track position cannot be negative")

    playlist = get_playlist(
        db=db,
        user_id=user_id,
        playlist_id=playlist_id,
    )

    if playlist is None:
        return None

    tracks = list(
        db.scalars(
            select(PlaylistTrack)
            .where(
                PlaylistTrack.playlist_id == playlist_id,
            )
            .order_by(
                PlaylistTrack.position.asc(),
                PlaylistTrack.id.asc(),
            )
        ).all()
    )

    target = next(
        (
            playlist_track
            for playlist_track in tracks
            if playlist_track.track_id == track_id
        ),
        None,
    )

    if target is None:
        return None

    tracks.remove(target)

    if position > len(tracks):
        position = len(tracks)

    tracks.insert(position, target)

    # Temporarily move every row away from the final positions
    # so the unique (playlist_id, position) constraint cannot
    # collide while the order is being rebuilt.
    for index, playlist_track in enumerate(tracks):
        playlist_track.position = -(index + 1)

    db.flush()

    for index, playlist_track in enumerate(tracks):
        playlist_track.position = index

    db.flush()

    return target
