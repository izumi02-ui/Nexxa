from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.auth.models import User
from app.database.base import Base
from app.music.playlist_service import (
    create_playlist,
    delete_playlist,
    get_playlist,
    list_playlists,
    update_playlist,
)


def create_test_database():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


def test_create_playlist() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        user = User(
            email="playlist@example.com",
            password_hash="hashed-password",
        )
        db.add(user)
        db.flush()

        playlist = create_playlist(
            db=db,
            user_id=user.id,
            name="My Playlist",
            description="Test playlist",
            artwork_url="https://example.com/artwork.jpg",
            is_public=False,
        )

        assert playlist.id is not None
        assert playlist.user_id == user.id
        assert playlist.name == "My Playlist"
        assert playlist.description == "Test playlist"
        assert playlist.artwork_url == "https://example.com/artwork.jpg"
        assert playlist.is_public is False


def test_get_playlist() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        user = User(
            email="get-playlist@example.com",
            password_hash="hashed-password",
        )
        db.add(user)
        db.flush()

        playlist = create_playlist(
            db=db,
            user_id=user.id,
            name="Get Playlist",
        )

        result = get_playlist(
            db=db,
            user_id=user.id,
            playlist_id=playlist.id,
        )

        assert result is not None
        assert result.id == playlist.id
        assert result.name == "Get Playlist"


def test_get_playlist_does_not_return_another_users_playlist() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        user_one = User(
            email="playlist-user-one@example.com",
            password_hash="hashed-password",
        )
        user_two = User(
            email="playlist-user-two@example.com",
            password_hash="hashed-password",
        )

        db.add_all([user_one, user_two])
        db.flush()

        playlist = create_playlist(
            db=db,
            user_id=user_one.id,
            name="Private Playlist",
        )

        result = get_playlist(
            db=db,
            user_id=user_two.id,
            playlist_id=playlist.id,
        )

        assert result is None


def test_list_playlists_only_returns_user_playlists() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        user_one = User(
            email="list-user-one@example.com",
            password_hash="hashed-password",
        )
        user_two = User(
            email="list-user-two@example.com",
            password_hash="hashed-password",
        )

        db.add_all([user_one, user_two])
        db.flush()

        first = create_playlist(
            db=db,
            user_id=user_one.id,
            name="First Playlist",
        )

        second = create_playlist(
            db=db,
            user_id=user_one.id,
            name="Second Playlist",
        )

        create_playlist(
            db=db,
            user_id=user_two.id,
            name="Other Playlist",
        )

        playlists = list_playlists(
            db=db,
            user_id=user_one.id,
        )

        assert {playlist.id for playlist in playlists} == {
            first.id,
            second.id,
        }


def test_update_playlist() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        user = User(
            email="update-playlist@example.com",
            password_hash="hashed-password",
        )
        db.add(user)
        db.flush()

        playlist = create_playlist(
            db=db,
            user_id=user.id,
            name="Original",
        )

        updated = update_playlist(
            db=db,
            user_id=user.id,
            playlist_id=playlist.id,
            name="Updated",
            description="Updated description",
            artwork_url="https://example.com/updated.jpg",
            is_public=True,
        )

        assert updated is not None
        assert updated.name == "Updated"
        assert updated.description == "Updated description"
        assert updated.artwork_url == "https://example.com/updated.jpg"
        assert updated.is_public is True


def test_update_playlist_returns_none_for_another_users_playlist() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        owner = User(
            email="playlist-owner@example.com",
            password_hash="hashed-password",
        )
        other_user = User(
            email="playlist-other@example.com",
            password_hash="hashed-password",
        )

        db.add_all([owner, other_user])
        db.flush()

        playlist = create_playlist(
            db=db,
            user_id=owner.id,
            name="Owner Playlist",
        )

        updated = update_playlist(
            db=db,
            user_id=other_user.id,
            playlist_id=playlist.id,
            name="Unauthorized Update",
        )

        assert updated is None


def test_delete_playlist() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        user = User(
            email="delete-playlist@example.com",
            password_hash="hashed-password",
        )
        db.add(user)
        db.flush()

        playlist = create_playlist(
            db=db,
            user_id=user.id,
            name="Delete Me",
        )

        deleted = delete_playlist(
            db=db,
            user_id=user.id,
            playlist_id=playlist.id,
        )

        assert deleted is True

        result = get_playlist(
            db=db,
            user_id=user.id,
            playlist_id=playlist.id,
        )

        assert result is None


def test_delete_playlist_returns_false_for_missing_playlist() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        deleted = delete_playlist(
            db=db,
            user_id=999,
            playlist_id=999,
        )

        assert deleted is False


def test_delete_playlist_returns_false_for_another_users_playlist() -> None:
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

        result = get_playlist(
            db=db,
            user_id=owner.id,
            playlist_id=playlist.id,
        )

        assert result is not None
