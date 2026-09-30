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


def test_history_list_route_is_registered() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/history")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_history_create_route_is_registered() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/history",
        json={
            "track_id": 1,
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_history_delete_route_is_registered() -> None:
    client = TestClient(app)

    response = client.delete("/api/v1/history/1")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_history_clear_route_is_registered() -> None:
    client = TestClient(app)

    response = client.delete("/api/v1/history")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"
