"""add_personal_digital_twin_and_frontend_compatibility

Revision ID: 776e3e3e2ae8
Revises: a1b2c3d4e5f6
Create Date: 2025-10-01 18:09:36.419981

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '776e3e3e2ae8'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add frontend-compatible fields to organizations table
    op.add_column('organizations', sa.Column('twin_health_score', sa.Float(), nullable=True))
    op.add_column('organizations', sa.Column('risk_landscape', sa.JSON(), nullable=True))
    op.add_column('organizations', sa.Column('compliance_status', sa.JSON(), nullable=True))
    op.add_column('organizations', sa.Column('departments', sa.JSON(), nullable=True))

    # Create personal_digital_twins table
    op.create_table(
        'personal_digital_twins',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('user_id', sa.String(length=50), nullable=False),
        sa.Column('organization_id', sa.String(length=50), nullable=True),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('workspace_config', sa.JSON(), nullable=False),
        sa.Column('personal_metrics', sa.JSON(), nullable=False),
        sa.Column('activity_patterns', sa.JSON(), nullable=False),
        sa.Column('twin_health_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('activity_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('last_sync', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('sync_status', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id')
    )

    # Create indexes for personal_digital_twins
    op.create_index('idx_personal_twin_user', 'personal_digital_twins', ['user_id'])
    op.create_index('idx_personal_twin_org', 'personal_digital_twins', ['organization_id'])
    op.create_index('idx_personal_twin_sync', 'personal_digital_twins', ['sync_status'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop personal_digital_twins table and indexes
    op.drop_index('idx_personal_twin_sync', table_name='personal_digital_twins')
    op.drop_index('idx_personal_twin_org', table_name='personal_digital_twins')
    op.drop_index('idx_personal_twin_user', table_name='personal_digital_twins')
    op.drop_table('personal_digital_twins')

    # Remove frontend-compatible fields from organizations
    op.drop_column('organizations', 'departments')
    op.drop_column('organizations', 'compliance_status')
    op.drop_column('organizations', 'risk_landscape')
    op.drop_column('organizations', 'twin_health_score')
