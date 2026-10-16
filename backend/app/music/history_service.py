from sqlalchemy import select
from sqlalchemy.orm import Session

from app.music.history_models import HistoryEntry
from app.music.models import Track


def create_history_entry(
    db: Session,
    user_id: int,
    track_id: int,
    position_ms: int | None = None,
    duration_ms: int | None = None,
) -> HistoryEntry | None:
    track = db.get(Track, track_id)
    if track is None:
        return None

    entry = HistoryEntry(
        user_id=user_id,
        track_id=track_id,
        position_ms=position_ms,
        duration_ms=duration_ms,
    )
    db.add(entry)
    db.flush()
    return entry


def list_history(
    db: Session,
    user_id: int,
) -> list[HistoryEntry]:
    statement = (
        select(HistoryEntry)
        .where(HistoryEntry.user_id == user_id)
        .order_by(
            HistoryEntry.played_at.desc(),
            HistoryEntry.id.desc(),
        )
    )
    return list(db.scalars(statement).all())


def delete_history_entry(
    db: Session,
    user_id: int,
    history_id: int,
) -> bool:
    entry = db.scalar(
        select(HistoryEntry).where(
            HistoryEntry.id == history_id,
            HistoryEntry.user_id == user_id,
        )
    )
    if entry is None:
        return False

    db.delete(entry)
    db.flush()
    return True


def clear_history(
    db: Session,
    user_id: int,
) -> int:
    entries = list_history(db=db, user_id=user_id)
    count = len(entries)

    for entry in entries:
        db.delete(entry)

    db.flush()
    return count