from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.music.models import Track
from app.recommendations.service import get_recommendations


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


def test_recommendations_returns_empty_for_zero_limit() -> None:
    db = create_test_db()

    try:
        result = get_recommendations(
            db=db,
            limit=0,
        )

        assert result == []
    finally:
        db.close()


def test_recommendations_returns_tracks_when_no_source_ids() -> None:
    db = create_test_db()

    try:
        db.add_all(
            [
                Track(
                    title="Track One",
                    artist_id=1,
                ),
                Track(
                    title="Track Two",
                    artist_id=1,
                ),
            ]
        )
        db.commit()

        result = get_recommendations(
            db=db,
            limit=20,
        )

        assert len(result) == 2
        assert result[0].title == "Track One"
        assert result[1].title == "Track Two"
    finally:
        db.close()


def test_recommendations_excludes_source_tracks() -> None:
    db = create_test_db()

    try:
        source = Track(
            title="Source Track",
            artist_id=1,
        )
        other = Track(
            title="Other Track",
            artist_id=1,
        )

        db.add_all([source, other])
        db.commit()
        db.refresh(source)

        result = get_recommendations(
            db=db,
            track_ids=[source.id],
            limit=20,
        )

        assert all(track.id != source.id for track in result)
        assert any(track.id == other.id for track in result)
    finally:
        db.close()


def test_recommendations_prioritize_same_album() -> None:
    db = create_test_db()

    try:
        source = Track(
            title="Source Track",
            artist_id=1,
            album_id=10,
        )
        same_album = Track(
            title="Same Album",
            artist_id=2,
            album_id=10,
        )
        same_artist = Track(
            title="Same Artist",
            artist_id=1,
            album_id=20,
        )
        unrelated = Track(
            title="Unrelated",
            artist_id=3,
            album_id=30,
        )

        db.add_all(
            [
                source,
                same_album,
                same_artist,
                unrelated,
            ]
        )
        db.commit()
        db.refresh(source)

        result = get_recommendations(
            db=db,
            track_ids=[source.id],
            limit=3,
        )

        assert result[0].id == same_album.id
        assert result[1].id == same_artist.id
        assert result[2].id == unrelated.id
    finally:
        db.close()
