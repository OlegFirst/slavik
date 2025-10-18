"""Add Community Level and Passive Learning tables

Revision ID: b7c8d9e0f1a2
Revises: 776e3e3e2ae8
Create Date: 2025-10-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b7c8d9e0f1a2'
down_revision: Union[str, None] = '776e3e3e2ae8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create Community Level and Passive Learning tables"""

    # ============================================
    # COMMUNITY LEVEL TABLES
    # ============================================

    # Community Learnings table (Knowledge Exchange)
    op.create_table(
        'community_learnings',
        sa.Column('learning_id', sa.String(50), primary_key=True),
        sa.Column('tenant_id', sa.String(255), sa.ForeignKey('tenants.id'), nullable=False, index=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('challenge', sa.Text(), nullable=False),
        sa.Column('solution', sa.Text(), nullable=False),
        sa.Column('outcome', sa.Text(), nullable=False),
        sa.Column('tags', postgresql.ARRAY(sa.String(100)), nullable=True),

        # Context (anonymized)
        sa.Column('industry', sa.String(100), nullable=False, index=True),
        sa.Column('size_category', sa.String(50), nullable=False, index=True),
        sa.Column('maturity_level', sa.String(50), nullable=False, index=True),

        # Metrics
        sa.Column('effectiveness_score', sa.Float(), nullable=False),
        sa.Column('times_used', sa.Integer(), nullable=False, default=0),
        sa.Column('success_rate', sa.Float(), nullable=False, default=0.0),
        sa.Column('average_rating', sa.Float(), nullable=True),

        # Anonymization
        sa.Column('anonymization_level', sa.String(50), nullable=False, default='standard'),
        sa.Column('contributor_twin_id', postgresql.UUID(), nullable=False),  # PRIVATE - not exposed in API, references organizations(id)

        # Metadata
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('verification_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, index=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),

        sa.ForeignKeyConstraint(['contributor_twin_id'], ['organizations.id'], ondelete='CASCADE'),
    )

    op.create_index('idx_learning_industry', 'community_learnings', ['industry'])
    op.create_index('idx_learning_size', 'community_learnings', ['size_category'])
    op.create_index('idx_learning_maturity', 'community_learnings', ['maturity_level'])
    op.create_index('idx_learning_effectiveness', 'community_learnings', ['effectiveness_score'])
    op.create_index('idx_learning_created', 'community_learnings', ['created_at'])

    # Learning Feedback table
    op.create_table(
        'learning_feedback',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('learning_id', sa.String(50), sa.ForeignKey('community_learnings.learning_id'), nullable=False, index=True),
        sa.Column('twin_id', postgresql.UUID(), sa.ForeignKey('organizations.id'), nullable=False, index=True),
        sa.Column('tenant_id', sa.String(255), sa.ForeignKey('tenants.id'), nullable=False, index=True),

        # Feedback
        sa.Column('applied', sa.Boolean(), nullable=False),
        sa.Column('was_helpful', sa.Boolean(), nullable=True),
        sa.Column('outcome_rating', sa.Float(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),

        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    op.create_index('idx_feedback_learning', 'learning_feedback', ['learning_id'])
    op.create_index('idx_feedback_twin', 'learning_feedback', ['twin_id'])

    # User Networking Profiles table (People Matching)
    op.create_table(
        'user_networking_profiles',
        sa.Column('user_id', sa.String(50), primary_key=True),
        sa.Column('twin_id', postgresql.UUID(), sa.ForeignKey('organizations.id'), nullable=False, index=True),
        sa.Column('tenant_id', sa.String(255), sa.ForeignKey('tenants.id'), nullable=False, index=True),

        # Profile
        sa.Column('display_name', sa.String(255), nullable=False),
        sa.Column('role', sa.String(100), nullable=False, index=True),
        sa.Column('experience_level', sa.String(50), nullable=False, index=True),
        sa.Column('bio', sa.Text(), nullable=True),

        # Skills and Interests
        sa.Column('bcm_certifications', postgresql.ARRAY(sa.String(100)), nullable=True),
        sa.Column('expertise_areas', postgresql.ARRAY(sa.String(100)), nullable=True),
        sa.Column('current_challenges', postgresql.ARRAY(sa.String(200)), nullable=True),
        sa.Column('learning_interests', postgresql.ARRAY(sa.String(100)), nullable=True),

        # Preferences
        sa.Column('languages', postgresql.ARRAY(sa.String(50)), nullable=True),
        sa.Column('open_to_mentoring', sa.Boolean(), default=False),
        sa.Column('seeking_mentor', sa.Boolean(), default=False),
        sa.Column('open_to_collaboration', sa.Boolean(), default=False),

        # Privacy
        sa.Column('visibility_level', sa.String(50), nullable=False, default='connections_only'),
        sa.Column('show_organization', sa.Boolean(), default=True),
        sa.Column('show_real_name', sa.Boolean(), default=True),

        # Metadata
        sa.Column('last_active', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),

        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    op.create_index('idx_profile_twin', 'user_networking_profiles', ['twin_id'])
    op.create_index('idx_profile_role', 'user_networking_profiles', ['role'])
    op.create_index('idx_profile_experience', 'user_networking_profiles', ['experience_level'])

    # Privacy Settings table
    op.create_table(
        'community_privacy_settings',
        sa.Column('user_id', sa.String(50), primary_key=True),
        sa.Column('tenant_id', sa.String(255), sa.ForeignKey('tenants.id'), nullable=False, index=True),

        # Twin Matching Privacy
        sa.Column('allow_twin_matching', sa.Boolean(), default=True),
        sa.Column('twin_visibility', sa.String(50), nullable=False, default='community'),

        # Knowledge Sharing Privacy
        sa.Column('share_learnings', sa.Boolean(), default=True),
        sa.Column('anonymize_contributions', sa.Boolean(), default=True),

        # People Matching Privacy
        sa.Column('show_in_people_search', sa.Boolean(), default=True),
        sa.Column('allow_connection_requests', sa.Boolean(), default=True),

        # Data Sharing
        sa.Column('share_organizational_data', sa.Boolean(), default=False),
        sa.Column('share_behavioral_patterns', sa.Boolean(), default=True),

        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),

        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # ============================================
    # PASSIVE LEARNING TABLES
    # ============================================

    # Learning Events table (event log)
    op.create_table(
        'learning_events',
        sa.Column('event_id', sa.String(50), primary_key=True),
        sa.Column('twin_id', postgresql.UUID(), sa.ForeignKey('organizations.id'), nullable=False, index=True),
        sa.Column('tenant_id', sa.String(255), sa.ForeignKey('tenants.id'), nullable=False, index=True),

        # Event details
        sa.Column('source', sa.String(50), nullable=False, index=True),  # bia, risk, incident, training, document
        sa.Column('event_type', sa.String(100), nullable=True),
        sa.Column('raw_data', postgresql.JSONB(), nullable=True),

        # Extracted insights
        sa.Column('insights', postgresql.JSONB(), nullable=False),

        # Metadata
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, index=True),
    )

    op.create_index('idx_event_twin', 'learning_events', ['twin_id'])
    op.create_index('idx_event_source', 'learning_events', ['source'])
    op.create_index('idx_event_created', 'learning_events', ['created_at'])

    # Learning Insights table (accumulated insights)
    op.create_table(
        'learning_insights',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('twin_id', postgresql.UUID(), sa.ForeignKey('organizations.id'), nullable=False, index=True),
        sa.Column('tenant_id', sa.String(255), sa.ForeignKey('tenants.id'), nullable=False, index=True),

        # Insight details
        sa.Column('insight_type', sa.String(100), nullable=False, index=True),
        sa.Column('insight_value', postgresql.JSONB(), nullable=False),

        # Metadata
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('source_event_count', sa.Integer(), nullable=False, default=1),
        sa.Column('last_updated_from_event_id', sa.String(50), nullable=True),

        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False, index=True),

        # Unique constraint: one insight per twin per type
        sa.UniqueConstraint('twin_id', 'insight_type', name='uq_twin_insight_type'),
    )

    op.create_index('idx_insight_twin', 'learning_insights', ['twin_id'])
    op.create_index('idx_insight_type', 'learning_insights', ['insight_type'])
    op.create_index('idx_insight_updated', 'learning_insights', ['updated_at'])

    # Organizational Context Cache table (pre-built contexts for performance)
    op.create_table(
        'organization_contexts',
        sa.Column('twin_id', postgresql.UUID(), primary_key=True),
        sa.Column('tenant_id', sa.String(255), sa.ForeignKey('tenants.id'), nullable=False, index=True),

        # Culture & Behavior
        sa.Column('organizational_culture', sa.String(100), nullable=True),
        sa.Column('decision_speed', sa.String(50), nullable=True),
        sa.Column('thoroughness', sa.String(50), nullable=True),
        sa.Column('learning_orientation', sa.String(50), nullable=True),

        # Risk Profile
        sa.Column('risk_tolerance', sa.String(50), nullable=True),
        sa.Column('risk_appetite', sa.String(50), nullable=True),
        sa.Column('control_preference', sa.String(50), nullable=True),

        # Communication
        sa.Column('communication_style', sa.String(50), nullable=True),
        sa.Column('response_speed', sa.String(50), nullable=True),

        # Operational Patterns
        sa.Column('avg_rto_hours', sa.Float(), nullable=True),
        sa.Column('dependency_count', sa.Integer(), nullable=True),
        sa.Column('primary_risk_focus', sa.String(100), nullable=True),

        # Knowledge & Capability
        sa.Column('knowledge_level', sa.String(50), nullable=True),
        sa.Column('knowledge_gaps', postgresql.ARRAY(sa.String(200)), nullable=True),
        sa.Column('engagement_level', sa.String(50), nullable=True),

        # BCM Maturity Indicators
        sa.Column('critical_functions', postgresql.ARRAY(sa.String(200)), nullable=True),
        sa.Column('recovery_time_hours', sa.Float(), nullable=True),

        # Patterns & Trends (stored as JSONB for flexibility)
        sa.Column('patterns', postgresql.JSONB(), nullable=True),
        sa.Column('trends', postgresql.JSONB(), nullable=True),

        # Metadata
        sa.Column('total_events', sa.Integer(), nullable=False, default=0),
        sa.Column('confidence_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('last_updated', sa.DateTime(), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),

        sa.ForeignKeyConstraint(['twin_id'], ['organizations.id'], ondelete='CASCADE'),
    )

    op.create_index('idx_context_twin', 'organization_contexts', ['twin_id'])
    op.create_index('idx_context_updated', 'organization_contexts', ['last_updated'])
    op.create_index('idx_context_confidence', 'organization_contexts', ['confidence_score'])


def downgrade() -> None:
    """Drop Community Level and Passive Learning tables"""

    # ============================================
    # DROP PASSIVE LEARNING TABLES
    # ============================================

    # Drop organization_contexts
    op.drop_index('idx_context_confidence', table_name='organization_contexts')
    op.drop_index('idx_context_updated', table_name='organization_contexts')
    op.drop_index('idx_context_twin', table_name='organization_contexts')
    op.drop_table('organization_contexts')

    # Drop learning_insights
    op.drop_index('idx_insight_updated', table_name='learning_insights')
    op.drop_index('idx_insight_type', table_name='learning_insights')
    op.drop_index('idx_insight_twin', table_name='learning_insights')
    op.drop_table('learning_insights')

    # Drop learning_events
    op.drop_index('idx_event_created', table_name='learning_events')
    op.drop_index('idx_event_source', table_name='learning_events')
    op.drop_index('idx_event_twin', table_name='learning_events')
    op.drop_table('learning_events')

    # ============================================
    # DROP COMMUNITY LEVEL TABLES
    # ============================================

    # Drop privacy_settings
    op.drop_table('community_privacy_settings')

    # Drop user_networking_profiles
    op.drop_index('idx_profile_experience', table_name='user_networking_profiles')
    op.drop_index('idx_profile_role', table_name='user_networking_profiles')
    op.drop_index('idx_profile_twin', table_name='user_networking_profiles')
    op.drop_table('user_networking_profiles')

    # Drop learning_feedback
    op.drop_index('idx_feedback_twin', table_name='learning_feedback')
    op.drop_index('idx_feedback_learning', table_name='learning_feedback')
    op.drop_table('learning_feedback')

    # Drop community_learnings
    op.drop_index('idx_learning_created', table_name='community_learnings')
    op.drop_index('idx_learning_effectiveness', table_name='community_learnings')
    op.drop_index('idx_learning_maturity', table_name='community_learnings')
    op.drop_index('idx_learning_size', table_name='community_learnings')
    op.drop_index('idx_learning_industry', table_name='community_learnings')
    op.drop_table('community_learnings')
