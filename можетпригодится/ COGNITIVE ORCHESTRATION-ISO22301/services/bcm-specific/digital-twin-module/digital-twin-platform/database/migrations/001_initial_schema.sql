-- Digital Twin Standalone - Initial Database Schema
-- Version: 1.0.0
-- Date: 2025-01-15

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ORGANIZATIONS table
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) CHECK (type IN ('non-profit', 'charity', 'foundation', 'association')),
    mission TEXT,
    description TEXT,
    size INTEGER,
    annual_budget DECIMAL(15, 2),
    website VARCHAR(255),
    contact_info JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    is_active BOOLEAN DEFAULT true
);

-- Indexes for organizations
CREATE INDEX idx_org_type ON organizations(type);
CREATE INDEX idx_org_active ON organizations(is_active);
CREATE INDEX idx_org_created ON organizations(created_at DESC);
CREATE INDEX idx_org_metadata ON organizations USING GIN(metadata);

-- DIGITAL_TWINS table
CREATE TABLE IF NOT EXISTS digital_twins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    twin_id VARCHAR(255) UNIQUE NOT NULL,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50) DEFAULT '1.0.0',
    configuration JSONB NOT NULL DEFAULT '{}',
    state JSONB DEFAULT '{}',
    health_score DECIMAL(3, 2) CHECK (health_score >= 0 AND health_score <= 1),
    efficiency_score DECIMAL(3, 2) CHECK (efficiency_score >= 0 AND efficiency_score <= 1),
    last_simulation_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    total_simulations INTEGER DEFAULT 0,
    total_predictions INTEGER DEFAULT 0,
    accuracy_rate DECIMAL(3, 2)
);

-- Indexes for digital_twins
CREATE INDEX idx_twin_org ON digital_twins(organization_id);
CREATE INDEX idx_twin_active ON digital_twins(is_active);
CREATE INDEX idx_twin_health ON digital_twins(health_score);
CREATE INDEX idx_twin_efficiency ON digital_twins(efficiency_score);

-- DEPARTMENTS table
CREATE TABLE IF NOT EXISTS departments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100),
    staff_count INTEGER DEFAULT 0,
    budget_allocation DECIMAL(15, 2),
    efficiency_score DECIMAL(3, 2),
    responsibilities TEXT[],
    kpis JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(organization_id, name)
);

-- Indexes for departments
CREATE INDEX idx_dept_org ON departments(organization_id);
CREATE INDEX idx_dept_type ON departments(type);

-- SIMULATIONS table
CREATE TABLE IF NOT EXISTS simulations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    simulation_id VARCHAR(255) UNIQUE NOT NULL,
    twin_id UUID REFERENCES digital_twins(id) ON DELETE CASCADE,
    scenario VARCHAR(100) NOT NULL,
    scenario_category VARCHAR(50),
    parameters JSONB NOT NULL DEFAULT '{}',
    initial_state JSONB,
    final_state JSONB,
    results JSONB,
    recommendations JSONB DEFAULT '[]',
    confidence_score DECIMAL(3, 2),
    status VARCHAR(50) DEFAULT 'pending',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled'))
);

-- Indexes for simulations
CREATE INDEX idx_sim_twin ON simulations(twin_id);
CREATE INDEX idx_sim_scenario ON simulations(scenario);
CREATE INDEX idx_sim_status ON simulations(status);
CREATE INDEX idx_sim_created ON simulations(created_at DESC);
CREATE INDEX idx_sim_category ON simulations(scenario_category);

-- METRICS table with partitioning support
CREATE TABLE IF NOT EXISTS metrics (
    id UUID DEFAULT gen_random_uuid(),
    twin_id UUID REFERENCES digital_twins(id) ON DELETE CASCADE,
    metric_type VARCHAR(100) NOT NULL,
    metric_category VARCHAR(50),
    value DECIMAL(15, 4) NOT NULL,
    unit VARCHAR(50),
    target_value DECIMAL(15, 4),
    threshold_min DECIMAL(15, 4),
    threshold_max DECIMAL(15, 4),
    is_critical BOOLEAN DEFAULT false,
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (id, timestamp)
) PARTITION BY RANGE (timestamp);

-- Create partitions for metrics (quarterly)
CREATE TABLE metrics_2025_q1 PARTITION OF metrics
    FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
CREATE TABLE metrics_2025_q2 PARTITION OF metrics
    FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');
CREATE TABLE metrics_2025_q3 PARTITION OF metrics
    FOR VALUES FROM ('2025-07-01') TO ('2025-10-01');
CREATE TABLE metrics_2025_q4 PARTITION OF metrics
    FOR VALUES FROM ('2025-10-01') TO ('2026-01-01');

-- Indexes for metrics
CREATE INDEX idx_metrics_twin ON metrics(twin_id);
CREATE INDEX idx_metrics_type ON metrics(metric_type);
CREATE INDEX idx_metrics_timestamp ON metrics(timestamp DESC);
CREATE INDEX idx_metrics_critical ON metrics(is_critical) WHERE is_critical = true;

-- PREDICTIONS table
CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    twin_id UUID REFERENCES digital_twins(id) ON DELETE CASCADE,
    prediction_type VARCHAR(100) NOT NULL,
    target_date DATE NOT NULL,
    predicted_value DECIMAL(15, 4),
    confidence_interval JSONB,
    confidence_score DECIMAL(3, 2),
    actual_value DECIMAL(15, 4),
    accuracy DECIMAL(3, 2),
    model_used VARCHAR(100),
    factors JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    validated_at TIMESTAMPTZ
);

-- Indexes for predictions
CREATE INDEX idx_pred_twin ON predictions(twin_id);
CREATE INDEX idx_pred_type ON predictions(prediction_type);
CREATE INDEX idx_pred_target ON predictions(target_date);
CREATE INDEX idx_pred_model ON predictions(model_used);

-- AUDIT_LOGS table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_id UUID REFERENCES auth.users(id),
    actor_email VARCHAR(255),
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    changes JSONB,
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255),
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for audit_logs
CREATE INDEX idx_audit_actor ON audit_logs(actor_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_created ON audit_logs(created_at DESC);

-- SESSIONS table
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    twin_id UUID REFERENCES digital_twins(id),
    data JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for sessions
CREATE INDEX idx_sessions_expires ON sessions(expires_at);
CREATE INDEX idx_sessions_user ON sessions(user_id);
CREATE INDEX idx_sessions_twin ON sessions(twin_id);

-- REPORTS table
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    twin_id UUID REFERENCES digital_twins(id) ON DELETE CASCADE,
    report_type VARCHAR(100) NOT NULL,
    title VARCHAR(255),
    content JSONB NOT NULL,
    format VARCHAR(20) DEFAULT 'json',
    file_url TEXT,
    generated_by UUID REFERENCES auth.users(id),
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    is_public BOOLEAN DEFAULT false
);

-- Indexes for reports
CREATE INDEX idx_reports_twin ON reports(twin_id);
CREATE INDEX idx_reports_type ON reports(report_type);
CREATE INDEX idx_reports_generated ON reports(generated_at DESC);

-- SCENARIOS table (library of simulation scenarios)
CREATE TABLE IF NOT EXISTS scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    description TEXT,
    parameters_schema JSONB NOT NULL,
    default_parameters JSONB,
    complexity VARCHAR(20) CHECK (complexity IN ('simple', 'moderate', 'complex')),
    estimated_duration_ms INTEGER,
    tags TEXT[],
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for scenarios
CREATE INDEX idx_scenarios_category ON scenarios(category);
CREATE INDEX idx_scenarios_active ON scenarios(is_active);
CREATE INDEX idx_scenarios_complexity ON scenarios(complexity);

-- AI_LEARNING_DATA table
CREATE TABLE IF NOT EXISTS ai_learning_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    twin_id UUID REFERENCES digital_twins(id) ON DELETE CASCADE,
    data_type VARCHAR(100) NOT NULL,
    input_data JSONB NOT NULL,
    output_data JSONB,
    model_version VARCHAR(50),
    accuracy_score DECIMAL(3, 2),
    feedback JSONB,
    processed_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for ai_learning_data
CREATE INDEX idx_ai_learning_twin ON ai_learning_data(twin_id);
CREATE INDEX idx_ai_learning_type ON ai_learning_data(data_type);
CREATE INDEX idx_ai_learning_processed ON ai_learning_data(processed_at DESC);

-- INTEGRATIONS table
CREATE TABLE IF NOT EXISTS integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    integration_type VARCHAR(100) NOT NULL,
    provider VARCHAR(100) NOT NULL,
    config JSONB DEFAULT '{}',
    credentials JSONB, -- encrypted
    status VARCHAR(50) DEFAULT 'inactive',
    last_sync_at TIMESTAMPTZ,
    sync_frequency_minutes INTEGER DEFAULT 60,
    error_count INTEGER DEFAULT 0,
    last_error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (status IN ('active', 'inactive', 'error', 'syncing'))
);

-- Indexes for integrations
CREATE INDEX idx_integrations_org ON integrations(organization_id);
CREATE INDEX idx_integrations_type ON integrations(integration_type);
CREATE INDEX idx_integrations_status ON integrations(status);

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update timestamp triggers
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_digital_twins_updated_at BEFORE UPDATE ON digital_twins
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_departments_updated_at BEFORE UPDATE ON departments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_scenarios_updated_at BEFORE UPDATE ON scenarios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_integrations_updated_at BEFORE UPDATE ON integrations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Function to calculate health score
CREATE OR REPLACE FUNCTION calculate_health_score(p_twin_id UUID)
RETURNS DECIMAL AS $$
DECLARE
    v_health_score DECIMAL;
BEGIN
    SELECT AVG(
        CASE 
            WHEN metric_type = 'efficiency' THEN value
            WHEN metric_type = 'financial_health' THEN value / 100
            WHEN metric_type = 'staff_satisfaction' THEN value / 10
            WHEN metric_type = 'grant_success_rate' THEN value
            ELSE 0.5
        END
    ) INTO v_health_score
    FROM metrics
    WHERE twin_id = p_twin_id
    AND timestamp > NOW() - INTERVAL '30 days';
    
    RETURN COALESCE(v_health_score, 0.5);
END;
$$ LANGUAGE plpgsql;

-- Function to get latest metrics
CREATE OR REPLACE FUNCTION get_latest_metrics(p_twin_id UUID, p_limit INTEGER DEFAULT 100)
RETURNS TABLE (
    metric_type VARCHAR,
    value DECIMAL,
    unit VARCHAR,
    timestamp TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT ON (m.metric_type) 
        m.metric_type,
        m.value,
        m.unit,
        m.timestamp
    FROM metrics m
    WHERE m.twin_id = p_twin_id
    ORDER BY m.metric_type, m.timestamp DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to archive old simulations
CREATE OR REPLACE FUNCTION archive_old_simulations()
RETURNS INTEGER AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    -- Move completed simulations older than 90 days to archive
    WITH archived AS (
        UPDATE simulations
        SET status = 'archived'
        WHERE status = 'completed'
        AND completed_at < NOW() - INTERVAL '90 days'
        RETURNING 1
    )
    SELECT COUNT(*) INTO archived_count FROM archived;
    
    RETURN archived_count;
END;
$$ LANGUAGE plpgsql;

-- Create views for common queries
CREATE OR REPLACE VIEW v_organization_summary AS
SELECT 
    o.id,
    o.organization_id,
    o.name,
    o.type,
    COUNT(DISTINCT dt.id) as twin_count,
    COUNT(DISTINCT d.id) as department_count,
    AVG(dt.health_score) as avg_health_score,
    AVG(dt.efficiency_score) as avg_efficiency_score,
    MAX(s.completed_at) as last_simulation_date
FROM organizations o
LEFT JOIN digital_twins dt ON o.id = dt.organization_id
LEFT JOIN departments d ON o.id = d.organization_id
LEFT JOIN simulations s ON dt.id = s.twin_id AND s.status = 'completed'
WHERE o.is_active = true
GROUP BY o.id, o.organization_id, o.name, o.type;

CREATE OR REPLACE VIEW v_simulation_performance AS
SELECT 
    s.scenario,
    s.scenario_category,
    COUNT(*) as run_count,
    AVG(s.duration_ms) as avg_duration_ms,
    AVG(s.confidence_score) as avg_confidence,
    COUNT(CASE WHEN s.status = 'completed' THEN 1 END) as success_count,
    COUNT(CASE WHEN s.status = 'failed' THEN 1 END) as failure_count
FROM simulations s
WHERE s.created_at > NOW() - INTERVAL '30 days'
GROUP BY s.scenario, s.scenario_category;

-- Grant permissions (adjust based on your needs)
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- Comments for documentation
COMMENT ON TABLE organizations IS 'Stores NPO organization profiles';
COMMENT ON TABLE digital_twins IS 'Digital twin instances for organizations';
COMMENT ON TABLE simulations IS 'Simulation runs and their results';
COMMENT ON TABLE metrics IS 'Time-series metrics data partitioned by quarter';
COMMENT ON TABLE predictions IS 'AI-generated predictions and forecasts';
COMMENT ON TABLE audit_logs IS 'Comprehensive audit trail for all operations';
COMMENT ON COLUMN digital_twins.health_score IS 'Overall health score from 0.0 to 1.0';
COMMENT ON COLUMN simulations.confidence_score IS 'AI confidence in simulation results from 0.0 to 1.0';