"""add is_notified flag and decimal prices

Revision ID: 7d1c2f0a4b56
Revises: 9305012c4c89
Create Date: 2026-11-25 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7d1c2f0a4b56"
down_revision: Union[str, Sequence[str], None] = "9305012c4c89"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("products") as batch_op:
        batch_op.add_column(
            sa.Column(
                "is_notified",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )
        batch_op.alter_column(
            "current_price",
            existing_type=sa.Float(),
            type_=sa.Numeric(10, 2),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "target_price",
            existing_type=sa.Float(),
            type_=sa.Numeric(10, 2),
            existing_nullable=True,
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("products") as batch_op:
        batch_op.alter_column(
            "target_price",
            existing_type=sa.Numeric(10, 2),
            type_=sa.Float(),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "current_price",
            existing_type=sa.Numeric(10, 2),
            type_=sa.Float(),
            existing_nullable=True,
        )
        batch_op.drop_column("is_notified")
