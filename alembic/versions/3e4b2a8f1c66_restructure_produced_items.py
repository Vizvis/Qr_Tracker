"""restructure produced_items to per-department remark shape

Revision ID: 3e4b2a8f1c66
Revises: 907b33b5cb54
Create Date: 2026-04-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3e4b2a8f1c66"
down_revision = "907b33b5cb54"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("produced_items", sa.Column("qr_id", sa.String(), nullable=True))
    op.add_column("produced_items", sa.Column("department_id", sa.UUID(), nullable=True))
    op.add_column("produced_items", sa.Column("general_remarks", sa.String(), nullable=True))
    op.add_column("produced_items", sa.Column("issue_remarks", sa.String(), nullable=True))
    op.add_column("produced_items", sa.Column("created_at", sa.DateTime(), nullable=True))

    op.execute("UPDATE produced_items SET qr_id = qr_code_id WHERE qr_id IS NULL")
    op.execute("UPDATE produced_items SET department_id = final_department WHERE department_id IS NULL")
    op.execute("UPDATE produced_items SET created_at = COALESCE(produced_date, NOW()) WHERE created_at IS NULL")

    op.execute("ALTER TABLE produced_items DROP CONSTRAINT IF EXISTS produced_items_qr_code_id_fkey")
    op.execute("ALTER TABLE produced_items DROP CONSTRAINT IF EXISTS produced_items_approval_id_fkey")
    op.execute("ALTER TABLE produced_items DROP CONSTRAINT IF EXISTS produced_items_final_department_fkey")

    op.drop_column("produced_items", "qr_code_id")
    op.drop_column("produced_items", "approval_id")
    op.drop_column("produced_items", "produced_date")
    op.drop_column("produced_items", "final_department")

    op.alter_column("produced_items", "qr_id", nullable=False)
    op.alter_column("produced_items", "department_id", nullable=False)
    op.alter_column("produced_items", "created_at", nullable=False)

    op.create_foreign_key(
        "produced_items_qr_id_fkey",
        "produced_items",
        "qr_codes",
        ["qr_id"],
        ["id"],
    )
    op.create_foreign_key(
        "produced_items_department_id_fkey",
        "produced_items",
        "department",
        ["department_id"],
        ["id"],
    )


def downgrade() -> None:
    op.add_column("produced_items", sa.Column("qr_code_id", sa.String(), nullable=True))
    op.add_column("produced_items", sa.Column("approval_id", sa.UUID(), nullable=True))
    op.add_column("produced_items", sa.Column("produced_date", sa.DateTime(), nullable=True))
    op.add_column("produced_items", sa.Column("final_department", sa.UUID(), nullable=True))

    op.execute("UPDATE produced_items SET qr_code_id = qr_id WHERE qr_code_id IS NULL")
    op.execute("UPDATE produced_items SET final_department = department_id WHERE final_department IS NULL")
    op.execute("UPDATE produced_items SET produced_date = COALESCE(created_at, NOW()) WHERE produced_date IS NULL")

    op.execute("ALTER TABLE produced_items DROP CONSTRAINT IF EXISTS produced_items_qr_id_fkey")
    op.execute("ALTER TABLE produced_items DROP CONSTRAINT IF EXISTS produced_items_department_id_fkey")

    op.drop_column("produced_items", "general_remarks")
    op.drop_column("produced_items", "issue_remarks")
    op.drop_column("produced_items", "created_at")
    op.drop_column("produced_items", "qr_id")
    op.drop_column("produced_items", "department_id")

    op.alter_column("produced_items", "qr_code_id", nullable=False)
    op.alter_column("produced_items", "approval_id", nullable=False)
    op.alter_column("produced_items", "final_department", nullable=False)

    op.create_foreign_key(
        "produced_items_qr_code_id_fkey",
        "produced_items",
        "qr_codes",
        ["qr_code_id"],
        ["id"],
    )
    op.create_foreign_key(
        "produced_items_approval_id_fkey",
        "produced_items",
        "users",
        ["approval_id"],
        ["id"],
    )
    op.create_foreign_key(
        "produced_items_final_department_fkey",
        "produced_items",
        "department",
        ["final_department"],
        ["id"],
    )
