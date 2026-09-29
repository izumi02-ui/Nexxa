from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.router import api_router


app = FastAPI()
app.include_router(api_router)


def test_favorites_routes_are_registered() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/favorites")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"
