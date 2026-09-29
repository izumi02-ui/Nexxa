from app.providers.base import MusicProvider
from app.providers.spotify.client import SpotifyClient
from app.providers.types import ProviderName, ProviderTrack


class SpotifyProvider(MusicProvider):
    """NEXXA adapter for the Spotify Web API."""

    def __init__(
        self,
        client: SpotifyClient,
    ) -> None:
        self.client = client

    @property
    def name(self) -> ProviderName:
        return ProviderName.SPOTIFY

    async def search_tracks(
        self,
        query: str,
        limit: int = 20,
    ) -> list[ProviderTrack]:
        """Search Spotify and normalize results."""

        response = await self.client.search_tracks(
            query=query,
            limit=min(limit, 10),
        )

        items = response.get("tracks", {}).get("items", [])

        return [
            self._normalize_track(item)
            for item in items
        ]

    async def get_track(
        self,
        external_id: str,
    ) -> ProviderTrack | None:
        """Retrieve and normalize one Spotify track."""

        if not external_id.strip():
            return None

        response = await self.client.get_track(
            external_id=external_id,
        )

        if not response:
            return None

        return self._normalize_track(response)

    @staticmethod
    def _normalize_track(
        item: dict,
    ) -> ProviderTrack:
        artists = item.get("artists") or []

        artist_name = (
            artists[0].get("name", "")
            if artists
            else ""
        )

        album = item.get("album") or {}

        return ProviderTrack(
            provider=ProviderName.SPOTIFY,
            external_id=item.get("id", ""),
            title=item.get("name", ""),
            artist_name=artist_name,
            album_name=album.get("name"),
            duration_ms=item.get("duration_ms"),
            external_url=(
                (item.get("external_urls") or {}).get("spotify")
            ),
        )