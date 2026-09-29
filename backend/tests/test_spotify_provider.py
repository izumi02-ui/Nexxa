from app.providers.spotify.client import SpotifyClient
from app.providers.spotify.provider import SpotifyProvider
from app.providers.types import ProviderName


def test_spotify_provider_name() -> None:
    client = SpotifyClient(
        client_id="test-client",
        client_secret="test-secret",
    )

    provider = SpotifyProvider(
        client=client,
        access_token="test-token",
    )

    assert provider.name == ProviderName.SPOTIFY


def test_spotify_track_normalization() -> None:
    item = {
        "id": "spotify-track-123",
        "name": "Test Track",
        "duration_ms": 180000,
        "artists": [
            {
                "name": "Test Artist",
            }
        ],
        "album": {
            "name": "Test Album",
            "images": [
                {
                    "url": "https://example.com/artwork.jpg",
                }
            ],
        },
        "external_urls": {
            "spotify": "https://open.spotify.com/track/spotify-track-123",
        },
    }

    result = SpotifyProvider._normalize_track(item)

    assert result.provider == ProviderName.SPOTIFY
    assert result.external_id == "spotify-track-123"
    assert result.title == "Test Track"
    assert result.artist_name == "Test Artist"
    assert result.album_name == "Test Album"
    assert result.duration_ms == 180000
    assert (
        result.external_url
        == "https://open.spotify.com/track/spotify-track-123"
    )