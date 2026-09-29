from app.providers.youtube.client import YouTubeClient


class YouTubeMusicAPIError(Exception):
    """Base error for YouTube Music provider access."""


class YouTubeMusicClient:
    """YouTube Music integration backed by the documented YouTube Data API."""

    def __init__(self, youtube_client: YouTubeClient) -> None:
        self.youtube_client = youtube_client

    async def search_tracks(
        self,
        query: str,
        limit: int = 20,
    ) -> list[dict]:
        """Search YouTube content for music-oriented results."""

        videos, _ = await self.youtube_client.search_videos(
            query=query,
            limit=limit,
        )

        return [
            {
                "external_id": video.video_id,
                "title": video.title,
                "artist_name": video.channel_name,
                "album_name": None,
                "duration_ms": None,
                "artwork_url": video.thumbnail_url,
                "external_url": video.url,
            }
            for video in videos
        ]

    async def get_track(
        self,
        external_id: str,
    ) -> dict | None:
        """Retrieve a YouTube video as a YouTube Music track."""

        video = await self.youtube_client.get_video(external_id)

        if video is None:
            return None

        return {
            "external_id": video.video_id,
            "title": video.title,
            "artist_name": video.channel_name,
            "album_name": None,
            "duration_ms": self._duration_to_ms(video.duration),
            "artwork_url": video.thumbnail_url,
            "external_url": video.url,
        }

    @staticmethod
    def _duration_to_ms(duration: str | None) -> int | None:
        """Convert an ISO 8601 YouTube duration to milliseconds."""

        if not duration or not duration.startswith("PT"):
            return None

        value = duration[2:]
        hours = 0
        minutes = 0
        seconds = 0
        number = ""

        for character in value:
            if character.isdigit():
                number += character
                continue

            if not number:
                return None

            amount = int(number)
            number = ""

            if character == "H":
                hours = amount
            elif character == "M":
                minutes = amount
            elif character == "S":
                seconds = amount
            else:
                return None

        if number:
            return None

        total_seconds = (
            hours * 3600
            + minutes * 60
            + seconds
        )

        return total_seconds * 1000
