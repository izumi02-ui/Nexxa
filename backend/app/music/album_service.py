from sqlalchemy import select
from sqlalchemy.orm import Session

from app.music.album_models import Album
from app.music.album_schemas import AlbumCreate
from app.music.models import Track


def create_album(
    db: Session,
    data: AlbumCreate,
) -> Album:
    """Create and persist an album."""

    album = Album(
        title=data.title,
        artist_id=data.artist_id,
        artwork_url=data.artwork_url,
        release_date=data.release_date,
    )

    db.add(album)
    db.flush()

    return album


def get_album(
    db: Session,
    album_id: int,
) -> Album | None:
    """Return an album by ID."""

    return db.scalar(
        select(Album).where(
            Album.id == album_id,
        )
    )


def list_albums(
    db: Session,
) -> list[Album]:
    """Return all albums in stable title/ID order."""

    return list(
        db.scalars(
            select(Album)
            .order_by(
                Album.title.asc(),
                Album.id.asc(),
            )
        ).all()
    )


def list_albums_by_artist(
    db: Session,
    artist_id: int,
) -> list[Album]:
    """Return all albums belonging to an artist."""

    return list(
        db.scalars(
            select(Album)
            .where(
                Album.artist_id == artist_id,
            )
            .order_by(
                Album.title.asc(),
                Album.id.asc(),
            )
        ).all()
    )


def list_album_tracks(
    db: Session,
    album_id: int,
) -> list[Track]:
    """Return all tracks belonging to an album in stable ID order."""

    return list(
        db.scalars(
            select(Track)
            .where(
                Track.album_id == album_id,
            )
            .order_by(
                Track.id.asc(),
            )
        ).all()
    )
