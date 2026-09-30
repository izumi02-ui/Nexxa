from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.music.history_models import HistoryEntry


def create_history_entry(
    db: Session,
    user_id: int,
    track_id: int,
    position_ms: int | None = None,
    duration_ms: int | None = None,
) -> HistoryEntry:
    """Create a playback history entry for a user."""

    entry = HistoryEntry(
        user_id=user_id,
        track_id=track_id,
        position_ms=position_ms,
        duration_ms=duration_ms,
    )

    db.add(entry)

    return entry


def list_history(
    db: Session,
    user_id: int,
) -> list[HistoryEntry]:
    """Return a user's playback history, newest first."""

    statement = (
        select(HistoryEntry)
        .where(
            HistoryEntry.user_id == user_id,
        )
        .order_by(
            HistoryEntry.played_at.desc(),
            HistoryEntry.id.desc(),
        )
    )

    return list(
        db.scalars(statement).all()
    )


def delete_history_entry(
    db: Session,
    user_id: int,
    history_id: int,
) -> bool:
    """Delete one history entry belonging to the user."""

    statement = (
        delete(HistoryEntry)
        .where(
            HistoryEntry.id == history_id,
            HistoryEntry.user_id == user_id,
        )
    )

    result = db.execute(statement)

    return result.rowcount > 0


def clear_history(
    db: Session,
    user_id: int,
) -> int:
    """Delete all playback history belonging to the user."""

    statement = (
        delete(HistoryEntry)
        .where(
            HistoryEntry.user_id == user_id,
        )
    )

    result = db.execute(statement)

    return result.rowcount or 0
