from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.router import api_router


app = FastAPI()
app.include_router(api_router)


def test_favorites_requires_authentication() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/favorites")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_favorites_rejects_invalid_token() -> None:
    client = TestClient(app)

    response = client.get(
        "/api/v1/favorites",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"
