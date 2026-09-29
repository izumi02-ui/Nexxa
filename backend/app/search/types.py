from dataclasses import dataclass

from app.providers.types import ProviderName


@dataclass(frozen=True)
class SearchQuery:
    """Normalized search request."""

    query: str
    limit: int = 20
    offset: int = 0


@dataclass(frozen=True)
class SearchResult:
    """Normalized search result from a music provider."""

    provider: ProviderName
    external_id: str
    title: str
    artist_name: str
    album_name: str | None = None
    duration_ms: int | None = None
    external_url: str | None = None