from fastapi import FastAPI

from app.api.router import api_router


def test_album_routes_are_registered() -> None:
    app = FastAPI()
    app.include_router(api_router)

    routes = {
        (
            route.path,
            frozenset(route.methods or set()),
        )
        for route in app.routes
        if hasattr(route, "path")
    }

    assert (
        "/api/v1/albums",
        frozenset({"POST"}),
    ) in routes

    assert (
        "/api/v1/albums",
        frozenset({"GET"}),
    ) in routes

    assert (
        "/api/v1/albums/{album_id}",
        frozenset({"GET"}),
    ) in routes

    assert (
        "/api/v1/albums/{album_id}/tracks",
        frozenset({"GET"}),
    ) in routes
