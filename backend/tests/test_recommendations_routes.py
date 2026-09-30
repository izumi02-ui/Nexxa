from fastapi import FastAPI

from app.recommendations.routes import router


def test_recommendations_routes_are_registered():
    app = FastAPI()
    app.include_router(
        router,
        prefix="/api/v1",
    )

    paths = {
        route.path: set(route.methods or set())
        for route in app.routes
        if hasattr(route, "path")
    }

    assert "/api/v1/recommendations" in paths
    assert "GET" in paths["/api/v1/recommendations"]
