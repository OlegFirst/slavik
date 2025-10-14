-- ================================================
-- MIGRATION 041: COLLECTIVE AGENT NETWORKS
-- ================================================
-- Purpose: Anonymous collaboration between organizations
--
-- Features:
-- - Collective Agents: Temporary AI from multiple orgs' experiences
-- - Stuck Detection: Identifies organizations needing help
-- - Privacy-Preserving: Source organizations never revealed
--
-- Innovation: Organizations help each other through AI without
--             revealing their identities
-- ================================================

BEGIN;

-- ================================================
-- ENUMS
-- ================================================

CREATE TYPE agent_status AS ENUM ('active', 'expired', 'archived');

-- ================================================
-- TABLE: collective_agents
-- ================================================
-- Temporary AI agents created from multiple organizations
--
-- Privacy guarantees:
-- - Source organizations NEVER revealed
-- - All data anonymized before aggregation
-- - Expires after 7 days (no long-term tracking)
-- ================================================

CREATE TABLE collective_agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requesting_org_id UUID NOT NULL,  -- Who requested help (NOT revealed to sources)
    problem_type VARCHAR(100) NOT NULL,  -- e.g., "supply_chain_complexity"

    -- Source information (anonymized)
    source_org_count INTEGER NOT NULL CHECK (source_org_count >= 5),  -- Minimum 5 for k-anonymity
    source_org_types TEXT[] NOT NULL,  -- e.g., ["healthcare_medium", "hospital_large"]

    -- Agent configuration
    system_prompt TEXT NOT NULL,  -- LLM system prompt with privacy rules
    approaches_data JSONB NOT NULL,  -- Anonymized approaches from source orgs

    -- Status and lifecycle
    status agent_status NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,  -- Auto-expire after 7 days

    -- Usage stats
    message_count INTEGER NOT NULL DEFAULT 0,
    last_interaction TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX idx_collective_agents_org ON collective_agents(requesting_org_id);
CREATE INDEX idx_collective_agents_status ON collective_agents(status) WHERE status = 'active';
CREATE INDEX idx_collective_agents_expires ON collective_agents(expires_at) WHERE status = 'active';
CREATE INDEX idx_collective_agents_problem ON collective_agents(problem_type);

-- ================================================
-- TABLE: collective_agent_messages
-- ================================================
-- Chat messages with Collective Agent
--
-- Privacy:
-- - Agent NEVER reveals source organizations
-- - All responses synthesized across multiple orgs
-- - Speaks as "Organizations that..." not "Org X did..."
-- ================================================

CREATE TABLE collective_agent_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES collective_agents(id) ON DELETE CASCADE,

    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,

    metadata JSONB,  -- Confidence scores, citations, etc.
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_agent_messages_agent ON collective_agent_messages(agent_id);
CREATE INDEX idx_agent_messages_created ON collective_agent_messages(agent_id, created_at);

-- ================================================
-- TABLE: stuck_detection_logs
-- ================================================
-- Tracks when organizations are detected as stuck
--
-- Signals:
-- - Days without progress
-- - Validation failures
-- - Low AI confidence
-- - Repeated questions
-- - Frustration indicators
--
-- When stuck → Offer collective agent
-- ================================================

CREATE TABLE stuck_detection_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL,
    module VARCHAR(50),

    -- Detection results
    stuck_score INTEGER NOT NULL,
    signals JSONB NOT NULL,  -- All signals contributing to stuck score

    -- Recommendations
    recommendations JSONB NOT NULL,

    -- Outcome
    help_offered BOOLEAN NOT NULL DEFAULT FALSE,
    help_accepted BOOLEAN NOT NULL DEFAULT FALSE,
    collective_agent_created UUID REFERENCES collective_agents(id),

    detected_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_stuck_detection_org ON stuck_detection_logs(org_id);
CREATE INDEX idx_stuck_detection_detected ON stuck_detection_logs(detected_at);
CREATE INDEX idx_stuck_detection_score ON stuck_detection_logs(stuck_score) WHERE stuck_score >= 4;

-- ================================================
-- ROW LEVEL SECURITY
-- ================================================

ALTER TABLE collective_agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE collective_agent_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE stuck_detection_logs ENABLE ROW LEVEL SECURITY;

-- Collective Agents: Only requesting org can access
CREATE POLICY collective_agents_select ON collective_agents
    FOR SELECT
    USING (
        requesting_org_id = (SELECT organization_id FROM individual_users WHERE auth_user_id = auth.uid())
    );

CREATE POLICY collective_agents_insert ON collective_agents
    FOR INSERT
    WITH CHECK (
        requesting_org_id = (SELECT organization_id FROM individual_users WHERE auth_user_id = auth.uid())
    );

-- Messages: Only if you own the agent
CREATE POLICY agent_messages_select ON collective_agent_messages
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM collective_agents
            WHERE id = agent_id
            AND requesting_org_id = (SELECT organization_id FROM individual_users WHERE auth_user_id = auth.uid())
        )
    );

CREATE POLICY agent_messages_insert ON collective_agent_messages
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM collective_agents
            WHERE id = agent_id
            AND requesting_org_id = (SELECT organization_id FROM individual_users WHERE auth_user_id = auth.uid())
        )
    );

-- Stuck Detection: Own org only
CREATE POLICY stuck_detection_select ON stuck_detection_logs
    FOR SELECT
    USING (
        org_id = (SELECT organization_id FROM individual_users WHERE auth_user_id = auth.uid())
    );

CREATE POLICY stuck_detection_insert ON stuck_detection_logs
    FOR INSERT
    WITH CHECK (
        org_id = (SELECT organization_id FROM individual_users WHERE auth_user_id = auth.uid())
    );

-- ================================================
-- FUNCTIONS
-- ================================================

-- Auto-expire old agents (cleanup job)
CREATE OR REPLACE FUNCTION expire_old_collective_agents()
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    expired_count INTEGER;
BEGIN
    -- Mark expired agents
    UPDATE collective_agents
    SET status = 'expired'
    WHERE status = 'active'
    AND expires_at < NOW();

    GET DIAGNOSTICS expired_count = ROW_COUNT;

    RETURN expired_count;
END;
$$;

-- Get stuck organizations (daily check)
CREATE OR REPLACE FUNCTION get_stuck_organizations(
    p_days_threshold INTEGER DEFAULT 7,
    p_stuck_score_threshold INTEGER DEFAULT 4
)
RETURNS TABLE(
    org_id UUID,
    latest_stuck_score INTEGER,
    days_since_detection INTEGER
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    WITH latest_detections AS (
        SELECT DISTINCT ON (sdl.org_id)
            sdl.org_id,
            sdl.stuck_score,
            sdl.detected_at
        FROM stuck_detection_logs sdl
        WHERE sdl.detected_at > NOW() - INTERVAL '30 days'
        ORDER BY sdl.org_id, sdl.detected_at DESC
    )
    SELECT
        ld.org_id,
        ld.stuck_score,
        EXTRACT(DAY FROM NOW() - ld.detected_at)::INTEGER
    FROM latest_detections ld
    WHERE ld.stuck_score >= p_stuck_score_threshold
    AND NOT EXISTS (
        -- Haven't already created agent recently
        SELECT 1 FROM collective_agents ca
        WHERE ca.requesting_org_id = ld.org_id
        AND ca.created_at > NOW() - INTERVAL '7 days'
    );
END;
$$;

-- Calculate k-anonymity for problem type
CREATE OR REPLACE FUNCTION calculate_k_anonymity(
    p_problem_type VARCHAR,
    p_exclude_org_id UUID DEFAULT NULL
)
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    org_count INTEGER;
BEGIN
    -- Count organizations with successful cases for this problem
    -- This would query case_library in production
    -- For now, return placeholder

    RETURN 7;  -- Placeholder
END;
$$;

-- ================================================
-- COMMENTS
-- ================================================

COMMENT ON TABLE collective_agents IS
'Temporary AI agents created from multiple organizations'' experiences. Privacy-preserving collective intelligence.';

COMMENT ON COLUMN collective_agents.source_org_count IS
'Number of source organizations. Minimum 5 required for k-anonymity privacy guarantee.';

COMMENT ON COLUMN collective_agents.system_prompt IS
'LLM system prompt with strict privacy rules: NEVER reveal source organizations, always speak as aggregate.';

COMMENT ON TABLE collective_agent_messages IS
'Chat history with collective agents. Agent responses synthesized from multiple orgs without attribution.';

COMMENT ON TABLE stuck_detection_logs IS
'Tracks organizations detected as stuck. Used to proactively offer collective help.';

COMMIT;
