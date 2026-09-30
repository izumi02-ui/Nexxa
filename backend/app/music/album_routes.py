from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.music.album_schemas import AlbumCreate, AlbumResponse
from app.music.album_service import create_album, get_album, list_albums

router = APIRouter(
    prefix="/albums",
    tags=["albums"],
)


@router.post(
    "",
    response_model=AlbumResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_album(
    payload: AlbumCreate,
    db: Session = Depends(get_db),
) -> AlbumResponse:
    album = create_album(
        db=db,
        data=payload,
    )

    db.commit()
    db.refresh(album)

    return AlbumResponse.model_validate(album)


@router.get(
    "",
    response_model=list[AlbumResponse],
)
def get_albums(
    db: Session = Depends(get_db),
) -> list[AlbumResponse]:
    albums = list_albums(db=db)

    return [
        AlbumResponse.model_validate(album)
        for album in albums
    ]


@router.get(
    "/{album_id}",
    response_model=AlbumResponse,
)
def get_album_by_id(
    album_id: int,
    db: Session = Depends(get_db),
) -> AlbumResponse:
    album = get_album(
        db=db,
        album_id=album_id,
    )

    if album is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Album not found",
        )

    return AlbumResponse.model_validate(album)
