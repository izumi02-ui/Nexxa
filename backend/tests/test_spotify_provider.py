import pytest

from app.providers.spotify.client import SpotifyClient, SpotifyToken
from app.providers.spotify.provider import SpotifyProvider
from app.providers.types import ProviderName


def make_spotify_track(
    track_id: str,
    title: str,
) -> dict:
    return {
        "id": track_id,
        "name": title,
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
                f"{track_id}"
            )
        },
    }


class FakeSpotifyClient:
    def __init__(
        self,
        tracks: list[dict] | None = None,
    ) -> None:
        self.tracks = tracks or [
            make_spotify_track(
                "spotify-track-1",
                "Test Track",
            )
        ]

        self.search_calls: list[dict] = []
        self.track_calls = 0

    async def search_tracks(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
    ) -> dict:
        self.search_calls.append(
            {
                "query": query,
                "limit": limit,
                "offset": offset,
            }
        )

        items = self.tracks[
            offset : offset + limit
        ]

        return {
            "tracks": {
                "items": items,
                "total": len(self.tracks),
                "limit": limit,
                "offset": offset,
            }
        }

    async def get_track(
        self,
        external_id: str,
    ) -> dict:
        self.track_calls += 1

        for track in self.tracks:
            if track.get("id") == external_id:
                return track

        return {}


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
        == "https://open.spotify.com/track/"
        "spotify-track-1"
    )

    assert len(client.search_calls) == 1


@pytest.mark.asyncio
async def test_spotify_provider_search_paginates() -> None:
    tracks = [
        make_spotify_track(
            f"spotify-track-{index}",
            f"Track {index}",
        )
        for index in range(1, 26)
    ]

    client = FakeSpotifyClient(tracks=tracks)
    provider = SpotifyProvider(client=client)

    results = await provider.search_tracks(
        query="test",
        limit=20,
    )

    assert len(results) == 20

    assert [
        track.external_id
        for track in results
    ] == [
        f"spotify-track-{index}"
        for index in range(1, 21)
    ]

    assert len(client.search_calls) == 2

    assert client.search_calls[0] == {
        "query": "test",
        "limit": 10,
        "offset": 0,
    }

    assert client.search_calls[1] == {
        "query": "test",
        "limit": 10,
        "offset": 10,
    }


@pytest.mark.asyncio
async def test_spotify_provider_search_stops_at_available_results() -> None:
    tracks = [
        make_spotify_track(
            f"spotify-track-{index}",
            f"Track {index}",
        )
        for index in range(1, 6)
    ]

    client = FakeSpotifyClient(tracks=tracks)
    provider = SpotifyProvider(client=client)

    results = await provider.search_tracks(
        query="test",
        limit=20,
    )

    assert len(results) == 5
    assert len(client.search_calls) == 1


@pytest.mark.asyncio
async def test_spotify_provider_search_rejects_blank_query() -> None:
    client = FakeSpotifyClient()
    provider = SpotifyProvider(client=client)

    results = await provider.search_tracks(
        query="   ",
        limit=20,
    )

    assert results == []
    assert client.search_calls == []


@pytest.mark.asyncio
async def test_spotify_provider_search_rejects_non_positive_limit() -> None:
    client = FakeSpotifyClient()
    provider = SpotifyProvider(client=client)

    results = await provider.search_tracks(
        query="test",
        limit=0,
    )

    assert results == []
    assert client.search_calls == []


@pytest.mark.asyncio
async def test_spotify_provider_skips_invalid_tracks() -> None:
    invalid_track = make_spotify_track(
        "spotify-invalid",
        "",
    )

    valid_track = make_spotify_track(
        "spotify-valid",
        "Valid Track",
    )

    client = FakeSpotifyClient(
        tracks=[
            invalid_track,
            valid_track,
        ]
    )

    provider = SpotifyProvider(client=client)

    results = await provider.search_tracks(
        query="test",
        limit=10,
    )

    assert len(results) == 1
    assert results[0].external_id == "spotify-valid"


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
async def test_spotify_provider_get_missing_track() -> None:
    client = FakeSpotifyClient()
    provider = SpotifyProvider(client=client)

    result = await provider.get_track(
        external_id="does-not-exist",
    )

    assert result is None
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