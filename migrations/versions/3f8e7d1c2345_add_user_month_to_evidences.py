"""Add user_id, year, month to evidences

Revision ID: 3f8e7d1c2345
Revises: 2a9c8d1e1234
Create Date: 2026-04-09 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '3f8e7d1c2345'
down_revision: Union[str, Sequence[str], None] = '2a9c8d1e1234'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('evidences', sa.Column('user_id', sa.UUID(), nullable=True))
    op.add_column('evidences', sa.Column('year', sa.Integer(), nullable=True))
    op.add_column('evidences', sa.Column('month', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('evidences', 'month')
    op.drop_column('evidences', 'year')
    op.drop_column('evidences', 'user_id')