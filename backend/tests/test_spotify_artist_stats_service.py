from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database.base import Base
from app.music.artist_models import Artist
from app.music.artist_provider_models import ArtistProviderProfile
from app.music.spotify_artist_stats_models import SpotifyArtistStats
from app.music.spotify_artist_stats_service import (
    get_spotify_artist_id,
    get_spotify_artist_stats,
    save_spotify_artist_stats,
)


def create_test_database():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        artist = Artist(name="Test Artist")
        db.add(artist)
        db.flush()

        db.add(
            ArtistProviderProfile(
                artist_id=artist.id,
                provider="spotify",
                external_id="spotify-artist-123",
                external_url=(
                    "https://open.spotify.com/artist/"
                    "spotify-artist-123"
                ),
            )
        )

        db.commit()

    return engine


def make_artist_data() -> dict:
    return {
        "id": "spotify-artist-123",
        "name": "Test Artist",
        "genres": ["pop", "rock"],
        "popularity": 85,
        "followers": {
            "total": 100000,
        },
        "external_urls": {
            "spotify": (
                "https://open.spotify.com/artist/"
                "spotify-artist-123"
            ),
        },
        "images": [
            {
                "url": "https://example.com/artist.jpg",
            },
        ],
    }


def make_albums_data() -> dict:
    return {
        "items": [
            {
                "id": "album-123",
                "name": "Test Album",
                "album_type": "album",
                "release_date": "2025-01-01",
                "total_tracks": 10,
                "images": [
                    {
                        "url": "https://example.com/album.jpg",
                    },
                ],
                "external_urls": {
                    "spotify": "https://open.spotify.com/album/album-123",
                },
            },
            {
                "id": "single-123",
                "name": "Test Single",
                "album_type": "single",
                "release_date": "2025-02-01",
                "total_tracks": 1,
                "images": [],
                "external_urls": {
                    "spotify": "https://open.spotify.com/album/single-123",
                },
            },
        ]
    }


def make_top_tracks_data() -> dict:
    return {
        "tracks": [
            {
                "id": "track-123",
                "name": "Popular Song",
                "duration_ms": 210000,
                "explicit": False,
                "popularity": 90,
                "album": {
                    "name": "Test Album",
                    "images": [
                        {
                            "url": "https://example.com/track-album.jpg",
                        },
                    ],
                },
                "external_urls": {
                    "spotify": "https://open.spotify.com/track/track-123",
                },
            },
        ]
    }


def test_get_spotify_artist_id_returns_mapped_id() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        artist = db.query(Artist).one()

        assert get_spotify_artist_id(
            db,
            artist.id,
        ) == "spotify-artist-123"


def test_get_spotify_artist_id_returns_none_without_mapping() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        artist = Artist(name="Unmapped Artist")
        db.add(artist)
        db.flush()

        assert get_spotify_artist_id(
            db,
            artist.id,
        ) is None


def test_get_spotify_artist_stats_returns_none_before_save() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        artist = db.query(Artist).one()

        assert get_spotify_artist_stats(
            db,
            artist.id,
        ) is None


def test_save_spotify_artist_stats_creates_statistics() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        artist = db.query(Artist).one()

        stats = save_spotify_artist_stats(
            db=db,
            artist_id=artist.id,
            artist_data=make_artist_data(),
            albums_data=make_albums_data(),
            top_tracks_data=make_top_tracks_data(),
        )

        assert stats.id is not None
        assert stats.artist_id == artist.id
        assert stats.spotify_artist_id == "spotify-artist-123"
        assert stats.followers == 100000
        assert stats.popularity == 85
        assert stats.monthly_listeners is None
        assert stats.genres == ["pop", "rock"]
        assert len(stats.albums) == 1
        assert len(stats.singles) == 1
        assert len(stats.top_tracks) == 1
        assert stats.statistics_available is True
        assert stats.statistics_fetched_at is not None


def test_save_spotify_artist_stats_updates_existing_record() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        artist = db.query(Artist).one()

        first = save_spotify_artist_stats(
            db=db,
            artist_id=artist.id,
            artist_data=make_artist_data(),
            albums_data=make_albums_data(),
            top_tracks_data=make_top_tracks_data(),
        )

        first_id = first.id

        updated_data = make_artist_data()
        updated_data["followers"]["total"] = 200000
        updated_data["popularity"] = 92

        second = save_spotify_artist_stats(
            db=db,
            artist_id=artist.id,
            artist_data=updated_data,
            albums_data=make_albums_data(),
            top_tracks_data=make_top_tracks_data(),
        )

        assert second.id == first_id
        assert second.followers == 200000
        assert second.popularity == 92

        assert db.query(SpotifyArtistStats).count() == 1


def test_save_spotify_artist_stats_updates_canonical_artist() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        artist = db.query(Artist).one()

        save_spotify_artist_stats(
            db=db,
            artist_id=artist.id,
            artist_data=make_artist_data(),
            albums_data=make_albums_data(),
            top_tracks_data=make_top_tracks_data(),
        )

        assert artist.image_url == "https://example.com/artist.jpg"
        assert artist.genres == ["pop", "rock"]


def test_save_spotify_artist_stats_rejects_missing_artist() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        try:
            save_spotify_artist_stats(
                db=db,
                artist_id=999999,
                artist_data=make_artist_data(),
                albums_data=make_albums_data(),
                top_tracks_data=make_top_tracks_data(),
            )
        except ValueError as exc:
            assert "does not exist" in str(exc)
        else:
            raise AssertionError("Expected missing artist to be rejected.")


def test_save_spotify_artist_stats_rejects_mismatched_mapping() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        artist = db.query(Artist).one()
        wrong_artist_data = make_artist_data()
        wrong_artist_data["id"] = "different-spotify-id"

        try:
            save_spotify_artist_stats(
                db=db,
                artist_id=artist.id,
                artist_data=wrong_artist_data,
                albums_data=make_albums_data(),
                top_tracks_data=make_top_tracks_data(),
            )
        except ValueError as exc:
            assert "does not match" in str(exc)
        else:
            raise AssertionError("Expected mismatched mapping to be rejected.")


def test_save_spotify_artist_stats_handles_malformed_items() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        artist = db.query(Artist).one()

        stats = save_spotify_artist_stats(
            db=db,
            artist_id=artist.id,
            artist_data=make_artist_data(),
            albums_data={
                "items": [
                    None,
                    {},
                    {
                        "id": "valid-album",
                        "name": "Valid Album",
                        "album_type": "album",
                    },
                ],
            },
            top_tracks_data={
                "tracks": [
                    None,
                    {},
                    {
                        "id": "valid-track",
                        "name": "Valid Track",
                    },
                ],
            },
        )

        assert len(stats.albums) == 1
        assert len(stats.top_tracks) == 1