from sqlalchemy import inspect

from app.auth.models import User
from app.database.base import Base
from app.music.album_models import Album
from app.music.artist_models import Artist
from app.music.models import Track
from app.music.playback_models import PlaybackState
from app.music.playlist_models import Playlist, PlaylistTrack
from app.music.queue_models import Queue


def test_music_models_are_registered_with_metadata() -> None:
    tables = set(Base.metadata.tables)

    assert "users" in tables
    assert "artists" in tables
    assert "albums" in tables
    assert "tracks" in tables
    assert "playlists" in tables
    assert "playlist_tracks" in tables
    assert "queue" in tables
    assert "playback_states" in tables


def test_track_has_expected_foreign_keys() -> None:
    mapper = inspect(Track)
    foreign_keys = {
        foreign_key.target_fullname
        for column in mapper.columns
        for foreign_key in column.foreign_keys
    }

    assert "artists.id" in foreign_keys
    assert "albums.id" in foreign_keys


def test_playlist_belongs_to_user() -> None:
    mapper = inspect(Playlist)
    foreign_keys = {
        foreign_key.target_fullname
        for column in mapper.columns
        for foreign_key in column.foreign_keys
    }

    assert "users.id" in foreign_keys


def test_playlist_track_has_expected_foreign_keys() -> None:
    mapper = inspect(PlaylistTrack)
    foreign_keys = {
        foreign_key.target_fullname
        for column in mapper.columns
        for foreign_key in column.foreign_keys
    }

    assert "playlists.id" in foreign_keys
    assert "tracks.id" in foreign_keys


def test_queue_has_expected_foreign_keys() -> None:
    mapper = inspect(Queue)
    foreign_keys = {
        foreign_key.target_fullname
        for column in mapper.columns
        for foreign_key in column.foreign_keys
    }

    assert "users.id" in foreign_keys
    assert "tracks.id" in foreign_keys


def test_playback_state_has_unique_user_constraint() -> None:
    table = PlaybackState.__table__

    unique_constraints = {
        constraint.name
        for constraint in table.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    }

    assert any(
        constraint_name
        for constraint_name in unique_constraints
        if constraint_name
    )


def test_playlist_track_has_unique_playlist_track_constraint() -> None:
    table = PlaylistTrack.__table__

    unique_constraints = [
        constraint
        for constraint in table.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    ]

    assert any(
        {
            column.name
            for column in constraint.columns
        }
        == {"playlist_id", "track_id"}
        for constraint in unique_constraints
    )


def test_playlist_track_has_unique_playlist_position_constraint() -> None:
    table = PlaylistTrack.__table__

    unique_constraints = [
        constraint
        for constraint in table.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    ]

    assert any(
        {
            column.name
            for column in constraint.columns
        }
        == {"playlist_id", "position"}
        for constraint in unique_constraints
    )


def test_queue_has_unique_user_position_constraint() -> None:
    table = Queue.__table__

    unique_constraints = [
        constraint
        for constraint in table.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    ]

    assert any(
        {
            column.name
            for column in constraint.columns
        }
        == {"user_id", "position"}
        for constraint in unique_constraints
    )


def test_core_models_are_importable() -> None:
    assert User.__tablename__ == "users"
    assert Artist.__tablename__ == "artists"
    assert Album.__tablename__ == "albums"
    assert Track.__tablename__ == "tracks"
    assert Playlist.__tablename__ == "playlists"
    assert PlaylistTrack.__tablename__ == "playlist_tracks"
    assert Queue.__tablename__ == "queue"
    assert PlaybackState.__tablename__ == "playback_states"
