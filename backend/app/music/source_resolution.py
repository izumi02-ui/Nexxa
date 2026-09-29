from dataclasses import dataclass

from app.providers.types import ProviderName


@dataclass(frozen=True)
class SourceReference:
    """Provider-specific reference for resolving a playable source."""

    provider: ProviderName
    external_id: str


@dataclass(frozen=True)
class ResolvedSource:
    """Resolved source information for playback."""

    provider: ProviderName
    external_id: str
    stream_url: str
    expires_at: int | None = None


class SourceResolver:
    """Base source-resolution abstraction."""

    async def resolve(
        self,
        source: SourceReference,
    ) -> ResolvedSource | None:
        """
        Resolve a provider reference into a playable source.

        Provider-specific implementations are added in Phase 3.
        """
        raise NotImplementedError