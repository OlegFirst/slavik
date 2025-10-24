-- =====================================================
-- COMMUNITY INTELLIGENCE FOUNDATION
-- Migration 037: All tables for Community Intelligence
-- =====================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- ENUMS
-- =====================================================

CREATE TYPE contribution_status AS ENUM (
    'draft',
    'pending_review',
    'in_review',
    'approved',
    'rejected'
);

-- =====================================================
-- CASE CONTRIBUTIONS
-- =====================================================

CREATE TABLE IF NOT EXISTS case_contributions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Contributor
    contributor_id UUID NOT NULL,
    contributor_type VARCHAR(50),

    -- Case data (anonymized)
    case_data JSONB NOT NULL,
    original_org_type VARCHAR(100),

    -- Status
    status contribution_status NOT NULL DEFAULT 'draft',

    -- Review
    reviewers UUID[],
    review_deadline TIMESTAMPTZ,

    -- Metadata
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    approved_at TIMESTAMPTZ,
    added_to_library BOOLEAN DEFAULT FALSE,
    library_case_id UUID,

    -- Tags for discovery
    tags VARCHAR[],
    module VARCHAR(50) NOT NULL,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for case_contributions
CREATE INDEX idx_case_contributions_contributor ON case_contributions(contributor_id);
CREATE INDEX idx_case_contributions_status ON case_contributions(status);
CREATE INDEX idx_case_contributions_module ON case_contributions(module);
CREATE INDEX idx_case_contributions_submitted ON case_contributions(submitted_at DESC);
CREATE INDEX idx_case_contributions_tags ON case_contributions USING GIN(tags);

-- =====================================================
-- PEER REVIEWS
-- =====================================================

CREATE TABLE IF NOT EXISTS peer_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    contribution_id UUID NOT NULL REFERENCES case_contributions(id) ON DELETE CASCADE,
    reviewer_id UUID NOT NULL,

    -- Review
    approved BOOLEAN,
    quality_score INTEGER CHECK (quality_score >= 1 AND quality_score <= 10),
    feedback TEXT,
    suggested_improvements JSONB,

    -- Criteria
    anonymization_ok BOOLEAN DEFAULT TRUE,
    relevance_ok BOOLEAN DEFAULT TRUE,
    completeness_ok BOOLEAN DEFAULT TRUE,
    lessons_clear BOOLEAN DEFAULT TRUE,

    -- Timestamps
    reviewed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for peer_reviews
CREATE INDEX idx_peer_reviews_contribution ON peer_reviews(contribution_id);
CREATE INDEX idx_peer_reviews_reviewer ON peer_reviews(reviewer_id);
CREATE INDEX idx_peer_reviews_reviewed_at ON peer_reviews(reviewed_at DESC);

-- Unique constraint: one review per reviewer per contribution
CREATE UNIQUE INDEX idx_peer_reviews_unique ON peer_reviews(contribution_id, reviewer_id);

-- =====================================================
-- USER REPUTATION
-- =====================================================

CREATE TABLE IF NOT EXISTS user_reputation (
    user_id UUID PRIMARY KEY,

    -- Overall
    total_points INTEGER NOT NULL DEFAULT 0,
    level VARCHAR(50) NOT NULL DEFAULT 'newcomer',

    -- Dimension scores
    contribution_points INTEGER NOT NULL DEFAULT 0,
    review_points INTEGER NOT NULL DEFAULT 0,
    helpfulness_points INTEGER NOT NULL DEFAULT 0,
    marketplace_rating NUMERIC(3,2),

    -- Expertise areas (BCI-style categories)
    expertise JSONB DEFAULT '{}',

    -- Badges
    badges VARCHAR[],

    -- Activity
    contributions_count INTEGER NOT NULL DEFAULT 0,
    reviews_count INTEGER NOT NULL DEFAULT 0,
    helpful_answers INTEGER NOT NULL DEFAULT 0,

    -- Timestamps
    first_contribution TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for user_reputation
CREATE INDEX idx_user_reputation_total_points ON user_reputation(total_points DESC);
CREATE INDEX idx_user_reputation_level ON user_reputation(level);
CREATE INDEX idx_user_reputation_expertise ON user_reputation USING GIN(expertise);

-- =====================================================
-- REPUTATION TRANSACTIONS
-- =====================================================

CREATE TABLE IF NOT EXISTS reputation_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    user_id UUID NOT NULL,
    points INTEGER NOT NULL,
    reason VARCHAR(100) NOT NULL,

    -- Context
    related_contribution_id UUID,
    related_review_id UUID,

    -- Timestamps
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for reputation_transactions
CREATE INDEX idx_reputation_transactions_user ON reputation_transactions(user_id);
CREATE INDEX idx_reputation_transactions_timestamp ON reputation_transactions(timestamp DESC);
CREATE INDEX idx_reputation_transactions_reason ON reputation_transactions(reason);

-- =====================================================
-- COMMUNITY ANNOTATIONS
-- =====================================================

CREATE TABLE IF NOT EXISTS community_annotations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- What's being annotated
    clause_id VARCHAR(50) NOT NULL,
    standard VARCHAR(50) DEFAULT 'ISO22301',

    -- Annotation
    author_id UUID NOT NULL,
    interpretation TEXT NOT NULL,

    -- Context
    industry_specific VARCHAR(100),
    organization_size VARCHAR(50),
    practical_examples JSONB,

    -- Community feedback
    upvotes INTEGER NOT NULL DEFAULT 0,
    downvotes INTEGER NOT NULL DEFAULT 0,
    helpful_count INTEGER NOT NULL DEFAULT 0,

    -- Status
    verified BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for community_annotations
CREATE INDEX idx_community_annotations_clause ON community_annotations(clause_id);
CREATE INDEX idx_community_annotations_author ON community_annotations(author_id);
CREATE INDEX idx_community_annotations_standard ON community_annotations(standard);
CREATE INDEX idx_community_annotations_industry ON community_annotations(industry_specific);
CREATE INDEX idx_community_annotations_score ON community_annotations((upvotes - downvotes) DESC);
CREATE INDEX idx_community_annotations_helpful ON community_annotations(helpful_count DESC);

-- =====================================================
-- SYNTHESIZED GUIDANCE
-- =====================================================

CREATE TABLE IF NOT EXISTS synthesized_guidance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    clause_id VARCHAR(50) NOT NULL UNIQUE,

    -- Sources used
    official_text TEXT,
    community_interpretations JSONB,
    case_examples JSONB,

    -- Synthesized content
    unified_guidance TEXT NOT NULL,
    practical_steps JSONB,
    common_pitfalls JSONB,
    success_patterns JSONB,

    -- Metadata
    synthesis_version INTEGER NOT NULL DEFAULT 1,
    synthesized_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    sources_count INTEGER,
    confidence_score NUMERIC(3,2),

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for synthesized_guidance
CREATE INDEX idx_synthesized_guidance_clause ON synthesized_guidance(clause_id);
CREATE INDEX idx_synthesized_guidance_synthesized_at ON synthesized_guidance(synthesized_at DESC);

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE case_contributions ENABLE ROW LEVEL SECURITY;
ALTER TABLE peer_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_reputation ENABLE ROW LEVEL SECURITY;
ALTER TABLE reputation_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_annotations ENABLE ROW LEVEL SECURITY;
ALTER TABLE synthesized_guidance ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- RLS POLICIES
-- =====================================================

-- Case Contributions: Owner and reviewers can view
CREATE POLICY case_contributions_select ON case_contributions
    FOR SELECT
    USING (
        contributor_id = auth.uid() OR
        auth.uid() = ANY(reviewers) OR
        status = 'approved'
    );

-- Case Contributions: Owner can insert
CREATE POLICY case_contributions_insert ON case_contributions
    FOR INSERT
    WITH CHECK (contributor_id = auth.uid());

-- Case Contributions: Owner can update draft
CREATE POLICY case_contributions_update ON case_contributions
    FOR UPDATE
    USING (contributor_id = auth.uid() AND status = 'draft');

-- Peer Reviews: Reviewers can insert
CREATE POLICY peer_reviews_insert ON peer_reviews
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM case_contributions
            WHERE id = peer_reviews.contribution_id
            AND auth.uid() = ANY(reviewers)
        )
    );

-- Peer Reviews: View if can view contribution
CREATE POLICY peer_reviews_select ON peer_reviews
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM case_contributions
            WHERE id = peer_reviews.contribution_id
            AND (
                contributor_id = auth.uid() OR
                auth.uid() = ANY(reviewers) OR
                status = 'approved'
            )
        )
    );

-- User Reputation: Everyone can view
CREATE POLICY user_reputation_select ON user_reputation
    FOR SELECT
    USING (true);

-- User Reputation: Only system can modify (via service)
-- No INSERT/UPDATE policies for users

-- Reputation Transactions: User can view their own
CREATE POLICY reputation_transactions_select ON reputation_transactions
    FOR SELECT
    USING (user_id = auth.uid());

-- Community Annotations: Everyone can view
CREATE POLICY community_annotations_select ON community_annotations
    FOR SELECT
    USING (true);

-- Community Annotations: Authenticated users can insert
CREATE POLICY community_annotations_insert ON community_annotations
    FOR INSERT
    WITH CHECK (auth.uid() IS NOT NULL);

-- Community Annotations: Author can update
CREATE POLICY community_annotations_update ON community_annotations
    FOR UPDATE
    USING (author_id = auth.uid());

-- Synthesized Guidance: Everyone can view
CREATE POLICY synthesized_guidance_select ON synthesized_guidance
    FOR SELECT
    USING (true);

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Auto-update updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_case_contributions_updated_at
    BEFORE UPDATE ON case_contributions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_community_annotations_updated_at
    BEFORE UPDATE ON community_annotations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_synthesized_guidance_updated_at
    BEFORE UPDATE ON synthesized_guidance
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_reputation_updated_at
    BEFORE UPDATE ON user_reputation
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- SAMPLE DATA (Optional - for testing)
-- =====================================================

-- Insert sample reputation levels
COMMENT ON TABLE user_reputation IS 'Multi-dimensional reputation system with levels: newcomer (0-99), contributor (100-499), expert (500-1999), master (2000+)';

-- =====================================================
-- GRANTS
-- =====================================================

-- Grant permissions to authenticated users
GRANT SELECT, INSERT, UPDATE ON case_contributions TO authenticated;
GRANT SELECT, INSERT ON peer_reviews TO authenticated;
GRANT SELECT ON user_reputation TO authenticated;
GRANT SELECT ON reputation_transactions TO authenticated;
GRANT SELECT, INSERT, UPDATE ON community_annotations TO authenticated;
GRANT SELECT ON synthesized_guidance TO authenticated;

-- Grant sequence permissions
-- (none needed as using UUID)

-- =====================================================
-- COMPLETION
-- =====================================================

COMMENT ON SCHEMA public IS 'Community Intelligence Foundation - Migration 037 applied';
