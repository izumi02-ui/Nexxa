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


def make_registry() -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register(FakeSpotifyProvider())
    return registry


def test_search_api_uses_provider_registry() -> None:
    with TestClient(app) as client:
        app.state.provider_registry = make_registry()

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


def test_search_api_accepts_pagination_parameters() -> None:
    with TestClient(app) as client:
        app.state.provider_registry = make_registry()

        response = client.get(
            "/api/v1/search",
            params={
                "query": "test",
                "limit": 10,
                "offset": 5,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["limit"] == 10
    assert data["offset"] == 5


def test_search_api_rejects_empty_query() -> None:
    with TestClient(app) as client:
        app.state.provider_registry = make_registry()

        response = client.get(
            "/api/v1/search",
            params={"query": ""},
        )

    assert response.status_code == 422


def test_search_api_rejects_query_longer_than_500_characters() -> None:
    with TestClient(app) as client:
        app.state.provider_registry = make_registry()

        response = client.get(
            "/api/v1/search",
            params={"query": "a" * 501},
        )

    assert response.status_code == 422


def test_search_api_rejects_zero_limit() -> None:
    with TestClient(app) as client:
        app.state.provider_registry = make_registry()

        response = client.get(
            "/api/v1/search",
            params={
                "query": "test",
                "limit": 0,
            },
        )

    assert response.status_code == 422


def test_search_api_rejects_limit_above_50() -> None:
    with TestClient(app) as client:
        app.state.provider_registry = make_registry()

        response = client.get(
            "/api/v1/search",
            params={
                "query": "test",
                "limit": 51,
            },
        )

    assert response.status_code == 422


def test_search_api_rejects_negative_offset() -> None:
    with TestClient(app) as client:
        app.state.provider_registry = make_registry()

        response = client.get(
            "/api/v1/search",
            params={
                "query": "test",
                "offset": -1,
            },
        )

    assert response.status_code == 422


def test_search_api_returns_503_without_providers() -> None:
    with TestClient(app) as client:
        app.state.provider_registry = ProviderRegistry()

        response = client.get(
            "/api/v1/search",
            params={"query": "test"},
        )

    assert response.status_code == 503

    data = response.json()

    assert data["error"]["code"] == "PROVIDER_UNAVAILABLE"
    assert (
        data["error"]["message"]
        == "No music provider is currently available."
    )
