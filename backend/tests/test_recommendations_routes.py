from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_recommendations_route_is_registered():
    response = client.get("/api/v1/recommendations")

    assert response.status_code != 404


def test_recommendations_accepts_limit():
    response = client.get(
        "/api/v1/recommendations",
        params={"limit": 5},
    )

    assert response.status_code != 404
