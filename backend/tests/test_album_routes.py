from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.router import api_router


app = FastAPI()
app.include_router(api_router)


def test_create_album_requires_valid_artist() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/albums",
        json={
            "title": "Test Album",
            "artist_id": 999999,
        },
    )

    assert response.status_code in {400, 404, 422, 500}
