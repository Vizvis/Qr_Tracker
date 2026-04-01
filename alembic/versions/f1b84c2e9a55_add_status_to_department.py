"""add status to department

Revision ID: f1b84c2e9a55
Revises: e4f9a2c8b7d1
Create Date: 2026-04-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f1b84c2e9a55"
down_revision = "e4f9a2c8b7d1"
branch_labels = None
depends_on = None


department_status_enum = sa.Enum("active", "inactive", name="departmentstatus")


def upgrade() -> None:
    department_status_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "department",
        sa.Column("status", department_status_enum, nullable=True),
    )

    op.execute("UPDATE department SET status = 'active' WHERE status IS NULL")

    op.alter_column("department", "status", nullable=False)


def downgrade() -> None:
    op.drop_column("department", "status")
    department_status_enum.drop(op.get_bind(), checkfirst=True)
