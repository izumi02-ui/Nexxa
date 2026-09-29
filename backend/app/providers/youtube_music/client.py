class YouTubeMusicAPIError(Exception):
    """Base error for YouTube Music provider access."""


class YouTubeMusicUnsupportedError(YouTubeMusicAPIError):
    """Raised when a requested YouTube Music operation is unsupported."""


class YouTubeMusicClient:
    """Isolated client boundary for YouTube Music integration."""

    async def search_tracks(
        self,
        query: str,
        limit: int = 20,
    ) -> list[dict]:
        raise YouTubeMusicUnsupportedError(
            "No documented public YouTube Music API is configured."
        )

    async def get_track(
        self,
        external_id: str,
    ) -> dict | None:
        raise YouTubeMusicUnsupportedError(
            "No documented public YouTube Music API is configured."
        )
