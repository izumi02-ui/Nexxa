from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.music.favorite_models import Favorite
from app.music.history_models import HistoryEntry
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
            user_id=1,
            limit=0,
        )

        assert result == []
    finally:
        db.close()


def test_recommendations_are_user_specific() -> None:
    db = create_test_db()

    try:
        tracks = [
            Track(title="User One Track", artist_id=1),
            Track(title="User Two Track", artist_id=2),
            Track(title="Recommended For User One", artist_id=1),
            Track(title="Recommended For User Two", artist_id=2),
        ]

        db.add_all(tracks)
        db.commit()

        db.add_all(
            [
                Favorite(
                    user_id=1,
                    track_id=tracks[0].id,
                ),
                Favorite(
                    user_id=2,
                    track_id=tracks[1].id,
                ),
            ]
        )
        db.commit()

        user_one = get_recommendations(
            db=db,
            user_id=1,
            limit=10,
        )

        user_two = get_recommendations(
            db=db,
            user_id=2,
            limit=10,
        )

        user_one_ids = {track.id for track in user_one}
        user_two_ids = {track.id for track in user_two}

        assert tracks[0].id not in user_one_ids
        assert tracks[1].id not in user_two_ids

        assert tracks[2].id in user_one_ids
        assert tracks[3].id in user_two_ids

        assert user_one_ids != user_two_ids
    finally:
        db.close()


def test_recommendations_use_user_history() -> None:
    db = create_test_db()

    try:
        source = Track(
            title="Recently Played",
            artist_id=10,
            album_id=100,
        )
        recommended = Track(
            title="Related Track",
            artist_id=10,
            album_id=200,
        )
        unrelated = Track(
            title="Unrelated Track",
            artist_id=20,
            album_id=300,
        )

        db.add_all(
            [
                source,
                recommended,
                unrelated,
            ]
        )
        db.commit()

        db.add(
            HistoryEntry(
                user_id=1,
                track_id=source.id,
            )
        )
        db.commit()

        result = get_recommendations(
            db=db,
            user_id=1,
            limit=10,
        )

        result_ids = {track.id for track in result}

        assert source.id not in result_ids
        assert recommended.id in result_ids
    finally:
        db.close()


def test_recommendations_use_user_favorites() -> None:
    db = create_test_db()

    try:
        favorite_track = Track(
            title="Favorite",
            artist_id=5,
            album_id=50,
        )
        related_track = Track(
            title="Related",
            artist_id=5,
            album_id=60,
        )

        db.add_all(
            [
                favorite_track,
                related_track,
            ]
        )
        db.commit()

        db.add(
            Favorite(
                user_id=7,
                track_id=favorite_track.id,
            )
        )
        db.commit()

        result = get_recommendations(
            db=db,
            user_id=7,
            limit=10,
        )

        result_ids = {track.id for track in result}

        assert favorite_track.id not in result_ids
        assert related_track.id in result_ids
    finally:
        db.close()
