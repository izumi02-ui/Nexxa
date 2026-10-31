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
        self.last_url = None
        self.last_params = None
        self.last_headers = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url, **kwargs):
        self.last_url = url
        self.last_params = kwargs.get("params")
        self.last_headers = kwargs.get("headers")

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
        "https://api.spotify.com/v1/test",
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


async def install_fake_token(
    monkeypatch,
    client: SpotifyClient,
) -> None:
    async def fake_access_token() -> str:
        return "test-token"

    monkeypatch.setattr(
        client,
        "get_access_token",
        fake_access_token,
    )


@pytest.mark.asyncio
async def test_get_artist_returns_artist_data(
    monkeypatch,
) -> None:
    client = make_client()
    await install_fake_token(monkeypatch, client)

    response = make_response(
        200,
        json_data={
            "id": "spotify-artist-123",
            "name": "Test Artist",
            "genres": ["pop", "rock"],
            "popularity": 85,
            "followers": {"total": 100000},
            "external_urls": {
                "spotify": (
                    "https://open.spotify.com/artist/"
                    "spotify-artist-123"
                ),
            },
            "images": [],
        },
    )

    fake = FakeAsyncClient(response)

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: fake,
    )

    result = await client.get_artist("spotify-artist-123")

    assert result["id"] == "spotify-artist-123"
    assert result["name"] == "Test Artist"
    assert result["genres"] == ["pop", "rock"]
    assert result["popularity"] == 85
    assert result["followers"]["total"] == 100000


@pytest.mark.asyncio
async def test_get_artist_rejects_empty_id() -> None:
    with pytest.raises(
        SpotifyAPIError,
        match="artist ID cannot be empty",
    ):
        await make_client().get_artist("   ")


@pytest.mark.asyncio
async def test_get_artist_handles_not_found(
    monkeypatch,
) -> None:
    client = make_client()
    await install_fake_token(monkeypatch, client)

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
    await install_fake_token(monkeypatch, client)

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: FakeAsyncClient(
            make_response(200, content=b"not-json")
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
    await install_fake_token(monkeypatch, client)

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


@pytest.mark.asyncio
async def test_get_artist_albums_returns_release_data(
    monkeypatch,
) -> None:
    client = make_client()
    await install_fake_token(monkeypatch, client)

    response = make_response(
        200,
        json_data={
            "items": [
                {
                    "id": "album-123",
                    "name": "First Album",
                    "album_type": "album",
                },
                {
                    "id": "single-123",
                    "name": "First Single",
                    "album_type": "single",
                },
            ],
            "total": 2,
            "limit": 50,
            "offset": 0,
            "next": None,
        },
    )

    fake = FakeAsyncClient(response)

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: fake,
    )

    result = await client.get_artist_albums(
        "spotify-artist-123"
    )

    assert len(result["items"]) == 2
    assert result["items"][0]["album_type"] == "album"
    assert result["items"][1]["album_type"] == "single"
    assert fake.last_url.endswith(
        "/artists/spotify-artist-123/albums"
    )
    assert fake.last_params["include_groups"] == "album,single"
    assert fake.last_params["limit"] == 50


@pytest.mark.asyncio
async def test_get_artist_albums_supports_pagination(
    monkeypatch,
) -> None:
    client = make_client()
    await install_fake_token(monkeypatch, client)

    fake = FakeAsyncClient(
        make_response(
            200,
            json_data={
                "items": [],
                "total": 100,
                "limit": 20,
                "offset": 40,
                "next": None,
            },
        )
    )

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: fake,
    )

    result = await client.get_artist_albums(
        "spotify-artist-123",
        limit=20,
        offset=40,
    )

    assert result["offset"] == 40
    assert fake.last_params["limit"] == 20
    assert fake.last_params["offset"] == 40


@pytest.mark.asyncio
async def test_get_artist_albums_can_request_only_albums(
    monkeypatch,
) -> None:
    client = make_client()
    await install_fake_token(monkeypatch, client)

    fake = FakeAsyncClient(
        make_response(
            200,
            json_data={"items": [], "total": 0},
        )
    )

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: fake,
    )

    await client.get_artist_albums(
        "spotify-artist-123",
        include_groups="album",
    )

    assert fake.last_params["include_groups"] == "album"


@pytest.mark.asyncio
async def test_get_artist_albums_can_request_only_singles(
    monkeypatch,
) -> None:
    client = make_client()
    await install_fake_token(monkeypatch, client)

    fake = FakeAsyncClient(
        make_response(
            200,
            json_data={"items": [], "total": 0},
        )
    )

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: fake,
    )

    await client.get_artist_albums(
        "spotify-artist-123",
        include_groups="single",
    )

    assert fake.last_params["include_groups"] == "single"


@pytest.mark.asyncio
async def test_get_artist_albums_rejects_empty_id() -> None:
    with pytest.raises(
        SpotifyAPIError,
        match="artist ID cannot be empty",
    ):
        await make_client().get_artist_albums("   ")


@pytest.mark.asyncio
async def test_get_artist_albums_rejects_invalid_groups() -> None:
    with pytest.raises(
        SpotifyAPIError,
        match="Invalid Spotify artist album groups",
    ):
        await make_client().get_artist_albums(
            "spotify-artist-123",
            include_groups="invalid",
        )


@pytest.mark.asyncio
async def test_get_artist_albums_limits_page_size(
    monkeypatch,
) -> None:
    client = make_client()
    await install_fake_token(monkeypatch, client)

    fake = FakeAsyncClient(
        make_response(
            200,
            json_data={"items": [], "total": 0},
        )
    )

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: fake,
    )

    await client.get_artist_albums(
        "spotify-artist-123",
        limit=100,
        offset=-5,
    )

    assert fake.last_params["limit"] == 50
    assert fake.last_params["offset"] == 0


@pytest.mark.asyncio
async def test_get_artist_albums_handles_not_found(
    monkeypatch,
) -> None:
    client = make_client()
    await install_fake_token(monkeypatch, client)

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: FakeAsyncClient(make_response(404)),
    )

    with pytest.raises(SpotifyNotFoundError):
        await client.get_artist_albums("missing-artist")


@pytest.mark.asyncio
async def test_get_artist_albums_handles_invalid_json(
    monkeypatch,
) -> None:
    client = make_client()
    await install_fake_token(monkeypatch, client)

    monkeypatch.setattr(
        "app.providers.spotify.client.httpx.AsyncClient",
        lambda: FakeAsyncClient(
            make_response(200, content=b"not-json")
        ),
    )

    with pytest.raises(
        SpotifyAPIError,
        match="invalid artist albums response data",
    ):
        await client.get_artist_albums("spotify-artist-123")