"""add disabled tracking to qr_codes

Revision ID: d7e5a1b9c2f3
Revises: c3d92a1f4b6e
Create Date: 2026-04-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d7e5a1b9c2f3"
down_revision = "c3d92a1f4b6e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("qr_codes", sa.Column("disabled_by", sa.UUID(), nullable=True))
    op.add_column("qr_codes", sa.Column("disabled_at", sa.DateTime(), nullable=True))
    op.create_foreign_key(
        "qr_codes_disabled_by_fkey",
        "qr_codes",
        "users",
        ["disabled_by"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("qr_codes_disabled_by_fkey", "qr_codes", type_="foreignkey")
    op.drop_column("qr_codes", "disabled_at")
    op.drop_column("qr_codes", "disabled_by")
