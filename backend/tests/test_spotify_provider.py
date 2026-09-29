import pytest

from app.providers.spotify.client import SpotifyClient, SpotifyToken
from app.providers.spotify.provider import SpotifyProvider
from app.providers.types import ProviderName


class FakeSpotifyClient:
    def __init__(self) -> None:
        self.search_calls = 0
        self.track_calls = 0

    async def search_tracks(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
    ) -> dict:
        self.search_calls += 1

        return {
            "tracks": {
                "items": [
                    {
                        "id": "spotify-track-1",
                        "name": "Test Track",
                        "duration_ms": 210000,
                        "artists": [
                            {
                                "name": "Test Artist",
                            }
                        ],
                        "album": {
                            "name": "Test Album",
                        },
                        "external_urls": {
                            "spotify": (
                                "https://open.spotify.com/track/"
                                "spotify-track-1"
                            )
                        },
                    }
                ]
            }
        }

    async def get_track(
        self,
        external_id: str,
    ) -> dict:
        self.track_calls += 1

        return {
            "id": external_id,
            "name": "Test Track",
            "duration_ms": 210000,
            "artists": [
                {
                    "name": "Test Artist",
                }
            ],
            "album": {
                "name": "Test Album",
            },
            "external_urls": {
                "spotify": (
                    "https://open.spotify.com/track/"
                    f"{external_id}"
                )
            },
        }


def test_spotify_provider_name() -> None:
    provider = SpotifyProvider(
        client=FakeSpotifyClient(),
    )

    assert provider.name is ProviderName.SPOTIFY


@pytest.mark.asyncio
async def test_spotify_provider_search_normalizes_track() -> None:
    client = FakeSpotifyClient()
    provider = SpotifyProvider(client=client)

    results = await provider.search_tracks(
        query="test",
        limit=20,
    )

    assert len(results) == 1

    track = results[0]

    assert track.provider is ProviderName.SPOTIFY
    assert track.external_id == "spotify-track-1"
    assert track.title == "Test Track"
    assert track.artist_name == "Test Artist"
    assert track.album_name == "Test Album"
    assert track.duration_ms == 210000
    assert (
        track.external_url
        == "https://open.spotify.com/track/spotify-track-1"
    )

    assert client.search_calls == 1


@pytest.mark.asyncio
async def test_spotify_provider_get_track() -> None:
    client = FakeSpotifyClient()
    provider = SpotifyProvider(client=client)

    result = await provider.get_track(
        external_id="spotify-track-1",
    )

    assert result is not None
    assert result.provider is ProviderName.SPOTIFY
    assert result.external_id == "spotify-track-1"
    assert result.title == "Test Track"
    assert result.artist_name == "Test Artist"

    assert client.track_calls == 1


@pytest.mark.asyncio
async def test_spotify_provider_empty_track_id_returns_none() -> None:
    client = FakeSpotifyClient()
    provider = SpotifyProvider(client=client)

    result = await provider.get_track(
        external_id="   ",
    )

    assert result is None
    assert client.track_calls == 0


class TokenTestClient(SpotifyClient):
    def __init__(self) -> None:
        super().__init__(
            client_id="test-client-id",
            client_secret="test-client-secret",
        )
        self.token_requests = 0

    async def get_client_credentials_token(
        self,
    ) -> SpotifyToken:
        self.token_requests += 1

        return SpotifyToken(
            access_token="test-access-token",
            expires_in=3600,
        )


@pytest.mark.asyncio
async def test_spotify_client_caches_access_token() -> None:
    client = TokenTestClient()

    first_token = await client.get_access_token()
    second_token = await client.get_access_token()

    assert first_token == "test-access-token"
    assert second_token == "test-access-token"
    assert client.token_requests == 1