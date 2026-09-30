from fastapi import FastAPI

from app.api.router import api_router


def test_recommendations_routes_are_registered():
    app = FastAPI()
    app.include_router(api_router)

    paths = {
        route.path: set(route.methods or set())
        for route in app.routes
    }

    assert "/api/v1/recommendations" in paths
    assert "GET" in paths["/api/v1/recommendations"]
