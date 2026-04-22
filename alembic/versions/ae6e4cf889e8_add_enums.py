"""add enums

Revision ID: ae6e4cf889e8
Revises: 6078a1e4f280
Create Date: 2026-03-18 22:40:41.637423

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ae6e4cf889e8'
down_revision: Union[str, Sequence[str], None] = '6078a1e4f280'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define enums
status_enum = sa.Enum(
    'pending', 'in_progress', 'blocked', 'completed',
    name='statusenum'
)

priority_enum = sa.Enum(
    'low', 'medium', 'high', 'urgent',
    name='priorityenum'
)


def upgrade() -> None:
    bind = op.get_bind()

    # Create enum types FIRST
    status_enum.create(bind, checkfirst=True)
    priority_enum.create(bind, checkfirst=True)

    # Alter columns with casting
    op.alter_column(
        'tasks',
        'status',
        existing_type=sa.VARCHAR(),
        type_=status_enum,
        existing_nullable=True,
        postgresql_using="status::text::statusenum"
    )

    op.alter_column(
        'tasks',
        'priority',
        existing_type=sa.VARCHAR(),
        type_=priority_enum,
        existing_nullable=True,
        postgresql_using="priority::text::priorityenum"
    )


def downgrade() -> None:
    bind = op.get_bind()

    # Convert back to string
    op.alter_column(
        'tasks',
        'priority',
        existing_type=priority_enum,
        type_=sa.VARCHAR(),
        existing_nullable=True
    )

    op.alter_column(
        'tasks',
        'status',
        existing_type=status_enum,
        type_=sa.VARCHAR(),
        existing_nullable=True
    )

    # Drop enums AFTER removing usage
    priority_enum.drop(bind, checkfirst=True)
    status_enum.drop(bind, checkfirst=True)