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
        """Search selected providers and apply deterministic pagination."""

        query = search.query.strip()

        if not query:
            return SearchResult(
                tracks=[],
                total=0,
                offset=search.offset,
                limit=search.limit,
            )

        selected_providers = (
            providers
            if providers is not None
            else [
                provider.name
                for provider in self.registry.all()
            ]
        )

        collected: list[ProviderTrack] = []

        for provider_name in selected_providers:
            provider = self.registry.get(provider_name)

            if provider is None:
                continue

            results = await provider.search_tracks(
                query=query,
                limit=search.limit,
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