from dataclasses import dataclass
from time import monotonic

import httpx


SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"


class SpotifyAPIError(Exception):
    """Raised when a Spotify API operation fails."""


@dataclass(frozen=True)
class SpotifyToken:
    """Spotify access token information."""

    access_token: str
    expires_in: int


class SpotifyClient:
    """Low-level asynchronous client for the Spotify Web API."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret

        self._access_token: str | None = None
        self._token_expires_at: float = 0.0

    async def get_access_token(self) -> str:
        """Return a cached access token or request a new one."""

        now = monotonic()

        if (
            self._access_token is not None
            and now < self._token_expires_at
        ):
            return self._access_token

        token = await self.get_client_credentials_token()

        self._access_token = token.access_token
        self._token_expires_at = (
            now + max(token.expires_in - 60, 1)
        )

        return self._access_token

    async def get_client_credentials_token(
        self,
    ) -> SpotifyToken:
        """Request an application access token from Spotify."""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    SPOTIFY_TOKEN_URL,
                    data={
                        "grant_type": "client_credentials",
                    },
                    auth=(
                        self.client_id,
                        self.client_secret,
                    ),
                    timeout=15.0,
                )
        except httpx.HTTPError as exc:
            raise SpotifyAPIError(
                "Unable to connect to Spotify token service."
            ) from exc

        if response.status_code != 200:
            raise SpotifyAPIError(
                "Spotify token request failed with status "
                f"{response.status_code}."
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise SpotifyAPIError(
                "Spotify returned invalid token response data."
            ) from exc

        access_token = data.get("access_token")
        expires_in = data.get("expires_in")

        if not access_token:
            raise SpotifyAPIError(
                "Spotify token response is missing an access token."
            )

        if not isinstance(expires_in, int) or expires_in <= 0:
            raise SpotifyAPIError(
                "Spotify token response contains an invalid expiration."
            )

        return SpotifyToken(
            access_token=access_token,
            expires_in=expires_in,
        )

    async def search_tracks(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
    ) -> dict:
        """Search Spotify's catalog for tracks."""

        query = query.strip()

        if not query:
            return {
                "tracks": {
                    "items": [],
                    "total": 0,
                    "limit": limit,
                    "offset": offset,
                }
            }

        limit = min(max(limit, 1), 10)
        offset = max(offset, 0)

        access_token = await self.get_access_token()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{SPOTIFY_API_BASE_URL}/search",
                    params={
                        "q": query,
                        "type": "track",
                        "limit": limit,
                        "offset": offset,
                    },
                    headers={
                        "Authorization": f"Bearer {access_token}",
                    },
                    timeout=15.0,
                )
        except httpx.HTTPError as exc:
            raise SpotifyAPIError(
                "Unable to connect to Spotify search service."
            ) from exc

        if response.status_code != 200:
            raise SpotifyAPIError(
                "Spotify search request failed with status "
                f"{response.status_code}."
            )

        try:
            return response.json()
        except ValueError as exc:
            raise SpotifyAPIError(
                "Spotify returned invalid search response data."
            ) from exc

    async def get_track(
        self,
        external_id: str,
    ) -> dict:
        """Retrieve one Spotify track by ID."""

        external_id = external_id.strip()

        if not external_id:
            raise SpotifyAPIError(
                "Spotify track ID cannot be empty."
            )

        access_token = await self.get_access_token()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{SPOTIFY_API_BASE_URL}/tracks/{external_id}",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                    },
                    timeout=15.0,
                )
        except httpx.HTTPError as exc:
            raise SpotifyAPIError(
                "Unable to connect to Spotify track service."
            ) from exc

        if response.status_code != 200:
            raise SpotifyAPIError(
                "Spotify track request failed with status "
                f"{response.status_code}."
            )

        try:
            return response.json()
        except ValueError as exc:
            raise SpotifyAPIError(
                "Spotify returned invalid track response data."
            ) from exc