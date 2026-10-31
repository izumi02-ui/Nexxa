import httpx
import pytest

from app.providers.spotify.client import (
    SpotifyAPIError,
    SpotifyClient,
    SpotifyNotFoundError,
)


class FakeAsyncClient:
    def __init__(
        self,
        response: httpx.Response,
        error: Exception | None = None,
    ) -> None:
        self.response = response
        self.error = error

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, *args, **kwargs):
        if self.error is not None:
            raise self.error
        return self.response


def make_response(
    status_code: int,
    *,
    json_data: dict | None = None,
    content: bytes | None = None,
) -> httpx.Response:
    request = httpx.Request(
        "GET",
        "https://api.spotify.com/v1/artists/test-artist",
    )

    if json_data is not None:
        return httpx.Response(
            status_code,
            json=json_data,
            request=request,
        )

    return httpx.Response(
        status_code,
        content=content,
        request=request,
    )


def make_client() -> SpotifyClient:
    return SpotifyClient(
        client_id="test-client-id",
        client_secret="test-client-secret",
    )


@pytest.mark.asyncio
async def test_get_artist_returns_artist_data(
    monkeypatch,
) -> None:
    client = make_client()

    async def fake_access_token() -> str:
        return "test-token"

    monkeypatch.setattr(
        client,
        "get_access_token",
        fake_access_token,
    )

    response = make_response(
        200,
        json_data={
            "id": "spotify-artist-123",
            "name": "Test Artist",
            "genres": ["pop", "rock"],
            "popularity": 85,
            "followers": {
                "total": 100000,
            },
            "external_urls": {
                "spotify": (
                    "https://open.spotify.com/artist/"
                    "spotify-artist-123"
                ),
            },
            "images": [],
        },
    )

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: FakeAsyncClient(response),
    )

    result = await client.get_artist("spotify-artist-123")

    assert result["id"] == "spotify-artist-123"
    assert result["name"] == "Test Artist"
    assert result["genres"] == ["pop", "rock"]
    assert result["popularity"] == 85
    assert result["followers"]["total"] == 100000
    assert (
        result["external_urls"]["spotify"]
        == "https://open.spotify.com/artist/spotify-artist-123"
    )


@pytest.mark.asyncio
async def test_get_artist_rejects_empty_id() -> None:
    client = make_client()

    with pytest.raises(
        SpotifyAPIError,
        match="artist ID cannot be empty",
    ):
        await client.get_artist("   ")


@pytest.mark.asyncio
async def test_get_artist_handles_not_found(
    monkeypatch,
) -> None:
    client = make_client()

    async def fake_access_token() -> str:
        return "test-token"

    monkeypatch.setattr(
        client,
        "get_access_token",
        fake_access_token,
    )

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: FakeAsyncClient(make_response(404)),
    )

    with pytest.raises(SpotifyNotFoundError):
        await client.get_artist("missing-artist")


@pytest.mark.asyncio
async def test_get_artist_handles_invalid_json(
    monkeypatch,
) -> None:
    client = make_client()

    async def fake_access_token() -> str:
        return "test-token"

    monkeypatch.setattr(
        client,
        "get_access_token",
        fake_access_token,
    )

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: FakeAsyncClient(
            make_response(
                200,
                content=b"not-json",
            )
        ),
    )

    with pytest.raises(
        SpotifyAPIError,
        match="invalid artist response data",
    ):
        await client.get_artist("spotify-artist-123")


@pytest.mark.asyncio
async def test_get_artist_converts_network_error(
    monkeypatch,
) -> None:
    client = make_client()

    async def fake_access_token() -> str:
        return "test-token"

    monkeypatch.setattr(
        client,
        "get_access_token",
        fake_access_token,
    )

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: FakeAsyncClient(
            make_response(200),
            error=httpx.ConnectError("connection failed"),
        ),
    )

    with pytest.raises(
        SpotifyAPIError,
        match="Unable to connect",
    ):
        await client.get_artist("spotify-artist-123")