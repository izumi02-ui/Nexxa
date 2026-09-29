from app.providers.base import MusicProvider
from app.search.types import SearchQuery, SearchResult


class SearchService:
    """Coordinates normalized search across registered providers."""

    def __init__(
        self,
        providers: list[MusicProvider],
    ) -> None:
        self._providers = providers

    async def search(
        self,
        search_query: SearchQuery,
    ) -> list[SearchResult]:
        results: list[SearchResult] = []

        for provider in self._providers:
            tracks = await provider.search_tracks(
                query=search_query.query,
                limit=search_query.limit,
            )

            for track in tracks:
                results.append(
                    SearchResult(
                        provider=track.provider,
                        external_id=track.external_id,
                        title=track.title,
                        artist_name=track.artist_name,
                        album_name=track.album_name,
                        duration_ms=track.duration_ms,
                        external_url=track.external_url,
                    )
                )

        return results