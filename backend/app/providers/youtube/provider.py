from app.providers.base import MusicProvider
from app.providers.types import ProviderName, ProviderTrack
from app.providers.youtube.client import YouTubeClient


class YouTubeProvider(MusicProvider):
    """NEXXA provider implementation for YouTube."""

    def __init__(self, client: YouTubeClient) -> None:
        self.client = client

    @property
    def name(self) -> ProviderName:
        return ProviderName.YOUTUBE

    async def search_tracks(
        self,
        query: str,
        limit: int = 20,
    ) -> list[ProviderTrack]:
        remaining = max(0, limit)
        if remaining == 0:
            return []

        tracks: list[ProviderTrack] = []
        page_token: str | None = None

        while remaining > 0:
            request_limit = min(remaining, 50)

            videos, next_page_token = await self.client.search_videos(
                query=query,
                limit=request_limit,
                page_token=page_token,
            )

            for video in videos:
                tracks.append(
                    ProviderTrack(
                        provider=ProviderName.YOUTUBE,
                        external_id=video.video_id,
                        title=video.title,
                        artist_name=video.channel_name,
                        album_name=None,
                        duration_ms=None,
                        artwork_url=video.thumbnail_url,
                        external_url=video.url,
                    )
                )

            remaining = limit - len(tracks)

            if remaining <= 0 or not next_page_token:
                break

            page_token = next_page_token

        return tracks[:limit]

    async def get_track(
        self,
        external_id: str,
    ) -> ProviderTrack | None:
        video = await self.client.get_video(external_id)

        if video is None:
            return None

        return ProviderTrack(
            provider=ProviderName.YOUTUBE,
            external_id=video.video_id,
            title=video.title,
            artist_name=video.channel_name,
            album_name=None,
            duration_ms=self._duration_to_ms(video.duration),
            artwork_url=video.thumbnail_url,
            external_url=video.url,
        )

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

        total_seconds = hours * 3600 + minutes * 60 + seconds
        return total_seconds * 1000
