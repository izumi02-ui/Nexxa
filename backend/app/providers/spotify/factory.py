from app.config import Settings
from app.providers.spotify.client import SpotifyClient
from app.providers.spotify.provider import SpotifyProvider


def create_spotify_provider(
    settings: Settings,
) -> SpotifyProvider | None:
    """Create Spotify when server credentials are configured."""

    if not settings.spotify_client_id:
        return None

    if not settings.spotify_client_secret:
        return None

    client = SpotifyClient(
        client_id=settings.spotify_client_id,
        client_secret=settings.spotify_client_secret,
    )

    return SpotifyProvider(
        client=client,
    )