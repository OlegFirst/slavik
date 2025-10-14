-- =====================================================================
-- Migration: 045_scenario_intelligence_simplified.sql
-- Description: Scenario Intelligence System - Simplified for Standalone
-- Author: AI Platform Team
-- Date: 2025-10-12
-- =====================================================================

-- =====================================================================
-- SCHEMA: scenario_intelligence
-- =====================================================================

CREATE SCHEMA IF NOT EXISTS scenario_intelligence;

COMMENT ON SCHEMA scenario_intelligence IS
'Scenario Intelligence System - гибридная система управления поведением платформы через сценарии.';

-- =====================================================================
-- TABLE: scenarios
-- =====================================================================

CREATE TABLE scenario_intelligence.scenarios (
    -- Primary key
    id TEXT PRIMARY KEY,

    -- Versioning
    version TEXT NOT NULL DEFAULT '1.0.0',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Metadata
    level INTEGER NOT NULL CHECK (level BETWEEN 1 AND 4),
    type TEXT NOT NULL,
    pillar TEXT,
    module TEXT,
    subsystem TEXT,

    -- Content (full YAML scenario)
    content JSONB NOT NULL,

    -- Status
    status TEXT NOT NULL DEFAULT 'active',
    deprecated_at TIMESTAMPTZ,
    deprecated_reason TEXT,

    -- Compliance
    iso_clauses TEXT[],
    compliance_tags TEXT[],

    -- Search optimization
    search_vector tsvector,

    CONSTRAINT scenarios_unique_version UNIQUE (id, version)
);

-- Indexes
CREATE INDEX idx_scenarios_level ON scenario_intelligence.scenarios(level);
CREATE INDEX idx_scenarios_type ON scenario_intelligence.scenarios(type);
CREATE INDEX idx_scenarios_module ON scenario_intelligence.scenarios(module) WHERE module IS NOT NULL;
CREATE INDEX idx_scenarios_subsystem ON scenario_intelligence.scenarios(subsystem) WHERE subsystem IS NOT NULL;
CREATE INDEX idx_scenarios_status ON scenario_intelligence.scenarios(status);
CREATE INDEX idx_scenarios_search ON scenario_intelligence.scenarios USING gin(search_vector);
CREATE INDEX idx_scenarios_content ON scenario_intelligence.scenarios USING gin(content);

-- Comments
COMMENT ON TABLE scenario_intelligence.scenarios IS 'Registered scenarios in YAML format';
COMMENT ON COLUMN scenario_intelligence.scenarios.level IS '1=Module, 2=Subsystem, 3=Inter-system, 4=User';

-- =====================================================================
-- TABLE: executions
-- =====================================================================

CREATE TABLE scenario_intelligence.executions (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign keys
    scenario_id TEXT NOT NULL REFERENCES scenario_intelligence.scenarios(id) ON DELETE CASCADE,
    scenario_version TEXT NOT NULL,

    -- Execution metadata
    executed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Context
    context JSONB,

    -- Results
    status TEXT NOT NULL,
    result JSONB,
    error_message TEXT,
    stack_trace TEXT,

    -- Performance
    duration_ms INTEGER NOT NULL,
    steps_executed INTEGER,
    steps_total INTEGER,

    -- Chaos experiment results
    chaos_result JSONB,
    steady_state_before JSONB,
    steady_state_after JSONB,
    hypothesis_validated BOOLEAN,

    -- Compliance results
    compliance_result JSONB,
    evidence_generated JSONB,

    -- Call graph
    called_scenarios TEXT[],
    emitted_events TEXT[],

    -- Search
    search_vector tsvector
);

-- Indexes
CREATE INDEX idx_executions_scenario ON scenario_intelligence.executions(scenario_id);
CREATE INDEX idx_executions_status ON scenario_intelligence.executions(status);
CREATE INDEX idx_executions_executed_at ON scenario_intelligence.executions(executed_at DESC);
CREATE INDEX idx_executions_duration ON scenario_intelligence.executions(duration_ms);

-- Comments
COMMENT ON TABLE scenario_intelligence.executions IS 'Execution history for all scenarios';

-- =====================================================================
-- TABLE: statistics
-- =====================================================================

CREATE TABLE scenario_intelligence.statistics (
    -- Primary key
    scenario_id TEXT PRIMARY KEY REFERENCES scenario_intelligence.scenarios(id) ON DELETE CASCADE,

    -- Execution counts
    total_executions INTEGER NOT NULL DEFAULT 0,
    successful_executions INTEGER NOT NULL DEFAULT 0,
    failed_executions INTEGER NOT NULL DEFAULT 0,

    -- Performance metrics
    avg_duration_ms NUMERIC(10, 2),
    min_duration_ms INTEGER,
    max_duration_ms INTEGER,
    p50_duration_ms INTEGER,
    p95_duration_ms INTEGER,
    p99_duration_ms INTEGER,

    -- Success rate
    success_rate NUMERIC(5, 4),

    -- Last execution
    last_executed_at TIMESTAMPTZ,
    last_status TEXT,

    -- Timestamps
    first_executed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_statistics_success_rate ON scenario_intelligence.statistics(success_rate);
CREATE INDEX idx_statistics_last_executed ON scenario_intelligence.statistics(last_executed_at DESC);

-- Comments
COMMENT ON TABLE scenario_intelligence.statistics IS 'Aggregated execution statistics per scenario';

-- =====================================================================
-- TABLE: patterns
-- =====================================================================

CREATE TABLE scenario_intelligence.patterns (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Pattern metadata
    pattern_type TEXT NOT NULL,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    confidence NUMERIC(5, 4) NOT NULL,

    -- Pattern definition
    scenarios_involved TEXT[] NOT NULL,
    pattern_data JSONB NOT NULL,

    -- Usage
    times_observed INTEGER NOT NULL DEFAULT 1,
    last_observed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Predictions
    predicted_next_scenarios TEXT[],
    prediction_confidence NUMERIC(5, 4),

    -- Status
    status TEXT NOT NULL DEFAULT 'active'
);

-- Indexes
CREATE INDEX idx_patterns_type ON scenario_intelligence.patterns(pattern_type);
CREATE INDEX idx_patterns_confidence ON scenario_intelligence.patterns(confidence DESC);
CREATE INDEX idx_patterns_detected_at ON scenario_intelligence.patterns(detected_at DESC);
CREATE INDEX idx_patterns_scenarios ON scenario_intelligence.patterns USING gin(scenarios_involved);

-- Comments
COMMENT ON TABLE scenario_intelligence.patterns IS 'ML-detected patterns in scenario executions';

-- =====================================================================
-- TABLE: predictions
-- =====================================================================

CREATE TABLE scenario_intelligence.predictions (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Context
    current_scenario_id TEXT NOT NULL REFERENCES scenario_intelligence.scenarios(id) ON DELETE CASCADE,
    pattern_id UUID REFERENCES scenario_intelligence.patterns(id) ON DELETE CASCADE,

    -- Prediction
    predicted_scenario_id TEXT NOT NULL REFERENCES scenario_intelligence.scenarios(id) ON DELETE CASCADE,
    confidence NUMERIC(5, 4) NOT NULL,

    -- Timestamps
    predicted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Validation
    validated BOOLEAN,
    validated_at TIMESTAMPTZ,
    correct BOOLEAN
);

-- Indexes
CREATE INDEX idx_predictions_current_scenario ON scenario_intelligence.predictions(current_scenario_id);
CREATE INDEX idx_predictions_predicted_scenario ON scenario_intelligence.predictions(predicted_scenario_id);
CREATE INDEX idx_predictions_pattern ON scenario_intelligence.predictions(pattern_id);
CREATE INDEX idx_predictions_confidence ON scenario_intelligence.predictions(confidence DESC);

-- Comments
COMMENT ON TABLE scenario_intelligence.predictions IS 'Predicted next scenarios based on patterns';

-- =====================================================================
-- TABLE: evidence_vault
-- =====================================================================

CREATE TABLE scenario_intelligence.evidence_vault (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign keys
    execution_id UUID NOT NULL REFERENCES scenario_intelligence.executions(id) ON DELETE CASCADE,
    scenario_id TEXT NOT NULL REFERENCES scenario_intelligence.scenarios(id) ON DELETE CASCADE,

    -- Evidence metadata
    evidence_type TEXT NOT NULL,
    format TEXT NOT NULL,

    -- Compliance
    iso_clause_id TEXT,
    iso_clause_name TEXT,

    -- Content
    content JSONB,
    file_path TEXT,
    file_size_bytes INTEGER,

    -- Retention
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    retention_period TEXT,
    retention_until TIMESTAMPTZ,
    archived BOOLEAN DEFAULT FALSE,
    archived_at TIMESTAMPTZ,

    -- Search
    search_vector tsvector
);

-- Indexes
CREATE INDEX idx_evidence_execution ON scenario_intelligence.evidence_vault(execution_id);
CREATE INDEX idx_evidence_scenario ON scenario_intelligence.evidence_vault(scenario_id);
CREATE INDEX idx_evidence_iso_clause ON scenario_intelligence.evidence_vault(iso_clause_id);
CREATE INDEX idx_evidence_retention_until ON scenario_intelligence.evidence_vault(retention_until);
CREATE INDEX idx_evidence_archived ON scenario_intelligence.evidence_vault(archived);

-- Comments
COMMENT ON TABLE scenario_intelligence.evidence_vault IS 'ISO 22301 compliance evidence';

-- =====================================================================
-- FUNCTIONS: Auto-update triggers
-- =====================================================================

-- Update scenarios.updated_at
CREATE OR REPLACE FUNCTION scenario_intelligence.update_scenario_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER scenarios_update_timestamp
    BEFORE UPDATE ON scenario_intelligence.scenarios
    FOR EACH ROW
    EXECUTE FUNCTION scenario_intelligence.update_scenario_timestamp();

-- Update search_vector for scenarios
CREATE OR REPLACE FUNCTION scenario_intelligence.update_scenario_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', COALESCE(NEW.id, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.type, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.module, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.subsystem, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.content::text, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER scenarios_update_search_vector
    BEFORE INSERT OR UPDATE ON scenario_intelligence.scenarios
    FOR EACH ROW
    EXECUTE FUNCTION scenario_intelligence.update_scenario_search_vector();

-- Auto-update statistics
CREATE OR REPLACE FUNCTION scenario_intelligence.update_statistics_on_execution()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO scenario_intelligence.statistics (
        scenario_id,
        total_executions,
        successful_executions,
        failed_executions,
        avg_duration_ms,
        min_duration_ms,
        max_duration_ms,
        last_executed_at,
        last_status,
        first_executed_at,
        updated_at
    )
    VALUES (
        NEW.scenario_id,
        1,
        CASE WHEN NEW.status = 'success' THEN 1 ELSE 0 END,
        CASE WHEN NEW.status = 'failed' THEN 1 ELSE 0 END,
        NEW.duration_ms,
        NEW.duration_ms,
        NEW.duration_ms,
        NEW.executed_at,
        NEW.status,
        NEW.executed_at,
        NOW()
    )
    ON CONFLICT (scenario_id) DO UPDATE SET
        total_executions = scenario_intelligence.statistics.total_executions + 1,
        successful_executions = scenario_intelligence.statistics.successful_executions +
            CASE WHEN NEW.status = 'success' THEN 1 ELSE 0 END,
        failed_executions = scenario_intelligence.statistics.failed_executions +
            CASE WHEN NEW.status = 'failed' THEN 1 ELSE 0 END,
        avg_duration_ms = (
            (scenario_intelligence.statistics.avg_duration_ms * scenario_intelligence.statistics.total_executions + NEW.duration_ms) /
            (scenario_intelligence.statistics.total_executions + 1)
        ),
        min_duration_ms = LEAST(scenario_intelligence.statistics.min_duration_ms, NEW.duration_ms),
        max_duration_ms = GREATEST(scenario_intelligence.statistics.max_duration_ms, NEW.duration_ms),
        last_executed_at = NEW.executed_at,
        last_status = NEW.status,
        updated_at = NOW(),
        success_rate = (
            (scenario_intelligence.statistics.successful_executions + CASE WHEN NEW.status = 'success' THEN 1 ELSE 0 END)::NUMERIC /
            (scenario_intelligence.statistics.total_executions + 1)::NUMERIC
        );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER executions_update_statistics
    AFTER INSERT ON scenario_intelligence.executions
    FOR EACH ROW
    EXECUTE FUNCTION scenario_intelligence.update_statistics_on_execution();

-- =====================================================================
-- VIEWS
-- =====================================================================

-- Active scenarios with statistics
CREATE OR REPLACE VIEW scenario_intelligence.scenarios_with_stats AS
SELECT
    s.*,
    COALESCE(st.total_executions, 0) as total_executions,
    COALESCE(st.successful_executions, 0) as successful_executions,
    COALESCE(st.failed_executions, 0) as failed_executions,
    COALESCE(st.success_rate, 0) as success_rate,
    st.avg_duration_ms,
    st.last_executed_at,
    st.last_status
FROM scenario_intelligence.scenarios s
LEFT JOIN scenario_intelligence.statistics st ON s.id = st.scenario_id
WHERE s.status = 'active';

COMMENT ON VIEW scenario_intelligence.scenarios_with_stats IS 'Active scenarios with statistics';

-- Recent executions (last 24h)
CREATE OR REPLACE VIEW scenario_intelligence.recent_executions AS
SELECT
    e.*,
    s.type as scenario_type,
    s.level as scenario_level,
    s.module as scenario_module
FROM scenario_intelligence.executions e
JOIN scenario_intelligence.scenarios s ON e.scenario_id = s.id
WHERE e.executed_at > NOW() - INTERVAL '24 hours'
ORDER BY e.executed_at DESC;

COMMENT ON VIEW scenario_intelligence.recent_executions IS 'Executions in last 24 hours';

-- =====================================================================
-- GRANTS
-- =====================================================================

GRANT USAGE ON SCHEMA scenario_intelligence TO postgres, anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA scenario_intelligence TO postgres, service_role;
GRANT SELECT ON ALL TABLES IN SCHEMA scenario_intelligence TO anon;
GRANT ALL ON ALL TABLES IN SCHEMA scenario_intelligence TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA scenario_intelligence TO postgres, authenticated, service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA scenario_intelligence TO postgres, anon, authenticated, service_role;

-- =====================================================================
-- INITIAL DATA
-- =====================================================================

INSERT INTO scenario_intelligence.scenarios (
    id,
    version,
    level,
    type,
    module,
    content,
    status,
    iso_clauses
) VALUES (
    'system-health-check',
    '1.0.0',
    1,
    'functional',
    'platform',
    '{"scenario": {"meta": {"id": "system-health-check", "version": "1.0.0", "level": 1, "type": "functional"}, "description": {"title": "System Health Check", "summary": "Verify all critical services"}}}'::jsonb,
    'active',
    ARRAY['4.4', '8.1']
) ON CONFLICT (id, version) DO NOTHING;

-- =====================================================================
-- END OF MIGRATION
-- =====================================================================

COMMENT ON SCHEMA scenario_intelligence IS 'Migration 045: Scenario Intelligence - Complete (Simplified)';
