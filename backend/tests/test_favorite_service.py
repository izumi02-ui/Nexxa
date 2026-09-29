from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.auth.models import User
from app.database.base import Base
from app.music.favorite_models import Favorite
from app.music.favorite_service import (
    create_favorite,
    delete_favorite,
    get_favorite,
    list_favorites,
)


def create_test_database():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


def test_create_favorite() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        user = User(
            email="favorite@example.com",
            password_hash="hashed-password",
        )
        db.add(user)
        db.flush()

        favorite = create_favorite(
            db=db,
            user_id=user.id,
            track_id=1,
        )

        assert favorite.id is not None
        assert favorite.user_id == user.id
        assert favorite.track_id == 1


def test_create_favorite_returns_existing_favorite() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        user = User(
            email="duplicate@example.com",
            password_hash="hashed-password",
        )
        db.add(user)
        db.flush()

        first = create_favorite(
            db=db,
            user_id=user.id,
            track_id=1,
        )

        second = create_favorite(
            db=db,
            user_id=user.id,
            track_id=1,
        )

        assert first.id == second.id


def test_get_favorite() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        user = User(
            email="get@example.com",
            password_hash="hashed-password",
        )
        db.add(user)
        db.flush()

        create_favorite(
            db=db,
            user_id=user.id,
            track_id=10,
        )

        favorite = get_favorite(
            db=db,
            user_id=user.id,
            track_id=10,
        )

        assert favorite is not None
        assert favorite.track_id == 10


def test_list_favorites_only_returns_user_favorites() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        user_one = User(
            email="user-one@example.com",
            password_hash="hashed-password",
        )
        user_two = User(
            email="user-two@example.com",
            password_hash="hashed-password",
        )

        db.add_all([user_one, user_two])
        db.flush()

        create_favorite(db, user_one.id, 1)
        create_favorite(db, user_one.id, 2)
        create_favorite(db, user_two.id, 3)

        favorites = list_favorites(
            db=db,
            user_id=user_one.id,
        )

        assert {favorite.track_id for favorite in favorites} == {1, 2}


def test_delete_favorite() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        user = User(
            email="delete@example.com",
            password_hash="hashed-password",
        )
        db.add(user)
        db.flush()

        create_favorite(
            db=db,
            user_id=user.id,
            track_id=20,
        )

        deleted = delete_favorite(
            db=db,
            user_id=user.id,
            track_id=20,
        )

        assert deleted is True
        assert get_favorite(
            db=db,
            user_id=user.id,
            track_id=20,
        ) is None


def test_delete_missing_favorite_returns_false() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        deleted = delete_favorite(
            db=db,
            user_id=999,
            track_id=999,
        )

        assert deleted is False
