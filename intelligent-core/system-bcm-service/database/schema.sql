-- System BCM Service - Database Schema
-- PostgreSQL Schema for System BCM service
-- Version: 1.0.0
-- Date: 2025-10-09

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- BCM Cycles Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS system_bcm_cycles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cycle_id VARCHAR(255) UNIQUE NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds DECIMAL(10, 2),
    status VARCHAR(50) NOT NULL DEFAULT 'running',
    phases JSONB NOT NULL DEFAULT '[]',

    -- Results from each phase
    bia_results JSONB,
    risk_results JSONB,
    recovery_results JSONB,
    priority_results JSONB,
    learning_results JSONB,

    -- Metrics
    critical_processes_count INTEGER,
    risks_identified INTEGER,
    high_priority_risks INTEGER,
    recovery_procedures_loaded INTEGER,
    insights_generated INTEGER,
    improvements_applied INTEGER,

    -- Performance
    rto_compliance_rate DECIMAL(5, 2),
    learning_effectiveness DECIMAL(5, 2),

    -- Metadata
    platform_version VARCHAR(50),
    bcm_version VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Index for quick lookups
CREATE INDEX idx_cycles_started_at ON system_bcm_cycles(started_at DESC);
CREATE INDEX idx_cycles_status ON system_bcm_cycles(status);
CREATE INDEX idx_cycles_completed_at ON system_bcm_cycles(completed_at DESC) WHERE completed_at IS NOT NULL;

-- ============================================================================
-- Recovery Executions Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS system_bcm_recovery_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id VARCHAR(255) UNIQUE NOT NULL,

    -- Recovery details
    service VARCHAR(255) NOT NULL,
    incident_type VARCHAR(255) NOT NULL,
    procedure_name VARCHAR(255) NOT NULL,

    -- Execution
    triggered_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds DECIMAL(10, 2),

    -- Results
    status VARCHAR(50) NOT NULL DEFAULT 'triggered',
    success BOOLEAN,
    steps_executed INTEGER,
    steps_failed INTEGER,
    error_message TEXT,

    -- RTO Tracking
    expected_rto_seconds INTEGER,
    actual_rto_seconds DECIMAL(10, 2),
    rto_met BOOLEAN,

    -- Context
    event_data JSONB,
    recovery_logs JSONB,

    -- Metadata
    cycle_id UUID REFERENCES system_bcm_cycles(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_recovery_service ON system_bcm_recovery_executions(service);
CREATE INDEX idx_recovery_triggered_at ON system_bcm_recovery_executions(triggered_at DESC);
CREATE INDEX idx_recovery_status ON system_bcm_recovery_executions(status);
CREATE INDEX idx_recovery_success ON system_bcm_recovery_executions(success);

-- ============================================================================
-- Insights Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS system_bcm_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    insight_id VARCHAR(255) UNIQUE NOT NULL,

    -- Insight details
    insight_type VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,

    -- Confidence and priority
    confidence DECIMAL(5, 2) NOT NULL,
    priority VARCHAR(50) NOT NULL,

    -- Context
    source VARCHAR(255),
    related_service VARCHAR(255),
    pattern_data JSONB,

    -- Recommended action
    recommended_action TEXT,
    action_applied BOOLEAN DEFAULT FALSE,
    action_applied_at TIMESTAMP WITH TIME ZONE,
    action_result JSONB,

    -- Validation
    validated BOOLEAN DEFAULT FALSE,
    validated_at TIMESTAMP WITH TIME ZONE,
    validation_result TEXT,
    effectiveness DECIMAL(5, 2),

    -- Metadata
    cycle_id UUID REFERENCES system_bcm_cycles(id) ON DELETE SET NULL,
    generated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_insights_generated_at ON system_bcm_insights(generated_at DESC);
CREATE INDEX idx_insights_type ON system_bcm_insights(insight_type);
CREATE INDEX idx_insights_priority ON system_bcm_insights(priority);
CREATE INDEX idx_insights_action_applied ON system_bcm_insights(action_applied);

-- ============================================================================
-- Platform Health Metrics Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS system_bcm_platform_health (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Service identification
    service_name VARCHAR(255) NOT NULL,
    service_tier VARCHAR(50) NOT NULL,

    -- Health metrics
    health_status VARCHAR(50) NOT NULL,
    availability DECIMAL(5, 2),
    response_time_ms DECIMAL(10, 2),
    error_rate DECIMAL(5, 4),

    -- Resource usage
    cpu_percent DECIMAL(5, 2),
    memory_percent DECIMAL(5, 2),
    disk_usage_percent DECIMAL(5, 2),

    -- Dependencies
    dependencies_healthy INTEGER,
    dependencies_unhealthy INTEGER,

    -- Last check
    last_check_at TIMESTAMP WITH TIME ZONE NOT NULL,
    next_check_at TIMESTAMP WITH TIME ZONE,

    -- Issues
    issues_detected INTEGER DEFAULT 0,
    issue_details JSONB,

    -- Metadata
    cycle_id UUID REFERENCES system_bcm_cycles(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_health_service ON system_bcm_platform_health(service_name);
CREATE INDEX idx_health_last_check ON system_bcm_platform_health(last_check_at DESC);
CREATE INDEX idx_health_status ON system_bcm_platform_health(health_status);

-- ============================================================================
-- Patterns Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS system_bcm_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pattern_id VARCHAR(255) UNIQUE NOT NULL,

    -- Pattern details
    pattern_type VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Detection
    first_detected_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_detected_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    detection_count INTEGER DEFAULT 1,

    -- Pattern data
    frequency VARCHAR(50),
    conditions JSONB NOT NULL,
    observed_values JSONB,

    -- Impact
    services_affected TEXT[],
    severity VARCHAR(50),

    -- Learning
    confidence DECIMAL(5, 2) NOT NULL,
    validated BOOLEAN DEFAULT FALSE,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_patterns_type ON system_bcm_patterns(pattern_type);
CREATE INDEX idx_patterns_last_detected ON system_bcm_patterns(last_detected_at DESC);
CREATE INDEX idx_patterns_detection_count ON system_bcm_patterns(detection_count DESC);

-- ============================================================================
-- Improvements Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS system_bcm_improvements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    improvement_id VARCHAR(255) UNIQUE NOT NULL,

    -- Improvement details
    improvement_type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,

    -- Source
    source_insight_id UUID REFERENCES system_bcm_insights(id) ON DELETE SET NULL,
    source_pattern_id UUID REFERENCES system_bcm_patterns(id) ON DELETE SET NULL,

    -- Application
    applied BOOLEAN DEFAULT FALSE,
    applied_at TIMESTAMP WITH TIME ZONE,
    auto_applied BOOLEAN DEFAULT FALSE,

    -- Configuration changes
    config_changes JSONB,
    before_values JSONB,
    after_values JSONB,

    -- Results
    success BOOLEAN,
    result_data JSONB,
    rollback_available BOOLEAN DEFAULT TRUE,
    rollback_data JSONB,

    -- Validation
    validated BOOLEAN DEFAULT FALSE,
    validated_at TIMESTAMP WITH TIME ZONE,
    effectiveness DECIMAL(5, 2),
    kept BOOLEAN,

    -- Metadata
    cycle_id UUID REFERENCES system_bcm_cycles(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_improvements_applied ON system_bcm_improvements(applied);
CREATE INDEX idx_improvements_type ON system_bcm_improvements(improvement_type);
CREATE INDEX idx_improvements_applied_at ON system_bcm_improvements(applied_at DESC);

-- ============================================================================
-- Events Table (EventBus integration tracking)
-- ============================================================================
CREATE TABLE IF NOT EXISTS system_bcm_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Event details
    event_type VARCHAR(255) NOT NULL,
    event_source VARCHAR(255) NOT NULL,
    event_data JSONB NOT NULL,

    -- Processing
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP WITH TIME ZONE,
    processing_result JSONB,

    -- Actions taken
    actions_triggered TEXT[],
    recovery_triggered BOOLEAN DEFAULT FALSE,

    -- Metadata
    received_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_events_type ON system_bcm_events(event_type);
CREATE INDEX idx_events_received_at ON system_bcm_events(received_at DESC);
CREATE INDEX idx_events_processed ON system_bcm_events(processed);

-- ============================================================================
-- Views
-- ============================================================================

-- Recent cycles summary
CREATE OR REPLACE VIEW v_recent_cycles AS
SELECT
    cycle_id,
    started_at,
    completed_at,
    duration_seconds,
    status,
    array_length(phases::text[]::text[], 1) as phases_count,
    insights_generated,
    improvements_applied,
    rto_compliance_rate,
    learning_effectiveness
FROM system_bcm_cycles
ORDER BY started_at DESC
LIMIT 100;

-- Recovery performance summary
CREATE OR REPLACE VIEW v_recovery_performance AS
SELECT
    service,
    procedure_name,
    COUNT(*) as total_executions,
    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_executions,
    ROUND(AVG(duration_seconds), 2) as avg_duration_seconds,
    ROUND(AVG(CASE WHEN rto_met THEN 1.0 ELSE 0.0 END) * 100, 2) as rto_compliance_percent,
    MAX(triggered_at) as last_execution
FROM system_bcm_recovery_executions
WHERE completed_at IS NOT NULL
GROUP BY service, procedure_name
ORDER BY total_executions DESC;

-- Active insights
CREATE OR REPLACE VIEW v_active_insights AS
SELECT
    insight_type,
    category,
    priority,
    COUNT(*) as total_insights,
    SUM(CASE WHEN action_applied THEN 1 ELSE 0 END) as actions_applied,
    ROUND(AVG(confidence), 2) as avg_confidence,
    MAX(generated_at) as latest_insight
FROM system_bcm_insights
WHERE generated_at > NOW() - INTERVAL '7 days'
GROUP BY insight_type, category, priority
ORDER BY priority, total_insights DESC;

-- Platform health summary
CREATE OR REPLACE VIEW v_platform_health_summary AS
SELECT
    service_tier,
    COUNT(*) as total_services,
    SUM(CASE WHEN health_status = 'healthy' THEN 1 ELSE 0 END) as healthy_services,
    ROUND(AVG(availability), 2) as avg_availability,
    ROUND(AVG(response_time_ms), 2) as avg_response_time_ms,
    SUM(issues_detected) as total_issues
FROM system_bcm_platform_health
WHERE last_check_at > NOW() - INTERVAL '1 hour'
GROUP BY service_tier
ORDER BY service_tier;

-- ============================================================================
-- Functions
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_cycles_updated_at BEFORE UPDATE ON system_bcm_cycles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_recovery_updated_at BEFORE UPDATE ON system_bcm_recovery_executions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_insights_updated_at BEFORE UPDATE ON system_bcm_insights
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_health_updated_at BEFORE UPDATE ON system_bcm_platform_health
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patterns_updated_at BEFORE UPDATE ON system_bcm_patterns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_improvements_updated_at BEFORE UPDATE ON system_bcm_improvements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Initial Data / Seed
-- ============================================================================

-- Insert system metadata
INSERT INTO system_bcm_cycles (cycle_id, status, platform_version, bcm_version, started_at, completed_at)
VALUES ('initial_setup', 'completed', '2.0.0', '1.0.0', NOW(), NOW())
ON CONFLICT (cycle_id) DO NOTHING;

-- ============================================================================
-- Permissions (optional, adjust as needed)
-- ============================================================================

-- Grant permissions to application user
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO system_bcm_user;
-- GRANT SELECT ON ALL VIEWS IN SCHEMA public TO system_bcm_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO system_bcm_user;

-- ============================================================================
-- Comments
-- ============================================================================

COMMENT ON TABLE system_bcm_cycles IS 'BCM cycle executions with results from all phases';
COMMENT ON TABLE system_bcm_recovery_executions IS 'Recovery procedure executions with RTO tracking';
COMMENT ON TABLE system_bcm_insights IS 'Generated insights from practice learning';
COMMENT ON TABLE system_bcm_platform_health IS 'Platform services health metrics';
COMMENT ON TABLE system_bcm_patterns IS 'Detected behavioral patterns';
COMMENT ON TABLE system_bcm_improvements IS 'Applied improvements with effectiveness tracking';
COMMENT ON TABLE system_bcm_events IS 'EventBus events received and processed';

-- Schema creation complete
SELECT 'System BCM database schema created successfully!' as status;
