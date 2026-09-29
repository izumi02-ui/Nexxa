from app.auth.models import User
from app.music.album_models import Album
from app.music.artist_models import Artist
from app.music.models import Track
from app.music.playback_models import PlaybackState
from app.music.playlist_models import Playlist, PlaylistTrack
from app.music.queue_models import Queue


def test_phase_two_models_are_registered() -> None:
    expected_tables = {
        "users",
        "artists",
        "albums",
        "tracks",
        "playlists",
        "playlist_tracks",
        "queues",
        "playback_states",
    }

    registered_tables = {
        User.__table__.name,
        Artist.__table__.name,
        Album.__table__.name,
        Track.__table__.name,
        Playlist.__table__.name,
        PlaylistTrack.__table__.name,
        Queue.__table__.name,
        PlaybackState.__table__.name,
    }

    assert registered_tables == expected_tables


def test_track_uses_normalized_artist_and_album_foreign_keys() -> None:
    artist_fk = next(iter(Track.__table__.c.artist_id.foreign_keys))
    album_fk = next(iter(Track.__table__.c.album_id.foreign_keys))

    assert artist_fk.target_fullname == "artists.id"
    assert album_fk.target_fullname == "albums.id"


def test_playlist_has_user_ownership() -> None:
    foreign_keys = {
        fk.target_fullname
        for fk in Playlist.__table__.c.user_id.foreign_keys
    }

    assert "users.id" in foreign_keys


def test_playlist_track_references_track() -> None:
    foreign_keys = {
        fk.target_fullname
        for fk in PlaylistTrack.__table__.c.track_id.foreign_keys
    }

    assert "tracks.id" in foreign_keys


def test_queue_references_user_and_track() -> None:
    user_foreign_keys = {
        fk.target_fullname
        for fk in Queue.__table__.c.user_id.foreign_keys
    }

    track_foreign_keys = {
        fk.target_fullname
        for fk in Queue.__table__.c.track_id.foreign_keys
    }

    assert "users.id" in user_foreign_keys
    assert "tracks.id" in track_foreign_keys


def test_playback_state_is_unique_per_user() -> None:
    constraints = {
        constraint.name
        for constraint in PlaybackState.__table__.constraints
        if constraint.name
    }

    assert "uq_playback_states_user_id" not in constraints

    user_column = PlaybackState.__table__.c.user_id

    assert user_column.unique is True