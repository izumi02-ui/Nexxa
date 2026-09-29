from abc import ABC, abstractmethod

from app.providers.types import ProviderName, ProviderTrack


class MusicProvider(ABC):
    """Base interface for all NEXXA music providers."""

    @property
    @abstractmethod
    def name(self) -> ProviderName:
        """Return the provider identifier."""
        raise NotImplementedError

    @abstractmethod
    async def search_tracks(
        self,
        query: str,
        limit: int = 20,
    ) -> list[ProviderTrack]:
        """Search for tracks using the provider."""
        raise NotImplementedError

    @abstractmethod
    async def get_track(
        self,
        external_id: str,
    ) -> ProviderTrack | None:
        """Retrieve one track by its provider-specific ID."""
        raise NotImplementedError