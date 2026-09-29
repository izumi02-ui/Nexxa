from abc import ABC, abstractmethod

from app.search.types import SearchQuery, SearchResult


class SearchProvider(ABC):
    """Interface for provider-independent music search."""

    @abstractmethod
    async def search(
        self,
        search_query: SearchQuery,
    ) -> list[SearchResult]:
        """Search for music using a normalized query."""
        raise NotImplementedError