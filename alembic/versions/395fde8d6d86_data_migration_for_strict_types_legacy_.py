"""Data migration for strict types legacy data

Revision ID: 395fde8d6d86
Revises: 531ffbc49d1b
Create Date: 2026-04-02 17:03:10.989649

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '395fde8d6d86'
down_revision = '531ffbc49d1b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
