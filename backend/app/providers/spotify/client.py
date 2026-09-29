from dataclasses import dataclass

import httpx


SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"


class SpotifyAPIError(Exception):
    """Raised when Spotify returns an API error."""


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

    async def get_client_credentials_token(self) -> SpotifyToken:
        """Request an application access token from Spotify."""

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

        if response.status_code != 200:
            raise SpotifyAPIError(
                f"Spotify token request failed with status "
                f"{response.status_code}."
            )

        data = response.json()

        return SpotifyToken(
            access_token=data["access_token"],
            expires_in=data["expires_in"],
        )

    async def search_tracks(
        self,
        access_token: str,
        query: str,
        limit: int = 10,
        offset: int = 0,
    ) -> dict:
        """Search Spotify's catalog for tracks."""

        if not query.strip():
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

        if response.status_code != 200:
            raise SpotifyAPIError(
                f"Spotify search request failed with status "
                f"{response.status_code}."
            )

        return response.json()

    async def get_track(
        self,
        access_token: str,
        external_id: str,
    ) -> dict:
        """Retrieve one Spotify track by ID."""

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SPOTIFY_API_BASE_URL}/tracks/{external_id}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
                timeout=15.0,
            )

        if response.status_code != 200:
            raise SpotifyAPIError(
                f"Spotify track request failed with status "
                f"{response.status_code}."
            )

        return response.json()