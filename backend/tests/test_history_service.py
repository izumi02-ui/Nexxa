from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.auth.models import User
from app.database.base import Base
from app.music.artist_models import Artist
from app.music.history_service import (
    clear_history,
    create_history_entry,
    delete_history_entry,
    list_history,
)
from app.music.models import Track


def create_test_database():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        artist = Artist(name="History Test Artist")
        db.add(artist)
        db.flush()

        db.add_all(
            [
                Track(
                    id=track_id,
                    title=f"Track {track_id}",
                    artist_id=artist.id,
                )
                for track_id in range(1, 21)
            ]
        )
        db.commit()

    return engine


def create_user(db: Session, email: str) -> User:
    user = User(
        email=email,
        password_hash="test-password-hash",
    )
    db.add(user)
    db.flush()
    return user


def test_create_history_entry() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        user = create_user(db, "history@example.com")

        entry = create_history_entry(
            db=db,
            user_id=user.id,
            track_id=1,
            position_ms=30_000,
            duration_ms=240_000,
        )

        assert entry is not None
        db.flush()

        assert entry.id is not None
        assert entry.user_id == user.id
        assert entry.track_id == 1
        assert entry.position_ms == 30_000
        assert entry.duration_ms == 240_000


def test_create_history_entry_sets_played_at() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        user = create_user(db, "history-time@example.com")
        before = datetime.now(timezone.utc)

        entry = create_history_entry(
            db=db,
            user_id=user.id,
            track_id=1,
        )

        assert entry is not None
        db.flush()
        after = datetime.now(timezone.utc)

        assert entry.played_at is not None
        assert before <= entry.played_at <= after


def test_create_history_entry_allows_missing_optional_fields() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        user = create_user(db, "history-optional@example.com")

        entry = create_history_entry(
            db=db,
            user_id=user.id,
            track_id=1,
        )

        assert entry is not None
        db.flush()

        assert entry.position_ms is None
        assert entry.duration_ms is None


def test_create_history_entry_rejects_missing_track() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        user = create_user(db, "history-missing-track@example.com")

        entry = create_history_entry(
            db=db,
            user_id=user.id,
            track_id=999999,
        )

        assert entry is None
        assert list_history(db=db, user_id=user.id) == []


def test_list_history_returns_newest_first() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        user = create_user(db, "history-order@example.com")

        first = create_history_entry(
            db=db,
            user_id=user.id,
            track_id=1,
        )
        assert first is not None
        db.flush()

        second = create_history_entry(
            db=db,
            user_id=user.id,
            track_id=2,
        )
        assert second is not None
        db.flush()

        entries = list_history(db=db, user_id=user.id)

        assert [entry.id for entry in entries] == [
            second.id,
            first.id,
        ]


def test_list_history_is_scoped_to_user() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        first_user = create_user(db, "history-user-one@example.com")
        second_user = create_user(db, "history-user-two@example.com")

        first = create_history_entry(
            db=db,
            user_id=first_user.id,
            track_id=1,
        )
        second = create_history_entry(
            db=db,
            user_id=second_user.id,
            track_id=2,
        )
        assert first is not None
        assert second is not None
        db.flush()

        first_entries = list_history(db=db, user_id=first_user.id)
        second_entries = list_history(db=db, user_id=second_user.id)

        assert [entry.id for entry in first_entries] == [first.id]
        assert [entry.id for entry in second_entries] == [second.id]


def test_delete_history_entry_only_deletes_owners_entry() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        owner = create_user(db, "history-owner@example.com")
        other_user = create_user(db, "history-other@example.com")

        entry = create_history_entry(
            db=db,
            user_id=owner.id,
            track_id=1,
        )
        assert entry is not None
        db.flush()

        assert delete_history_entry(
            db=db,
            user_id=other_user.id,
            history_id=entry.id,
        ) is False

        assert delete_history_entry(
            db=db,
            user_id=owner.id,
            history_id=entry.id,
        ) is True

        assert list_history(db=db, user_id=owner.id) == []


def test_delete_history_entry_returns_false_when_missing() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        user = create_user(db, "history-delete-missing@example.com")

        assert delete_history_entry(
            db=db,
            user_id=user.id,
            history_id=999999,
        ) is False


def test_clear_history_only_deletes_current_users_entries() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        first_user = create_user(db, "history-clear-one@example.com")
        second_user = create_user(db, "history-clear-two@example.com")

        for track_id in (1, 2, 3):
            entry = create_history_entry(
                db=db,
                user_id=first_user.id,
                track_id=track_id,
            )
            assert entry is not None

        other_entry = create_history_entry(
            db=db,
            user_id=second_user.id,
            track_id=4,
        )
        assert other_entry is not None
        db.flush()

        deleted_count = clear_history(db=db, user_id=first_user.id)

        assert deleted_count == 3
        assert list_history(db=db, user_id=first_user.id) == []

        remaining = list_history(db=db, user_id=second_user.id)
        assert len(remaining) == 1
        assert remaining[0].id == other_entry.id


def test_clear_history_returns_zero_when_empty() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        user = create_user(db, "history-empty@example.com")

        assert clear_history(db=db, user_id=user.id) == 0