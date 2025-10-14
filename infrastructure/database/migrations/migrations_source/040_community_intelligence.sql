-- Migration 040: Community Intelligence System
-- Creates tables for community-driven knowledge creation
--
-- Features:
-- - Case contributions with peer review
-- - Reputation and gamification
-- - Expertise tracking
-- - Quality assurance
--
-- Date: 2025-10-04

-- Create community schema if not exists
CREATE SCHEMA IF NOT EXISTS community;

-- Grant usage
GRANT USAGE ON SCHEMA community TO authenticated;
GRANT USAGE ON SCHEMA community TO service_role;

-- =============================================================================
-- ENUMS
-- =============================================================================

CREATE TYPE community.contribution_status AS ENUM (
    'pending_review',
    'in_review',
    'approved',
    'rejected'
);

CREATE TYPE community.reputation_level AS ENUM (
    'newcomer',
    'contributor',
    'expert',
    'master'
);

-- =============================================================================
-- TABLES
-- =============================================================================

-- Case Contributions
CREATE TABLE community.case_contributions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contributor_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    org_id UUID NOT NULL,

    -- Case data
    case_data JSONB NOT NULL,
    module VARCHAR(50) NOT NULL CHECK (module IN ('bia', 'risk', 'governance', 'planning', 'plans', 'response', 'validation', 'compliance', 'documents', 'learning')),
    tags TEXT[] DEFAULT '{}',
    original_org_type VARCHAR(100),

    -- Review process
    status community.contribution_status DEFAULT 'pending_review' NOT NULL,
    reviewers UUID[] DEFAULT '{}',
    review_deadline TIMESTAMP WITH TIME ZONE,

    -- Approval
    approved_at TIMESTAMP WITH TIME ZONE,
    added_to_library BOOLEAN DEFAULT false,
    library_case_id UUID,

    -- Metadata
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

    -- Constraints
    CONSTRAINT valid_reviewers_count CHECK (array_length(reviewers, 1) <= 5),
    CONSTRAINT approved_has_timestamp CHECK (
        (status = 'approved' AND approved_at IS NOT NULL) OR
        (status != 'approved')
    )
);

-- Peer Reviews
CREATE TABLE community.peer_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contribution_id UUID NOT NULL REFERENCES community.case_contributions(id) ON DELETE CASCADE,
    reviewer_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Review decision
    approved BOOLEAN NOT NULL,
    quality_score INTEGER NOT NULL CHECK (quality_score BETWEEN 1 AND 10),

    -- Detailed feedback
    feedback TEXT,
    suggested_improvements TEXT,

    -- Quality checks
    anonymization_ok BOOLEAN DEFAULT true NOT NULL,
    relevance_ok BOOLEAN DEFAULT true NOT NULL,
    completeness_ok BOOLEAN DEFAULT true NOT NULL,
    lessons_clear BOOLEAN DEFAULT true NOT NULL,

    -- Metadata
    reviewed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

    -- Constraints
    CONSTRAINT one_review_per_user UNIQUE (contribution_id, reviewer_id),
    CONSTRAINT feedback_required_on_reject CHECK (
        (approved = false AND feedback IS NOT NULL AND length(feedback) >= 10) OR
        approved = true
    )
);

-- User Reputation
CREATE TABLE community.user_reputation (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    org_id UUID NOT NULL,

    -- Total points and level
    total_points INTEGER DEFAULT 0 NOT NULL CHECK (total_points >= 0),
    level community.reputation_level DEFAULT 'newcomer' NOT NULL,

    -- Module-specific expertise ({"bia": 150, "risk": 80})
    expertise JSONB DEFAULT '{}' NOT NULL,

    -- Contribution metrics
    contribution_points INTEGER DEFAULT 0 NOT NULL CHECK (contribution_points >= 0),
    contributions_count INTEGER DEFAULT 0 NOT NULL CHECK (contributions_count >= 0),
    cases_approved INTEGER DEFAULT 0 NOT NULL CHECK (cases_approved >= 0),
    cases_rejected INTEGER DEFAULT 0 NOT NULL CHECK (cases_rejected >= 0),
    avg_case_quality DECIMAL(3,2) DEFAULT 0.0 NOT NULL CHECK (avg_case_quality BETWEEN 0 AND 10),
    first_contribution TIMESTAMP WITH TIME ZONE,

    -- Review metrics
    review_points INTEGER DEFAULT 0 NOT NULL CHECK (review_points >= 0),
    reviews_count INTEGER DEFAULT 0 NOT NULL CHECK (reviews_count >= 0),
    helpful_reviews_count INTEGER DEFAULT 0 NOT NULL CHECK (helpful_reviews_count >= 0),

    -- Marketplace impact
    marketplace_priority INTEGER DEFAULT 0 NOT NULL CHECK (marketplace_priority BETWEEN 0 AND 1000),

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Reputation Transactions
CREATE TABLE community.reputation_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Transaction details
    points INTEGER NOT NULL,
    reason VARCHAR(100) NOT NULL,
    related_contribution_id UUID REFERENCES community.case_contributions(id) ON DELETE SET NULL,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- =============================================================================
-- INDEXES
-- =============================================================================

-- Case Contributions
CREATE INDEX idx_contributions_contributor ON community.case_contributions(contributor_id);
CREATE INDEX idx_contributions_org ON community.case_contributions(org_id);
CREATE INDEX idx_contributions_status ON community.case_contributions(status);
CREATE INDEX idx_contributions_module ON community.case_contributions(module);
CREATE INDEX idx_contributions_approved_at ON community.case_contributions(approved_at) WHERE status = 'approved';
CREATE INDEX idx_contributions_tags ON community.case_contributions USING gin(tags);
CREATE INDEX idx_contributions_reviewers ON community.case_contributions USING gin(reviewers);

-- Peer Reviews
CREATE INDEX idx_reviews_contribution ON community.peer_reviews(contribution_id);
CREATE INDEX idx_reviews_reviewer ON community.peer_reviews(reviewer_id);
CREATE INDEX idx_reviews_approved ON community.peer_reviews(approved);
CREATE INDEX idx_reviews_quality_score ON community.peer_reviews(quality_score);

-- User Reputation
CREATE INDEX idx_reputation_org ON community.user_reputation(org_id);
CREATE INDEX idx_reputation_total_points ON community.user_reputation(total_points DESC);
CREATE INDEX idx_reputation_level ON community.user_reputation(level);
CREATE INDEX idx_reputation_marketplace_priority ON community.user_reputation(marketplace_priority DESC);
CREATE INDEX idx_reputation_expertise ON community.user_reputation USING gin(expertise);

-- Reputation Transactions
CREATE INDEX idx_transactions_user ON community.reputation_transactions(user_id);
CREATE INDEX idx_transactions_created_at ON community.reputation_transactions(created_at DESC);
CREATE INDEX idx_transactions_reason ON community.reputation_transactions(reason);

-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================================================

ALTER TABLE community.case_contributions ENABLE ROW LEVEL SECURITY;
ALTER TABLE community.peer_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE community.user_reputation ENABLE ROW LEVEL SECURITY;
ALTER TABLE community.reputation_transactions ENABLE ROW LEVEL SECURITY;

-- Case Contributions RLS
-- Users can:
-- - View approved cases (public)
-- - View their own contributions
-- - View contributions they're assigned to review
CREATE POLICY contributions_select_policy ON community.case_contributions
    FOR SELECT
    USING (
        status = 'approved'::community.contribution_status  -- Approved are public
        OR contributor_id = auth.uid()  -- Own contributions
        OR auth.uid() = ANY(reviewers)  -- Assigned reviewers
    );

-- Users can insert their own contributions
CREATE POLICY contributions_insert_policy ON community.case_contributions
    FOR INSERT
    WITH CHECK (contributor_id = auth.uid());

-- Users can update their own pending contributions
CREATE POLICY contributions_update_policy ON community.case_contributions
    FOR UPDATE
    USING (
        contributor_id = auth.uid()
        AND status IN ('pending_review'::community.contribution_status, 'in_review'::community.contribution_status)
    );

-- Users can delete their own pending contributions
CREATE POLICY contributions_delete_policy ON community.case_contributions
    FOR DELETE
    USING (
        contributor_id = auth.uid()
        AND status = 'pending_review'::community.contribution_status
    );

-- Peer Reviews RLS
-- Users can view reviews for contributions they can see
CREATE POLICY reviews_select_policy ON community.peer_reviews
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM community.case_contributions cc
            WHERE cc.id = peer_reviews.contribution_id
            AND (
                cc.status = 'approved'::community.contribution_status
                OR cc.contributor_id = auth.uid()
                OR auth.uid() = ANY(cc.reviewers)
            )
        )
    );

-- Users can insert reviews for assigned contributions
CREATE POLICY reviews_insert_policy ON community.peer_reviews
    FOR INSERT
    WITH CHECK (
        reviewer_id = auth.uid()
        AND EXISTS (
            SELECT 1 FROM community.case_contributions cc
            WHERE cc.id = contribution_id
            AND auth.uid() = ANY(cc.reviewers)
        )
    );

-- User Reputation RLS
-- All authenticated users can view reputation profiles
CREATE POLICY reputation_select_policy ON community.user_reputation
    FOR SELECT
    TO authenticated
    USING (true);

-- Users can update their own reputation (service role can update all)
CREATE POLICY reputation_update_policy ON community.user_reputation
    FOR UPDATE
    USING (user_id = auth.uid());

-- Reputation Transactions RLS
-- Users can view their own transactions
CREATE POLICY transactions_select_policy ON community.reputation_transactions
    FOR SELECT
    USING (user_id = auth.uid());

-- =============================================================================
-- FUNCTIONS
-- =============================================================================

-- Function to update contribution status
CREATE OR REPLACE FUNCTION community.update_contribution_status()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER trigger_update_contribution_timestamp
    BEFORE UPDATE ON community.case_contributions
    FOR EACH ROW
    EXECUTE FUNCTION community.update_contribution_status();

-- Function to update reputation timestamp
CREATE OR REPLACE FUNCTION community.update_reputation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER trigger_update_reputation_timestamp
    BEFORE UPDATE ON community.user_reputation
    FOR EACH ROW
    EXECUTE FUNCTION community.update_reputation_timestamp();

-- =============================================================================
-- GRANTS
-- =============================================================================

-- Grant table access
GRANT SELECT, INSERT, UPDATE, DELETE ON community.case_contributions TO authenticated;
GRANT SELECT, INSERT ON community.peer_reviews TO authenticated;
GRANT SELECT, UPDATE ON community.user_reputation TO authenticated;
GRANT SELECT ON community.reputation_transactions TO authenticated;

-- Service role gets full access
GRANT ALL ON ALL TABLES IN SCHEMA community TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA community TO service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA community TO service_role;

-- =============================================================================
-- COMMENTS
-- =============================================================================

COMMENT ON TABLE community.case_contributions IS 'Community-contributed case studies with peer review';
COMMENT ON TABLE community.peer_reviews IS 'Peer reviews for case contributions';
COMMENT ON TABLE community.user_reputation IS 'User reputation and expertise tracking';
COMMENT ON TABLE community.reputation_transactions IS 'History of reputation point awards';

COMMENT ON COLUMN community.case_contributions.case_data IS 'Anonymized workflow case data (JSONB)';
COMMENT ON COLUMN community.case_contributions.reviewers IS 'Array of assigned reviewer UUIDs';
COMMENT ON COLUMN community.user_reputation.expertise IS 'Module-specific expertise points (JSONB)';
COMMENT ON COLUMN community.user_reputation.marketplace_priority IS 'Priority score for marketplace matching (0-1000)';
