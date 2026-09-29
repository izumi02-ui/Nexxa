from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.music.favorite_models import Favorite


def create_favorite(
    db: Session,
    user_id: int,
    track_id: int,
) -> Favorite:
    """Create a favorite for a user and track."""

    existing = db.scalar(
        select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.track_id == track_id,
        )
    )

    if existing is not None:
        return existing

    favorite = Favorite(
        user_id=user_id,
        track_id=track_id,
    )

    db.add(favorite)
    db.flush()

    return favorite


def get_favorite(
    db: Session,
    user_id: int,
    track_id: int,
) -> Favorite | None:
    """Return a user's favorite for a track."""

    return db.scalar(
        select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.track_id == track_id,
        )
    )


def list_favorites(
    db: Session,
    user_id: int,
) -> list[Favorite]:
    """Return all favorites belonging to a user."""

    return list(
        db.scalars(
            select(Favorite)
            .where(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc(), Favorite.id.desc())
        ).all()
    )


def delete_favorite(
    db: Session,
    user_id: int,
    track_id: int,
) -> bool:
    """Delete a user's favorite for a track.

    Returns True when a favorite was deleted, otherwise False.
    """

    result = db.execute(
        delete(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.track_id == track_id,
        )
    )

    return result.rowcount > 0
