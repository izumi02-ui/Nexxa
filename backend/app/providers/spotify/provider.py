from app.providers.base import MusicProvider
from app.providers.spotify.client import SpotifyClient
from app.providers.types import ProviderName, ProviderTrack


class SpotifyProvider(MusicProvider):
    """NEXXA adapter for the Spotify Web API."""

    _MAX_RESULTS_PER_REQUEST = 10

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
        """Search Spotify and normalize the requested number of results."""

        query = query.strip()

        if not query or limit <= 0:
            return []

        results: list[ProviderTrack] = []
        offset = 0

        while len(results) < limit:
            request_limit = min(
                self._MAX_RESULTS_PER_REQUEST,
                limit - len(results),
            )

            response = await self.client.search_tracks(
                query=query,
                limit=request_limit,
                offset=offset,
            )

            items = response.get("tracks", {}).get("items", [])

            if not items:
                break

            for item in items:
                try:
                    results.append(
                        self._normalize_track(item)
                    )
                except ValueError:
                    continue

                if len(results) >= limit:
                    break

            offset += len(items)

            if len(items) < request_limit:
                break

        return results

    async def get_track(
        self,
        external_id: str,
    ) -> ProviderTrack | None:
        """Retrieve and normalize one Spotify track."""

        external_id = external_id.strip()

        if not external_id:
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
        external_id = str(item.get("id") or "").strip()
        title = str(item.get("name") or "").strip()

        if not external_id:
            raise ValueError(
                "Spotify track is missing an external ID."
            )

        if not title:
            raise ValueError(
                "Spotify track is missing a title."
            )

        artists = item.get("artists") or []

        artist_name = ""

        if artists:
            artist_name = str(
                artists[0].get("name") or ""
            ).strip()

        if not artist_name:
            raise ValueError(
                "Spotify track is missing an artist."
            )

        album = item.get("album") or {}

        album_name = album.get("name")

        if album_name is not None:
            album_name = str(album_name).strip() or None

        external_urls = item.get("external_urls") or {}

        external_url = external_urls.get("spotify")

        if external_url is not None:
            external_url = str(external_url).strip() or None

        duration_ms = item.get("duration_ms")

        if duration_ms is not None:
            try:
                duration_ms = int(duration_ms)
            except (TypeError, ValueError):
                duration_ms = None

        return ProviderTrack(
            provider=ProviderName.SPOTIFY,
            external_id=external_id,
            title=title,
            artist_name=artist_name,
            album_name=album_name,
            duration_ms=duration_ms,
            external_url=external_url,
        )