import pytest

from app.errors.exceptions import ProviderUnavailableError
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
                external_id="youtube-1",
                title="Test Track",
                artist_name="Test Artist",
                album_name="Test Album",
                duration_ms=180000,
                artwork_url="https://example.com/artwork.jpg",
                external_url="https://youtube.com/watch?v=youtube-1",
            )
        ]


@pytest.mark.asyncio
async def test_provider_failure_does_not_break_other_providers() -> None:
    registry = ProviderRegistry()
    registry.register(FailingSpotifyProvider())
    registry.register(WorkingYouTubeProvider())

    service = SearchService(registry)

    result = await service.search_tracks(
        SearchQuery(
            query="test",
            limit=20,
            offset=0,
        )
    )

    assert result.total == 1
    assert len(result.tracks) == 1
    assert result.tracks[0].provider == ProviderName.YOUTUBE
    assert result.tracks[0].title == "Test Track"


@pytest.mark.asyncio
async def test_search_returns_results_when_only_working_provider_exists() -> None:
    registry = ProviderRegistry()
    registry.register(WorkingYouTubeProvider())

    service = SearchService(registry)

    result = await service.search_tracks(
        SearchQuery(
            query="test",
            limit=20,
            offset=0,
        )
    )

    assert result.total == 1
    assert result.tracks[0].external_id == "youtube-1"
    assert result.tracks[0].artwork_url == "https://example.com/artwork.jpg"


@pytest.mark.asyncio
async def test_search_raises_when_all_providers_fail() -> None:
    registry = ProviderRegistry()
    registry.register(FailingSpotifyProvider())

    service = SearchService(registry)

    with pytest.raises(ProviderUnavailableError) as exc_info:
        await service.search_tracks(
            SearchQuery(
                query="test",
                limit=20,
                offset=0,
            )
        )

    assert exc_info.value.code == "PROVIDER_UNAVAILABLE"


@pytest.mark.asyncio
async def test_search_raises_when_no_providers_are_registered() -> None:
    registry = ProviderRegistry()
    service = SearchService(registry)

    with pytest.raises(ProviderUnavailableError) as exc_info:
        await service.search_tracks(
            SearchQuery(
                query="test",
                limit=20,
                offset=0,
            )
        )

    assert exc_info.value.code == "PROVIDER_UNAVAILABLE"


@pytest.mark.asyncio
async def test_search_returns_empty_for_blank_query() -> None:
    registry = ProviderRegistry()
    registry.register(WorkingYouTubeProvider())

    service = SearchService(registry)

    result = await service.search_tracks(
        SearchQuery(
            query="   ",
            limit=20,
            offset=0,
        )
    )

    assert result.total == 0
    assert result.tracks == []
