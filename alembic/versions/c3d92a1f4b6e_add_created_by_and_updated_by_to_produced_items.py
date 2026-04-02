"""add created_by and updated_by to produced_items

Revision ID: c3d92a1f4b6e
Revises: f0b1d7c6a2a1
Create Date: 2026-04-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c3d92a1f4b6e"
down_revision = "f0b1d7c6a2a1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("produced_items", sa.Column("created_by", sa.UUID(), nullable=True))
    op.add_column("produced_items", sa.Column("updated_by", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "produced_items_created_by_fkey",
        "produced_items",
        "users",
        ["created_by"],
        ["id"],
    )
    op.create_foreign_key(
        "produced_items_updated_by_fkey",
        "produced_items",
        "users",
        ["updated_by"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("produced_items_updated_by_fkey", "produced_items", type_="foreignkey")
    op.drop_constraint("produced_items_created_by_fkey", "produced_items", type_="foreignkey")
    op.drop_column("produced_items", "updated_by")
    op.drop_column("produced_items", "created_by")
