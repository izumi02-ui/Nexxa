import logging
from dataclasses import dataclass
from time import monotonic

import httpx


logger = logging.getLogger(__name__)


SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"


class SpotifyAPIError(Exception):
    """Base exception for Spotify API failures."""


class SpotifyAuthenticationError(SpotifyAPIError):
    """Raised when Spotify rejects authentication."""


class SpotifyNotFoundError(SpotifyAPIError):
    """Raised when a Spotify resource does not exist."""


class SpotifyRateLimitError(SpotifyAPIError):
    """Raised when Spotify rate-limits a request."""

    def __init__(
        self,
        message: str,
        retry_after: int | None = None,
    ) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class SpotifyServerError(SpotifyAPIError):
    """Raised when Spotify returns a server-side error."""


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
            logger.debug("Using cached Spotify access token.")
            return self._access_token

        logger.debug("Requesting a new Spotify access token.")

        token = await self.get_client_credentials_token()

        self._access_token = token.access_token
        self._token_expires_at = (
            now + max(token.expires_in - 60, 1)
        )

        logger.info("Spotify access token refreshed successfully.")

        return self._access_token

    async def get_client_credentials_token(
        self,
    ) -> SpotifyToken:
        """Request an application access token from Spotify."""

        logger.debug("Requesting Spotify client-credentials token.")

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
            logger.exception(
                "Spotify token service connection failed."
            )
            raise SpotifyAPIError(
                "Unable to connect to Spotify token service."
            ) from exc

        logger.debug(
            "Spotify token service responded with status %s.",
            response.status_code,
        )

        self._raise_for_status(
            response,
            operation="Spotify token request",
        )

        try:
            data = response.json()
        except ValueError as exc:
            logger.error(
                "Spotify token service returned invalid JSON."
            )
            raise SpotifyAPIError(
                "Spotify returned invalid token response data."
            ) from exc

        access_token = data.get("access_token")
        expires_in = data.get("expires_in")

        if not access_token:
            logger.error(
                "Spotify token response did not contain an access token."
            )
            raise SpotifyAPIError(
                "Spotify token response is missing an access token."
            )

        if not isinstance(expires_in, int) or expires_in <= 0:
            logger.error(
                "Spotify token response contained invalid expiration."
            )
            raise SpotifyAPIError(
                "Spotify token response contains an invalid expiration."
            )

        logger.debug(
            "Spotify token received with %s second expiration.",
            expires_in,
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
            logger.debug("Skipping Spotify search because query is empty.")
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

        logger.debug(
            "Searching Spotify tracks with limit=%s offset=%s.",
            limit,
            offset,
        )

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
            logger.exception("Spotify search request failed.")
            raise SpotifyAPIError(
                "Unable to connect to Spotify search service."
            ) from exc

        logger.debug(
            "Spotify search request completed with status %s.",
            response.status_code,
        )

        self._raise_for_status(
            response,
            operation="Spotify search request",
        )

        try:
            return response.json()
        except ValueError as exc:
            logger.error(
                "Spotify search service returned invalid JSON."
            )
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
            logger.debug(
                "Skipping Spotify track request because track ID is empty."
            )
            raise SpotifyAPIError(
                "Spotify track ID cannot be empty."
            )

        logger.debug("Requesting Spotify track metadata.")

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
            logger.exception("Spotify track request failed.")
            raise SpotifyAPIError(
                "Unable to connect to Spotify track service."
            ) from exc

        logger.debug(
            "Spotify track request completed with status %s.",
            response.status_code,
        )

        self._raise_for_status(
            response,
            operation="Spotify track request",
        )

        try:
            return response.json()
        except ValueError as exc:
            logger.error(
                "Spotify track service returned invalid JSON."
            )
            raise SpotifyAPIError(
                "Spotify returned invalid track response data."
            ) from exc

    @staticmethod
    def _raise_for_status(
        response: httpx.Response,
        operation: str,
    ) -> None:
        """Convert Spotify HTTP failures into typed exceptions."""

        status_code = response.status_code

        if status_code < 400:
            return

        logger.warning(
            "%s returned Spotify HTTP status %s.",
            operation,
            status_code,
        )

        if status_code in (401, 403):
            raise SpotifyAuthenticationError(
                f"{operation} was rejected by Spotify "
                f"with status {status_code}."
            )

        if status_code == 404:
            raise SpotifyNotFoundError(
                f"{operation} could not find the requested resource."
            )

        if status_code == 429:
            retry_after: int | None = None

            value = response.headers.get("Retry-After")

            if value is not None:
                try:
                    retry_after = max(int(value), 0)
                except ValueError:
                    logger.warning(
                        "Spotify returned an invalid Retry-After header."
                    )
                    retry_after = None

            logger.warning(
                "Spotify rate limit exceeded; retry_after=%s.",
                retry_after,
            )

            raise SpotifyRateLimitError(
                "Spotify rate limit exceeded.",
                retry_after=retry_after,
            )

        if 500 <= status_code <= 599:
            logger.error(
                "Spotify returned a server-side error: %s.",
                status_code,
            )
            raise SpotifyServerError(
                f"{operation} failed because Spotify returned "
                f"server status {status_code}."
            )

        raise SpotifyAPIError(
            f"{operation} failed with status {status_code}."
        )
