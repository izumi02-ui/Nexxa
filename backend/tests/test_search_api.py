from fastapi.testclient import TestClient

from app.main import app
from app.providers.base import MusicProvider
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
                external_url="https://open.spotify.com/track/spotify-test-1",
            )
        ]

    async def get_track(
        self,
        external_id: str,
    ) -> ProviderTrack | None:
        return None


def test_search_api_uses_provider_registry() -> None:
    from app.providers.registry import ProviderRegistry

    registry = ProviderRegistry()
    registry.register(FakeSpotifyProvider())

    app.state.provider_registry = registry

    with TestClient(app) as client:
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