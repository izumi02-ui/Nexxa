import pytest
from pydantic import ValidationError

from app.music.favorite_schemas import FavoriteCreate, FavoriteResponse


def test_favorite_create_accepts_valid_track_id() -> None:
    favorite = FavoriteCreate(track_id=1)

    assert favorite.track_id == 1


def test_favorite_create_rejects_zero_track_id() -> None:
    with pytest.raises(ValidationError):
        FavoriteCreate(track_id=0)


def test_favorite_create_rejects_negative_track_id() -> None:
    with pytest.raises(ValidationError):
        FavoriteCreate(track_id=-1)


def test_favorite_response_accepts_expected_data() -> None:
    response = FavoriteResponse(
        id=1,
        user_id=2,
        track_id=3,
        created_at="2026-01-01T00:00:00Z",
    )

    assert response.id == 1
    assert response.user_id == 2
    assert response.track_id == 3
