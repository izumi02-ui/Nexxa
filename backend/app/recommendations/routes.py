from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.database.session import get_db
from app.recommendations.service import get_recommendations


router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"],
)


@router.get("")
def recommendations(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_recommendations(
        db=db,
        user_id=current_user.id,
        limit=limit,
    )
