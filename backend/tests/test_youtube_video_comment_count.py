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
async def test_get_channel_video_comment_count(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = FakeAsyncClient(
        [
            make_response(
                {
                    "items": [
                        {
                            "id": "video_123",
                            "snippet": {
                                "channelId": "UC_test",
                                "title": "Test Song",
                            },
                            "statistics": {
                                "commentCount": "250",
                            },
                        }
                    ]
                }
            )
        ]
    )

    monkeypatch.setattr(
        "app.providers.youtube.client.httpx.AsyncClient",
        lambda *args, **kwargs: fake_client,
    )

    client = YouTubeClient(api_key="test-api-key")

    result = await client.get_channel_video_comment_count(
        channel_id="UC_test",
        video_id="video_123",
    )

    assert result == {
        "video_id": "video_123",
        "channel_id": "UC_test",
        "title": "Test Song",
        "comment_count": 250,
    }

    url, params = fake_client.requests[0]
    assert url.endswith("/videos")
    assert params["part"] == "snippet,statistics"
    assert params["id"] == "video_123"


@pytest.mark.asyncio
async def test_video_comment_count_is_none_when_not_public(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = FakeAsyncClient(
        [
            make_response(
                {
                    "items": [
                        {
                            "id": "video_123",
                            "snippet": {
                                "channelId": "UC_test",
                                "title": "Test Song",
                            },
                            "statistics": {},
                        }
                    ]
                }
            )
        ]
    )

    monkeypatch.setattr(
        "app.providers.youtube.client.httpx.AsyncClient",
        lambda *args, **kwargs: fake_client,
    )

    client = YouTubeClient(api_key="test-api-key")

    result = await client.get_channel_video_comment_count(
        channel_id="UC_test",
        video_id="video_123",
    )

    assert result is not None
    assert result["comment_count"] is None


@pytest.mark.asyncio
async def test_video_comment_count_rejects_video_from_another_channel(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = FakeAsyncClient(
        [
            make_response(
                {
                    "items": [
                        {
                            "id": "video_123",
                            "snippet": {
                                "channelId": "UC_different",
                                "title": "Another Artist Song",
                            },
                            "statistics": {
                                "commentCount": "500",
                            },
                        }
                    ]
                }
            )
        ]
    )

    monkeypatch.setattr(
        "app.providers.youtube.client.httpx.AsyncClient",
        lambda *args, **kwargs: fake_client,
    )

    client = YouTubeClient(api_key="test-api-key")

    result = await client.get_channel_video_comment_count(
        channel_id="UC_test",
        video_id="video_123",
    )

    assert result is None


@pytest.mark.asyncio
async def test_video_comment_count_returns_none_for_missing_video(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = FakeAsyncClient(
        [
            make_response({"items": []}),
        ]
    )

    monkeypatch.setattr(
        "app.providers.youtube.client.httpx.AsyncClient",
        lambda *args, **kwargs: fake_client,
    )

    client = YouTubeClient(api_key="test-api-key")

    result = await client.get_channel_video_comment_count(
        channel_id="UC_test",
        video_id="missing_video",
    )

    assert result is None


@pytest.mark.asyncio
async def test_video_comment_count_returns_none_for_blank_ids() -> None:
    client = YouTubeClient(api_key="test-api-key")

    result = await client.get_channel_video_comment_count(
        channel_id=" ",
        video_id="video_123",
    )

    assert result is None