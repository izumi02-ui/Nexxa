from app.providers.spotify.provider import SpotifyProvider
from app.providers.types import ProviderName


def make_spotify_track(
    track_id: str = "track-1",
    title: str = "Test Track",
    artist: str = "Test Artist",
    album: str = "Test Album",
    duration_ms: int = 180000,
    artwork_url: str | None = "https://i.scdn.co/image/test",
    external_url: str | None = "https://open.spotify.com/track/track-1",
) -> dict:
    return {
        "id": track_id,
        "name": title,
        "artists": [
            {
                "name": artist,
            }
        ],
        "album": {
            "name": album,
            "images": (
                [{"url": artwork_url}]
                if artwork_url is not None
                else []
            ),
        },
        "duration_ms": duration_ms,
        "external_urls": {
            "spotify": external_url,
        },
    }


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

        if not self.search_responses:
            return {
                "tracks": {
                    "items": [],
                    "total": 0,
                    "limit": limit,
                    "offset": offset,
                }
            }

        index = len(self.search_calls) - 1

        if index >= len(self.search_responses):
            return self.search_responses[-1]

        return self.search_responses[index]

    async def get_track(self, external_id: str) -> dict:
        self.track_calls.append(external_id)

        if self.track_response is None:
            return {}

        return self.track_response


def make_search_response(items: list[dict]) -> dict:
    return {
        "tracks": {
            "items": items,
            "total": len(items),
            "limit": len(items),
            "offset": 0,
        }
    }


def test_provider_name() -> None:
    provider = SpotifyProvider(FakeSpotifyClient())

    assert provider.name == ProviderName.SPOTIFY


async def test_search_normalizes_spotify_track() -> None:
    client = FakeSpotifyClient(
        search_responses=[
            make_search_response(
                [
                    make_spotify_track(),
                ]
            )
        ]
    )

    provider = SpotifyProvider(client)

    tracks = await provider.search_tracks(
        query="test track",
        limit=1,
    )

    assert len(tracks) == 1

    track = tracks[0]

    assert track.provider == ProviderName.SPOTIFY
    assert track.external_id == "track-1"
    assert track.title == "Test Track"
    assert track.artist_name == "Test Artist"
    assert track.album_name == "Test Album"
    assert track.duration_ms == 180000
    assert track.artwork_url == "https://i.scdn.co/image/test"
    assert track.external_url == "https://open.spotify.com/track/track-1"


async def test_search_paginates_until_requested_limit() -> None:
    first_page = [
        make_spotify_track(
            track_id=f"track-{index}",
            title=f"Track {index}",
        )
        for index in range(10)
    ]

    second_page = [
        make_spotify_track(
            track_id=f"track-{index}",
            title=f"Track {index}",
        )
        for index in range(10, 20)
    ]

    client = FakeSpotifyClient(
        search_responses=[
            make_search_response(first_page),
            make_search_response(second_page),
        ]
    )

    provider = SpotifyProvider(client)

    tracks = await provider.search_tracks(
        query="test",
        limit=20,
    )

    assert len(tracks) == 20

    assert client.search_calls == [
        {
            "query": "test",
            "limit": 10,
            "offset": 0,
        },
        {
            "query": "test",
            "limit": 10,
            "offset": 10,
        },
    ]


async def test_search_stops_when_page_has_fewer_results() -> None:
    first_page = [
        make_spotify_track(
            track_id=f"track-{index}",
        )
        for index in range(5)
    ]

    client = FakeSpotifyClient(
        search_responses=[
            make_search_response(first_page),
        ]
    )

    provider = SpotifyProvider(client)

    tracks = await provider.search_tracks(
        query="test",
        limit=20,
    )

    assert len(tracks) == 5

    assert len(client.search_calls) == 1


async def test_search_returns_empty_for_blank_query() -> None:
    client = FakeSpotifyClient()

    provider = SpotifyProvider(client)

    tracks = await provider.search_tracks(
        query="   ",
        limit=20,
    )

    assert tracks == []
    assert client.search_calls == []


async def test_search_handles_non_positive_limit() -> None:
    client = FakeSpotifyClient(
        search_responses=[
            make_search_response(
                [
                    make_spotify_track(),
                ]
            )
        ]
    )

    provider = SpotifyProvider(client)

    tracks = await provider.search_tracks(
        query="test",
        limit=0,
    )

    assert len(tracks) == 1


async def test_search_skips_invalid_track() -> None:
    invalid_track = {
        "id": "",
        "name": "",
        "artists": [],
    }

    valid_track = make_spotify_track(
        track_id="valid-track",
    )

    client = FakeSpotifyClient(
        search_responses=[
            make_search_response(
                [
                    invalid_track,
                    valid_track,
                ]
            )
        ]
    )

    provider = SpotifyProvider(client)

    tracks = await provider.search_tracks(
        query="test",
        limit=10,
    )

    assert len(tracks) == 1
    assert tracks[0].external_id == "valid-track"


async def test_search_handles_missing_artwork() -> None:
    track = make_spotify_track(
        artwork_url=None,
    )

    client = FakeSpotifyClient(
        search_responses=[
            make_search_response([track]),
        ]
    )

    provider = SpotifyProvider(client)

    tracks = await provider.search_tracks(
        query="test",
        limit=1,
    )

    assert len(tracks) == 1
    assert tracks[0].artwork_url is None


async def test_get_track() -> None:
    client = FakeSpotifyClient(
        track_response=make_spotify_track(
            track_id="track-42",
            title="Requested Track",
        )
    )

    provider = SpotifyProvider(client)

    track = await provider.get_track("track-42")

    assert track is not None
    assert track.external_id == "track-42"
    assert track.title == "Requested Track"
    assert track.artwork_url == "https://i.scdn.co/image/test"

    assert client.track_calls == ["track-42"]


async def test_get_track_returns_none_for_missing_response() -> None:
    client = FakeSpotifyClient(
        track_response=None,
    )

    provider = SpotifyProvider(client)

    track = await provider.get_track("track-42")

    assert track is None


async def test_get_track_returns_none_for_empty_id() -> None:
    client = FakeSpotifyClient()

    provider = SpotifyProvider(client)

    track = await provider.get_track("   ")

    assert track is None
    assert client.track_calls == []
