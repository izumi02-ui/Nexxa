from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.security import create_access_token
from app.database.base import Base
from app.main import app


def test_favorites_requires_authentication() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/favorites")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_favorites_rejects_invalid_token() -> None:
    client = TestClient(app)

    response = client.get(
        "/api/v1/favorites",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"
