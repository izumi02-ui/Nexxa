from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.database.base import Base
from app.database.session import get_db
from app.music.playlist_routes import router as playlist_router


def create_test_database():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine


def create_test_app(engine, user: User | None = None):
    app = FastAPI()
    app.include_router(playlist_router)

    def override_get_db():
        with Session(engine) as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db

    if user is not None:
        app.dependency_overrides[get_current_user] = lambda: user

    return app


def create_user(engine, email: str) -> User:
    with Session(engine) as db:
        user = User(
            email=email,
            password_hash="hashed-password",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


def test_create_playlist_route() -> None:
    engine = create_test_database()
    user = create_user(engine, "create-route@example.com")
    app = create_test_app(engine, user)
    client = TestClient(app)

    response = client.post(
        "/playlists",
        json={
            "name": "My Playlist",
            "description": "Test playlist",
            "artwork_url": "https://example.com/artwork.jpg",
            "is_public": False,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] > 0
    assert data["user_id"] == user.id
    assert data["name"] == "My Playlist"
    assert data["description"] == "Test playlist"
    assert data["artwork_url"] == "https://example.com/artwork.jpg"
    assert data["is_public"] is False


def test_list_playlists_route_only_returns_current_users_playlists() -> None:
    engine = create_test_database()
    user = create_user(engine, "list-route@example.com")

    other_user = create_user(
        engine,
        "other-list-route@example.com",
    )

    app = create_test_app(engine, user)
    client = TestClient(app)

    client.post(
        "/playlists",
        json={
            "name": "My Playlist",
        },
    )

    other_app = create_test_app(engine, other_user)
    other_client = TestClient(other_app)

    other_client.post(
        "/playlists",
        json={
            "name": "Other Playlist",
        },
    )

    response = client.get("/playlists")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "My Playlist"
    assert data[0]["user_id"] == user.id


def test_get_playlist_route() -> None:
    engine = create_test_database()
    user = create_user(engine, "get-route@example.com")
    app = create_test_app(engine, user)
    client = TestClient(app)

    create_response = client.post(
        "/playlists",
        json={
            "name": "Get Playlist",
        },
    )

    playlist_id = create_response.json()["id"]

    response = client.get(
        f"/playlists/{playlist_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == playlist_id
    assert data["name"] == "Get Playlist"
    assert data["user_id"] == user.id


def test_get_missing_playlist_returns_404() -> None:
    engine = create_test_database()
    user = create_user(engine, "missing-route@example.com")
    app = create_test_app(engine, user)
    client = TestClient(app)

    response = client.get("/playlists/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Playlist not found"


def test_get_another_users_playlist_returns_404() -> None:
    engine = create_test_database()

    owner = create_user(
        engine,
        "route-owner@example.com",
    )

    other_user = create_user(
        engine,
        "route-other@example.com",
    )

    owner_app = create_test_app(engine, owner)
    owner_client = TestClient(owner_app)

    create_response = owner_client.post(
        "/playlists",
        json={
            "name": "Private Playlist",
        },
    )

    playlist_id = create_response.json()["id"]

    other_app = create_test_app(engine, other_user)
    other_client = TestClient(other_app)

    response = other_client.get(
        f"/playlists/{playlist_id}",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Playlist not found"


def test_update_playlist_route() -> None:
    engine = create_test_database()
    user = create_user(engine, "update-route@example.com")
    app = create_test_app(engine, user)
    client = TestClient(app)

    create_response = client.post(
        "/playlists",
        json={
            "name": "Original Playlist",
        },
    )

    playlist_id = create_response.json()["id"]

    response = client.put(
        f"/playlists/{playlist_id}",
        json={
            "name": "Updated Playlist",
            "description": "Updated description",
            "artwork_url": "https://example.com/updated.jpg",
            "is_public": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == playlist_id
    assert data["name"] == "Updated Playlist"
    assert data["description"] == "Updated description"
    assert data["artwork_url"] == "https://example.com/updated.jpg"
    assert data["is_public"] is True


def test_update_another_users_playlist_returns_404() -> None:
    engine = create_test_database()

    owner = create_user(
        engine,
        "update-owner-route@example.com",
    )

    other_user = create_user(
        engine,
        "update-other-route@example.com",
    )

    owner_app = create_test_app(engine, owner)
    owner_client = TestClient(owner_app)

    create_response = owner_client.post(
        "/playlists",
        json={
            "name": "Owner Playlist",
        },
    )

    playlist_id = create_response.json()["id"]

    other_app = create_test_app(engine, other_user)
    other_client = TestClient(other_app)

    response = other_client.put(
        f"/playlists/{playlist_id}",
        json={
            "name": "Unauthorized Update",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Playlist not found"


def test_delete_playlist_route() -> None:
    engine = create_test_database()
    user = create_user(engine, "delete-route@example.com")
    app = create_test_app(engine, user)
    client = TestClient(app)

    create_response = client.post(
        "/playlists",
        json={
            "name": "Delete Playlist",
        },
    )

    playlist_id = create_response.json()["id"]

    response = client.delete(
        f"/playlists/{playlist_id}",
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/playlists/{playlist_id}",
    )

    assert get_response.status_code == 404


def test_delete_another_users_playlist_returns_404() -> None:
    engine = create_test_database()

    owner = create_user(
        engine,
        "delete-owner-route@example.com",
    )

    other_user = create_user(
        engine,
        "delete-other-route@example.com",
    )

    owner_app = create_test_app(engine, owner)
    owner_client = TestClient(owner_app)

    create_response = owner_client.post(
        "/playlists",
        json={
            "name": "Protected Playlist",
        },
    )

    playlist_id = create_response.json()["id"]

    other_app = create_test_app(engine, other_user)
    other_client = TestClient(other_app)

    response = other_client.delete(
        f"/playlists/{playlist_id}",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Playlist not found"

    owner_response = owner_client.get(
        f"/playlists/{playlist_id}",
    )

    assert owner_response.status_code == 200


def test_playlist_routes_require_authentication() -> None:
    engine = create_test_database()
    app = create_test_app(engine)
    client = TestClient(app)

    response = client.get("/playlists")

    assert response.status_code == 401


def test_create_playlist_validates_required_name() -> None:
    engine = create_test_database()
    user = create_user(engine, "validation-route@example.com")
    app = create_test_app(engine, user)
    client = TestClient(app)

    response = client.post(
        "/playlists",
        json={},
    )

    assert response.status_code == 422


def test_create_playlist_rejects_empty_name() -> None:
    engine = create_test_database()
    user = create_user(engine, "empty-name-route@example.com")
    app = create_test_app(engine, user)
    client = TestClient(app)

    response = client.post(
        "/playlists",
        json={
            "name": "",
        },
    )

    assert response.status_code == 422


def test_create_playlist_rejects_unknown_fields() -> None:
    engine = create_test_database()
    user = create_user(engine, "extra-field-route@example.com")
    app = create_test_app(engine, user)
    client = TestClient(app)

    response = client.post(
        "/playlists",
        json={
            "name": "Valid Playlist",
            "unexpected": "field",
        },
    )

    assert response.status_code == 422
