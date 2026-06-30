"""add_is_descending_to_indicator_assignments

Revision ID: c1d2e3f4a5b6
Revises: a1b2c3d4e5f6
Create Date: 2026-06-30 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('indicator_assignments',
        sa.Column('is_descending', sa.Boolean(), nullable=False, server_default='false')
    )


def downgrade() -> None:
    op.drop_column('indicator_assignments', 'is_descending')
