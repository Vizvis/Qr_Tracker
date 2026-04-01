"""drop production_sessions table

Revision ID: d2c8a17f4e90
Revises: c7a3f6d21b44
Create Date: 2026-04-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "d2c8a17f4e90"
down_revision = "c7a3f6d21b44"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("production_sessions")


def downgrade() -> None:
    op.create_table(
        "production_sessions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("qr_code_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("batch_number", sa.String(), nullable=True),
        sa.Column("product_type", sa.String(), nullable=True),
        sa.Column("product_name", sa.String(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=True),
        sa.Column("session_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("started_by", sa.UUID(), nullable=True),
        sa.Column("closed_by", sa.UUID(), nullable=True),
        sa.Column("voided_by", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["closed_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["qr_code_id"], ["qr_codes.id"]),
        sa.ForeignKeyConstraint(["started_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["voided_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
