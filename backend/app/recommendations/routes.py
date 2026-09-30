from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.recommendations.service import get_recommendations


router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"],
)


@router.get("")
def recommendations(
    track_ids: list[int] = Query(default=[]),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return get_recommendations(
        db=db,
        track_ids=track_ids,
        limit=limit,
    )
