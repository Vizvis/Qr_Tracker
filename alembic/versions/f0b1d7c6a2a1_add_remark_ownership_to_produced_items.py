"""add remark ownership to produced_items

Revision ID: f0b1d7c6a2a1
Revises: a2c9e1d4f7b0
Create Date: 2026-04-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f0b1d7c6a2a1"
down_revision = "a2c9e1d4f7b0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("produced_items", sa.Column("remark_by", sa.UUID(), nullable=True))
    op.add_column("produced_items", sa.Column("remark_updated", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "produced_items_remark_by_fkey",
        "produced_items",
        "users",
        ["remark_by"],
        ["id"],
    )
    op.create_foreign_key(
        "produced_items_remark_updated_fkey",
        "produced_items",
        "users",
        ["remark_updated"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("produced_items_remark_updated_fkey", "produced_items", type_="foreignkey")
    op.drop_constraint("produced_items_remark_by_fkey", "produced_items", type_="foreignkey")
    op.drop_column("produced_items", "remark_updated")
    op.drop_column("produced_items", "remark_by")