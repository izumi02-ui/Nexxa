import httpx
import pytest

from app.providers.youtube.client import YouTubeClient


class FakeAsyncClient:
    def __init__(self, responses: list[httpx.Response]) -> None:
        self.responses = responses
        self.requests: list[tuple[str, dict]] = []

    async def __aenter__(self) -> "FakeAsyncClient":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        return None

    async def get(self, url: str, params: dict) -> httpx.Response:
        self.requests.append((url, params))
        return self.responses.pop(0)


def make_response(data: dict) -> httpx.Response:
    return httpx.Response(
        status_code=200,
        json=data,
        request=httpx.Request(
            "GET",
            "https://www.googleapis.com/youtube/v3/test",
        ),
    )


@pytest.mark.asyncio
async def test_channel_videos_are_sorted_by_available_like_count(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = FakeAsyncClient(
        [
            make_response(
                {
                    "items": [
                        {"id": {"videoId": "video_a"}},
                        {"id": {"videoId": "video_b"}},
                        {"id": {"videoId": "video_c"}},
                    ],
                    "nextPageToken": "NEXT",
                }
            ),
            make_response(
                {
                    "items": [
                        {
                            "id": "video_a",
                            "snippet": {
                                "title": "Song A",
                                "channelTitle": "Test Artist",
                                "description": "",
                                "thumbnails": {},
                            },
                            "contentDetails": {"duration": "PT3M"},
                            "statistics": {"likeCount": "100"},
                        },
                        {
                            "id": "video_b",
                            "snippet": {
                                "title": "Song B",
                                "channelTitle": "Test Artist",
                                "description": "",
                                "thumbnails": {},
                            },
                            "contentDetails": {"duration": "PT4M"},
                            "statistics": {"likeCount": "500"},
                        },
                        {
                            "id": "video_c",
                            "snippet": {
                                "title": "Song C",
                                "channelTitle": "Test Artist",
                                "description": "",
                                "thumbnails": {},
                            },
                            "contentDetails": {"duration": "PT2M"},
                            "statistics": {},
                        },
                    ]
                }
            ),
        ]
    )

    monkeypatch.setattr(
        "app.providers.youtube.client.httpx.AsyncClient",
        lambda *args, **kwargs: fake_client,
    )

    client = YouTubeClient(api_key="test-api-key")

    videos, next_token = await client.get_channel_videos_by_likes(
        channel_id="UC_test",
        limit=10,
    )

    assert [video["video_id"] for video in videos] == [
        "video_b",
        "video_a",
        "video_c",
    ]
    assert [video["like_count"] for video in videos] == [
        500,
        100,
        None,
    ]
    assert videos[0]["title"] == "Song B"
    assert videos[0]["url"] == (
        "https://www.youtube.com/watch?v=video_b"
    )
    assert next_token == "NEXT"

    search_url, search_params = fake_client.requests[0]
    assert search_url.endswith("/search")
    assert search_params["channelId"] == "UC_test"
    assert search_params["order"] == "viewCount"
    assert search_params["maxResults"] == 10

    videos_url, videos_params = fake_client.requests[1]
    assert videos_url.endswith("/videos")
    assert videos_params["part"] == "snippet,contentDetails,statistics"
    assert videos_params["id"] == "video_a,video_b,video_c"


@pytest.mark.asyncio
async def test_channel_videos_by_likes_returns_empty_for_blank_channel() -> None:
    client = YouTubeClient(api_key="test-api-key")

    videos, next_token = await client.get_channel_videos_by_likes("   ")

    assert videos == []
    assert next_token is None


@pytest.mark.asyncio
async def test_channel_videos_by_likes_returns_empty_when_no_search_results(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = FakeAsyncClient(
        [
            make_response(
                {
                    "items": [],
                    "nextPageToken": None,
                }
            ),
        ]
    )

    monkeypatch.setattr(
        "app.providers.youtube.client.httpx.AsyncClient",
        lambda *args, **kwargs: fake_client,
    )

    client = YouTubeClient(api_key="test-api-key")

    videos, next_token = await client.get_channel_videos_by_likes(
        channel_id="UC_test",
    )

    assert videos == []
    assert next_token is None
    assert len(fake_client.requests) == 1