    async def get_channel_videos_by_views(
        self,
        channel_id: str,
        limit: int = 10,
        page_token: str | None = None,
    ) -> tuple[list[dict[str, Any]], str | None]:
        """Return public channel videos ordered by view count."""

        if not channel_id.strip():
            return [], None

        limit = max(1, min(limit, 50))

        search_params: dict[str, Any] = {
            "key": self._api_key,
            "part": "snippet",
            "type": "video",
            "channelId": channel_id.strip(),
            "order": "viewCount",
            "maxResults": limit,
        }

        if page_token:
            search_params["pageToken"] = page_token

        search_response = await self._request(
            "search",
            search_params,
        )
        search_data = search_response.json()

        items = search_data.get("items", [])
        video_ids = [
            item.get("id", {}).get("videoId")
            for item in items
            if item.get("id", {}).get("videoId")
        ]

        if not video_ids:
            return [], search_data.get("nextPageToken")

        videos_response = await self._request(
            "videos",
            {
                "key": self._api_key,
                "part": "snippet,contentDetails,statistics",
                "id": ",".join(video_ids),
            },
        )
        videos_data = videos_response.json()

        videos: list[dict[str, Any]] = []

        for item in videos_data.get("items", []):
            video_id = item.get("id")
            snippet = item.get("snippet", {})
            details = item.get("contentDetails", {})
            statistics = item.get("statistics", {})

            if not video_id:
                continue

            raw_views = statistics.get("viewCount")
            view_count = int(raw_views) if raw_views is not None else None

            videos.append(
                {
                    "video_id": video_id,
                    "title": snippet.get("title", ""),
                    "channel_name": snippet.get("channelTitle", ""),
                    "description": snippet.get("description", ""),
                    "thumbnail_url": self._get_thumbnail_url(snippet),
                    "duration": details.get("duration"),
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "view_count": view_count,
                }
            )

        videos.sort(
            key=lambda video: (
                video["view_count"] is not None,
                video["view_count"] if video["view_count"] is not None else -1,
            ),
            reverse=True,
        )

        return videos, search_data.get("nextPageToken")