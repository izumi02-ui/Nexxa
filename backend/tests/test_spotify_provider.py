import pytest

from app.providers.spotify.provider import SpotifyProvider
from app.providers.types import ProviderName


class FakeSpotifyClient:
    def __init__(
        self,
        search_responses: list[dict] | None = None,
        track_response: dict | None = None,
    ) -> None:
        self.search_responses = search_responses or []
        self.track_response = track_response
        self.search_calls: list[dict] = []
        self.track_calls: list[str] = []

    async def search_tracks(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        self.search_calls.append(
            {
                "query": query,
                "limit": limit,
                "offset": offset,
            }
        )

        if self.search_responses:
            return self.search_responses.pop(0)

        return {
            "tracks": {
                "items": [],
            }
        }

    async def get_track(
        self,
        external_id: str,
    ) -> dict | None:
        self.track_calls.append(external_id)
        return self.track_response


def make_spotify_track(
    external_id: str = "track-1",
    title: str = "Test Track",
    artist_name: str = "Test Artist",
    album_name: str = "Test Album",
    artwork_url: str | None = "https://example.com/artwork.jpg",
    duration_ms: int = 180000,
    external_url: str | None = "https://open.spotify.com/track/track-1",
) -> dict:
    album = {
        "name": album_name,
        "images": (
            [{"url": artwork_url}]
            if artwork_url is not None
            else []
        ),
    }

    return {
        "id": external_id,
        "name": title,
        "artists": [
            {
                "name": artist_name,
            }
        ],
        "album": album,
        "duration_ms": duration_ms,
        "external_urls": {
            "spotify": external_url,
        },
    }


@pytest.mark.asyncio
async def test_spotify_provider_name() -> None:
    client = FakeSpotifyClient()
    provider = SpotifyProvider(client)

    assert provider.name is ProviderName.SPOTIFY


@pytest.mark.asyncio
async def test_search_tracks_normalizes_results() -> None:
    client = FakeSpotifyClient(
        search_responses=[
            {
                "tracks": {
                    "items": [
                        make_spotify_track(),
                    ],
                },
            }
        ]
    )

    provider = SpotifyProvider(client)

    results = await provider.search_tracks(
        query="  test song  ",
        limit=1,
    )

    assert len(results) == 1

    track = results[0]

    assert track.provider is ProviderName.SPOTIFY
    assert track.external_id == "track-1"
    assert track.title == "Test Track"
    assert track.artist_name == "Test Artist"
    assert track.album_name == "Test Album"
    assert track.duration_ms == 180000
    assert track.artwork_url == "https://example.com/artwork.jpg"
    assert (
        track.external_url
        == "https://open.spotify.com/track/track-1"
    )


@pytest.mark.asyncio
async def test_search_tracks_supports_pagination() -> None:
    first_page = [
        make_spotify_track(external_id="track-1"),
        make_spotify_track(external_id="track-2"),
    ]

    second_page = [
        make_spotify_track(external_id="track-3"),
    ]

    client = FakeSpotifyClient(
        search_responses=[
            {
                "tracks": {
                    "items": first_page,
                },
            },
            {
                "tracks": {
                    "items": second_page,
                },
            },
        ]
    )

    provider = SpotifyProvider(client)

    results = await provider.search_tracks(
        query="test",
        limit=3,
    )

    assert len(results) == 3
    assert [track.external_id for track in results] == [
        "track-1",
        "track-2",
        "track-3",
    ]

    assert client.search_calls == [
        {
            "query": "test",
            "limit": 3,
            "offset": 0,
        },
    ]


@pytest.mark.asyncio
async def test_search_tracks_requests_multiple_pages_when_needed() -> None:
    first_page = [
        make_spotify_track(external_id="track-1"),
        make_spotify_track(external_id="track-2"),
    ]

    second_page = [
        make_spotify_track(external_id="track-3"),
        make_spotify_track(external_id="track-4"),
    ]

    client = FakeSpotifyClient(
        search_responses=[
            {
                "tracks": {
                    "items": first_page,
                },
            },
            {
                "tracks": {
                    "items": second_page,
                },
            },
        ]
    )

    provider = SpotifyProvider(client)

    results = await provider.search_tracks(
        query="test",
        limit=4,
    )

    assert len(results) == 4

    assert client.search_calls == [
        {
            "query": "test",
            "limit": 4,
            "offset": 0,
        },
    ]


@pytest.mark.asyncio
async def test_search_tracks_stops_on_short_page() -> None:
    client = FakeSpotifyClient(
        search_responses=[
            {
                "tracks": {
                    "items": [
                        make_spotify_track(
                            external_id="track-1",
                        ),
                    ],
                },
            }
        ]
    )

    provider = SpotifyProvider(client)

    results = await provider.search_tracks(
        query="test",
        limit=5,
    )

    assert len(results) == 1
    assert client.search_calls[0]["offset"] == 0


@pytest.mark.asyncio
async def test_search_tracks_returns_empty_for_blank_query() -> None:
    client = FakeSpotifyClient()

    provider = SpotifyProvider(client)

    results = await provider.search_tracks(
        query="   ",
        limit=20,
    )

    assert results == []
    assert client.search_calls == []


@pytest.mark.asyncio
async def test_search_tracks_normalizes_non_positive_limit() -> None:
    client = FakeSpotifyClient(
        search_responses=[
            {
                "tracks": {
                    "items": [
                        make_spotify_track(),
                    ],
                },
            }
        ]
    )

    provider = SpotifyProvider(client)

    results = await provider.search_tracks(
        query="test",
        limit=0,
    )

    assert len(results) == 1


@pytest.mark.asyncio
async def test_search_tracks_skips_invalid_tracks() -> None:
    client = FakeSpotifyClient(
        search_responses=[
            {
                "tracks": {
                    "items": [
                        {
                            "name": "Invalid Track",
                        },
                        make_spotify_track(
                            external_id="valid-track",
                        ),
                    ],
                },
            }
        ]
    )

    provider = SpotifyProvider(client)

    results = await provider.search_tracks(
        query="test",
        limit=2,
    )

    assert len(results) == 1
    assert results[0].external_id == "valid-track"


@pytest.mark.asyncio
async def test_search_tracks_handles_missing_artwork() -> None:
    client = FakeSpotifyClient(
        search_responses=[
            {
                "tracks": {
                    "items": [
                        make_spotify_track(
                            artwork_url=None,
                        ),
                    ],
                },
            }
        ]
    )

    provider = SpotifyProvider(client)

    results = await provider.search_tracks(
        query="test",
        limit=1,
    )

    assert len(results) == 1
    assert results[0].artwork_url is None


@pytest.mark.asyncio
async def test_get_track() -> None:
    client = FakeSpotifyClient(
        track_response=make_spotify_track(
            external_id="spotify-track-123",
        )
    )

    provider = SpotifyProvider(client)

    result = await provider.get_track(
        " spotify-track-123 ",
    )

    assert result is not None
    assert result.external_id == "spotify-track-123"
    assert result.provider is ProviderName.SPOTIFY
    assert client.track_calls == ["spotify-track-123"]


@pytest.mark.asyncio
async def test_get_track_returns_none_when_client_returns_none() -> None:
    client = FakeSpotifyClient(
        track_response=None,
    )

    provider = SpotifyProvider(client)

    result = await provider.get_track("missing-track")

    assert result is None


@pytest.mark.asyncio
async def test_get_track_returns_none_for_empty_id() -> None:
    client = FakeSpotifyClient()

    provider = SpotifyProvider(client)

    result = await provider.get_track("   ")

    assert result is None
    assert client.track_calls == []
