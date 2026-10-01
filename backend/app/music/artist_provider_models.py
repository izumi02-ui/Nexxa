from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ArtistProviderProfile(Base):
    """Provider-specific profile and external identity for an artist."""

    __tablename__ = "artist_provider_profiles"

    __table_args__ = (
        UniqueConstraint(
            "artist_id",
            "provider",
            name="uq_artist_provider_profile",
        ),
        UniqueConstraint(
            "provider",
            "external_id",
            name="uq_artist_provider_external_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    artist_id: Mapped[int] = mapped_column(
        ForeignKey("artists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    external_id: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    external_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
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
