from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.auth.models import User
from app.database.base import Base
from app.music.playlist_service import (
    add_track_to_playlist,
    delete_playlist,
    get_playlist,
    get_playlist_tracks,
    remove_track_from_playlist,
    update_playlist,
    update_playlist_track_position,
)


def create_test_database():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


def test_user_cannot_read_another_users_playlist() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        owner = User(
            email="owner@example.com",
            password_hash="hashed-password",
        )
        other_user = User(
            email="other@example.com",
            password_hash="hashed-password",
        )

        db.add_all([owner, other_user])
        db.flush()

        from app.music.playlist_service import create_playlist

        playlist = create_playlist(
            db=db,
            user_id=owner.id,
            name="Private Playlist",
        )

        result = get_playlist(
            db=db,
            user_id=other_user.id,
            playlist_id=playlist.id,
        )

        assert result is None


def test_user_cannot_update_another_users_playlist() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        owner = User(
            email="update-owner@example.com",
            password_hash="hashed-password",
        )
        other_user = User(
            email="update-other@example.com",
            password_hash="hashed-password",
        )

        db.add_all([owner, other_user])
        db.flush()

        from app.music.playlist_service import create_playlist

        playlist = create_playlist(
            db=db,
            user_id=owner.id,
            name="Original Playlist",
        )

        result = update_playlist(
            db=db,
            user_id=other_user.id,
            playlist_id=playlist.id,
            name="Unauthorized Playlist",
        )

        assert result is None

        owner_playlist = get_playlist(
            db=db,
            user_id=owner.id,
            playlist_id=playlist.id,
        )

        assert owner_playlist is not None
        assert owner_playlist.name == "Original Playlist"


def test_user_cannot_delete_another_users_playlist() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        owner = User(
            email="delete-owner@example.com",
            password_hash="hashed-password",
        )
        other_user = User(
            email="delete-other@example.com",
            password_hash="hashed-password",
        )

        db.add_all([owner, other_user])
        db.flush()

        from app.music.playlist_service import create_playlist

        playlist = create_playlist(
            db=db,
            user_id=owner.id,
            name="Protected Playlist",
        )

        deleted = delete_playlist(
            db=db,
            user_id=other_user.id,
            playlist_id=playlist.id,
        )

        assert deleted is False

        owner_playlist = get_playlist(
            db=db,
            user_id=owner.id,
            playlist_id=playlist.id,
        )

        assert owner_playlist is not None


def test_user_cannot_add_track_to_another_users_playlist() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        owner = User(
            email="track-owner@example.com",
            password_hash="hashed-password",
        )
        other_user = User(
            email="track-other@example.com",
            password_hash="hashed-password",
        )

        db.add_all([owner, other_user])
        db.flush()

        from app.music.playlist_service import create_playlist

        playlist = create_playlist(
            db=db,
            user_id=owner.id,
            name="Protected Playlist",
        )

        result = add_track_to_playlist(
            db=db,
            user_id=other_user.id,
            playlist_id=playlist.id,
            track_id=1,
            position=0,
        )

        assert result is None


def test_user_cannot_remove_track_from_another_users_playlist() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        owner = User(
            email="remove-owner@example.com",
            password_hash="hashed-password",
        )
        other_user = User(
            email="remove-other@example.com",
            password_hash="hashed-password",
        )

        db.add_all([owner, other_user])
        db.flush()

        from app.music.playlist_service import create_playlist

        playlist = create_playlist(
            db=db,
            user_id=owner.id,
            name="Protected Playlist",
        )

        result = remove_track_from_playlist(
            db=db,
            user_id=other_user.id,
            playlist_id=playlist.id,
            track_id=1,
        )

        assert result is False


def test_user_cannot_read_tracks_from_another_users_playlist() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        owner = User(
            email="read-track-owner@example.com",
            password_hash="hashed-password",
        )
        other_user = User(
            email="read-track-other@example.com",
            password_hash="hashed-password",
        )

        db.add_all([owner, other_user])
        db.flush()

        from app.music.playlist_service import create_playlist

        playlist = create_playlist(
            db=db,
            user_id=owner.id,
            name="Protected Playlist",
        )

        result = get_playlist_tracks(
            db=db,
            user_id=other_user.id,
            playlist_id=playlist.id,
        )

        assert result is None


def test_user_cannot_reorder_another_users_playlist() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        owner = User(
            email="reorder-owner@example.com",
            password_hash="hashed-password",
        )
        other_user = User(
            email="reorder-other@example.com",
            password_hash="hashed-password",
        )

        db.add_all([owner, other_user])
        db.flush()

        from app.music.playlist_service import create_playlist

        playlist = create_playlist(
            db=db,
            user_id=owner.id,
            name="Protected Playlist",
        )

        result = update_playlist_track_position(
            db=db,
            user_id=other_user.id,
            playlist_id=playlist.id,
            track_id=1,
            position=0,
        )

        assert result is None


def test_negative_playlist_track_position_is_rejected() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        owner = User(
            email="position-owner@example.com",
            password_hash="hashed-password",
        )
        db.add(owner)
        db.flush()

        from app.music.playlist_service import create_playlist

        playlist = create_playlist(
            db=db,
            user_id=owner.id,
            name="Position Playlist",
        )

        try:
            update_playlist_track_position(
                db=db,
                user_id=owner.id,
                playlist_id=playlist.id,
                track_id=1,
                position=-1,
            )
        except ValueError as exc:
            assert str(exc) == "Playlist track position cannot be negative"
        else:
            raise AssertionError(
                "Negative playlist track position was accepted"
            )
