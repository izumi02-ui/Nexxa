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
async def test_channel_latest_videos_are_returned_newest_first(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = FakeAsyncClient(
        [
            make_response(
                {
                    "items": [
                        {"id": {"videoId": "video_old"}},
                        {"id": {"videoId": "video_new"}},
                    ],
                    "nextPageToken": "NEXT",
                }
            ),
            make_response(
                {
                    "items": [
                        {
                            "id": "video_old",
                            "snippet": {
                                "title": "Older Song",
                                "channelTitle": "Test Artist",
                                "description": "",
                                "publishedAt": "2025-01-01T10:00:00Z",
                                "thumbnails": {},
                            },
                            "contentDetails": {"duration": "PT3M"},
                        },
                        {
                            "id": "video_new",
                            "snippet": {
                                "title": "Latest Song",
                                "channelTitle": "Test Artist",
                                "description": "",
                                "publishedAt": "2026-01-01T10:00:00Z",
                                "thumbnails": {},
                            },
                            "contentDetails": {"duration": "PT4M"},
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

    videos, next_token = await client.get_channel_latest_videos(
        channel_id="UC_test",
        limit=10,
    )

    assert [video["video_id"] for video in videos] == [
        "video_new",
        "video_old",
    ]
    assert videos[0]["title"] == "Latest Song"
    assert videos[0]["published_at"] == "2026-01-01T10:00:00Z"
    assert videos[0]["url"] == (
        "https://www.youtube.com/watch?v=video_new"
    )
    assert next_token == "NEXT"

    search_url, search_params = fake_client.requests[0]
    assert search_url.endswith("/search")
    assert search_params["channelId"] == "UC_test"
    assert search_params["order"] == "date"
    assert search_params["maxResults"] == 10

    videos_url, videos_params = fake_client.requests[1]
    assert videos_url.endswith("/videos")
    assert videos_params["part"] == "snippet,contentDetails"
    assert videos_params["id"] == "video_old,video_new"


@pytest.mark.asyncio
async def test_channel_latest_videos_returns_empty_for_blank_channel() -> None:
    client = YouTubeClient(api_key="test-api-key")

    videos, next_token = await client.get_channel_latest_videos("   ")

    assert videos == []
    assert next_token is None


@pytest.mark.asyncio
async def test_channel_latest_videos_returns_empty_when_no_search_results(
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

    videos, next_token = await client.get_channel_latest_videos(
        channel_id="UC_test",
    )

    assert videos == []
    assert next_token is None
    assert len(fake_client.requests) == 1