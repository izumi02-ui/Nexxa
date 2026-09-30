from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.router import api_router


app = FastAPI()
app.include_router(api_router)

client = TestClient(app)


def test_recommendations_route_requires_authentication():
    response = client.get("/api/v1/recommendations")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"
