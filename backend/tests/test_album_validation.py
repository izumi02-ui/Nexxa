from datetime import date

import pytest
from pydantic import ValidationError

from app.music.album_schemas import AlbumCreate


def test_album_create_accepts_valid_data() -> None:
    album = AlbumCreate(
        title="Valid Album",
        artist_id=1,
        artwork_url="https://example.com/artwork.jpg",
        release_date=date(2026, 1, 1),
    )

    assert album.title == "Valid Album"
    assert album.artist_id == 1
    assert album.artwork_url == "https://example.com/artwork.jpg"
    assert album.release_date == date(2026, 1, 1)


def test_album_title_cannot_be_empty() -> None:
    with pytest.raises(ValidationError):
        AlbumCreate(
            title="",
            artist_id=1,
        )


def test_album_title_cannot_exceed_500_characters() -> None:
    with pytest.raises(ValidationError):
        AlbumCreate(
            title="A" * 501,
            artist_id=1,
        )


def test_album_artist_id_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        AlbumCreate(
            title="Valid Album",
            artist_id=0,
        )


def test_album_artist_id_cannot_be_negative() -> None:
    with pytest.raises(ValidationError):
        AlbumCreate(
            title="Valid Album",
            artist_id=-1,
        )


def test_album_optional_fields_can_be_omitted() -> None:
    album = AlbumCreate(
        title="Minimal Album",
        artist_id=1,
    )

    assert album.artwork_url is None
    assert album.release_date is None


def test_album_release_date_accepts_valid_date() -> None:
    album = AlbumCreate(
        title="Dated Album",
        artist_id=1,
        release_date=date(2026, 9, 29),
    )

    assert album.release_date == date(2026, 9, 29)
