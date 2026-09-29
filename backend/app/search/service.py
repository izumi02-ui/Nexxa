from app.providers.registry import ProviderRegistry
from app.providers.types import ProviderName, ProviderTrack
from app.search.types import SearchQuery, SearchResult


class SearchService:
    """Coordinates track searches across registered providers."""

    def __init__(self, registry: ProviderRegistry) -> None:
        self.registry = registry

    async def search_tracks(
        self,
        search: SearchQuery,
        providers: list[ProviderName] | None = None,
    ) -> SearchResult:
        """Search registered providers and return normalized results."""

        if not search.query.strip():
            return SearchResult(
                tracks=[],
                total=0,
                offset=search.offset,
                limit=search.limit,
            )

        selected_providers = (
            providers
            if providers is not None
            else [provider.name for provider in self.registry.all()]
        )

        collected: list[ProviderTrack] = []

        for provider_name in selected_providers:
            provider = self.registry.get(provider_name)

            if provider is None:
                continue

            requested_limit = search.offset + search.limit

            results = await provider.search_tracks(
                query=search.query,
                limit=requested_limit,
            )

            collected.extend(results)

        total = len(collected)

        start = search.offset
        end = start + search.limit

        return SearchResult(
            tracks=collected[start:end],
            total=total,
            offset=search.offset,
            limit=search.limit,
        )