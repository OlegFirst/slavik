"""Initial System BCM schema

Revision ID: 001_initial
Revises:
Create Date: 2025-10-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply the initial schema"""
    # Run the schema SQL file
    with open('database/schema.sql', 'r') as f:
        schema_sql = f.read()
        op.execute(schema_sql)


def downgrade() -> None:
    """Remove the initial schema"""
    # Drop all tables
    op.execute('DROP TABLE IF EXISTS system_bcm_events CASCADE')
    op.execute('DROP TABLE IF EXISTS system_bcm_improvements CASCADE')
    op.execute('DROP TABLE IF EXISTS system_bcm_patterns CASCADE')
    op.execute('DROP TABLE IF EXISTS system_bcm_platform_health CASCADE')
    op.execute('DROP TABLE IF EXISTS system_bcm_insights CASCADE')
    op.execute('DROP TABLE IF EXISTS system_bcm_recovery_executions CASCADE')
    op.execute('DROP TABLE IF EXISTS system_bcm_cycles CASCADE')

    # Drop views
    op.execute('DROP VIEW IF EXISTS v_platform_health_summary')
    op.execute('DROP VIEW IF EXISTS v_active_insights')
    op.execute('DROP VIEW IF EXISTS v_recovery_performance')
    op.execute('DROP VIEW IF EXISTS v_recent_cycles')

    # Drop functions
    op.execute('DROP FUNCTION IF EXISTS update_updated_at_column()')

    # Drop extension
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
