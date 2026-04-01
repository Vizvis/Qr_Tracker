"""add created_at to remarks

Revision ID: b8f14e2c3a11
Revises: f1b84c2e9a55
Create Date: 2026-04-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b8f14e2c3a11"
down_revision = "f1b84c2e9a55"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("remarks", sa.Column("created_at", sa.DateTime(), nullable=True))

    op.execute("UPDATE remarks SET created_at = NOW() WHERE created_at IS NULL")

    op.alter_column("remarks", "created_at", nullable=False)


def downgrade() -> None:
    op.drop_column("remarks", "created_at")
