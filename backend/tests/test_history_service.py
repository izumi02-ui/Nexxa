from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.auth.models import User
from app.database.base import Base
from app.music.history_models import HistoryEntry
from app.music.history_service import create_history_entry


def create_test_database():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


def test_create_history_entry() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        user = User(
            email="history@example.com",
            password_hash="hashed-password",
        )

        db.add(user)
        db.flush()

        entry = create_history_entry(
            db=db,
            user_id=user.id,
            track_id=1,
            position_ms=30_000,
            duration_ms=240_000,
        )

        assert entry.id is not None
        assert entry.user_id == user.id
        assert entry.track_id == 1
        assert entry.position_ms == 30_000
        assert entry.duration_ms == 240_000


def test_create_history_entry_sets_played_at() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        user = User(
            email="history-time@example.com",
            password_hash="hashed-password",
        )

        db.add(user)
        db.flush()

        before = datetime.now(timezone.utc)

        entry = create_history_entry(
            db=db,
            user_id=user.id,
            track_id=1,
        )

        after = datetime.now(timezone.utc)

        assert entry.played_at is not None
        assert before <= entry.played_at <= after


def test_create_history_entry_allows_missing_playback_position() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        user = User(
            email="history-position@example.com",
            password_hash="hashed-password",
        )

        db.add(user)
        db.flush()

        entry = create_history_entry(
            db=db,
            user_id=user.id,
            track_id=5,
        )

        assert entry.position_ms is None
        assert entry.duration_ms is None


def test_create_multiple_history_entries() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        user = User(
            email="history-multiple@example.com",
            password_hash="hashed-password",
        )

        db.add(user)
        db.flush()

        first = create_history_entry(
            db=db,
            user_id=user.id,
            track_id=1,
        )

        second = create_history_entry(
            db=db,
            user_id=user.id,
            track_id=2,
        )

        assert first.id is not None
        assert second.id is not None
        assert first.id != second.id

        assert first.track_id == 1
        assert second.track_id == 2


def test_history_entries_belong_to_correct_users() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        user_one = User(
            email="history-user-one@example.com",
            password_hash="hashed-password",
        )

        user_two = User(
            email="history-user-two@example.com",
            password_hash="hashed-password",
        )

        db.add_all([user_one, user_two])
        db.flush()

        first = create_history_entry(
            db=db,
            user_id=user_one.id,
            track_id=10,
        )

        second = create_history_entry(
            db=db,
            user_id=user_two.id,
            track_id=20,
        )

        assert first.user_id == user_one.id
        assert second.user_id == user_two.id
        assert first.user_id != second.user_id
