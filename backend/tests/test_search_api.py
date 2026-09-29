from fastapi.testclient import TestClient

from app.main import app
from app.providers.base import MusicProvider
from app.providers.registry import ProviderRegistry
from app.providers.types import ProviderName, ProviderTrack


class FakeSpotifyProvider(MusicProvider):
    @property
    def name(self) -> ProviderName:
        return ProviderName.SPOTIFY

    async def search_tracks(
        self,
        query: str,
        limit: int = 20,
    ) -> list[ProviderTrack]:
        return [
            ProviderTrack(
                provider=ProviderName.SPOTIFY,
                external_id="spotify-1",
                title="Test Track",
                artist_name="Test Artist",
                album_name="Test Album",
                duration_ms=180000,
                artwork_url="https://example.com/artwork.jpg",
                external_url="https://open.spotify.com/track/spotify-1",
            )
        ]

    async def get_track(
        self,
        external_id: str,
    ) -> ProviderTrack | None:
        return None


def set_provider_registry(
    client: TestClient,
    registry: ProviderRegistry,
) -> None:
    client.app.state.provider_registry = registry


def test_search_returns_tracks() -> None:
    registry = ProviderRegistry()
    registry.register(FakeSpotifyProvider())

    with TestClient(app) as client:
        set_provider_registry(client, registry)

        response = client.get(
            "/api/v1/search",
            params={"query": "test"},
        )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["offset"] == 0
    assert data["limit"] == 20
    assert len(data["tracks"]) == 1

    track = data["tracks"][0]

    assert track["provider"] == "spotify"
    assert track["external_id"] == "spotify-1"
    assert track["title"] == "Test Track"
    assert track["artist_name"] == "Test Artist"
    assert track["album_name"] == "Test Album"
    assert track["duration_ms"] == 180000
    assert track["artwork_url"] == "https://example.com/artwork.jpg"
    assert (
        track["external_url"]
        == "https://open.spotify.com/track/spotify-1"
    )


def test_search_supports_limit_and_offset() -> None:
    registry = ProviderRegistry()
    registry.register(FakeSpotifyProvider())

    with TestClient(app) as client:
        set_provider_registry(client, registry)

        response = client.get(
            "/api/v1/search",
            params={
                "query": "test",
                "limit": 5,
                "offset": 0,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["limit"] == 5
    assert data["offset"] == 0


def test_search_rejects_empty_query() -> None:
    registry = ProviderRegistry()
    registry.register(FakeSpotifyProvider())

    with TestClient(app) as client:
        set_provider_registry(client, registry)

        response = client.get(
            "/api/v1/search",
            params={"query": ""},
        )

    assert response.status_code == 422


def test_search_rejects_invalid_limit() -> None:
    registry = ProviderRegistry()
    registry.register(FakeSpotifyProvider())

    with TestClient(app) as client:
        set_provider_registry(client, registry)

        response = client.get(
            "/api/v1/search",
            params={
                "query": "test",
                "limit": 0,
            },
        )

    assert response.status_code == 422


def test_search_rejects_invalid_offset() -> None:
    registry = ProviderRegistry()
    registry.register(FakeSpotifyProvider())

    with TestClient(app) as client:
        set_provider_registry(client, registry)

        response = client.get(
            "/api/v1/search",
            params={
                "query": "test",
                "offset": -1,
            },
        )

    assert response.status_code == 422


def test_search_returns_503_when_no_provider_is_available() -> None:
    registry = ProviderRegistry()

    with TestClient(app) as client:
        set_provider_registry(client, registry)

        response = client.get(
            "/api/v1/search",
            params={"query": "test"},
        )

    assert response.status_code == 503

    data = response.json()

    assert data["error"]["code"] == "PROVIDER_UNAVAILABLE"


def test_search_handles_provider_failure() -> None:
    class FailingProvider(MusicProvider):
        @property
        def name(self) -> ProviderName:
            return ProviderName.SPOTIFY

        async def search_tracks(
            self,
            query: str,
            limit: int = 20,
        ) -> list[ProviderTrack]:
            raise RuntimeError("provider failure")

        async def get_track(
            self,
            external_id: str,
        ) -> ProviderTrack | None:
            return None

    registry = ProviderRegistry()
    registry.register(FailingProvider())

    with TestClient(app) as client:
        set_provider_registry(client, registry)

        response = client.get(
            "/api/v1/search",
            params={"query": "test"},
        )

    assert response.status_code == 503

    data = response.json()

    assert data["error"]["code"] == "PROVIDER_UNAVAILABLE"
