from fastapi import FastAPI

from app.api.router import api_router


def test_album_routes_are_registered() -> None:
    app = FastAPI()
    app.include_router(api_router)

    routes = {
        (route.path, tuple(route.methods or []))
        for route in app.routes
    }

    assert (
        "/api/v1/albums",
        ("POST",),
    ) in routes

    assert (
        "/api/v1/albums",
        ("GET",),
    ) in routes

    assert (
        "/api/v1/albums/{album_id}",
        ("GET",),
    ) in routes

    assert (
        "/api/v1/albums/{album_id}/tracks",
        ("GET",),
    ) in routes
