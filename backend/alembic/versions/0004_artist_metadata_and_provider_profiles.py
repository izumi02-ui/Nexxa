"""add artist metadata and provider profile tables

Revision ID: 0004
Revises: 0003
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "artists",
        sa.Column(
            "biography",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "artists",
        sa.Column(
            "genres",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
    )

    op.alter_column(
        "artists",
        "genres",
        server_default=None,
    )

    op.create_table(
        "artist_provider_profiles",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "artist_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "provider",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "external_id",
            sa.String(length=500),
            nullable=False,
        ),
        sa.Column(
            "external_url",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["artist_id"],
            ["artists.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "artist_id",
            "provider",
            name="uq_artist_provider_profile",
        ),
        sa.UniqueConstraint(
            "provider",
            "external_id",
            name="uq_artist_provider_external_id",
        ),
    )

    op.create_index(
        "ix_artist_provider_profiles_artist_id",
        "artist_provider_profiles",
        ["artist_id"],
    )
    op.create_index(
        "ix_artist_provider_profiles_provider",
        "artist_provider_profiles",
        ["provider"],
    )

    op.create_table(
        "spotify_artist_stats",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "artist_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "spotify_artist_id",
            sa.String(length=500),
            nullable=True,
        ),
        sa.Column(
            "spotify_url",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "followers",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "popularity",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "genres",
            sa.JSON(),
            nullable=False,
        ),
        sa.Column(
            "albums",
            sa.JSON(),
            nullable=False,
        ),
        sa.Column(
            "singles",
            sa.JSON(),
            nullable=False,
        ),
        sa.Column(
            "top_tracks",
            sa.JSON(),
            nullable=False,
        ),
        sa.Column(
            "statistics_available",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "statistics_fetched_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["artist_id"],
            ["artists.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_spotify_artist_stats_artist_id",
        "spotify_artist_stats",
        ["artist_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_spotify_artist_stats_artist_id",
        table_name="spotify_artist_stats",
    )
    op.drop_table("spotify_artist_stats")

    op.drop_index(
        "ix_artist_provider_profiles_provider",
        table_name="artist_provider_profiles",
    )
    op.drop_index(
        "ix_artist_provider_profiles_artist_id",
        table_name="artist_provider_profiles",
    )
    op.drop_table("artist_provider_profiles")

    op.drop_column("artists", "genres")
    op.drop_column("artists", "biography")