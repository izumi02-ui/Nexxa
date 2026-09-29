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
        raise RuntimeError("spotify failure")

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
                external_id="youtube-1",
                title="YouTube Track",
                artist_name="YouTube Artist",
                album_name=None,
                duration_ms=200000,
                artwork_url="https://example.com/youtube.jpg",
                external_url="https://youtube.com/watch?v=youtube-1",
            )
        ]

    async def get_track(
        self,
        external_id: str,
    ) -> ProviderTrack | None:
        return None


@pytest.mark.asyncio
async def test_search_service_returns_provider_results() -> None:
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
    assert len(result.tracks) == 1
    assert result.tracks[0].provider is ProviderName.YOUTUBE
    assert result.tracks[0].external_id == "youtube-1"


@pytest.mark.asyncio
async def test_search_service_isolates_failed_provider() -> None:
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
    assert result.tracks[0].provider is ProviderName.YOUTUBE


@pytest.mark.asyncio
async def test_search_service_raises_when_all_providers_fail() -> None:
    registry = ProviderRegistry()
    registry.register(FailingSpotifyProvider())

    service = SearchService(registry)

    with pytest.raises(ProviderUnavailableError):
        await service.search_tracks(
            SearchQuery(
                query="test",
                limit=20,
                offset=0,
            )
        )


@pytest.mark.asyncio
async def test_search_service_returns_empty_for_blank_query() -> None:
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


@pytest.mark.asyncio
async def test_search_service_can_select_specific_provider() -> None:
    registry = ProviderRegistry()
    registry.register(FailingSpotifyProvider())
    registry.register(WorkingYouTubeProvider())

    service = SearchService(registry)

    result = await service.search_tracks(
        SearchQuery(
            query="test",
            limit=20,
            offset=0,
        ),
        providers=[ProviderName.YOUTUBE],
    )

    assert result.total == 1
    assert result.tracks[0].provider is ProviderName.YOUTUBE


@pytest.mark.asyncio
async def test_search_service_raises_when_selected_provider_is_missing() -> None:
    registry = ProviderRegistry()

    service = SearchService(registry)

    with pytest.raises(ProviderUnavailableError):
        await service.search_tracks(
            SearchQuery(
                query="test",
                limit=20,
                offset=0,
            ),
            providers=[ProviderName.SPOTIFY],
        )
