import pytest
from pydantic import ValidationError

from app.music.spotify_artist_stats_schemas import (
    SpotifyArtistRefreshResponse,
    SpotifyArtistReleaseResponse,
    SpotifyArtistStatsResponse,
    SpotifyArtistTopTrackResponse,
)


def make_stats_data() -> dict:
    return {
        "artist_id": 1,
        "spotify_artist_id": "spotify-artist-123",
        "spotify_url": (
            "https://open.spotify.com/artist/"
            "spotify-artist-123"
        ),
        "followers": 100000,
        "popularity": 85,
        "monthly_listeners": None,
        "genres": ["pop", "rock"],
        "albums": [
            {
                "id": "album-123",
                "name": "Test Album",
                "album_type": "album",
                "release_date": "2025-01-01",
                "total_tracks": 10,
                "image_url": "https://example.com/album.jpg",
                "external_url": "https://open.spotify.com/album/album-123",
            }
        ],
        "singles": [
            {
                "id": "single-123",
                "name": "Test Single",
                "album_type": "single",
                "release_date": "2025-02-01",
                "total_tracks": 1,
            }
        ],
        "top_tracks": [
            {
                "id": "track-123",
                "name": "Popular Song",
                "album_name": "Test Album",
                "duration_ms": 210000,
                "explicit": False,
                "popularity": 90,
                "image_url": "https://example.com/track.jpg",
                "external_url": "https://open.spotify.com/track/track-123",
            }
        ],
        "statistics_available": True,
        "statistics_fetched_at": "2026-01-01T12:00:00Z",
        "updated_at": "2026-01-01T12:00:00Z",
    }


def test_spotify_artist_stats_response_validates() -> None:
    response = SpotifyArtistStatsResponse(
        **make_stats_data()
    )

    assert response.artist_id == 1
    assert response.followers == 100000
    assert response.popularity == 85
    assert response.monthly_listeners is None
    assert len(response.albums) == 1
    assert len(response.singles) == 1
    assert len(response.top_tracks) == 1


def test_spotify_artist_stats_response_supports_empty_lists() -> None:
    data = make_stats_data()
    data["albums"] = []
    data["singles"] = []
    data["top_tracks"] = []
    data["genres"] = []

    response = SpotifyArtistStatsResponse(**data)

    assert response.albums == []
    assert response.singles == []
    assert response.top_tracks == []
    assert response.genres == []


def test_spotify_artist_stats_rejects_negative_followers() -> None:
    data = make_stats_data()
    data["followers"] = -1

    with pytest.raises(ValidationError):
        SpotifyArtistStatsResponse(**data)


def test_spotify_artist_stats_rejects_invalid_popularity() -> None:
    data = make_stats_data()
    data["popularity"] = 101

    with pytest.raises(ValidationError):
        SpotifyArtistStatsResponse(**data)


def test_spotify_artist_stats_rejects_invalid_artist_id() -> None:
    data = make_stats_data()
    data["artist_id"] = 0

    with pytest.raises(ValidationError):
        SpotifyArtistStatsResponse(**data)


def test_spotify_artist_release_response_validates() -> None:
    response = SpotifyArtistReleaseResponse(
        id="album-123",
        name="Test Album",
        album_type="album",
        total_tracks=10,
    )

    assert response.id == "album-123"
    assert response.total_tracks == 10


def test_spotify_artist_release_rejects_negative_track_count() -> None:
    with pytest.raises(ValidationError):
        SpotifyArtistReleaseResponse(
            id="album-123",
            name="Test Album",
            total_tracks=-1,
        )


def test_spotify_artist_top_track_response_validates() -> None:
    response = SpotifyArtistTopTrackResponse(
        id="track-123",
        name="Popular Song",
        duration_ms=210000,
        popularity=90,
    )

    assert response.id == "track-123"
    assert response.duration_ms == 210000
    assert response.popularity == 90


def test_spotify_artist_top_track_rejects_invalid_popularity() -> None:
    with pytest.raises(ValidationError):
        SpotifyArtistTopTrackResponse(
            id="track-123",
            name="Popular Song",
            popularity=101,
        )


def test_spotify_artist_refresh_response_validates() -> None:
    stats = SpotifyArtistStatsResponse(**make_stats_data())

    response = SpotifyArtistRefreshResponse(
        artist_id=1,
        refreshed=True,
        message="Spotify artist statistics refreshed.",
        statistics=stats,
    )

    assert response.refreshed is True
    assert response.statistics is not None
    assert response.statistics.artist_id == 1


def test_spotify_artist_refresh_response_supports_unavailable_stats() -> None:
    response = SpotifyArtistRefreshResponse(
        artist_id=1,
        refreshed=False,
        message="Spotify artist mapping not found.",
        statistics=None,
    )

    assert response.refreshed is False
    assert response.statistics is None