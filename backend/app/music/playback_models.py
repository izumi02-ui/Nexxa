from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class PlaybackState(Base):
    """Persistent playback state for a NEXXA user."""

    __tablename__ = "playback_states"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        unique=True,
    )

    track_id: Mapped[int | None] = mapped_column(
        ForeignKey("tracks.id"),
        nullable=True,
    )

    position_ms: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    is_playing: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )