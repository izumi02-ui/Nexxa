from abc import ABC, abstractmethod

from app.providers.types import ProviderTrack


class SearchProvider(ABC):
    """Provider interface for NEXXA search operations."""

    @abstractmethod
    async def search_tracks(
        self,
        query: str,
        limit: int = 20,
    ) -> list[ProviderTrack]:
        """Search for tracks using a provider."""
        raise NotImplementedError