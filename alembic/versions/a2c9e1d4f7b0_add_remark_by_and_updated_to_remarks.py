"""add remark_by and remark_updated to remarks

Revision ID: a2c9e1d4f7b0
Revises: 8f3c1a2b4d99
Create Date: 2026-04-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a2c9e1d4f7b0"
down_revision = "8f3c1a2b4d99"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("remarks", sa.Column("remark_by", sa.UUID(), nullable=True))
    op.add_column("remarks", sa.Column("remark_updated", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "remarks_remark_by_fkey",
        "remarks",
        "users",
        ["remark_by"],
        ["id"],
    )
    op.create_foreign_key(
        "remarks_remark_updated_fkey",
        "remarks",
        "users",
        ["remark_updated"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("remarks_remark_updated_fkey", "remarks", type_="foreignkey")
    op.drop_constraint("remarks_remark_by_fkey", "remarks", type_="foreignkey")
    op.drop_column("remarks", "remark_updated")
    op.drop_column("remarks", "remark_by")
