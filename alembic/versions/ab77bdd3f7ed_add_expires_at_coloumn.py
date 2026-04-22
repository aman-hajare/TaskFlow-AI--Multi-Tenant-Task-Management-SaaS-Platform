"""add expires_at column + fix role enum

Revision ID: ab77bdd3f7ed
Revises: bbea28fc584a
Create Date: 2026-03-23
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'ab77bdd3f7ed'
down_revision: Union[str, Sequence[str], None] = 'bbea28fc584a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add expires_at column
    op.add_column(
        'invites',
        sa.Column('expires_at', sa.DateTime(), nullable=False)
    )

    # 2. Add new enum value (IMPORTANT FIX)
    op.execute("ALTER TYPE roleenum ADD VALUE IF NOT EXISTS 'super_admin'")

    # 3. Ensure column uses enum
    op.alter_column(
        'invites',
        'role',
        existing_type=sa.VARCHAR(),
        type_=sa.Enum('admin', 'manager', 'employee', 'super_admin', name='roleenum'),
        postgresql_using="role::roleenum",
        existing_nullable=False
    )


def downgrade() -> None:

    op.alter_column(
        'invites',
        'role',
        existing_type=sa.Enum('admin', 'manager', 'employee', 'super_admin', name='roleenum'),
        type_=sa.VARCHAR(),
        existing_nullable=False
    )

    op.drop_column('invites', 'expires_at')