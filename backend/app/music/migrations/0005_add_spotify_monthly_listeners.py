"""add spotify monthly listeners

Revision ID: 0005
Revises: 0004
"""

from alembic import op
import sqlalchemy as sa


revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "spotify_artist_stats",
        sa.Column(
            "monthly_listeners",
            sa.Integer(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "spotify_artist_stats",
        "monthly_listeners",
    )
