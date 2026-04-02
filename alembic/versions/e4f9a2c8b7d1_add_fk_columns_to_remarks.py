"""add qr and department foreign keys to remarks

Revision ID: e4f9a2c8b7d1
Revises: d2c8a17f4e90
Create Date: 2026-04-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e4f9a2c8b7d1"
down_revision = "d2c8a17f4e90"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("remarks", sa.Column("qr_id", sa.String(), nullable=True))
    op.add_column("remarks", sa.Column("department_id", sa.UUID(), nullable=True))

    op.create_foreign_key(
        "fk_remarks_qr_id_qr_codes",
        "remarks",
        "qr_codes",
        ["qr_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_remarks_department_id_department",
        "remarks",
        "department",
        ["department_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_remarks_department_id_department", "remarks", type_="foreignkey")
    op.drop_constraint("fk_remarks_qr_id_qr_codes", "remarks", type_="foreignkey")

    op.drop_column("remarks", "department_id")
    op.drop_column("remarks", "qr_id")
