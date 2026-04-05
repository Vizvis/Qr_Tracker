"""replace_department_id_with_department_name_in_produced_items

Revision ID: c89a2607b01e
Revises: e404eb2b2f1c
Create Date: 2026-04-05 18:07:29.132396

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c89a2607b01e'
down_revision = 'e404eb2b2f1c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add department_name as nullable first (to allow backfill)
    op.add_column('produced_items', sa.Column('department_name', sa.String(), nullable=True))

    # 2. Backfill: resolve department_id -> department.name for existing rows
    op.execute("""
        UPDATE produced_items
        SET department_name = d.name
        FROM department d
        WHERE produced_items.department_id = d.id
    """)

    # 3. Any rows where the department was deleted get 'Unknown'
    op.execute("""
        UPDATE produced_items
        SET department_name = 'Unknown'
        WHERE department_name IS NULL
    """)

    # 4. Make department_name NOT NULL now that all rows have a value
    op.alter_column('produced_items', 'department_name', nullable=False)

    # 5. Drop the old FK and column
    op.drop_constraint('produced_items_department_id_fkey', 'produced_items', type_='foreignkey')
    op.drop_column('produced_items', 'department_id')


def downgrade() -> None:
    op.add_column('produced_items', sa.Column('department_id', sa.UUID(), autoincrement=False, nullable=True))

    # Best-effort: try to resolve department_name back to department.id
    op.execute("""
        UPDATE produced_items
        SET department_id = d.id
        FROM department d
        WHERE produced_items.department_name = d.name
    """)

    op.alter_column('produced_items', 'department_id', nullable=False)
    op.create_foreign_key('produced_items_department_id_fkey', 'produced_items', 'department', ['department_id'], ['id'])
    op.drop_column('produced_items', 'department_name')
