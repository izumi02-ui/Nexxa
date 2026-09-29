from app.providers.base import MusicProvider
from app.providers.types import ProviderName, ProviderTrack
from app.providers.youtube_music.client import YouTubeMusicClient


class YouTubeMusicProvider(MusicProvider):
    """NEXXA provider boundary for YouTube Music."""

    def __init__(self, client: YouTubeMusicClient) -> None:
        self.client = client

    @property
    def name(self) -> ProviderName:
        return ProviderName.YOUTUBE_MUSIC

    async def search_tracks(
        self,
        query: str,
        limit: int = 20,
    ) -> list[ProviderTrack]:
        results = await self.client.search_tracks(
            query=query,
            limit=limit,
        )

        return [
            ProviderTrack(
                provider=ProviderName.YOUTUBE_MUSIC,
                external_id=result["external_id"],
                title=result["title"],
                artist_name=result["artist_name"],
                album_name=result.get("album_name"),
                duration_ms=result.get("duration_ms"),
                artwork_url=result.get("artwork_url"),
                external_url=result.get("external_url"),
            )
            for result in results
        ]

    async def get_track(
        self,
        external_id: str,
    ) -> ProviderTrack | None:
        result = await self.client.get_track(external_id)

        if result is None:
            return None

        return ProviderTrack(
            provider=ProviderName.YOUTUBE_MUSIC,
            external_id=result["external_id"],
            title=result["title"],
            artist_name=result["artist_name"],
            album_name=result.get("album_name"),
            duration_ms=result.get("duration_ms"),
            artwork_url=result.get("artwork_url"),
            external_url=result.get("external_url"),
        )
