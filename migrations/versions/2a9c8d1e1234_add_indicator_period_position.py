"""Add start_month, end_month and position snapshot to indicator_assignments

Revision ID: 2a9c8d1e1234
Revises: b3baea75c882
Create Date: 2026-04-09 11:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '2a9c8d1e1234'
down_revision: Union[str, Sequence[str], None] = 'b3baea75c882'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('indicator_assignments', sa.Column('start_month', sa.Integer(), server_default='1', nullable=False))
    op.add_column('indicator_assignments', sa.Column('end_month', sa.Integer(), server_default='12', nullable=False))
    op.add_column('indicator_assignments', sa.Column('position_name_at_assignment', sa.String(), nullable=True))
    op.add_column('indicator_assignments', sa.Column('area_at_assignment', sa.String(), nullable=True))
    op.add_column('indicator_assignments', sa.Column('subarea_at_assignment', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('indicator_assignments', 'subarea_at_assignment')
    op.drop_column('indicator_assignments', 'area_at_assignment')
    op.drop_column('indicator_assignments', 'position_name_at_assignment')
    op.drop_column('indicator_assignments', 'end_month')
    op.drop_column('indicator_assignments', 'start_month')