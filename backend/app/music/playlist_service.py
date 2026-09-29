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
