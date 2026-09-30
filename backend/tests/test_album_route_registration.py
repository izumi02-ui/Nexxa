from app.main import app


def test_album_routes_are_registered() -> None:
    paths = app.openapi()["paths"]

    assert "/api/v1/albums" in paths
    assert "get" in paths["/api/v1/albums"]
    assert "post" in paths["/api/v1/albums"]

    assert "/api/v1/albums/{album_id}" in paths
    assert "get" in paths["/api/v1/albums/{album_id}"]

    assert "/api/v1/albums/{album_id}/tracks" in paths
    assert "get" in paths["/api/v1/albums/{album_id}/tracks"]
