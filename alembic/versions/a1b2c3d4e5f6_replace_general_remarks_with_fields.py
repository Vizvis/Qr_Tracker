"""Replace general_remarks with field_1..5 integer columns.

Revision ID: a1b2c3d4e5f6
Revises: 8c24cc53fef0
Create Date: 2026-05-09

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'c89a2607b01e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- remarks table ---
    # Drop old column
    op.drop_column('remarks', 'general_remarks')
    # Add new integer columns
    op.add_column('remarks', sa.Column('field_1', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('remarks', sa.Column('field_2', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('remarks', sa.Column('field_3', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('remarks', sa.Column('field_4', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('remarks', sa.Column('field_5', sa.Integer(), nullable=True, server_default='0'))

    # --- produced_items table ---
    op.drop_column('produced_items', 'general_remarks')
    op.add_column('produced_items', sa.Column('field_1', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('produced_items', sa.Column('field_2', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('produced_items', sa.Column('field_3', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('produced_items', sa.Column('field_4', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('produced_items', sa.Column('field_5', sa.Integer(), nullable=True, server_default='0'))


def downgrade() -> None:
    # --- produced_items table ---
    op.drop_column('produced_items', 'field_5')
    op.drop_column('produced_items', 'field_4')
    op.drop_column('produced_items', 'field_3')
    op.drop_column('produced_items', 'field_2')
    op.drop_column('produced_items', 'field_1')
    op.add_column('produced_items', sa.Column('general_remarks', sa.String(), nullable=True))

    # --- remarks table ---
    op.drop_column('remarks', 'field_5')
    op.drop_column('remarks', 'field_4')
    op.drop_column('remarks', 'field_3')
    op.drop_column('remarks', 'field_2')
    op.drop_column('remarks', 'field_1')
    op.add_column('remarks', sa.Column('general_remarks', sa.String(), nullable=True))
