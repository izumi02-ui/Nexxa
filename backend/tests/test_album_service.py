from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.music.album_models import Album
from app.music.album_service import (
    create_album,
    get_album,
    list_album_tracks,
    list_albums,
    list_albums_by_artist,
)
from app.music.album_schemas import AlbumCreate
from app.music.models import Track


def create_test_db() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    return Session(engine)


def test_create_album() -> None:
    db = create_test_db()

    try:
        album = create_album(
            db=db,
            data=AlbumCreate(
                title="Test Album",
                artist_id=1,
                artwork_url="https://example.com/artwork.jpg",
                release_date=date(2026, 1, 1),
            ),
        )

        assert album.title == "Test Album"
        assert album.artist_id == 1
        assert album.artwork_url == "https://example.com/artwork.jpg"
        assert album.release_date == date(2026, 1, 1)

        db.commit()
    finally:
        db.close()


def test_get_album() -> None:
    db = create_test_db()

    try:
        album = Album(
            title="Test Album",
            artist_id=1,
        )

        db.add(album)
        db.commit()
        db.refresh(album)

        result = get_album(
            db=db,
            album_id=album.id,
        )

        assert result is not None
        assert result.id == album.id
        assert result.title == "Test Album"
    finally:
        db.close()


def test_get_missing_album() -> None:
    db = create_test_db()

    try:
        result = get_album(
            db=db,
            album_id=999999,
        )

        assert result is None
    finally:
        db.close()


def test_list_albums() -> None:
    db = create_test_db()

    try:
        db.add_all(
            [
                Album(
                    title="Zeta Album",
                    artist_id=1,
                ),
                Album(
                    title="Alpha Album",
                    artist_id=1,
                ),
            ]
        )

        db.commit()

        albums = list_albums(db=db)

        assert len(albums) == 2
        assert albums[0].title == "Alpha Album"
        assert albums[1].title == "Zeta Album"
    finally:
        db.close()


def test_list_albums_by_artist() -> None:
    db = create_test_db()

    try:
        db.add_all(
            [
                Album(
                    title="Artist One Album",
                    artist_id=1,
                ),
                Album(
                    title="Artist Two Album",
                    artist_id=2,
                ),
                Album(
                    title="Artist One Second Album",
                    artist_id=1,
                ),
            ]
        )

        db.commit()

        albums = list_albums_by_artist(
            db=db,
            artist_id=1,
        )

        assert len(albums) == 2
        assert all(album.artist_id == 1 for album in albums)
        assert albums[0].title == "Artist One Album"
        assert albums[1].title == "Artist One Second Album"
    finally:
        db.close()


def test_list_album_tracks() -> None:
    db = create_test_db()

    try:
        album = Album(
            title="Test Album",
            artist_id=1,
        )

        db.add(album)
        db.commit()
        db.refresh(album)

        db.add_all(
            [
                Track(
                    title="Track Two",
                    artist_id=1,
                    album_id=album.id,
                ),
                Track(
                    title="Track One",
                    artist_id=1,
                    album_id=album.id,
                ),
            ]
        )

        db.commit()

        tracks = list_album_tracks(
            db=db,
            album_id=album.id,
        )

        assert len(tracks) == 2
        assert tracks[0].title == "Track Two"
        assert tracks[1].title == "Track One"
        assert all(
            track.album_id == album.id
            for track in tracks
        )
    finally:
        db.close()
