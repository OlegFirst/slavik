-- =====================================================
-- Migration 044: KQM Knowledge Management
-- =====================================================
-- Knowledge Quality Manager (KQM) - Complete database schema
-- Implements Trinity Philosophy: Knowledge, Protection, Self-Realization
-- Date: 2025-10-11
-- =====================================================

-- SCENARIOS TABLE
CREATE TABLE IF NOT EXISTS public.kqm_scenarios (
    -- Primary keys
    id VARCHAR(255) PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('existing', 'generated', 'standard', 'community')),

    -- Classification
    service VARCHAR(100),
    category VARCHAR(100),
    iso_clause VARCHAR(20),

    -- Metadata
    source VARCHAR(255) NOT NULL,
    confidence DECIMAL(3,2) CHECK (confidence >= 0 AND confidence <= 1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Additional details
    inputs TEXT,
    outputs TEXT,
    events TEXT,
    components TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_kqm_scenarios_service ON public.kqm_scenarios(service);
CREATE INDEX IF NOT EXISTS idx_kqm_scenarios_type ON public.kqm_scenarios(type);
CREATE INDEX IF NOT EXISTS idx_kqm_scenarios_iso_clause ON public.kqm_scenarios(iso_clause);
CREATE INDEX IF NOT EXISTS idx_kqm_scenarios_created_at ON public.kqm_scenarios(created_at DESC);

-- Comments
COMMENT ON TABLE public.kqm_scenarios IS 'KQM: Scenarios catalog - all platform usage scenarios';
COMMENT ON COLUMN public.kqm_scenarios.type IS 'Scenario type: existing (catalog), generated (auto), standard (ISO), community (patterns)';
COMMENT ON COLUMN public.kqm_scenarios.confidence IS 'LLM generation confidence (0-1)';

-- =====================================================
-- KNOWLEDGE GAPS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS public.kqm_knowledge_gaps (
    -- Primary keys
    id VARCHAR(255) PRIMARY KEY,
    type VARCHAR(50) NOT NULL CHECK (type IN ('standard_requirement', 'platform_capability', 'user_request', 'community_pattern')),
    description TEXT NOT NULL,
    priority INTEGER CHECK (priority >= 1 AND priority <= 10),

    -- Context
    standard VARCHAR(50),
    clause VARCHAR(20),
    service VARCHAR(100),
    capability VARCHAR(255),
    user_question TEXT,

    -- Metadata
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'detected' CHECK (status IN ('detected', 'in_progress', 'resolved'))
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_kqm_gaps_type ON public.kqm_knowledge_gaps(type);
CREATE INDEX IF NOT EXISTS idx_kqm_gaps_priority ON public.kqm_knowledge_gaps(priority DESC);
CREATE INDEX IF NOT EXISTS idx_kqm_gaps_status ON public.kqm_knowledge_gaps(status);
CREATE INDEX IF NOT EXISTS idx_kqm_gaps_detected_at ON public.kqm_knowledge_gaps(detected_at DESC);

-- Comments
COMMENT ON TABLE public.kqm_knowledge_gaps IS 'KQM: Detected knowledge gaps requiring scenarios';
COMMENT ON COLUMN public.kqm_knowledge_gaps.type IS 'Gap type: standard_requirement, platform_capability, user_request, community_pattern';
COMMENT ON COLUMN public.kqm_knowledge_gaps.priority IS 'Priority 1-10 (10 = highest)';

-- =====================================================
-- SCENARIO VALIDATIONS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS public.kqm_scenario_validations (
    -- Primary keys
    id SERIAL PRIMARY KEY,
    scenario_id VARCHAR(255) NOT NULL REFERENCES public.kqm_scenarios(id) ON DELETE CASCADE,

    -- Validation results
    iso_compliant BOOLEAN NOT NULL,
    technically_valid BOOLEAN NOT NULL,
    expert_approved BOOLEAN NOT NULL,
    quality_score DECIMAL(3,2) CHECK (quality_score >= 0 AND quality_score <= 1),

    -- Status
    status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'in_review', 'approved', 'rejected', 'needs_revision')),
    validation_notes TEXT,
    validated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Expert info
    expert_id VARCHAR(100),
    expert_domain VARCHAR(100)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_kqm_validations_scenario ON public.kqm_scenario_validations(scenario_id);
CREATE INDEX IF NOT EXISTS idx_kqm_validations_status ON public.kqm_scenario_validations(status);
CREATE INDEX IF NOT EXISTS idx_kqm_validations_quality ON public.kqm_scenario_validations(quality_score DESC);

-- Comments
COMMENT ON TABLE public.kqm_scenario_validations IS 'KQM: Scenario validation results (ISO + Technical + Expert)';
COMMENT ON COLUMN public.kqm_scenario_validations.quality_score IS 'Combined quality score (0-1)';

-- =====================================================
-- KNOWLEDGE METRICS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS public.kqm_knowledge_metrics (
    -- Primary keys
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Coverage metrics
    iso_coverage DECIMAL(3,2),
    platform_coverage DECIMAL(3,2),
    user_gaps INTEGER,
    total_scenarios INTEGER,
    iso_clauses_total INTEGER,
    iso_clauses_documented INTEGER,
    endpoints_total INTEGER,
    endpoints_documented INTEGER,

    -- Quality metrics
    validation_rate DECIMAL(3,2),
    expert_approval_rate DECIMAL(3,2),
    usage_rate DECIMAL(3,2),
    stale_count INTEGER,
    avg_confidence DECIMAL(3,2),

    -- Generation metrics
    scenarios_generated_today INTEGER,
    scenarios_generated_this_week INTEGER,
    scenarios_generated_this_month INTEGER,
    pending_validation INTEGER,
    approved_today INTEGER,

    -- Performance metrics
    search_latency_ms DECIMAL(10,2),
    generation_time_min DECIMAL(10,2),
    cache_hit_rate DECIMAL(3,2),
    avg_quality_score DECIMAL(3,2),

    -- Gaps by type (JSON)
    gaps_detected JSONB
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_kqm_metrics_timestamp ON public.kqm_knowledge_metrics(timestamp DESC);

-- Comments
COMMENT ON TABLE public.kqm_knowledge_metrics IS 'KQM: Complete knowledge quality metrics (daily snapshots)';

-- =====================================================
-- COMPLIANCE STATUS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS public.kqm_compliance_status (
    -- Primary keys
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- ISO 22301
    iso_22301_compliance JSONB,

    -- NIST SP 800-34
    nist_sp_800_34_compliance JSONB,

    -- WHO Emergency
    who_emergency_compliance JSONB,

    -- Overall
    overall_compliance DECIMAL(3,2) CHECK (overall_compliance >= 0 AND overall_compliance <= 1),
    critical_gaps TEXT[]
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_kqm_compliance_timestamp ON public.kqm_compliance_status(timestamp DESC);

-- Comments
COMMENT ON TABLE public.kqm_compliance_status IS 'KQM: Compliance status across all standards (ISO/NIST/WHO)';

-- =====================================================
-- SCENARIO USAGE TRACKING TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS public.kqm_scenario_usage (
    -- Primary keys
    id SERIAL PRIMARY KEY,
    scenario_id VARCHAR(255) NOT NULL REFERENCES public.kqm_scenarios(id) ON DELETE CASCADE,

    -- Usage info
    used_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(100),
    context VARCHAR(255),

    -- Feedback
    helpful BOOLEAN,
    feedback_text TEXT,

    -- Session
    session_id VARCHAR(100)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_kqm_usage_scenario ON public.kqm_scenario_usage(scenario_id);
CREATE INDEX IF NOT EXISTS idx_kqm_usage_used_at ON public.kqm_scenario_usage(used_at DESC);
CREATE INDEX IF NOT EXISTS idx_kqm_usage_helpful ON public.kqm_scenario_usage(helpful);

-- Comments
COMMENT ON TABLE public.kqm_scenario_usage IS 'KQM: Scenario usage tracking for Self-Realization metrics';

-- =====================================================
-- GENERATION QUEUE TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS public.kqm_generation_queue (
    -- Primary keys
    id SERIAL PRIMARY KEY,
    gap_id VARCHAR(255) NOT NULL REFERENCES public.kqm_knowledge_gaps(id) ON DELETE CASCADE,

    -- Queue info
    priority INTEGER,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),

    -- Processing
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,

    -- Result
    generated_scenario_id VARCHAR(255) REFERENCES public.kqm_scenarios(id),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_kqm_queue_status ON public.kqm_generation_queue(status);
CREATE INDEX IF NOT EXISTS idx_kqm_queue_priority ON public.kqm_generation_queue(priority DESC);

-- Comments
COMMENT ON TABLE public.kqm_generation_queue IS 'KQM: Generation queue for 24-hour orchestration cycle';

-- =====================================================
-- KNOWLEDGE VALUE TRACKING TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS public.kqm_knowledge_value (
    -- Primary keys
    id SERIAL PRIMARY KEY,
    scenario_id VARCHAR(255) NOT NULL REFERENCES public.kqm_scenarios(id) ON DELETE CASCADE,

    -- Value calculation
    confidence_score DECIMAL(3,2),
    relevance_score DECIMAL(3,2),
    reusability_score DECIMAL(3,2),
    compliance_score DECIMAL(3,2),

    -- Total value
    total_value DECIMAL(10,2),

    -- Timestamp
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_kqm_value_scenario ON public.kqm_knowledge_value(scenario_id);
CREATE INDEX IF NOT EXISTS idx_kqm_value_total ON public.kqm_knowledge_value(total_value DESC);

-- Comments
COMMENT ON TABLE public.kqm_knowledge_value IS 'KQM: Knowledge economics - value calculation for scenarios';

-- =====================================================
-- VIEWS
-- =====================================================

-- View: Recent approved scenarios
CREATE OR REPLACE VIEW public.kqm_recent_approved AS
SELECT
    s.*,
    v.quality_score,
    v.validated_at
FROM public.kqm_scenarios s
JOIN public.kqm_scenario_validations v ON s.id = v.scenario_id
WHERE v.status = 'approved'
ORDER BY v.validated_at DESC;

-- View: Gap analysis summary
CREATE OR REPLACE VIEW public.kqm_gap_summary AS
SELECT
    type,
    COUNT(*) as gap_count,
    AVG(priority) as avg_priority,
    COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_count
FROM public.kqm_knowledge_gaps
GROUP BY type;

-- View: Latest metrics
CREATE OR REPLACE VIEW public.kqm_latest_metrics AS
SELECT *
FROM public.kqm_knowledge_metrics
ORDER BY timestamp DESC
LIMIT 1;

-- =====================================================
-- FUNCTIONS
-- =====================================================

-- Function: Update scenario updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_kqm_scenario_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Auto-update scenario timestamp
DROP TRIGGER IF EXISTS trigger_update_kqm_scenario_timestamp ON public.kqm_scenarios;
CREATE TRIGGER trigger_update_kqm_scenario_timestamp
BEFORE UPDATE ON public.kqm_scenarios
FOR EACH ROW
EXECUTE FUNCTION public.update_kqm_scenario_timestamp();

-- Function: Calculate knowledge value
CREATE OR REPLACE FUNCTION public.calculate_kqm_knowledge_value(
    p_scenario_id VARCHAR(255)
)
RETURNS DECIMAL(10,2) AS $$
DECLARE
    v_confidence DECIMAL(3,2);
    v_relevance DECIMAL(3,2);
    v_reusability DECIMAL(3,2);
    v_compliance DECIMAL(3,2);
    v_value DECIMAL(10,2);
BEGIN
    -- Get scenario details
    SELECT
        COALESCE(confidence, 0.5),
        CASE WHEN type = 'standard' THEN 0.9 ELSE 0.7 END,
        CASE WHEN type = 'standard' THEN 0.9 ELSE 0.7 END,
        CASE WHEN iso_clause IS NOT NULL THEN 1.0 ELSE 0.5 END
    INTO v_confidence, v_relevance, v_reusability, v_compliance
    FROM public.kqm_scenarios
    WHERE id = p_scenario_id;

    -- Calculate value: confidence × relevance × reusability × compliance × 100
    v_value := v_confidence * v_relevance * v_reusability * v_compliance * 100;

    -- Store value
    INSERT INTO public.kqm_knowledge_value (
        scenario_id,
        confidence_score,
        relevance_score,
        reusability_score,
        compliance_score,
        total_value
    ) VALUES (
        p_scenario_id,
        v_confidence,
        v_relevance,
        v_reusability,
        v_compliance,
        v_value
    );

    RETURN v_value;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- INITIAL DATA
-- =====================================================

-- Insert initial compliance status
INSERT INTO public.kqm_compliance_status (
    iso_22301_compliance,
    nist_sp_800_34_compliance,
    who_emergency_compliance,
    overall_compliance,
    critical_gaps
) VALUES (
    '{}',
    '{}',
    '{}',
    0.0,
    ARRAY[]::TEXT[]
) ON CONFLICT DO NOTHING;

-- =====================================================
-- GRANTS (RLS will be added later if needed)
-- =====================================================

-- Grant access to authenticated users
GRANT SELECT, INSERT, UPDATE, DELETE ON public.kqm_scenarios TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.kqm_knowledge_gaps TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.kqm_scenario_validations TO authenticated;
GRANT SELECT, INSERT ON public.kqm_knowledge_metrics TO authenticated;
GRANT SELECT, INSERT ON public.kqm_compliance_status TO authenticated;
GRANT SELECT, INSERT ON public.kqm_scenario_usage TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.kqm_generation_queue TO authenticated;
GRANT SELECT, INSERT ON public.kqm_knowledge_value TO authenticated;

-- Grant sequence usage
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

-- Log migration
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 044: KQM Knowledge Management - COMPLETE';
    RAISE NOTICE '   Tables: 8 created';
    RAISE NOTICE '   Views: 3 created';
    RAISE NOTICE '   Functions: 2 created';
    RAISE NOTICE '   Philosophy: Trinity (Knowledge, Protection, Self-Realization)';
END $$;
