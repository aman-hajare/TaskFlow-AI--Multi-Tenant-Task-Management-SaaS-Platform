"""add columns

Revision ID: 5c4906efa073
Revises: c2ecb3cd49b7
Create Date: 2026-03-16 18:15:43.638630

"""
from typing import Sequence, Union
from sqlalchemy.dialects import postgresql
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c4906efa073'
down_revision: Union[str, Sequence[str], None] = 'c2ecb3cd49b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    """Upgrade schema."""

    role_enum = postgresql.ENUM(
        'admin',
        'manager',
        'employee',
        name='roleenum'
    )

    skill_enum = postgresql.ENUM(
        'frontend',
        'backend',
        'fullstack',
        'devops',
        'qa',
        'design',
        name='skillenum'
    )

    # create enum types
    role_enum.create(op.get_bind(), checkfirst=True)
    skill_enum.create(op.get_bind(), checkfirst=True)

    # convert role column to enum
    op.alter_column(
        "users",
        "role",
        existing_type=sa.VARCHAR(),
        type_=role_enum,
        postgresql_using="role::roleenum",
        existing_nullable=True
    )

    # add skill column
    op.add_column(
        "users",
        sa.Column("skill", skill_enum, nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""

    role_enum = postgresql.ENUM(
        'admin',
        'manager',
        'employee',
        name='roleenum'
    )

    skill_enum = postgresql.ENUM(
        'frontend',
        'backend',
        'fullstack',
        'devops',
        'qa',
        'design',
        name='skillenum'
    )

    # drop skill column
    op.drop_column("users", "skill")

    # convert role back to varchar
    op.alter_column(
        "users",
        "role",
        existing_type=role_enum,
        type_=sa.VARCHAR(),
        postgresql_using="role::text",
        existing_nullable=True
    )

    # drop enums
    skill_enum.drop(op.get_bind(), checkfirst=True)
    role_enum.drop(op.get_bind(), checkfirst=True)
