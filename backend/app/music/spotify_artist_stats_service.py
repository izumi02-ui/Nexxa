from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.music.artist_models import Artist
from app.music.artist_provider_models import ArtistProviderProfile
from app.music.spotify_artist_stats_models import SpotifyArtistStats
from app.providers.spotify.client import SpotifyClient


def get_spotify_artist_id(
    db: Session,
    artist_id: int,
) -> str | None:
    """Return the Spotify artist ID mapped to a Nexxa artist."""

    artist = db.get(Artist, artist_id)

    if artist is None:
        return None

    profile = db.scalar(
        select(ArtistProviderProfile).where(
            ArtistProviderProfile.artist_id == artist_id,
            ArtistProviderProfile.provider == "spotify",
        )
    )

    if profile is None:
        return None

    return profile.external_id


def get_spotify_artist_stats(
    db: Session,
    artist_id: int,
) -> SpotifyArtistStats | None:
    """Return saved Spotify artist statistics."""

    return db.scalar(
        select(SpotifyArtistStats).where(
            SpotifyArtistStats.artist_id == artist_id,
        )
    )


def _normalize_release(item: dict[str, Any]) -> dict[str, Any] | None:
    """Normalize a Spotify album or single response."""

    external_id = item.get("id")
    name = item.get("name")

    if not isinstance(external_id, str) or not external_id.strip():
        return None

    if not isinstance(name, str) or not name.strip():
        return None

    images = item.get("images")
    image_url = None

    if isinstance(images, list) and images:
        first_image = images[0]

        if isinstance(first_image, dict):
            image_url = first_image.get("url")

    external_urls = item.get("external_urls")
    external_url = None

    if isinstance(external_urls, dict):
        external_url = external_urls.get("spotify")

    return {
        "id": external_id.strip(),
        "name": name.strip(),
        "album_type": item.get("album_type"),
        "release_date": item.get("release_date"),
        "total_tracks": item.get("total_tracks"),
        "image_url": image_url,
        "external_url": external_url,
    }


def _normalize_track(item: dict[str, Any]) -> dict[str, Any] | None:
    """Normalize a Spotify top-track response."""

    external_id = item.get("id")
    name = item.get("name")

    if not isinstance(external_id, str) or not external_id.strip():
        return None

    if not isinstance(name, str) or not name.strip():
        return None

    album = item.get("album")
    album_name = None
    album_image_url = None

    if isinstance(album, dict):
        album_name = album.get("name")

        images = album.get("images")

        if isinstance(images, list) and images:
            first_image = images[0]

            if isinstance(first_image, dict):
                album_image_url = first_image.get("url")

    external_urls = item.get("external_urls")
    external_url = None

    if isinstance(external_urls, dict):
        external_url = external_urls.get("spotify")

    duration_ms = item.get("duration_ms")

    if not isinstance(duration_ms, int) or duration_ms < 0:
        duration_ms = None

    return {
        "id": external_id.strip(),
        "name": name.strip(),
        "album_name": album_name,
        "duration_ms": duration_ms,
        "explicit": item.get("explicit"),
        "popularity": item.get("popularity"),
        "image_url": album_image_url,
        "external_url": external_url,
    }


def save_spotify_artist_stats(
    db: Session,
    artist_id: int,
    artist_data: dict[str, Any],
    albums_data: dict[str, Any],
    top_tracks_data: dict[str, Any],
) -> SpotifyArtistStats:
    """Insert or update Spotify artist statistics."""

    artist = db.get(Artist, artist_id)

    if artist is None:
        raise ValueError("Nexxa artist does not exist.")

    spotify_artist_id = artist_data.get("id")

    if (
        not isinstance(spotify_artist_id, str)
        or not spotify_artist_id.strip()
    ):
        raise ValueError("Spotify artist response has no valid ID.")

    mapped_id = get_spotify_artist_id(
        db=db,
        artist_id=artist_id,
    )

    if mapped_id is not None and mapped_id != spotify_artist_id:
        raise ValueError(
            "Spotify artist ID does not match the mapped artist profile."
        )

    followers_data = artist_data.get("followers")
    followers = None

    if isinstance(followers_data, dict):
        raw_followers = followers_data.get("total")

        if isinstance(raw_followers, int) and raw_followers >= 0:
            followers = raw_followers

    popularity = artist_data.get("popularity")

    if (
        not isinstance(popularity, int)
        or not 0 <= popularity <= 100
    ):
        popularity = None

    genres_data = artist_data.get("genres")
    genres = []

    if isinstance(genres_data, list):
        genres = [
            genre.strip()
            for genre in genres_data
            if isinstance(genre, str) and genre.strip()
        ]

    external_urls = artist_data.get("external_urls")
    spotify_url = None

    if isinstance(external_urls, dict):
        raw_url = external_urls.get("spotify")

        if isinstance(raw_url, str) and raw_url.strip():
            spotify_url = raw_url.strip()

    image_url = None
    images = artist_data.get("images")

    if isinstance(images, list) and images:
        first_image = images[0]

        if isinstance(first_image, dict):
            raw_image_url = first_image.get("url")

            if isinstance(raw_image_url, str):
                image_url = raw_image_url.strip() or None

    album_items = albums_data.get("items", [])
    albums = []
    singles = []

    if isinstance(album_items, list):
        for item in album_items:
            if not isinstance(item, dict):
                continue

            normalized = _normalize_release(item)

            if normalized is None:
                continue

            if normalized["album_type"] == "single":
                singles.append(normalized)
            elif normalized["album_type"] == "album":
                albums.append(normalized)

    track_items = top_tracks_data.get("tracks", [])
    top_tracks = []

    if isinstance(track_items, list):
        for item in track_items:
            if not isinstance(item, dict):
                continue

            normalized = _normalize_track(item)

            if normalized is not None:
                top_tracks.append(normalized)

    stats = get_spotify_artist_stats(
        db=db,
        artist_id=artist_id,
    )

    fetched_at = datetime.now(timezone.utc)

    if stats is None:
        stats = SpotifyArtistStats(
            artist_id=artist_id,
        )
        db.add(stats)

    stats.spotify_artist_id = spotify_artist_id
    stats.spotify_url = spotify_url
    stats.followers = followers
    stats.popularity = popularity

    # Spotify's standard Web API does not expose monthly listeners.
    stats.monthly_listeners = None

    stats.genres = genres
    stats.albums = albums
    stats.singles = singles
    stats.top_tracks = top_tracks
    stats.statistics_available = True
    stats.statistics_fetched_at = fetched_at

    if image_url:
        artist.image_url = image_url

    if genres:
        artist.genres = genres

    db.flush()

    return stats


async def refresh_spotify_artist_stats(
    db: Session,
    artist_id: int,
    client: SpotifyClient,
    market: str = "US",
) -> SpotifyArtistStats | None:
    """Fetch Spotify artist data and save it to Nexxa."""

    spotify_artist_id = get_spotify_artist_id(
        db=db,
        artist_id=artist_id,
    )

    if spotify_artist_id is None:
        return None

    artist_data = await client.get_artist(
        spotify_artist_id,
    )

    albums_data = await client.get_artist_albums(
        spotify_artist_id,
        include_groups="album,single",
        limit=50,
        offset=0,
        market=market,
    )

    top_tracks_data = await client.get_artist_top_tracks(
        spotify_artist_id,
        market=market,
    )

    return save_spotify_artist_stats(
        db=db,
        artist_id=artist_id,
        artist_data=artist_data,
        albums_data=albums_data,
        top_tracks_data=top_tracks_data,
    )