from sqlalchemy import inspect

from app.music.favorite_models import Favorite


def test_favorite_model_has_expected_table() -> None:
    assert Favorite.__tablename__ == "favorites"


def test_favorite_has_expected_foreign_keys() -> None:
    mapper = inspect(Favorite)

    foreign_keys = {
        foreign_key.target_fullname
        for column in mapper.columns
        for foreign_key in column.foreign_keys
    }

    assert "users.id" in foreign_keys
    assert "tracks.id" in foreign_keys


def test_favorite_has_unique_user_track_constraint() -> None:
    table = Favorite.__table__

    unique_constraints = [
        constraint
        for constraint in table.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    ]

    assert any(
        {
            column.name
            for column in constraint.columns
        }
        == {"user_id", "track_id"}
        for constraint in unique_constraints
    )
