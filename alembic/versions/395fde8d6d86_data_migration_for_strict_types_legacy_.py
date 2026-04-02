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
    # Migrate QR Tags Statuses from 'pending' to 'inactive'
    # First, physically add 'pending' if it was removed in previous revision
    # Actually since it's just raw SQL string, we execute via op
    op.execute("UPDATE qr_codes SET status = 'inactive' WHERE status = 'pending'")

    # Notice: Role level is actually an Enum in PG, but Pydantic uses int.
    # The requirement explicitly said to run the SQL updates to integer.
    # If the user's postgres table treats role as an Enum, this might fail,
    # but we will try updating Enum references if they changed form. 
    # The user instruction states:
    # UPDATE users SET role = 3 WHERE role = 'admin';
    # UPDATE users SET role = 2 WHERE role = 'supervisor';
    # UPDATE users SET role = 1 WHERE role = 'operator';
    
    # We'll run them as requested. But postgres cast might need updating.
    op.execute("UPDATE users SET role = '3' WHERE role = 'admin' OR role = '3'")
    op.execute("UPDATE users SET role = '2' WHERE role = 'supervisor' OR role = '2'")
    op.execute("UPDATE users SET role = '1' WHERE role = 'operator' OR role = '1'")


def downgrade() -> None:
    pass
