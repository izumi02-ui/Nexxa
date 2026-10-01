from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.music.album_models import Album
from app.music.artist_models import Artist
from app.music.models import Track


def get_artist(
    db: Session,
    artist_id: int,
) -> Artist | None:
    """Return one artist by its canonical database ID."""

    return db.scalar(
        select(Artist).where(
            Artist.id == artist_id,
        )
    )


def get_artist_profile(
    db: Session,
    artist_id: int,
) -> dict[str, int | str | None] | None:
    """
    Return the unified artist profile.

    The profile currently combines the canonical artist entity with
    database-backed album and track counts.
    """

    artist = get_artist(
        db=db,
        artist_id=artist_id,
    )

    if artist is None:
        return None

    album_count = db.scalar(
        select(func.count(Album.id)).where(
            Album.artist_id == artist_id,
        )
    ) or 0

    track_count = db.scalar(
        select(func.count(Track.id)).where(
            Track.artist_id == artist_id,
        )
    ) or 0

    return {
        "id": artist.id,
        "name": artist.name,
        "image_url": artist.image_url,
        "album_count": album_count,
        "track_count": track_count,
    }


def list_artist_profiles(
    db: Session,
) -> list[dict[str, int | str | None]]:
    """Return all unified artist profiles in stable order."""

    artists = list(
        db.scalars(
            select(Artist).order_by(
                Artist.name.asc(),
                Artist.id.asc(),
            )
        ).all()
    )

    profiles: list[dict[str, int | str | None]] = []

    for artist in artists:
        profile = get_artist_profile(
            db=db,
            artist_id=artist.id,
        )

        if profile is not None:
            profiles.append(profile)

    return profiles
