"""add YouTube statistics retrieval timestamp

Revision ID: 0008
Revises: 0007
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "youtube_artist_stats",
        sa.Column(
            "statistics_fetched_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "youtube_artist_stats",
        "statistics_fetched_at",
    )