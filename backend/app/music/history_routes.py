from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.database.session import get_db
from app.music.history_service import (
    clear_history,
    create_history_entry,
    delete_history_entry,
    list_history,
)
from app.music.history_schemas import HistoryCreate, HistoryResponse

router = APIRouter(prefix="/history", tags=["history"])


@router.post(
    "",
    response_model=HistoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_history(
    payload: HistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = create_history_entry(
        db=db,
        user_id=current_user.id,
        track_id=payload.track_id,
        position_ms=payload.position_ms,
        duration_ms=payload.duration_ms,
    )

    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found",
        )

    db.commit()
    db.refresh(entry)
    return entry


@router.get("", response_model=list[HistoryResponse])
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_history(db=db, user_id=current_user.id)


@router.delete(
    "/{history_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_history_entry(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = delete_history_entry(
        db=db,
        user_id=current_user.id,
        history_id=history_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History entry not found",
        )

    db.commit()
    return None


@router.delete("", status_code=status.HTTP_200_OK)
def remove_all_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted_count = clear_history(
        db=db,
        user_id=current_user.id,
    )
    db.commit()
    return {"deleted_count": deleted_count}