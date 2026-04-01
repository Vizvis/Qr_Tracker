"""add item_id to remarks

Revision ID: 6a2d9f4b1e77
Revises: 3e4b2a8f1c66
Create Date: 2026-04-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6a2d9f4b1e77"
down_revision = "3e4b2a8f1c66"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("remarks", sa.Column("item_id", sa.String(), nullable=True))
    op.execute("UPDATE remarks SET item_id = COALESCE(item_id, 'legacy-item')")
    op.alter_column("remarks", "item_id", nullable=False)


def downgrade() -> None:
    op.drop_column("remarks", "item_id")
