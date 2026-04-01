"""add unique constraint to remarks for active session duplicates

Revision ID: 8f3c1a2b4d99
Revises: 6a2d9f4b1e77
Create Date: 2026-04-01 00:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "8f3c1a2b4d99"
down_revision = "6a2d9f4b1e77"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Keep only the earliest row for each (qr_id, item_id, department_id) triple.
    op.execute(
        """
        DELETE FROM remarks r
        USING (
            SELECT id
            FROM (
                SELECT
                    id,
                    ROW_NUMBER() OVER (
                        PARTITION BY qr_id, item_id, department_id
                        ORDER BY created_at ASC, id ASC
                    ) AS rn
                FROM remarks
                WHERE qr_id IS NOT NULL
                  AND item_id IS NOT NULL
                  AND department_id IS NOT NULL
            ) dedup
            WHERE dedup.rn > 1
        ) d
        WHERE r.id = d.id
        """
    )

    op.create_unique_constraint(
        "uq_remarks_qr_item_department",
        "remarks",
        ["qr_id", "item_id", "department_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_remarks_qr_item_department", "remarks", type_="unique")
