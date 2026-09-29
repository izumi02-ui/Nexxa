import httpx
import pytest

from app.providers.spotify.client import (
    SpotifyAPIError,
    SpotifyClient,
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
        if self.error is not None:
            raise self.error
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


@pytest.mark.asyncio
async def test_token_request_rejects_non_200(
    monkeypatch,
) -> None:
    response = httpx.Response(
        status_code=401,
        request=httpx.Request(
            "POST",
            "https://accounts.spotify.com/api/token",
        ),
    )

    fake_client = FakeAsyncClient(response=response)

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: fake_client,
    )

    client = SpotifyClient(
        client_id="client-id",
        client_secret="client-secret",
    )

    with pytest.raises(SpotifyAPIError, match="status 401"):
        await client.get_client_credentials_token()


@pytest.mark.asyncio
async def test_token_request_rejects_invalid_json(
    monkeypatch,
) -> None:
    response = httpx.Response(
        status_code=200,
        content=b"not-json",
        request=httpx.Request(
            "POST",
            "https://accounts.spotify.com/api/token",
        ),
    )

    fake_client = FakeAsyncClient(response=response)

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: fake_client,
    )

    client = SpotifyClient(
        client_id="client-id",
        client_secret="client-secret",
    )

    with pytest.raises(
        SpotifyAPIError,
        match="invalid token response data",
    ):
        await client.get_client_credentials_token()


@pytest.mark.asyncio
async def test_token_request_rejects_missing_access_token(
    monkeypatch,
) -> None:
    response = httpx.Response(
        status_code=200,
        json={
            "expires_in": 3600,
        },
        request=httpx.Request(
            "POST",
            "https://accounts.spotify.com/api/token",
        ),
    )

    fake_client = FakeAsyncClient(response=response)

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: fake_client,
    )

    client = SpotifyClient(
        client_id="client-id",
        client_secret="client-secret",
    )

    with pytest.raises(
        SpotifyAPIError,
        match="missing an access token",
    ):
        await client.get_client_credentials_token()


@pytest.mark.asyncio
async def test_token_request_rejects_invalid_expiration(
    monkeypatch,
) -> None:
    response = httpx.Response(
        status_code=200,
        json={
            "access_token": "test-token",
            "expires_in": 0,
        },
        request=httpx.Request(
            "POST",
            "https://accounts.spotify.com/api/token",
        ),
    )

    fake_client = FakeAsyncClient(response=response)

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: fake_client,
    )

    client = SpotifyClient(
        client_id="client-id",
        client_secret="client-secret",
    )

    with pytest.raises(
        SpotifyAPIError,
        match="invalid expiration",
    ):
        await client.get_client_credentials_token()


@pytest.mark.asyncio
async def test_token_request_handles_network_error(
    monkeypatch,
) -> None:
    fake_client = FakeAsyncClient(
        error=httpx.ConnectError(
            "connection failed"
        ),
    )

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: fake_client,
    )

    client = SpotifyClient(
        client_id="client-id",
        client_secret="client-secret",
    )

    with pytest.raises(
        SpotifyAPIError,
        match="Unable to connect",
    ):
        await client.get_client_credentials_token()


@pytest.mark.asyncio
async def test_search_rejects_empty_query_without_request() -> None:
    client = SpotifyClient(
        client_id="client-id",
        client_secret="client-secret",
    )

    result = await client.search_tracks(
        query="   ",
    )

    assert result["tracks"]["items"] == []
    assert result["tracks"]["total"] == 0


@pytest.mark.asyncio
async def test_get_track_rejects_empty_id() -> None:
    client = SpotifyClient(
        client_id="client-id",
        client_secret="client-secret",
    )

    with pytest.raises(
        SpotifyAPIError,
        match="track ID cannot be empty",
    ):
        await client.get_track("   ")


@pytest.mark.asyncio
async def test_access_token_is_cached(monkeypatch) -> None:
    client = SpotifyClient(
        client_id="client-id",
        client_secret="client-secret",
    )

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