-- ============================================================================
-- Process Analytics Schema for Supabase
-- ============================================================================
-- Purpose: Advanced process mining and analytics for BCM Platform workflows
-- Schema: process_analytics.*
-- Version: 1.0.0
-- Date: 2025-10-07
-- ============================================================================

-- Create schema
CREATE SCHEMA IF NOT EXISTS process_analytics;

-- Grant permissions
GRANT USAGE ON SCHEMA process_analytics TO postgres, anon, authenticated, service_role;

-- ============================================================================
-- TABLES
-- ============================================================================

-- 1. Process Executions (Process Instances)
-- ============================================================================
CREATE TABLE IF NOT EXISTS process_analytics.executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_id VARCHAR(255) NOT NULL,
    execution_id VARCHAR(255) NOT NULL UNIQUE,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    status VARCHAR(50) NOT NULL CHECK (status IN ('running', 'completed', 'failed', 'cancelled')),
    duration_minutes FLOAT,
    executed_by VARCHAR(255),
    execution_metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_executions_process_id ON process_analytics.executions(process_id);
CREATE INDEX idx_executions_status ON process_analytics.executions(status);
CREATE INDEX idx_executions_start_time ON process_analytics.executions(start_time);
CREATE INDEX idx_executions_executed_by ON process_analytics.executions(executed_by);

COMMENT ON TABLE process_analytics.executions IS 'Process execution instances with timing and status tracking';
COMMENT ON COLUMN process_analytics.executions.process_id IS 'Identifier for the process definition (e.g., bia_workflow, risk_assessment)';
COMMENT ON COLUMN process_analytics.executions.execution_id IS 'Unique identifier for this specific execution instance';
COMMENT ON COLUMN process_analytics.executions.status IS 'Current status: running, completed, failed, cancelled';
COMMENT ON COLUMN process_analytics.executions.duration_minutes IS 'Total execution time in minutes (calculated on completion)';

-- 2. Process Events (Individual Steps)
-- ============================================================================
CREATE TABLE IF NOT EXISTS process_analytics.events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID NOT NULL REFERENCES process_analytics.executions(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN ('start', 'end', 'checkpoint', 'error', 'decision', 'approval', 'rejection')),
    step_name VARCHAR(255) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    duration_minutes FLOAT,
    actor VARCHAR(255),
    event_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_events_execution_id ON process_analytics.events(execution_id);
CREATE INDEX idx_events_step_name ON process_analytics.events(step_name);
CREATE INDEX idx_events_event_type ON process_analytics.events(event_type);
CREATE INDEX idx_events_timestamp ON process_analytics.events(timestamp);
CREATE INDEX idx_events_actor ON process_analytics.events(actor);

COMMENT ON TABLE process_analytics.events IS 'Individual events within process executions (steps, decisions, errors)';
COMMENT ON COLUMN process_analytics.events.event_type IS 'Type: start, end, checkpoint, error, decision, approval, rejection';
COMMENT ON COLUMN process_analytics.events.step_name IS 'Name of the process step (e.g., bia_data_collection, risk_analysis)';
COMMENT ON COLUMN process_analytics.events.actor IS 'User or system that triggered this event';

-- 3. Discovered Patterns
-- ============================================================================
CREATE TABLE IF NOT EXISTS process_analytics.patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_id VARCHAR(255) NOT NULL,
    pattern_type VARCHAR(50) NOT NULL CHECK (pattern_type IN ('sequence', 'parallel', 'loop', 'skip', 'conditional')),
    pattern_name VARCHAR(255) NOT NULL,
    frequency INTEGER NOT NULL DEFAULT 0,
    confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    pattern_data JSONB NOT NULL,
    discovered_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_patterns_process_id ON process_analytics.patterns(process_id);
CREATE INDEX idx_patterns_type ON process_analytics.patterns(pattern_type);
CREATE INDEX idx_patterns_confidence ON process_analytics.patterns(confidence);
CREATE INDEX idx_patterns_frequency ON process_analytics.patterns(frequency);

COMMENT ON TABLE process_analytics.patterns IS 'Discovered patterns in process executions (sequences, loops, parallels)';
COMMENT ON COLUMN process_analytics.patterns.pattern_type IS 'Type: sequence (A→B→C), parallel (A||B), loop (A→A), skip (A→C bypassing B)';
COMMENT ON COLUMN process_analytics.patterns.frequency IS 'Number of times this pattern was observed';
COMMENT ON COLUMN process_analytics.patterns.confidence IS 'Confidence score 0-1 (how reliably this pattern occurs)';
COMMENT ON COLUMN process_analytics.patterns.pattern_data IS 'Pattern details: {steps: [...], transitions: [...], metrics: {...}}';

-- 4. Process Deviations
-- ============================================================================
CREATE TABLE IF NOT EXISTS process_analytics.deviations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID NOT NULL REFERENCES process_analytics.executions(id) ON DELETE CASCADE,
    deviation_type VARCHAR(50) NOT NULL CHECK (deviation_type IN ('timing', 'sequence', 'resource', 'quality', 'compliance')),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    description TEXT,
    expected_value VARCHAR(500),
    actual_value VARCHAR(500),
    impact_score FLOAT CHECK (impact_score >= 0 AND impact_score <= 10),
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT
);

CREATE INDEX idx_deviations_execution_id ON process_analytics.deviations(execution_id);
CREATE INDEX idx_deviations_type ON process_analytics.deviations(deviation_type);
CREATE INDEX idx_deviations_severity ON process_analytics.deviations(severity);
CREATE INDEX idx_deviations_detected_at ON process_analytics.deviations(detected_at);

COMMENT ON TABLE process_analytics.deviations IS 'Detected deviations from expected process behavior';
COMMENT ON COLUMN process_analytics.deviations.deviation_type IS 'Type: timing (took too long), sequence (wrong order), resource (wrong person), quality (errors), compliance (violated rules)';
COMMENT ON COLUMN process_analytics.deviations.severity IS 'Impact level: low, medium, high, critical';
COMMENT ON COLUMN process_analytics.deviations.impact_score IS 'Business impact score 0-10 (10 = most severe)';

-- 5. Process Bottlenecks
-- ============================================================================
CREATE TABLE IF NOT EXISTS process_analytics.bottlenecks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_id VARCHAR(255) NOT NULL,
    step_name VARCHAR(255) NOT NULL,
    bottleneck_type VARCHAR(50) NOT NULL CHECK (bottleneck_type IN ('duration', 'waiting_time', 'resource_contention', 'error_rate', 'throughput')),
    avg_duration_minutes FLOAT,
    occurrence_count INTEGER NOT NULL DEFAULT 0,
    impact_score FLOAT CHECK (impact_score >= 0 AND impact_score <= 10),
    suggested_improvements TEXT[],
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_bottlenecks_process_id ON process_analytics.bottlenecks(process_id);
CREATE INDEX idx_bottlenecks_step_name ON process_analytics.bottlenecks(step_name);
CREATE INDEX idx_bottlenecks_type ON process_analytics.bottlenecks(bottleneck_type);
CREATE INDEX idx_bottlenecks_impact ON process_analytics.bottlenecks(impact_score);

COMMENT ON TABLE process_analytics.bottlenecks IS 'Identified bottlenecks causing process delays or inefficiencies';
COMMENT ON COLUMN process_analytics.bottlenecks.bottleneck_type IS 'Type: duration (slow step), waiting_time (idle), resource_contention (overloaded), error_rate (failures), throughput (capacity limit)';
COMMENT ON COLUMN process_analytics.bottlenecks.occurrence_count IS 'How many times this bottleneck was observed';
COMMENT ON COLUMN process_analytics.bottlenecks.suggested_improvements IS 'Array of improvement suggestions based on analysis';

-- 6. Performance Snapshots (Daily/Hourly Aggregates)
-- ============================================================================
CREATE TABLE IF NOT EXISTS process_analytics.performance_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_id VARCHAR(255) NOT NULL,
    snapshot_time TIMESTAMPTZ NOT NULL,
    time_period VARCHAR(20) NOT NULL CHECK (time_period IN ('hourly', 'daily', 'weekly', 'monthly')),
    total_executions INTEGER NOT NULL DEFAULT 0,
    completed_executions INTEGER NOT NULL DEFAULT 0,
    failed_executions INTEGER NOT NULL DEFAULT 0,
    cancelled_executions INTEGER NOT NULL DEFAULT 0,
    avg_duration_minutes FLOAT,
    median_duration_minutes FLOAT,
    p95_duration_minutes FLOAT,
    min_duration_minutes FLOAT,
    max_duration_minutes FLOAT,
    success_rate FLOAT,
    throughput FLOAT,
    metrics_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_snapshots_process_id ON process_analytics.performance_snapshots(process_id);
CREATE INDEX idx_snapshots_time ON process_analytics.performance_snapshots(snapshot_time);
CREATE INDEX idx_snapshots_period ON process_analytics.performance_snapshots(time_period);

COMMENT ON TABLE process_analytics.performance_snapshots IS 'Aggregated performance metrics over time periods for trend analysis';
COMMENT ON COLUMN process_analytics.performance_snapshots.success_rate IS 'Percentage of completed executions (0-100)';
COMMENT ON COLUMN process_analytics.performance_snapshots.throughput IS 'Executions per hour for this time period';

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View: Active Process Executions
-- ============================================================================
CREATE OR REPLACE VIEW process_analytics.active_executions AS
SELECT
    e.id,
    e.process_id,
    e.execution_id,
    e.start_time,
    e.status,
    e.executed_by,
    EXTRACT(EPOCH FROM (NOW() - e.start_time))/60 AS running_minutes,
    COUNT(ev.id) AS event_count,
    MAX(ev.timestamp) AS last_event_time
FROM process_analytics.executions e
LEFT JOIN process_analytics.events ev ON e.id = ev.execution_id
WHERE e.status = 'running'
GROUP BY e.id, e.process_id, e.execution_id, e.start_time, e.status, e.executed_by;

COMMENT ON VIEW process_analytics.active_executions IS 'Currently running process executions with activity metrics';

-- View: Recent Bottlenecks
-- ============================================================================
CREATE OR REPLACE VIEW process_analytics.recent_bottlenecks AS
SELECT
    b.process_id,
    b.step_name,
    b.bottleneck_type,
    b.avg_duration_minutes,
    b.occurrence_count,
    b.impact_score,
    b.suggested_improvements,
    b.detected_at,
    b.last_updated
FROM process_analytics.bottlenecks b
WHERE b.last_updated >= NOW() - INTERVAL '7 days'
ORDER BY b.impact_score DESC, b.occurrence_count DESC;

COMMENT ON VIEW process_analytics.recent_bottlenecks IS 'Bottlenecks detected in the last 7 days, ordered by impact';

-- View: Process Health Summary
-- ============================================================================
CREATE OR REPLACE VIEW process_analytics.process_health AS
SELECT
    e.process_id,
    COUNT(*) AS total_executions_30d,
    COUNT(*) FILTER (WHERE e.status = 'completed') AS completed,
    COUNT(*) FILTER (WHERE e.status = 'failed') AS failed,
    COUNT(*) FILTER (WHERE e.status = 'running') AS running,
    ROUND(AVG(e.duration_minutes), 2) AS avg_duration_minutes,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY e.duration_minutes), 2) AS median_duration_minutes,
    ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY e.duration_minutes), 2) AS p95_duration_minutes,
    ROUND(100.0 * COUNT(*) FILTER (WHERE e.status = 'completed') / NULLIF(COUNT(*), 0), 1) AS success_rate,
    COUNT(DISTINCT d.id) AS deviation_count,
    COUNT(DISTINCT b.id) AS bottleneck_count
FROM process_analytics.executions e
LEFT JOIN process_analytics.deviations d ON e.id = d.execution_id
LEFT JOIN process_analytics.bottlenecks b ON e.process_id = b.process_id
WHERE e.start_time >= NOW() - INTERVAL '30 days'
GROUP BY e.process_id;

COMMENT ON VIEW process_analytics.process_health IS 'Health metrics for all processes over last 30 days';

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger: Update execution duration on completion
-- ============================================================================
CREATE OR REPLACE FUNCTION process_analytics.update_execution_duration()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.end_time IS NOT NULL AND OLD.end_time IS NULL THEN
        NEW.duration_minutes := EXTRACT(EPOCH FROM (NEW.end_time - NEW.start_time)) / 60;
    END IF;
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_execution_duration
    BEFORE UPDATE ON process_analytics.executions
    FOR EACH ROW
    EXECUTE FUNCTION process_analytics.update_execution_duration();

COMMENT ON FUNCTION process_analytics.update_execution_duration IS 'Automatically calculate duration when execution completes';

-- Trigger: Update pattern last_seen_at
-- ============================================================================
CREATE OR REPLACE FUNCTION process_analytics.update_pattern_last_seen()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_seen_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_pattern_last_seen
    BEFORE UPDATE ON process_analytics.patterns
    FOR EACH ROW
    WHEN (NEW.frequency > OLD.frequency)
    EXECUTE FUNCTION process_analytics.update_pattern_last_seen();

COMMENT ON FUNCTION process_analytics.update_pattern_last_seen IS 'Update last_seen_at when pattern frequency increases';

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE process_analytics.executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE process_analytics.events ENABLE ROW LEVEL SECURITY;
ALTER TABLE process_analytics.patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE process_analytics.deviations ENABLE ROW LEVEL SECURITY;
ALTER TABLE process_analytics.bottlenecks ENABLE ROW LEVEL SECURITY;
ALTER TABLE process_analytics.performance_snapshots ENABLE ROW LEVEL SECURITY;

-- Policy: service_role has full access (for backend services)
-- ============================================================================
CREATE POLICY "service_role_all_access_executions" ON process_analytics.executions
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "service_role_all_access_events" ON process_analytics.events
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "service_role_all_access_patterns" ON process_analytics.patterns
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "service_role_all_access_deviations" ON process_analytics.deviations
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "service_role_all_access_bottlenecks" ON process_analytics.bottlenecks
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "service_role_all_access_snapshots" ON process_analytics.performance_snapshots
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Policy: authenticated users can read all analytics data
-- ============================================================================
CREATE POLICY "authenticated_read_executions" ON process_analytics.executions
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "authenticated_read_events" ON process_analytics.events
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "authenticated_read_patterns" ON process_analytics.patterns
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "authenticated_read_deviations" ON process_analytics.deviations
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "authenticated_read_bottlenecks" ON process_analytics.bottlenecks
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "authenticated_read_snapshots" ON process_analytics.performance_snapshots
    FOR SELECT TO authenticated USING (true);

-- Policy: authenticated users can insert execution data (for logging from frontend)
-- ============================================================================
CREATE POLICY "authenticated_insert_executions" ON process_analytics.executions
    FOR INSERT TO authenticated WITH CHECK (executed_by = auth.email());

CREATE POLICY "authenticated_insert_events" ON process_analytics.events
    FOR INSERT TO authenticated WITH CHECK (true);

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function: Get process performance summary
-- ============================================================================
CREATE OR REPLACE FUNCTION process_analytics.get_process_summary(
    p_process_id VARCHAR,
    p_days_back INTEGER DEFAULT 30
)
RETURNS TABLE (
    process_id VARCHAR,
    total_executions BIGINT,
    avg_duration_minutes NUMERIC,
    success_rate NUMERIC,
    bottleneck_count BIGINT,
    deviation_count BIGINT,
    most_common_pattern JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.process_id,
        COUNT(*) AS total_executions,
        ROUND(AVG(e.duration_minutes)::numeric, 2) AS avg_duration_minutes,
        ROUND((100.0 * COUNT(*) FILTER (WHERE e.status = 'completed') / NULLIF(COUNT(*), 0))::numeric, 1) AS success_rate,
        COUNT(DISTINCT b.id) AS bottleneck_count,
        COUNT(DISTINCT d.id) AS deviation_count,
        (SELECT jsonb_build_object(
            'name', p.pattern_name,
            'frequency', p.frequency,
            'confidence', p.confidence
        )
        FROM process_analytics.patterns p
        WHERE p.process_id = e.process_id
        ORDER BY p.frequency DESC
        LIMIT 1) AS most_common_pattern
    FROM process_analytics.executions e
    LEFT JOIN process_analytics.bottlenecks b ON e.process_id = b.process_id
    LEFT JOIN process_analytics.deviations d ON e.id = d.execution_id
    WHERE e.process_id = p_process_id
        AND e.start_time >= NOW() - (p_days_back || ' days')::INTERVAL
    GROUP BY e.process_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION process_analytics.get_process_summary IS 'Get comprehensive summary for a specific process';

-- ============================================================================
-- GRANTS
-- ============================================================================

-- Grant schema usage
GRANT USAGE ON SCHEMA process_analytics TO postgres, anon, authenticated, service_role;

-- Grant table permissions
GRANT SELECT ON ALL TABLES IN SCHEMA process_analytics TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA process_analytics TO service_role;

-- Grant sequence permissions
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA process_analytics TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA process_analytics TO service_role;

-- Grant function execution
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA process_analytics TO anon, authenticated, service_role;

-- ============================================================================
-- INITIAL DATA / SAMPLE
-- ============================================================================

-- Insert sample process definitions (for reference)
COMMENT ON SCHEMA process_analytics IS 'Process mining and analytics schema - tracks workflow executions, patterns, bottlenecks, and deviations for continuous process improvement';

-- ============================================================================
-- MIGRATION NOTES
-- ============================================================================
--
-- This schema replaces the previous public.* tables:
-- - public.process_executions    → process_analytics.executions
-- - public.process_events         → process_analytics.events
-- - public.discovered_patterns    → process_analytics.patterns
-- - public.process_deviations     → process_analytics.deviations
--
-- Migration steps:
-- 1. Create this schema (this file)
-- 2. Migrate data from public.* tables (if exist)
-- 3. Update application code to use process_analytics.* tables
-- 4. Drop old public.* tables
--
-- ============================================================================
