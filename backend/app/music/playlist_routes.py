from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.database.session import get_db
from app.music.playlist_schemas import (
    PlaylistCreate,
    PlaylistResponse,
)
from app.music.playlist_service import (
    create_playlist,
    delete_playlist,
    get_playlist,
    list_playlists,
    update_playlist,
)

router = APIRouter(
    prefix="/playlists",
    tags=["playlists"],
)


@router.post(
    "",
    response_model=PlaylistResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_playlist(
    payload: PlaylistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PlaylistResponse:
    playlist = create_playlist(
        db=db,
        user_id=current_user.id,
        name=payload.name,
        description=payload.description,
        artwork_url=payload.artwork_url,
        is_public=payload.is_public,
    )

    db.commit()
    db.refresh(playlist)

    return PlaylistResponse.model_validate(playlist)


@router.get(
    "",
    response_model=list[PlaylistResponse],
)
def get_playlists(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[PlaylistResponse]:
    playlists = list_playlists(
        db=db,
        user_id=current_user.id,
    )

    return [
        PlaylistResponse.model_validate(playlist)
        for playlist in playlists
    ]


@router.get(
    "/{playlist_id}",
    response_model=PlaylistResponse,
)
def get_playlist_by_id(
    playlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PlaylistResponse:
    playlist = get_playlist(
        db=db,
        user_id=current_user.id,
        playlist_id=playlist_id,
    )

    if playlist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found",
        )

    return PlaylistResponse.model_validate(playlist)


@router.put(
    "/{playlist_id}",
    response_model=PlaylistResponse,
)
def edit_playlist(
    playlist_id: int,
    payload: PlaylistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PlaylistResponse:
    playlist = update_playlist(
        db=db,
        user_id=current_user.id,
        playlist_id=playlist_id,
        name=payload.name,
        description=payload.description,
        artwork_url=payload.artwork_url,
        is_public=payload.is_public,
    )

    if playlist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found",
        )

    db.commit()
    db.refresh(playlist)

    return PlaylistResponse.model_validate(playlist)


@router.delete(
    "/{playlist_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_playlist(
    playlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    deleted = delete_playlist(
        db=db,
        user_id=current_user.id,
        playlist_id=playlist_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found",
        )

    db.commit()
