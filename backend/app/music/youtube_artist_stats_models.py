
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class YouTubeArtistStats(Base):
    """Persisted YouTube total-view statistic for a canonical artist."""

    __tablename__ = "youtube_artist_stats"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    artist_id: Mapped[int] = mapped_column(
        ForeignKey("artists.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    total_views: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
