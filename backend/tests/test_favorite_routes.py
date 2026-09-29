from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.router import api_router


app = FastAPI()
app.include_router(api_router)


def test_add_favorite_requires_authentication() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/favorites",
        json={"track_id": 1},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_list_favorites_requires_authentication() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/favorites")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_delete_favorite_requires_authentication() -> None:
    client = TestClient(app)

    response = client.delete("/api/v1/favorites/1")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"
