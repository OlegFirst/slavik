"""Add Simulation Hub tables (scenarios, exercises, predictions, bia)

Revision ID: a1b2c3d4e5f6
Revises: 76253af070c2
Create Date: 2025-10-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '76253af070c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create Simulation Hub tables"""

    # Scenario Templates table
    op.create_table(
        'scenario_templates',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('tenant_id', sa.String(50), sa.ForeignKey('tenants.id'), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(100), nullable=False, index=True),
        sa.Column('scenario_type', sa.String(100), nullable=False, index=True),
        sa.Column('detailed_scenario', sa.Text(), nullable=True),
        sa.Column('parameters_template', sa.JSON(), nullable=True),
        sa.Column('severity_levels', sa.JSON(), nullable=True),
        sa.Column('ai_generated', sa.Boolean(), default=False),
        sa.Column('ai_prompt', sa.Text(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('source', sa.String(255), nullable=True),
        sa.Column('is_public', sa.Boolean(), default=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, index=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    op.create_index('idx_scenario_tenant', 'scenario_templates', ['tenant_id'])
    op.create_index('idx_scenario_type', 'scenario_templates', ['scenario_type'])
    op.create_index('idx_scenario_category', 'scenario_templates', ['category'])

    # Exercises table
    op.create_table(
        'exercises',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('tenant_id', sa.String(50), sa.ForeignKey('tenants.id'), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('exercise_type', sa.String(100), nullable=False, index=True),
        sa.Column('scenario_template_id', sa.String(50), sa.ForeignKey('scenario_templates.id'), nullable=True, index=True),
        sa.Column('objectives', sa.JSON(), nullable=True),
        sa.Column('participants', sa.JSON(), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True, index=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='planned', index=True),
        sa.Column('simulation_result_id', sa.String(50), sa.ForeignKey('simulations.id'), nullable=True),
        sa.Column('findings', sa.JSON(), nullable=True),
        sa.Column('action_items', sa.JSON(), nullable=True),
        sa.Column('evaluation_score', sa.Float(), nullable=True),
        sa.Column('organization_id', sa.String(50), sa.ForeignKey('organizations.id'), nullable=True, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    op.create_index('idx_exercise_tenant', 'exercises', ['tenant_id'])
    op.create_index('idx_exercise_status', 'exercises', ['status'])
    op.create_index('idx_exercise_scheduled', 'exercises', ['scheduled_at'])

    # Predictions table
    op.create_table(
        'predictions',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('tenant_id', sa.String(50), sa.ForeignKey('tenants.id'), nullable=False, index=True),
        sa.Column('prediction_type', sa.String(100), nullable=False, index=True),
        sa.Column('scenario_template_id', sa.String(50), sa.ForeignKey('scenario_templates.id'), nullable=True),
        sa.Column('input_parameters', sa.JSON(), nullable=False),
        sa.Column('prediction_result', sa.JSON(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('predicted_date', sa.DateTime(), nullable=True),
        sa.Column('predicted_value', sa.Float(), nullable=True),
        sa.Column('factors', sa.JSON(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('assumptions', sa.JSON(), nullable=True),
        sa.Column('model_used', sa.String(100), nullable=True),
        sa.Column('model_version', sa.String(50), nullable=True),
        sa.Column('methodology', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='pending', index=True),
        sa.Column('organization_id', sa.String(50), sa.ForeignKey('organizations.id'), nullable=True, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, index=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    op.create_index('idx_prediction_tenant', 'predictions', ['tenant_id'])
    op.create_index('idx_prediction_type', 'predictions', ['prediction_type'])
    op.create_index('idx_prediction_status', 'predictions', ['status'])

    # BIA Analyses table
    op.create_table(
        'bia_analyses',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('tenant_id', sa.String(50), sa.ForeignKey('tenants.id'), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('analysis_type', sa.String(100), nullable=False, index=True),
        sa.Column('status', sa.String(50), nullable=False, default='pending', index=True),
        sa.Column('processes', sa.JSON(), nullable=False),
        sa.Column('context', sa.JSON(), nullable=True),
        sa.Column('rto_recommendations', sa.JSON(), nullable=True),
        sa.Column('rpo_recommendations', sa.JSON(), nullable=True),
        sa.Column('financial_impact', sa.JSON(), nullable=True),
        sa.Column('recovery_strategies', sa.JSON(), nullable=True),
        sa.Column('dependencies', sa.JSON(), nullable=True),
        sa.Column('criticality_scores', sa.JSON(), nullable=True),
        sa.Column('time_horizons', sa.JSON(), nullable=True),
        sa.Column('impact_categories', sa.JSON(), nullable=True),
        sa.Column('organization_id', sa.String(50), sa.ForeignKey('organizations.id'), nullable=True, index=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, index=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    op.create_index('idx_bia_tenant', 'bia_analyses', ['tenant_id'])
    op.create_index('idx_bia_type', 'bia_analyses', ['analysis_type'])
    op.create_index('idx_bia_status', 'bia_analyses', ['status'])


def downgrade() -> None:
    """Drop Simulation Hub tables"""

    # Drop indexes first
    op.drop_index('idx_bia_status', table_name='bia_analyses')
    op.drop_index('idx_bia_type', table_name='bia_analyses')
    op.drop_index('idx_bia_tenant', table_name='bia_analyses')

    op.drop_index('idx_prediction_status', table_name='predictions')
    op.drop_index('idx_prediction_type', table_name='predictions')
    op.drop_index('idx_prediction_tenant', table_name='predictions')

    op.drop_index('idx_exercise_scheduled', table_name='exercises')
    op.drop_index('idx_exercise_status', table_name='exercises')
    op.drop_index('idx_exercise_tenant', table_name='exercises')

    op.drop_index('idx_scenario_category', table_name='scenario_templates')
    op.drop_index('idx_scenario_type', table_name='scenario_templates')
    op.drop_index('idx_scenario_tenant', table_name='scenario_templates')

    # Drop tables in reverse order (respect foreign keys)
    op.drop_table('bia_analyses')
    op.drop_table('predictions')
    op.drop_table('exercises')
    op.drop_table('scenario_templates')
