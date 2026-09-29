from dataclasses import dataclass

from app.providers.types import ProviderTrack


@dataclass(frozen=True)
class SearchQuery:
    """Normalized search request."""

    query: str
    limit: int = 20
    offset: int = 0


@dataclass(frozen=True)
class SearchResult:
    """Normalized search response."""

    tracks: list[ProviderTrack]
    total: int
    offset: int
    limit: int