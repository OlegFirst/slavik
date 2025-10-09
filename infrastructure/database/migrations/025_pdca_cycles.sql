-- ============================================================================
-- Migration 025: PDCA Cycles Storage
-- ============================================================================
-- Purpose: Store PDCA cycle data for continuous learning and benchmarking
-- Created: 2025-10-09
-- Schema: workflow_intelligence
-- ============================================================================

-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS workflow_intelligence;

-- ============================================================================
-- Table: pdca_cycles
-- ============================================================================
-- Stores complete PDCA cycle data for each workflow execution
-- Enables: benchmarking, learning, pattern detection, continuous improvement

CREATE TABLE workflow_intelligence.pdca_cycles (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Workflow identification
    workflow_id VARCHAR(255) NOT NULL,
    module VARCHAR(100) NOT NULL,  -- bia, risk, planning, etc.
    tenant_id UUID NOT NULL,
    user_id UUID,

    -- Timing
    cycle_started_at TIMESTAMPTZ NOT NULL,
    cycle_completed_at TIMESTAMPTZ,
    do_duration FLOAT,  -- seconds

    -- ========================================================================
    -- PLAN PHASE DATA
    -- ========================================================================
    plan_data JSONB NOT NULL,
    -- Expected structure:
    -- {
    --   "workflow_data": {...},
    --   "expected_outcomes": {...},
    --   "estimated_duration": 3600
    -- }

    plan_recommendations TEXT[],
    -- AI recommendations from Case Library:
    -- ["Based on 12 similar cases: Use workshops", ...]

    expected_outcomes JSONB,
    -- Predicted outcomes:
    -- {
    --   "completion_rate": 0.9,
    --   "quality_score": 85,
    --   "key_milestones": [...]
    -- }

    estimated_duration FLOAT,
    -- Predicted duration in seconds

    similar_cases_count INTEGER DEFAULT 0,
    -- How many similar cases were used for planning

    -- ========================================================================
    -- DO PHASE DATA
    -- ========================================================================
    do_data JSONB,
    -- Execution data:
    -- {
    --   "stages_completed": [...],
    --   "actions_taken": [...],
    --   "progress_snapshots": [...]
    -- }

    -- ========================================================================
    -- CHECK PHASE DATA
    -- ========================================================================
    check_data JSONB,
    -- Final validation data:
    -- {
    --   "actual_outcomes": {...},
    --   "completion_rate": 0.95,
    --   "final_quality_score": 88
    -- }

    deviations TEXT[],
    -- List of deviations from plan:
    -- ["Duration exceeded by 20%", "Quality below threshold", ...]

    benchmarks JSONB,
    -- Comparison with historical data:
    -- {
    --   "avg_duration": 3200,
    --   "min_duration": 1800,
    --   "max_duration": 7200,
    --   "median_duration": 3000,
    --   "p95_duration": 5400
    -- }

    quality_score FLOAT,
    -- 0-100 score based on deviations and benchmarks

    -- ========================================================================
    -- ACT PHASE DATA
    -- ========================================================================
    lessons_learned TEXT[],
    -- Extracted lessons:
    -- ["Workshop approach effective for small orgs", ...]

    patterns_detected TEXT[],
    -- Detected patterns:
    -- ["bia_success_pattern", "workshop_method", ...]

    improvements TEXT[],
    -- Suggested improvements:
    -- ["Reduce planning time by 15%", "Add stakeholder template", ...]

    -- ========================================================================
    -- METADATA
    -- ========================================================================
    saved_to_knowledge_base BOOLEAN DEFAULT FALSE,
    -- Whether lessons were saved to Knowledge Base

    saved_to_case_library BOOLEAN DEFAULT FALSE,
    -- Whether cycle was contributed to Case Library

    contributed_to_predictive BOOLEAN DEFAULT FALSE,
    -- Whether feedback was sent to Predictive Engine

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Primary lookups
CREATE INDEX idx_pdca_cycles_workflow ON workflow_intelligence.pdca_cycles(workflow_id);
CREATE INDEX idx_pdca_cycles_module ON workflow_intelligence.pdca_cycles(module);
CREATE INDEX idx_pdca_cycles_tenant ON workflow_intelligence.pdca_cycles(tenant_id);
CREATE INDEX idx_pdca_cycles_user ON workflow_intelligence.pdca_cycles(user_id);

-- Analytics queries
CREATE INDEX idx_pdca_cycles_completed
    ON workflow_intelligence.pdca_cycles(cycle_completed_at)
    WHERE cycle_completed_at IS NOT NULL;

CREATE INDEX idx_pdca_cycles_module_completed
    ON workflow_intelligence.pdca_cycles(module, cycle_completed_at)
    WHERE cycle_completed_at IS NOT NULL;

-- Quality filtering
CREATE INDEX idx_pdca_cycles_quality
    ON workflow_intelligence.pdca_cycles(quality_score)
    WHERE quality_score IS NOT NULL;

-- JSONB indexes for fast queries
CREATE INDEX idx_pdca_cycles_plan_gin ON workflow_intelligence.pdca_cycles USING GIN (plan_data);
CREATE INDEX idx_pdca_cycles_check_gin ON workflow_intelligence.pdca_cycles USING GIN (check_data);
CREATE INDEX idx_pdca_cycles_benchmarks_gin ON workflow_intelligence.pdca_cycles USING GIN (benchmarks);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

ALTER TABLE workflow_intelligence.pdca_cycles ENABLE ROW LEVEL SECURITY;

-- Tenant isolation policy
CREATE POLICY pdca_cycles_tenant_isolation
    ON workflow_intelligence.pdca_cycles
    FOR ALL
    USING (
        tenant_id = current_setting('app.current_tenant_id', true)::UUID
    );

-- User can see their own cycles
CREATE POLICY pdca_cycles_user_access
    ON workflow_intelligence.pdca_cycles
    FOR SELECT
    USING (
        user_id = current_setting('app.current_user_id', true)::UUID
        OR
        tenant_id = current_setting('app.current_tenant_id', true)::UUID
    );

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function: Get benchmarks for module
CREATE OR REPLACE FUNCTION workflow_intelligence.get_pdca_benchmarks(
    p_module VARCHAR,
    p_tenant_id UUID,
    p_days_back INTEGER DEFAULT 90
)
RETURNS TABLE(
    avg_duration FLOAT,
    min_duration FLOAT,
    max_duration FLOAT,
    median_duration FLOAT,
    p95_duration FLOAT,
    avg_quality_score FLOAT,
    total_cycles INTEGER,
    success_rate FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        AVG(do_duration) as avg_duration,
        MIN(do_duration) as min_duration,
        MAX(do_duration) as max_duration,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY do_duration) as median_duration,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY do_duration) as p95_duration,
        AVG(quality_score) as avg_quality_score,
        COUNT(*)::INTEGER as total_cycles,
        (COUNT(*) FILTER (WHERE quality_score >= 70))::FLOAT / NULLIF(COUNT(*), 0) as success_rate
    FROM workflow_intelligence.pdca_cycles
    WHERE module = p_module
    AND tenant_id = p_tenant_id
    AND cycle_completed_at IS NOT NULL
    AND cycle_completed_at > NOW() - (p_days_back || ' days')::INTERVAL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Get recent patterns
CREATE OR REPLACE FUNCTION workflow_intelligence.get_recent_patterns(
    p_module VARCHAR,
    p_tenant_id UUID,
    p_limit INTEGER DEFAULT 20
)
RETURNS TABLE(
    pattern TEXT,
    frequency INTEGER,
    avg_quality_score FLOAT,
    last_seen TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        UNNEST(patterns_detected) as pattern,
        COUNT(*)::INTEGER as frequency,
        AVG(quality_score) as avg_quality_score,
        MAX(cycle_completed_at) as last_seen
    FROM workflow_intelligence.pdca_cycles
    WHERE module = p_module
    AND tenant_id = p_tenant_id
    AND patterns_detected IS NOT NULL
    AND cycle_completed_at IS NOT NULL
    GROUP BY UNNEST(patterns_detected)
    ORDER BY frequency DESC, last_seen DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Get lessons learned
CREATE OR REPLACE FUNCTION workflow_intelligence.get_lessons_learned(
    p_module VARCHAR,
    p_tenant_id UUID,
    p_min_quality FLOAT DEFAULT 70.0,
    p_limit INTEGER DEFAULT 50
)
RETURNS TABLE(
    lesson TEXT,
    cycle_id UUID,
    quality_score FLOAT,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        UNNEST(lessons_learned) as lesson,
        id as cycle_id,
        quality_score,
        created_at
    FROM workflow_intelligence.pdca_cycles
    WHERE module = p_module
    AND tenant_id = p_tenant_id
    AND quality_score >= p_min_quality
    AND lessons_learned IS NOT NULL
    AND cycle_completed_at IS NOT NULL
    ORDER BY created_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION workflow_intelligence.update_pdca_cycles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER pdca_cycles_updated_at
    BEFORE UPDATE ON workflow_intelligence.pdca_cycles
    FOR EACH ROW
    EXECUTE FUNCTION workflow_intelligence.update_pdca_cycles_updated_at();

-- ============================================================================
-- GRANTS
-- ============================================================================

-- Service role can do anything
GRANT ALL ON workflow_intelligence.pdca_cycles TO service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA workflow_intelligence TO service_role;

-- Authenticated users can insert and select their own
GRANT SELECT, INSERT, UPDATE ON workflow_intelligence.pdca_cycles TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA workflow_intelligence TO authenticated;

-- Anon users have no access
REVOKE ALL ON workflow_intelligence.pdca_cycles FROM anon;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE workflow_intelligence.pdca_cycles IS 'PDCA cycle data for continuous learning and improvement';
COMMENT ON COLUMN workflow_intelligence.pdca_cycles.workflow_id IS 'Reference to workflow execution';
COMMENT ON COLUMN workflow_intelligence.pdca_cycles.module IS 'Module type: bia, risk, planning, etc.';
COMMENT ON COLUMN workflow_intelligence.pdca_cycles.plan_recommendations IS 'AI recommendations from similar cases';
COMMENT ON COLUMN workflow_intelligence.pdca_cycles.deviations IS 'Where actual execution deviated from plan';
COMMENT ON COLUMN workflow_intelligence.pdca_cycles.lessons_learned IS 'Lessons extracted for knowledge base';
COMMENT ON COLUMN workflow_intelligence.pdca_cycles.patterns_detected IS 'Success/failure patterns identified';

COMMENT ON FUNCTION workflow_intelligence.get_pdca_benchmarks IS 'Get statistical benchmarks for module performance';
COMMENT ON FUNCTION workflow_intelligence.get_recent_patterns IS 'Get frequently occurring patterns';
COMMENT ON FUNCTION workflow_intelligence.get_lessons_learned IS 'Get high-quality lessons for learning';

-- ============================================================================
-- VERIFICATION QUERY
-- ============================================================================
-- Run this to verify migration success:
/*
SELECT
    schemaname,
    tablename,
    tableowner,
    rowsecurity
FROM pg_tables
WHERE schemaname = 'workflow_intelligence'
AND tablename = 'pdca_cycles';

SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'workflow_intelligence'
AND tablename = 'pdca_cycles';

SELECT
    policyname,
    permissive,
    roles,
    cmd,
    qual
FROM pg_policies
WHERE schemaname = 'workflow_intelligence'
AND tablename = 'pdca_cycles';
*/
