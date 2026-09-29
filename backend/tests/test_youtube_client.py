import httpx
import pytest

from app.providers.youtube.client import (
    YouTubeAPIError,
    YouTubeAuthenticationError,
    YouTubeClient,
    YouTubeNotFoundError,
    YouTubeRateLimitError,
    YouTubeServerError,
)


class FakeAsyncClient:
    def __init__(
        self,
        response: httpx.Response,
    ) -> None:
        self.response = response
        self.requests: list[tuple[str, dict]] = []

    async def __aenter__(self) -> "FakeAsyncClient":
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        return None

    async def get(
        self,
        url: str,
        params: dict,
    ) -> httpx.Response:
        self.requests.append((url, params))
        return self.response


class FailingAsyncClient:
    async def __aenter__(self) -> "FailingAsyncClient":
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        return None

    async def get(
        self,
        url: str,
        params: dict,
    ) -> httpx.Response:
        raise httpx.ConnectError(
            "connection failed",
            request=httpx.Request("GET", url),
        )


def make_response(
    status_code: int,
    json_data: dict,
) -> httpx.Response:
    return httpx.Response(
        status_code=status_code,
        json=json_data,
        request=httpx.Request(
            "GET",
            "https://www.googleapis.com/youtube/v3/test",
        ),
    )


@pytest.mark.asyncio
async def test_search_videos_parses_results(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = make_response(
        200,
        {
            "items": [
                {
                    "id": {
                        "videoId": "abc123",
                    },
                    "snippet": {
                        "title": "Test Song",
                        "channelTitle": "Test Artist",
                        "description": "Test description",
                        "thumbnails": {
                            "high": {
                                "url": "https://example.com/high.jpg",
                            },
                        },
                    },
                },
            ],
            "nextPageToken": "NEXT_TOKEN",
        },
    )

    fake_client = FakeAsyncClient(response)

    def create_client(*args, **kwargs) -> FakeAsyncClient:
        return fake_client

    monkeypatch.setattr(
        "app.providers.youtube.client.httpx.AsyncClient",
        create_client,
    )

    client = YouTubeClient(
        api_key="test-api-key",
    )

    videos, next_page_token = await client.search_videos(
        query="test song",
        limit=10,
    )

    assert len(videos) == 1
    assert videos[0].video_id == "abc123"
    assert videos[0].title == "Test Song"
    assert videos[0].channel_name == "Test Artist"
    assert videos[0].description == "Test description"
    assert videos[0].thumbnail_url == (
        "https://example.com/high.jpg"
    )
    assert videos[0].duration is None
    assert videos[0].url == (
        "https://www.youtube.com/watch?v=abc123"
    )

    assert next_page_token == "NEXT_TOKEN"

    assert len(fake_client.requests) == 1

    url, params = fake_client.requests[0]

    assert url == "https://www.googleapis.com/youtube/v3/search"
    assert params["key"] == "test-api-key"
    assert params["part"] == "snippet"
    assert params["type"] == "video"
    assert params["q"] == "test song"
    assert params["maxResults"] == 10
    assert "pageToken" not in params


@pytest.mark.asyncio
async def test_search_videos_sends_page_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = make_response(
        200,
        {
            "items": [],
            "nextPageToken": None,
        },
    )

    fake_client = FakeAsyncClient(response)

    def create_client(*args, **kwargs) -> FakeAsyncClient:
        return fake_client

    monkeypatch.setattr(
        "app.providers.youtube.client.httpx.AsyncClient",
        create_client,
    )

    client = YouTubeClient(
        api_key="test-api-key",
    )

    videos, next_page_token = await client.search_videos(
        query="test song",
        limit=20,
        page_token="PAGE_TOKEN",
    )

    assert videos == []
    assert next_page_token is None

    _, params = fake_client.requests[0]

    assert params["pageToken"] == "PAGE_TOKEN"


@pytest.mark.asyncio
async def test_search_videos_clamps_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = make_response(
        200,
        {
            "items": [],
        },
    )

    fake_client = FakeAsyncClient(response)

    def create_client(*args, **kwargs) -> FakeAsyncClient:
        return fake_client

    monkeypatch.setattr(
        "app.providers.youtube.client.httpx.AsyncClient",
        create_client,
    )

    client = YouTubeClient(
        api_key="test-api-key",
    )

    await client.search_videos(
        query="test",
        limit=100,
    )

    _, params = fake_client.requests[0]

    assert params["maxResults"] == 50


@pytest.mark.asyncio
async def test_search_videos_returns_empty_for_blank_query() -> None:
    client = YouTubeClient(
        api_key="test-api-key",
    )

    videos, next_page_token = await client.search_videos(
        query="   ",
    )

    assert videos == []
    assert next_page_token is None


@pytest.mark.asyncio
async def test_get_video_parses_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = make_response(
        200,
        {
            "items": [
                {
                    "id": "abc123",
                    "snippet": {
                        "title": "Test Song",
                        "channelTitle": "Test Artist",
                        "description": "Test description",
                        "thumbnails": {
                            "medium": {
                                "url": "https://example.com/medium.jpg",
                            },
                        },
                    },
                    "contentDetails": {
                        "duration": "PT3M30S",
                    },
                },
            ],
        },
    )

    fake_client = FakeAsyncClient(response)

    def create_client(*args, **kwargs) -> FakeAsyncClient:
        return fake_client

    monkeypatch.setattr(
        "app.providers.youtube.client.httpx.AsyncClient",
        create_client,
    )

    client = YouTubeClient(
        api_key="test-api-key",
    )

    video = await client.get_video("abc123")

    assert video is not None
    assert video.video_id == "abc123"
    assert video.title == "Test Song"
    assert video.channel_name == "Test Artist"
    assert video.description == "Test description"
    assert video.thumbnail_url == (
        "https://example.com/medium.jpg"
    )
    assert video.duration == "PT3M30S"
    assert video.url == (
        "https://www.youtube.com/watch?v=abc123"
    )

    _, params = fake_client.requests[0]

    assert params["key"] == "test-api-key"
    assert params["part"] == "snippet,contentDetails"
    assert params["id"] == "abc123"


@pytest.mark.asyncio
async def test_get_video_returns_none_when_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = make_response(
        200,
        {
            "items": [],
        },
    )

    fake_client = FakeAsyncClient(response)

    def create_client(*args, **kwargs) -> FakeAsyncClient:
        return fake_client

    monkeypatch.setattr(
        "app.providers.youtube.client.httpx.AsyncClient",
        create_client,
    )

    client = YouTubeClient(
        api_key="test-api-key",
    )

    video = await client.get_video("missing")

    assert video is None


@pytest.mark.asyncio
async def test_get_video_returns_none_for_blank_id() -> None:
    client = YouTubeClient(
        api_key="test-api-key",
    )

    video = await client.get_video("   ")

    assert video is None


@pytest.mark.asyncio
async def test_request_converts_network_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def create_client(*args, **kwargs) -> FailingAsyncClient:
        return FailingAsyncClient()

    monkeypatch.setattr(
        "app.providers.youtube.client.httpx.AsyncClient",
        create_client,
    )

    client = YouTubeClient(
        api_key="test-api-key",
    )

    with pytest.raises(YouTubeAPIError, match="request failed"):
        await client.get_video("abc123")


def test_client_requires_api_key() -> None:
    with pytest.raises(ValueError):
        YouTubeClient(api_key="")


@pytest.mark.parametrize(
    ("status_code", "exception"),
    [
        (401, YouTubeAuthenticationError),
        (403, YouTubeAuthenticationError),
        (404, YouTubeNotFoundError),
        (429, YouTubeRateLimitError),
        (500, YouTubeServerError),
        (502, YouTubeServerError),
        (400, YouTubeAPIError),
    ],
)
def test_raise_for_status_maps_errors(
    status_code: int,
    exception: type[Exception],
) -> None:
    response = make_response(
        status_code,
        {
            "error": {
                "message": "test",
            },
        },
    )

    with pytest.raises(exception):
        YouTubeClient._raise_for_status(response)


def test_thumbnail_fallback() -> None:
    snippet = {
        "thumbnails": {
            "default": {
                "url": "https://example.com/default.jpg",
            },
        },
    }

    assert YouTubeClient._get_thumbnail_url(snippet) == (
        "https://example.com/default.jpg"
    )


def test_thumbnail_returns_none_when_missing() -> None:
    assert YouTubeClient._get_thumbnail_url({}) is None
