import httpx
import pytest

from app.providers.spotify.client import (
    SpotifyAPIError,
    SpotifyAuthenticationError,
    SpotifyClient,
    SpotifyNotFoundError,
    SpotifyRateLimitError,
    SpotifyServerError,
    SpotifyToken,
)


class FakeAsyncClient:
    def __init__(
        self,
        response: httpx.Response | None = None,
        error: Exception | None = None,
    ) -> None:
        self.response = response
        self.error = error

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, *args, **kwargs):
        if self.error is not None:
            raise self.error
        return self.response

    async def get(self, *args, **kwargs):
        if self.error is not None:
            raise self.error
        return self.response


def make_response(
    status_code: int,
    *,
    json: dict | None = None,
    content: bytes | None = None,
    headers: dict[str, str] | None = None,
    method: str = "GET",
    url: str = "https://api.spotify.com/v1/test",
) -> httpx.Response:
    request = httpx.Request(method, url)

    if json is not None:
        return httpx.Response(
            status_code=status_code,
            json=json,
            headers=headers,
            request=request,
        )

    return httpx.Response(
        status_code=status_code,
        content=content,
        headers=headers,
        request=request,
    )


def make_client() -> SpotifyClient:
    return SpotifyClient(
        client_id="client-id",
        client_secret="client-secret",
    )


@pytest.mark.asyncio
async def test_token_request_rejects_401(
    monkeypatch,
) -> None:
    response = make_response(
        401,
        method="POST",
        url="https://accounts.spotify.com/api/token",
    )

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: FakeAsyncClient(response=response),
    )

    with pytest.raises(SpotifyAuthenticationError):
        await make_client().get_client_credentials_token()


@pytest.mark.asyncio
async def test_token_request_rejects_403(
    monkeypatch,
) -> None:
    response = make_response(
        403,
        method="POST",
        url="https://accounts.spotify.com/api/token",
    )

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: FakeAsyncClient(response=response),
    )

    with pytest.raises(SpotifyAuthenticationError):
        await make_client().get_client_credentials_token()


@pytest.mark.asyncio
async def test_search_rejects_404(
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

    response = make_response(404)

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: FakeAsyncClient(response=response),
    )

    with pytest.raises(SpotifyNotFoundError):
        await client.search_tracks("test")


@pytest.mark.asyncio
async def test_search_handles_rate_limit(
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
        429,
        headers={
            "Retry-After": "30",
        },
    )

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: FakeAsyncClient(response=response),
    )

    with pytest.raises(SpotifyRateLimitError) as exc_info:
        await client.search_tracks("test")

    assert exc_info.value.retry_after == 30


@pytest.mark.asyncio
async def test_search_handles_invalid_retry_after(
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
        429,
        headers={
            "Retry-After": "invalid",
        },
    )

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: FakeAsyncClient(response=response),
    )

    with pytest.raises(SpotifyRateLimitError) as exc_info:
        await client.search_tracks("test")

    assert exc_info.value.retry_after is None


@pytest.mark.asyncio
async def test_search_handles_spotify_server_error(
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

    response = make_response(503)

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: FakeAsyncClient(response=response),
    )

    with pytest.raises(SpotifyServerError):
        await client.search_tracks("test")


@pytest.mark.asyncio
async def test_search_handles_other_client_error(
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

    response = make_response(400)

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: FakeAsyncClient(response=response),
    )

    with pytest.raises(SpotifyAPIError) as exc_info:
        await client.search_tracks("test")

    assert type(exc_info.value) is SpotifyAPIError


@pytest.mark.asyncio
async def test_track_not_found(
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

    response = make_response(404)

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: FakeAsyncClient(response=response),
    )

    with pytest.raises(SpotifyNotFoundError):
        await client.get_track("missing-track")


@pytest.mark.asyncio
async def test_network_error_is_converted_to_spotify_error(
    monkeypatch,
) -> None:
    client = make_client()

    fake_client = FakeAsyncClient(
        error=httpx.ConnectError("connection failed"),
    )

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: fake_client,
    )

    with pytest.raises(SpotifyAPIError, match="Unable to connect"):
        await client.get_client_credentials_token()


@pytest.mark.asyncio
async def test_invalid_token_json_is_rejected(
    monkeypatch,
) -> None:
    response = make_response(
        200,
        content=b"not-json",
        method="POST",
        url="https://accounts.spotify.com/api/token",
    )

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: FakeAsyncClient(response=response),
    )

    with pytest.raises(
        SpotifyAPIError,
        match="invalid token response data",
    ):
        await make_client().get_client_credentials_token()


@pytest.mark.asyncio
async def test_missing_access_token_is_rejected(
    monkeypatch,
) -> None:
    response = make_response(
        200,
        json={
            "expires_in": 3600,
        },
        method="POST",
        url="https://accounts.spotify.com/api/token",
    )

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: FakeAsyncClient(response=response),
    )

    with pytest.raises(
        SpotifyAPIError,
        match="missing an access token",
    ):
        await make_client().get_client_credentials_token()


@pytest.mark.asyncio
async def test_invalid_token_expiration_is_rejected(
    monkeypatch,
) -> None:
    response = make_response(
        200,
        json={
            "access_token": "test-token",
            "expires_in": 0,
        },
        method="POST",
        url="https://accounts.spotify.com/api/token",
    )

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: FakeAsyncClient(response=response),
    )

    with pytest.raises(
        SpotifyAPIError,
        match="invalid expiration",
    ):
        await make_client().get_client_credentials_token()


@pytest.mark.asyncio
async def test_access_token_is_cached(
    monkeypatch,
) -> None:
    client = make_client()

    calls = 0

    async def fake_token() -> SpotifyToken:
        nonlocal calls
        calls += 1

        return SpotifyToken(
            access_token="cached-token",
            expires_in=3600,
        )

    monkeypatch.setattr(
        client,
        "get_client_credentials_token",
        fake_token,
    )

    first = await client.get_access_token()
    second = await client.get_access_token()

    assert first == "cached-token"
    assert second == "cached-token"
    assert calls == 1


@pytest.mark.asyncio
async def test_empty_search_does_not_request_token() -> None:
    client = make_client()

    result = await client.search_tracks("   ")

    assert result["tracks"]["items"] == []
    assert result["tracks"]["total"] == 0


@pytest.mark.asyncio
async def test_empty_track_id_is_rejected() -> None:
    client = make_client()

    with pytest.raises(
        SpotifyAPIError,
        match="track ID cannot be empty",
    ):
        await client.get_track("   ")
