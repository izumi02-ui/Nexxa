from dataclasses import dataclass

from app.providers.types import ProviderName, ProviderTrack


@dataclass(frozen=True)
class ResolvedSource:
    """Resolved playback source for a canonical NEXXA track."""

    provider: ProviderName
    external_id: str
    url: str


class SourceResolutionError(Exception):
    """Raised when a playable source cannot be resolved."""


class SourceResolver:
    """Resolves provider metadata into a playable source."""

    def resolve(self, track: ProviderTrack) -> ResolvedSource:
        if not track.external_id.strip():
            raise SourceResolutionError(
                "Provider track does not contain an external ID."
            )

        if not track.external_url:
            raise SourceResolutionError(
                "Provider track does not contain a playable external URL."
            )

        return ResolvedSource(
            provider=track.provider,
            external_id=track.external_id,
            url=track.external_url,
        )