import pytest

from app.providers.base import MusicProvider
from app.providers.registry import ProviderRegistry
from app.providers.types import ProviderName, ProviderTrack
from app.search.service import SearchService
from app.search.types import SearchQuery


class FailingSpotifyProvider(MusicProvider):
    @property
    def name(self) -> ProviderName:
        return ProviderName.SPOTIFY

    async def search_tracks(
        self,
        query: str,
        limit: int = 20,
    ) -> list[ProviderTrack]:
        raise RuntimeError("Spotify is unavailable")

    async def get_track(
        self,
        external_id: str,
    ) -> ProviderTrack | None:
        return None


class WorkingYouTubeProvider(MusicProvider):
    @property
    def name(self) -> ProviderName:
        return ProviderName.YOUTUBE

    async def search_tracks(
        self,
        query: str,
        limit: int = 20,
    ) -> list[ProviderTrack]:
        return [
            ProviderTrack(
                provider=ProviderName.YOUTUBE,
                external_id="youtube-test-1",
                title="Working Result",
                artist_name="Test Artist",
                album_name="Test Album",
                duration_ms=180000,
                artwork_url="https://example.com/artwork.jpg",
                external_url="https://youtube.com/watch?v=test",
            )
        ]

    async def get_track(
        self,
        external_id: str,
    ) -> ProviderTrack | None:
        return None


@pytest.mark.asyncio
async def test_provider_failure_does_not_break_other_providers() -> None:
    registry = ProviderRegistry()

    registry.register(FailingSpotifyProvider())
    registry.register(WorkingYouTubeProvider())

    service = SearchService(registry)

    result = await service.search_tracks(
        SearchQuery(
            query="test song",
            limit=20,
        )
    )

    assert result.total == 1
    assert len(result.tracks) == 1

    track = result.tracks[0]

    assert track.provider is ProviderName.YOUTUBE
    assert track.external_id == "youtube-test-1"
    assert track.title == "Working Result"


@pytest.mark.asyncio
async def test_search_returns_results_when_only_working_provider_exists() -> None:
    registry = ProviderRegistry()

    registry.register(WorkingYouTubeProvider())

    service = SearchService(registry)

    result = await service.search_tracks(
        SearchQuery(
            query="test song",
            limit=20,
        )
    )

    assert result.total == 1
    assert len(result.tracks) == 1


@pytest.mark.asyncio
async def test_search_returns_empty_when_all_providers_fail() -> None:
    registry = ProviderRegistry()

    registry.register(FailingSpotifyProvider())

    service = SearchService(registry)

    result = await service.search_tracks(
        SearchQuery(
            query="test song",
            limit=20,
        )
    )

    assert result.tracks == []
    assert result.total == 0
