"""create history

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-30
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "history_entries",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "track_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "played_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "position_ms",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "duration_ms",
            sa.Integer(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["track_id"],
            ["tracks.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_history_entries_user_id",
        "history_entries",
        ["user_id"],
    )

    op.create_index(
        "ix_history_entries_track_id",
        "history_entries",
        ["track_id"],
    )

    op.create_index(
        "ix_history_entries_played_at",
        "history_entries",
        ["played_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_history_entries_played_at",
        table_name="history_entries",
    )

    op.drop_index(
        "ix_history_entries_track_id",
        table_name="history_entries",
    )

    op.drop_index(
        "ix_history_entries_user_id",
        table_name="history_entries",
    )

    op.drop_table("history_entries")
