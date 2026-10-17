
"""add YouTube artist total views

Revision ID: 0006
Revises: 0005
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "youtube_artist_stats",
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
            "total_views",
            sa.Integer(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["artist_id"],
            ["artists.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_youtube_artist_stats_artist_id",
        "youtube_artist_stats",
        ["artist_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_youtube_artist_stats_artist_id",
        table_name="youtube_artist_stats",
    )
    op.drop_table("youtube_artist_stats")
