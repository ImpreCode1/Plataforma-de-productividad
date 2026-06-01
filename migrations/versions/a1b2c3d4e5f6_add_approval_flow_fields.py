"""add approval flow fields

Revision ID: a1b2c3d4e5f6
Revises: 91cdc669197d
Create Date: 2026-05-28 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '91cdc669197d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add approval fields to indicator_trackings
    op.add_column('indicator_trackings', sa.Column('approval_status', sa.String(), server_default='PENDIENTE', nullable=True))
    op.add_column('indicator_trackings', sa.Column('submitted_at', sa.DateTime(), nullable=True))
    op.add_column('indicator_trackings', sa.Column('submitted_by', sa.UUID(), nullable=True))
    op.add_column('indicator_trackings', sa.Column('approved_by', sa.UUID(), nullable=True))
    op.add_column('indicator_trackings', sa.Column('approved_at', sa.DateTime(), nullable=True))
    op.add_column('indicator_trackings', sa.Column('rejection_comment', sa.Text(), nullable=True))
    op.create_foreign_key('fk_trackings_submitted_by', 'indicator_trackings', 'users', ['submitted_by'], ['id'])
    op.create_foreign_key('fk_trackings_approved_by', 'indicator_trackings', 'users', ['approved_by'], ['id'])

    # Add evidence fields
    op.add_column('evidences', sa.Column('original_filename', sa.String(), nullable=True))
    op.add_column('evidences', sa.Column('file_size', sa.Integer(), nullable=True))

    # Create approval_configs table
    op.create_table('approval_configs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('config_type', sa.String(), nullable=False),
        sa.Column('config_value', sa.String(), nullable=False),
        sa.Column('load_mode', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Set default approval_status for existing rows
    op.execute("UPDATE indicator_trackings SET approval_status = 'APROBADO' WHERE is_closed = TRUE")
    op.execute("UPDATE indicator_trackings SET approval_status = 'EN_REVISION' WHERE status = 'COMPLETED' AND is_closed = FALSE")
    op.execute("UPDATE indicator_trackings SET approval_status = 'PENDIENTE' WHERE approval_status IS NULL")

    op.alter_column('indicator_trackings', 'approval_status', nullable=False)


def downgrade() -> None:
    op.drop_table('approval_configs')
    op.drop_column('evidences', 'file_size')
    op.drop_column('evidences', 'original_filename')
    op.drop_constraint('fk_trackings_approved_by', 'indicator_trackings', type_='foreignkey')
    op.drop_constraint('fk_trackings_submitted_by', 'indicator_trackings', type_='foreignkey')
    op.drop_column('indicator_trackings', 'rejection_comment')
    op.drop_column('indicator_trackings', 'approved_at')
    op.drop_column('indicator_trackings', 'approved_by')
    op.drop_column('indicator_trackings', 'submitted_by')
    op.drop_column('indicator_trackings', 'submitted_at')
    op.drop_column('indicator_trackings', 'approval_status')
