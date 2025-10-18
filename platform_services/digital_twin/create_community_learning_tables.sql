-- ============================================
-- Digital Twin: Community and Learning Tables
-- Manual Creation Script
-- ============================================
-- Due to schema conflicts (core.organizations vs public.organizations),
-- we create these tables manually without FK constraints on organizations.
-- The application layer will enforce referential integrity.

-- ============================================
-- COMMUNITY LEVEL TABLES
-- ============================================

-- Community Learnings table (Knowledge Exchange)
CREATE TABLE IF NOT EXISTS public.community_learnings (
    learning_id VARCHAR(50) PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL REFERENCES public.tenants(id),
    title VARCHAR(500) NOT NULL,
    challenge TEXT NOT NULL,
    solution TEXT NOT NULL,
    outcome TEXT NOT NULL,
    tags TEXT[],

    -- Context (anonymized)
    industry VARCHAR(100) NOT NULL,
    size_category VARCHAR(50) NOT NULL,
    maturity_level VARCHAR(50) NOT NULL,

    -- Metrics
    effectiveness_score FLOAT NOT NULL,
    times_used INTEGER NOT NULL DEFAULT 0,
    success_rate FLOAT NOT NULL DEFAULT 0.0,
    average_rating FLOAT,

    -- Anonymization
    anonymization_level VARCHAR(50) NOT NULL DEFAULT 'standard',
    contributor_twin_id UUID NOT NULL,  -- References public.organizations(id) - enforced in app

    -- Metadata
    is_verified BOOLEAN DEFAULT FALSE,
    verification_date TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_learning_industry ON public.community_learnings(industry);
CREATE INDEX IF NOT EXISTS idx_learning_size ON public.community_learnings(size_category);
CREATE INDEX IF NOT EXISTS idx_learning_maturity ON public.community_learnings(maturity_level);
CREATE INDEX IF NOT EXISTS idx_learning_effectiveness ON public.community_learnings(effectiveness_score);
CREATE INDEX IF NOT EXISTS idx_learning_created ON public.community_learnings(created_at);
CREATE INDEX IF NOT EXISTS idx_learning_tenant ON public.community_learnings(tenant_id);

-- Learning Feedback table
CREATE TABLE IF NOT EXISTS public.learning_feedback (
    id VARCHAR(50) PRIMARY KEY,
    learning_id VARCHAR(50) NOT NULL REFERENCES public.community_learnings(learning_id) ON DELETE CASCADE,
    twin_id UUID NOT NULL,  -- References public.organizations(id) - enforced in app
    tenant_id VARCHAR(255) NOT NULL REFERENCES public.tenants(id),

    -- Feedback
    applied BOOLEAN NOT NULL,
    was_helpful BOOLEAN,
    outcome_rating FLOAT,
    comment TEXT,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_feedback_learning ON public.learning_feedback(learning_id);
CREATE INDEX IF NOT EXISTS idx_feedback_twin ON public.learning_feedback(twin_id);
CREATE INDEX IF NOT EXISTS idx_feedback_tenant ON public.learning_feedback(tenant_id);

-- User Networking Profiles table (People Matching)
CREATE TABLE IF NOT EXISTS public.user_networking_profiles (
    user_id VARCHAR(50) PRIMARY KEY REFERENCES public.users(id) ON DELETE CASCADE,
    twin_id UUID NOT NULL,  -- References public.organizations(id) - enforced in app
    tenant_id VARCHAR(255) NOT NULL REFERENCES public.tenants(id),

    -- Profile
    display_name VARCHAR(255) NOT NULL,
    role VARCHAR(100) NOT NULL,
    experience_level VARCHAR(50) NOT NULL,
    bio TEXT,

    -- Skills and Interests
    bcm_certifications TEXT[],
    expertise_areas TEXT[],
    current_challenges TEXT[],
    learning_interests TEXT[],

    -- Preferences
    languages TEXT[],
    open_to_mentoring BOOLEAN DEFAULT FALSE,
    seeking_mentor BOOLEAN DEFAULT FALSE,
    open_to_collaboration BOOLEAN DEFAULT FALSE,

    -- Privacy
    visibility_level VARCHAR(50) NOT NULL DEFAULT 'connections_only',
    show_organization BOOLEAN DEFAULT TRUE,
    show_real_name BOOLEAN DEFAULT TRUE,

    -- Metadata
    last_active TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_profile_twin ON public.user_networking_profiles(twin_id);
CREATE INDEX IF NOT EXISTS idx_profile_role ON public.user_networking_profiles(role);
CREATE INDEX IF NOT EXISTS idx_profile_experience ON public.user_networking_profiles(experience_level);
CREATE INDEX IF NOT EXISTS idx_profile_tenant ON public.user_networking_profiles(tenant_id);

-- Privacy Settings table
CREATE TABLE IF NOT EXISTS public.community_privacy_settings (
    user_id VARCHAR(50) PRIMARY KEY REFERENCES public.users(id) ON DELETE CASCADE,
    tenant_id VARCHAR(255) NOT NULL REFERENCES public.tenants(id),

    -- Twin Matching Privacy
    allow_twin_matching BOOLEAN DEFAULT TRUE,
    twin_visibility VARCHAR(50) NOT NULL DEFAULT 'community',

    -- Knowledge Sharing Privacy
    share_learnings BOOLEAN DEFAULT TRUE,
    anonymize_contributions BOOLEAN DEFAULT TRUE,

    -- People Matching Privacy
    show_in_people_search BOOLEAN DEFAULT TRUE,
    allow_connection_requests BOOLEAN DEFAULT TRUE,

    -- Data Sharing
    share_organizational_data BOOLEAN DEFAULT FALSE,
    share_behavioral_patterns BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ============================================
-- PASSIVE LEARNING TABLES
-- ============================================

-- Learning Events table (event log)
CREATE TABLE IF NOT EXISTS public.learning_events (
    event_id VARCHAR(50) PRIMARY KEY,
    twin_id UUID NOT NULL,  -- References public.organizations(id) - enforced in app
    tenant_id VARCHAR(255) NOT NULL REFERENCES public.tenants(id),

    -- Event details
    source VARCHAR(50) NOT NULL,  -- bia, risk, incident, training, document
    event_type VARCHAR(100),
    raw_data JSONB,

    -- Extracted insights
    insights JSONB NOT NULL,

    -- Metadata
    confidence FLOAT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_event_twin ON public.learning_events(twin_id);
CREATE INDEX IF NOT EXISTS idx_event_source ON public.learning_events(source);
CREATE INDEX IF NOT EXISTS idx_event_created ON public.learning_events(created_at);
CREATE INDEX IF NOT EXISTS idx_event_tenant ON public.learning_events(tenant_id);

-- Learning Insights table (accumulated insights)
CREATE TABLE IF NOT EXISTS public.learning_insights (
    id VARCHAR(50) PRIMARY KEY,
    twin_id UUID NOT NULL,  -- References public.organizations(id) - enforced in app
    tenant_id VARCHAR(255) NOT NULL REFERENCES public.tenants(id),

    -- Insight details
    insight_type VARCHAR(100) NOT NULL,
    insight_value JSONB NOT NULL,

    -- Metadata
    confidence FLOAT NOT NULL,
    source_event_count INTEGER NOT NULL DEFAULT 1,
    last_updated_from_event_id VARCHAR(50),

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Unique constraint: one insight per twin per type
    UNIQUE(twin_id, insight_type)
);

CREATE INDEX IF NOT EXISTS idx_insight_twin ON public.learning_insights(twin_id);
CREATE INDEX IF NOT EXISTS idx_insight_type ON public.learning_insights(insight_type);
CREATE INDEX IF NOT EXISTS idx_insight_updated ON public.learning_insights(updated_at);
CREATE INDEX IF NOT EXISTS idx_insight_tenant ON public.learning_insights(tenant_id);

-- Organizational Context Cache table (pre-built contexts for performance)
CREATE TABLE IF NOT EXISTS public.organization_contexts (
    twin_id UUID PRIMARY KEY,  -- References public.organizations(id) - enforced in app
    tenant_id VARCHAR(255) NOT NULL REFERENCES public.tenants(id),

    -- Culture & Behavior
    organizational_culture VARCHAR(100),
    decision_speed VARCHAR(50),
    thoroughness VARCHAR(50),
    learning_orientation VARCHAR(50),

    -- Risk Profile
    risk_tolerance VARCHAR(50),
    risk_appetite VARCHAR(50),
    control_preference VARCHAR(50),

    -- Communication
    communication_style VARCHAR(50),
    response_speed VARCHAR(50),

    -- Operational Patterns
    avg_rto_hours FLOAT,
    dependency_count INTEGER,
    primary_risk_focus VARCHAR(100),

    -- Knowledge & Capability
    knowledge_level VARCHAR(50),
    knowledge_gaps TEXT[],
    engagement_level VARCHAR(50),

    -- BCM Maturity Indicators
    critical_functions TEXT[],
    recovery_time_hours FLOAT,

    -- Patterns & Trends (stored as JSONB for flexibility)
    patterns JSONB,
    trends JSONB,

    -- Metadata
    total_events INTEGER NOT NULL DEFAULT 0,
    confidence_score FLOAT NOT NULL DEFAULT 0.0,
    last_updated TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_context_twin ON public.organization_contexts(twin_id);
CREATE INDEX IF NOT EXISTS idx_context_updated ON public.organization_contexts(last_updated);
CREATE INDEX IF NOT EXISTS idx_context_confidence ON public.organization_contexts(confidence_score);
CREATE INDEX IF NOT EXISTS idx_context_tenant ON public.organization_contexts(tenant_id);

-- ============================================
-- VERIFICATION
-- ============================================

SELECT 'Created tables:' as info;
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
    'community_learnings',
    'learning_feedback',
    'user_networking_profiles',
    'community_privacy_settings',
    'learning_events',
    'learning_insights',
    'organization_contexts'
)
ORDER BY table_name;
