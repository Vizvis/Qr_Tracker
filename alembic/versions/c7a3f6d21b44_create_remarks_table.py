"""create remarks table

Revision ID: c7a3f6d21b44
Revises: 9d41c2e5a1f0
Create Date: 2026-04-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c7a3f6d21b44"
down_revision = "9d41c2e5a1f0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "remarks",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("general_remarks", sa.String(), nullable=True),
        sa.Column("issue_remarks", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("remarks")
