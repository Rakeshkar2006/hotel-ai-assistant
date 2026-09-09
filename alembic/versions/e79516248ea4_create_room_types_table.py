"""create room types table

Revision ID: e79516248ea4
Revises: 4afa56de4722
Create Date: 2026-09-04 22:32:29.460493

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e79516248ea4"
down_revision: Union[str, Sequence[str], None] = "4afa56de4722"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Rename existing columns instead of deleting their data.
    op.alter_column(
        "room_types",
        "price_per_night",
        new_column_name="base_price",
        existing_type=sa.Integer(),
        type_=sa.Float(),
        existing_nullable=False,
    )

    op.alter_column(
        "room_types",
        "capacity",
        new_column_name="max_guests",
        existing_type=sa.Integer(),
        existing_nullable=False,
    )

    op.alter_column(
        "room_types",
        "description",
        existing_type=sa.TEXT(),
        type_=sa.String(length=500),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "room_types",
        "description",
        existing_type=sa.String(length=500),
        type_=sa.TEXT(),
        existing_nullable=True,
    )

    op.alter_column(
        "room_types",
        "max_guests",
        new_column_name="capacity",
        existing_type=sa.Integer(),
        existing_nullable=False,
    )

    op.alter_column(
        "room_types",
        "base_price",
        new_column_name="price_per_night",
        existing_type=sa.Float(),
        type_=sa.Integer(),
        existing_nullable=False,
    )