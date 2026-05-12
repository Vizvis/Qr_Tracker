"""add activated_by, activated_at, released_by, released_at to produced_items

Revision ID: a4b9c2d3e5f6
Revises: f40ba6a7dad8
Create Date: 2026-05-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'a4b9c2d3e5f6'
down_revision = 'f40ba6a7dad8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('produced_items', sa.Column('activated_by', UUID(), nullable=True))
    op.add_column('produced_items', sa.Column('activated_at', sa.DateTime(), nullable=True))
    op.add_column('produced_items', sa.Column('released_by', UUID(), nullable=True))
    op.add_column('produced_items', sa.Column('released_at', sa.DateTime(), nullable=True))
    op.create_foreign_key(
        'produced_items_activated_by_fkey',
        'produced_items', 'users',
        ['activated_by'], ['id'],
    )
    op.create_foreign_key(
        'produced_items_released_by_fkey',
        'produced_items', 'users',
        ['released_by'], ['id'],
    )


def downgrade() -> None:
    op.drop_constraint('produced_items_released_by_fkey', 'produced_items', type_='foreignkey')
    op.drop_constraint('produced_items_activated_by_fkey', 'produced_items', type_='foreignkey')
    op.drop_column('produced_items', 'released_at')
    op.drop_column('produced_items', 'released_by')
    op.drop_column('produced_items', 'activated_at')
    op.drop_column('produced_items', 'activated_by')
