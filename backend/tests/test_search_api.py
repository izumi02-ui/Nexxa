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
                external_id="spotify-test-1",
                title="Test Song",
                artist_name="Test Artist",
                album_name="Test Album",
                duration_ms=180000,
                artwork_url="https://i.scdn.co/image/test-artwork",
                external_url=(
                    "https://open.spotify.com/track/spotify-test-1"
                ),
            )
        ]

    async def get_track(
        self,
        external_id: str,
    ) -> ProviderTrack | None:
        return None


def make_registry() -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register(FakeSpotifyProvider())
    return registry


def test_search_api_uses_provider_registry() -> None:
    with TestClient(app) as client:
        app.state.provider_registry = make_registry()

        response = client.get(
            "/api/v1/search",
            params={
                "query": "Test Song",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["offset"] == 0
    assert data["limit"] == 20

    track = data["tracks"][0]

    assert track["provider"] == "spotify"
    assert track["external_id"] == "spotify-test-1"
    assert track["title"] == "Test Song"
    assert track["artist_name"] == "Test Artist"
    assert track["album_name"] == "Test Album"
    assert track["duration_ms"] == 180000
    assert track["artwork_url"] == (
        "https://i.scdn.co/image/test-artwork"
    )
    assert track["external_url"] == (
        "https://open.spotify.com/track/spotify-test-1"
    )


def test_search_api_accepts_pagination_parameters() -> None:
    with TestClient(app) as client:
        app.state.provider_registry = make_registry()

        response = client.get(
            "/api/v1/search",
            params={
                "query": "Test Song",
                "limit": 10,
                "offset": 5,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["offset"] == 5
    assert data["limit"] == 10


def test_search_api_rejects_empty_query() -> None:
    with TestClient(app) as client:
        app.state.provider_registry = make_registry()

        response = client.get(
            "/api/v1/search",
            params={
                "query": "",
            },
        )

    assert response.status_code == 422


def test_search_api_rejects_query_longer_than_500_characters() -> None:
    with TestClient(app) as client:
        app.state.provider_registry = make_registry()

        response = client.get(
            "/api/v1/search",
            params={
                "query": "x" * 501,
            },
        )

    assert response.status_code == 422


def test_search_api_rejects_invalid_limit() -> None:
    with TestClient(app) as client:
        app.state.provider_registry = make_registry()

        response = client.get(
            "/api/v1/search",
            params={
                "query": "Test Song",
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
                "query": "Test Song",
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
                "query": "Test Song",
                "offset": -1,
            },
        )

    assert response.status_code == 422


def test_search_api_returns_empty_results_without_providers() -> None:
    with TestClient(app) as client:
        app.state.provider_registry = ProviderRegistry()

        response = client.get(
            "/api/v1/search",
            params={
                "query": "Test Song",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["tracks"] == []
    assert data["total"] == 0
    assert data["offset"] == 0
    assert data["limit"] == 20
