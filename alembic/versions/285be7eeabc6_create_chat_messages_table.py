"""create chat messages table

Revision ID: 285be7eeabc6
Revises: 510c76d89a1e
Create Date: 2026-09-08 21:19:43.362276

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "285be7eeabc6"
down_revision: Union[str, Sequence[str], None] = "510c76d89a1e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create chat_messages table."""

    op.create_table(
        "chat_messages",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False,
        ),

        sa.Column(
            "session_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "question",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "answer",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["session_id"],
            ["chat_sessions.id"],
            ondelete="CASCADE",
        ),
    )

    op.create_index(
        "ix_chat_messages_id",
        "chat_messages",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_chat_messages_session_id",
        "chat_messages",
        ["session_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop chat_messages table."""

    op.drop_table(
        "chat_messages",
        if_exists=True,
    )