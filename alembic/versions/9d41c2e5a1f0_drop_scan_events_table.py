"""drop scan_events table

Revision ID: 9d41c2e5a1f0
Revises: 66285b8d0b09
Create Date: 2026-04-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9d41c2e5a1f0"
down_revision = "66285b8d0b09"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("scan_events")


def downgrade() -> None:
    op.create_table(
        "scan_events",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("session_id", sa.UUID(), nullable=False),
        sa.Column("qr_code_id", sa.UUID(), nullable=False),
        sa.Column("scanned_by", sa.UUID(), nullable=False),
        sa.Column("department", sa.UUID(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("scanned_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["department"], ["department.id"]),
        sa.ForeignKeyConstraint(["qr_code_id"], ["qr_codes.id"]),
        sa.ForeignKeyConstraint(["scanned_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["session_id"], ["production_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
