from app.providers.base import MusicProvider
from app.providers.spotify.client import SpotifyAPIError, SpotifyClient
from app.providers.types import ProviderName, ProviderTrack


class SpotifyProvider(MusicProvider):
    """Spotify implementation of the NEXXA music provider interface."""

    _MAX_RESULTS_PER_REQUEST = 10

    def __init__(self, client: SpotifyClient) -> None:
        self.client = client

    @property
    def name(self) -> ProviderName:
        return ProviderName.SPOTIFY

    async def search_tracks(
        self,
        query: str,
        limit: int = 20,
    ) -> list[ProviderTrack]:
        query = query.strip()

        if not query:
            return []

        limit = max(limit, 1)

        normalized_tracks: list[ProviderTrack] = []
        offset = 0

        while len(normalized_tracks) < limit:
            remaining = limit - len(normalized_tracks)

            request_limit = min(
                remaining,
                self._MAX_RESULTS_PER_REQUEST,
            )

            response = await self.client.search_tracks(
                query=query,
                limit=request_limit,
                offset=offset,
            )

            tracks = response.get("tracks")

            if not isinstance(tracks, dict):
                raise SpotifyAPIError(
                    "Spotify search response is missing track data."
                )

            items = tracks.get("items")

            if not isinstance(items, list):
                raise SpotifyAPIError(
                    "Spotify search response contains invalid track items."
                )

            if not items:
                break

            total = tracks.get("total")

            for item in items:
                if not isinstance(item, dict):
                    continue

                try:
                    normalized_tracks.append(
                        self._normalize_track(item)
                    )
                except SpotifyAPIError:
                    # Ignore malformed provider records instead of
                    # allowing one bad result to break the entire search.
                    continue

                if len(normalized_tracks) >= limit:
                    break

            offset += len(items)

            if len(normalized_tracks) >= limit:
                break

            if isinstance(total, int) and total >= 0:
                if offset >= total:
                    break

        return normalized_tracks[:limit]

    async def get_track(
        self,
        external_id: str,
    ) -> ProviderTrack | None:
        external_id = external_id.strip()

        if not external_id:
            return None

        response = await self.client.get_track(external_id)

        if not response:
            return None

        return self._normalize_track(response)

    @staticmethod
    def _normalize_track(item: dict) -> ProviderTrack:
        external_id = item.get("id")

        if not isinstance(external_id, str) or not external_id.strip():
            raise SpotifyAPIError(
                "Spotify track response is missing a valid track ID."
            )

        title = item.get("name")

        if not isinstance(title, str) or not title.strip():
            raise SpotifyAPIError(
                "Spotify track response is missing a valid track title."
            )

        artists = item.get("artists")

        if not isinstance(artists, list) or not artists:
            raise SpotifyAPIError(
                "Spotify track response is missing artist data."
            )

        first_artist = artists[0]

        if not isinstance(first_artist, dict):
            raise SpotifyAPIError(
                "Spotify track response contains invalid artist data."
            )

        artist_name = first_artist.get("name")

        if not isinstance(artist_name, str) or not artist_name.strip():
            raise SpotifyAPIError(
                "Spotify track response is missing a valid artist name."
            )

        album_name: str | None = None
        artwork_url: str | None = None

        album = item.get("album")

        if isinstance(album, dict):
            raw_album_name = album.get("name")

            if isinstance(raw_album_name, str):
                album_name = raw_album_name.strip() or None

            images = album.get("images")

            if isinstance(images, list) and images:
                first_image = images[0]

                if isinstance(first_image, dict):
                    raw_url = first_image.get("url")

                    if isinstance(raw_url, str):
                        artwork_url = raw_url.strip() or None

        duration_ms = item.get("duration_ms")

        if duration_ms is not None:
            if not isinstance(duration_ms, int) or duration_ms < 0:
                duration_ms = None

        external_url: str | None = None

        external_urls = item.get("external_urls")

        if isinstance(external_urls, dict):
            raw_external_url = external_urls.get("spotify")

            if isinstance(raw_external_url, str):
                external_url = raw_external_url.strip() or None

        return ProviderTrack(
            provider=ProviderName.SPOTIFY,
            external_id=external_id.strip(),
            title=title.strip(),
            artist_name=artist_name.strip(),
            album_name=album_name,
            duration_ms=duration_ms,
            artwork_url=artwork_url,
            external_url=external_url,
        )
