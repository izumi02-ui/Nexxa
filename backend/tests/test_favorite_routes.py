from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.database.session import get_db
from app.music.favorite_routes import (
    get_current_user_id,
    router,
)


app = FastAPI()
app.include_router(router)


def test_add_favorite_requires_authentication() -> None:
    client = TestClient(app)

    response = client.post(
        "/favorites",
        json={"track_id": 1},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_list_favorites_requires_authentication() -> None:
    client = TestClient(app)

    response = client.get("/favorites")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_delete_favorite_requires_authentication() -> None:
    client = TestClient(app)

    response = client.delete("/favorites/1")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"
