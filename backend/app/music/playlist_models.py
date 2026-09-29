from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Playlist(Base):
    """Canonical NEXXA playlist entity."""

    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    artwork_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_public: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class PlaylistTrack(Base):
    """Track membership and ordering within a playlist."""

    __tablename__ = "playlist_tracks"

    __table_args__ = (
        UniqueConstraint(
            "playlist_id",
            "track_id",
            name="uq_playlist_track",
        ),
        UniqueConstraint(
            "playlist_id",
            "position",
            name="uq_playlist_position",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    playlist_id: Mapped[int] = mapped_column(
        ForeignKey("playlists.id"),
        nullable=False,
        index=True,
    )

    track_id: Mapped[int] = mapped_column(
        ForeignKey("tracks.id"),
        nullable=False,
        index=True,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )