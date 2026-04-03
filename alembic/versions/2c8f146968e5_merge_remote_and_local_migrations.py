"""merge remote and local migrations

Revision ID: 2c8f146968e5
Revises: 395fde8d6d86, d7e5a1b9c2f3, e49463e9160d
Create Date: 2026-04-02 20:39:48.027042

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2c8f146968e5'
down_revision = ('395fde8d6d86', 'd7e5a1b9c2f3', 'e49463e9160d')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
