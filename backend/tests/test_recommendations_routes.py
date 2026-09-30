from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.recommendations.routes import router


app = FastAPI()
app.include_router(
    router,
    prefix="/api/v1",
)

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
