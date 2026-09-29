from app.providers.base import MusicProvider
from app.providers.types import ProviderName


class ProviderRegistry:
    """Registry for available NEXXA music providers."""

    def __init__(self) -> None:
        self._providers: dict[ProviderName, MusicProvider] = {}

    def register(self, provider: MusicProvider) -> None:
        self._providers[provider.name] = provider

    def get(self, name: ProviderName) -> MusicProvider | None:
        return self._providers.get(name)

    def all(self) -> list[MusicProvider]:
        return list(self._providers.values())