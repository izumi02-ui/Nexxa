from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.database.session import get_db
from app.music.favorite_schemas import FavoriteCreate, FavoriteResponse
from app.music.favorite_service import (
    create_favorite,
    delete_favorite,
    list_favorites,
)

router = APIRouter(
    prefix="/favorites",
    tags=["favorites"],
)


@router.post(
    "",
    response_model=FavoriteResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_favorite(
    payload: FavoriteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FavoriteResponse:
    favorite = create_favorite(
        db=db,
        user_id=current_user.id,
        track_id=payload.track_id,
    )

    db.commit()
    db.refresh(favorite)

    return FavoriteResponse.model_validate(favorite)


@router.get(
    "",
    response_model=list[FavoriteResponse],
)
def get_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FavoriteResponse]:
    favorites = list_favorites(
        db=db,
        user_id=current_user.id,
    )

    return [
        FavoriteResponse.model_validate(favorite)
        for favorite in favorites
    ]


@router.delete(
    "/{track_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_favorite(
    track_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    deleted = delete_favorite(
        db=db,
        user_id=current_user.id,
        track_id=track_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found",
        )

    db.commit()
