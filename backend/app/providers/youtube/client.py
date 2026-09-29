from dataclasses import dataclass
from typing import Any

import httpx


YOUTUBE_API_BASE_URL = "https://www.googleapis.com/youtube/v3"


class YouTubeAPIError(Exception):
    """Base exception for YouTube Data API errors."""


class YouTubeAuthenticationError(YouTubeAPIError):
    """Raised when YouTube API authentication fails."""


class YouTubeRateLimitError(YouTubeAPIError):
    """Raised when the YouTube API rate limit or quota is exceeded."""


class YouTubeNotFoundError(YouTubeAPIError):
    """Raised when a requested YouTube resource is not found."""


class YouTubeServerError(YouTubeAPIError):
    """Raised when the YouTube API returns a server-side error."""


@dataclass(frozen=True)
class YouTubeVideo:
    """Raw normalized video data returned by the YouTube API."""

    video_id: str
    title: str
    channel_name: str
    description: str
    thumbnail_url: str | None
    duration: str | None
    url: str


class YouTubeClient:
    """Async client for the official YouTube Data API v3."""

    def __init__(
        self,
        api_key: str,
        timeout: float = 15.0,
    ) -> None:
        if not api_key:
            raise ValueError("YouTube API key is required.")

        self._api_key = api_key
        self._timeout = timeout

    async def search_videos(
        self,
        query: str,
        limit: int = 10,
        page_token: str | None = None,
    ) -> tuple[list[YouTubeVideo], str | None]:
        """Search YouTube videos and return results with the next page token."""
        if not query.strip():
            return [], None

        limit = max(1, min(limit, 50))

        params: dict[str, Any] = {
            "key": self._api_key,
            "part": "snippet",
            "type": "video",
            "q": query.strip(),
            "maxResults": limit,
        }

        if page_token:
            params["pageToken"] = page_token

        response = await self._request("search", params)
        data = response.json()

        videos: list[YouTubeVideo] = []

        for item in data.get("items", []):
            video_id = item.get("id", {}).get("videoId")
            snippet = item.get("snippet", {})

            if not video_id:
                continue

            videos.append(
                YouTubeVideo(
                    video_id=video_id,
                    title=snippet.get("title", ""),
                    channel_name=snippet.get("channelTitle", ""),
                    description=snippet.get("description", ""),
                    thumbnail_url=self._get_thumbnail_url(snippet),
                    duration=None,
                    url=f"https://www.youtube.com/watch?v={video_id}",
                )
            )

        return videos, data.get("nextPageToken")

    async def get_video(self, external_id: str) -> YouTubeVideo | None:
        """Retrieve one YouTube video by its video ID."""
        if not external_id.strip():
            return None

        params: dict[str, Any] = {
            "key": self._api_key,
            "part": "snippet,contentDetails",
            "id": external_id.strip(),
        }

        response = await self._request("videos", params)
        data = response.json()
        items = data.get("items", [])

        if not items:
            return None

        item = items[0]
        snippet = item.get("snippet", {})
        content_details = item.get("contentDetails", {})

        video_id = item.get("id")

        if not video_id:
            return None

        return YouTubeVideo(
            video_id=video_id,
            title=snippet.get("title", ""),
            channel_name=snippet.get("channelTitle", ""),
            description=snippet.get("description", ""),
            thumbnail_url=self._get_thumbnail_url(snippet),
            duration=content_details.get("duration"),
            url=f"https://www.youtube.com/watch?v={video_id}",
        )

    async def _request(
        self,
        endpoint: str,
        params: dict[str, Any],
    ) -> httpx.Response:
        url = f"{YOUTUBE_API_BASE_URL}/{endpoint}"

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url, params=params)
        except httpx.HTTPError as exc:
            raise YouTubeAPIError(
                "YouTube API request failed."
            ) from exc

        self._raise_for_status(response)

        return response

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        if response.status_code in {401, 403}:
            raise YouTubeAuthenticationError(
                "YouTube API authentication or quota access failed."
            )

        if response.status_code == 404:
            raise YouTubeNotFoundError(
                "YouTube resource was not found."
            )

        if response.status_code == 429:
            raise YouTubeRateLimitError(
                "YouTube API rate limit was exceeded."
            )

        if response.status_code >= 500:
            raise YouTubeServerError(
                "YouTube API server error."
            )

        if response.status_code >= 400:
            raise YouTubeAPIError(
                "YouTube API request was rejected."
            )

        response.raise_for_status()

    @staticmethod
    def _get_thumbnail_url(
        snippet: dict[str, Any],
    ) -> str | None:
        thumbnails = snippet.get("thumbnails", {})

        for name in ("high", "medium", "default"):
            thumbnail = thumbnails.get(name)

            if isinstance(thumbnail, dict):
                url = thumbnail.get("url")

                if url:
                    return url

        return None
