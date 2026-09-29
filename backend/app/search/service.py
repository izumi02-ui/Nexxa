import logging

from app.errors.exceptions import ProviderUnavailableError
from app.providers.registry import ProviderRegistry
from app.providers.types import ProviderName, ProviderTrack
from app.search.types import SearchQuery, SearchResult

logger = logging.getLogger(__name__)


class SearchService:
    """Coordinates searches across registered music providers."""

    def __init__(self, registry: ProviderRegistry) -> None:
        self.registry = registry

    async def search_tracks(
        self,
        search: SearchQuery,
        providers: list[ProviderName] | None = None,
    ) -> SearchResult:
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
            else [provider.name for provider in self.registry.all()]
        )

        if not selected_providers:
            raise ProviderUnavailableError()

        collected: list[ProviderTrack] = []
        successful_providers = 0
        failed_providers: list[ProviderName] = []

        for provider_name in selected_providers:
            provider = self.registry.get(provider_name)

            if provider is None:
                failed_providers.append(provider_name)
                logger.warning(
                    "Requested provider is not registered: %s",
                    provider_name.value,
                )
                continue

            try:
                results = await provider.search_tracks(
                    query=query,
                    limit=search.limit,
                )
            except Exception:
                failed_providers.append(provider_name)
                logger.exception(
                    "Provider search failed: %s",
                    provider_name.value,
                )
                continue

            successful_providers += 1
            collected.extend(results)

        if successful_providers == 0:
            raise ProviderUnavailableError(
                "No selected music provider is currently available."
            )

        total = len(collected)
        start = search.offset
        end = start + search.limit

        return SearchResult(
            tracks=collected[start:end],
            total=total,
            offset=search.offset,
            limit=search.limit,
        )
