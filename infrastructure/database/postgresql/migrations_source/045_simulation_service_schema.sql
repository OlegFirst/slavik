-- Simulation Service Schema Migration
-- Version: 2.0.0
-- Date: 2025-10-14
-- Description: Create schema and tables for unified simulation service
-- Dependencies: 002_rls_functions.sql

BEGIN;

-- Create schema
CREATE SCHEMA IF NOT EXISTS simulation;

-- ===========================================================================
-- 1. SIMULATIONS TABLE
-- ===========================================================================
-- Main table for simulation configurations and lifecycle tracking

CREATE TABLE simulation.simulations (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    simulation_type VARCHAR(50) NOT NULL, -- what_if, monte_carlo, scenario, bia, jaamsim
    engine VARCHAR(50), -- internal, jaamsim, ciw, external
    parameters JSONB NOT NULL DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'draft', -- draft, ready, running, completed, failed, cancelled
    created_by VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    tags JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    CONSTRAINT valid_simulation_type CHECK (simulation_type IN ('what_if', 'monte_carlo', 'scenario', 'optimization', 'bia', 'jaamsim')),
    CONSTRAINT valid_status CHECK (status IN ('draft', 'ready', 'running', 'completed', 'failed', 'cancelled'))
);

-- Indexes for performance
CREATE INDEX idx_simulations_tenant ON simulation.simulations(tenant_id);
CREATE INDEX idx_simulations_type ON simulation.simulations(simulation_type);
CREATE INDEX idx_simulations_status ON simulation.simulations(status);
CREATE INDEX idx_simulations_created ON simulation.simulations(created_at);
CREATE INDEX idx_simulations_created_by ON simulation.simulations(created_by);

-- ===========================================================================
-- 2. SCENARIOS TABLE
-- ===========================================================================
-- BCM exercise scenarios with AI generation support

CREATE TABLE simulation.scenarios (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50), -- cyber, pandemic, disaster, supply_chain
    complexity INTEGER CHECK (complexity BETWEEN 1 AND 5),
    scenario_type VARCHAR(50), -- tabletop, functional, full_scale, hybrid
    content TEXT,
    timeline JSONB,
    injects JSONB,
    success_metrics JSONB,
    participant_roles JSONB,
    recommended_participants_count INTEGER,
    is_ai_generated BOOLEAN DEFAULT FALSE,
    ai_generation_params JSONB,
    ai_confidence_score FLOAT CHECK (ai_confidence_score BETWEEN 0 AND 1),
    tags JSONB DEFAULT '[]',
    industry VARCHAR(100),
    organization_size VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_scenarios_tenant ON simulation.scenarios(tenant_id);
CREATE INDEX idx_scenarios_category ON simulation.scenarios(category);
CREATE INDEX idx_scenarios_complexity ON simulation.scenarios(complexity);
CREATE INDEX idx_scenarios_ai_generated ON simulation.scenarios(is_ai_generated);
CREATE INDEX idx_scenarios_created ON simulation.scenarios(created_at);
CREATE INDEX idx_scenarios_industry ON simulation.scenarios(industry);

-- ===========================================================================
-- 3. EXECUTIONS TABLE
-- ===========================================================================
-- Simulation execution history and results

CREATE TABLE simulation.executions (
    id SERIAL PRIMARY KEY,
    simulation_id INTEGER NOT NULL REFERENCES simulation.simulations(id) ON DELETE CASCADE,
    execution_number INTEGER,
    run_id VARCHAR(100),
    parameters JSONB,
    status VARCHAR(50) NOT NULL, -- running, completed, failed, cancelled
    progress FLOAT DEFAULT 0.0,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_seconds FLOAT,
    results JSONB,
    metrics JSONB,
    error_message TEXT,
    error_details JSONB,
    executed_by VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT valid_execution_status CHECK (status IN ('running', 'completed', 'failed', 'cancelled')),
    CONSTRAINT valid_progress CHECK (progress BETWEEN 0 AND 100)
);

-- Indexes for performance
CREATE INDEX idx_executions_simulation ON simulation.executions(simulation_id);
CREATE INDEX idx_executions_status ON simulation.executions(status);
CREATE INDEX idx_executions_run_id ON simulation.executions(run_id);
CREATE INDEX idx_executions_started ON simulation.executions(started_at);
CREATE INDEX idx_executions_executed_by ON simulation.executions(executed_by);

-- ===========================================================================
-- 4. RESULTS TABLE
-- ===========================================================================
-- Time-series results for detailed tracking (optimized for TimescaleDB if available)

CREATE TABLE simulation.results (
    id SERIAL PRIMARY KEY,
    simulation_id INTEGER NOT NULL,
    execution_id INTEGER,
    result_type VARCHAR(50) NOT NULL, -- final, intermediate, metric, event, log
    metric_name VARCHAR(100),
    result_data JSONB NOT NULL,
    confidence_score FLOAT CHECK (confidence_score BETWEEN 0 AND 1),
    quality_score FLOAT CHECK (quality_score BETWEEN 0 AND 1),
    metadata JSONB DEFAULT '{}',
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance (optimized for time-series queries)
CREATE INDEX idx_results_simulation ON simulation.results(simulation_id);
CREATE INDEX idx_results_execution ON simulation.results(execution_id);
CREATE INDEX idx_results_type ON simulation.results(result_type);
CREATE INDEX idx_results_metric ON simulation.results(metric_name);
CREATE INDEX idx_results_recorded ON simulation.results(recorded_at DESC);
CREATE INDEX idx_results_simulation_recorded ON simulation.results(simulation_id, recorded_at DESC);

-- ===========================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ===========================================================================
-- Multi-tenancy isolation using tenant_id

-- Enable RLS
ALTER TABLE simulation.simulations ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulation.scenarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulation.executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulation.results ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their tenant's simulations
CREATE POLICY simulations_tenant_isolation ON simulation.simulations
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id', true));

-- Policy: Users can see their tenant's scenarios + public scenarios (tenant_id IS NULL)
CREATE POLICY scenarios_tenant_isolation ON simulation.scenarios
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id', true) OR tenant_id IS NULL);

-- Policy: Users can only see executions of their tenant's simulations
CREATE POLICY executions_tenant_isolation ON simulation.executions
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM simulation.simulations s
            WHERE s.id = simulation_id
            AND s.tenant_id = current_setting('app.current_tenant_id', true)
        )
    );

-- Policy: Users can only see results of their tenant's simulations
CREATE POLICY results_tenant_isolation ON simulation.results
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM simulation.simulations s
            WHERE s.id = simulation_id
            AND s.tenant_id = current_setting('app.current_tenant_id', true)
        )
    );

-- ===========================================================================
-- GRANTS
-- ===========================================================================
-- Grant permissions to authenticated users

GRANT USAGE ON SCHEMA simulation TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA simulation TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA simulation TO authenticated;

-- Grant public read access to scenarios (for scenario library)
GRANT SELECT ON simulation.scenarios TO anon;

-- ===========================================================================
-- TRIGGERS
-- ===========================================================================
-- Auto-update timestamps

CREATE OR REPLACE FUNCTION simulation.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_simulations_updated_at
    BEFORE UPDATE ON simulation.simulations
    FOR EACH ROW
    EXECUTE FUNCTION simulation.update_updated_at_column();

CREATE TRIGGER update_scenarios_updated_at
    BEFORE UPDATE ON simulation.scenarios
    FOR EACH ROW
    EXECUTE FUNCTION simulation.update_updated_at_column();

-- ===========================================================================
-- VIEWS
-- ===========================================================================
-- Convenient views for common queries

-- View: Active simulations with execution count
CREATE VIEW simulation.active_simulations AS
SELECT
    s.*,
    COUNT(e.id) as execution_count,
    MAX(e.started_at) as last_execution_at
FROM simulation.simulations s
LEFT JOIN simulation.executions e ON s.id = e.simulation_id
WHERE s.status IN ('draft', 'ready', 'running')
GROUP BY s.id;

-- View: Simulation statistics
CREATE VIEW simulation.simulation_stats AS
SELECT
    s.id,
    s.name,
    s.simulation_type,
    COUNT(e.id) as total_executions,
    COUNT(CASE WHEN e.status = 'completed' THEN 1 END) as successful_executions,
    COUNT(CASE WHEN e.status = 'failed' THEN 1 END) as failed_executions,
    AVG(e.duration_seconds) as avg_duration_seconds,
    MAX(e.completed_at) as last_completed_at
FROM simulation.simulations s
LEFT JOIN simulation.executions e ON s.id = e.simulation_id
GROUP BY s.id, s.name, s.simulation_type;

-- ===========================================================================
-- COMMENTS
-- ===========================================================================
-- Documentation for tables and columns

COMMENT ON SCHEMA simulation IS 'Simulation service schema for BCM exercises and analysis';
COMMENT ON TABLE simulation.simulations IS 'Main simulation configurations and lifecycle tracking';
COMMENT ON TABLE simulation.scenarios IS 'BCM exercise scenarios with AI generation support';
COMMENT ON TABLE simulation.executions IS 'Simulation execution history and results';
COMMENT ON TABLE simulation.results IS 'Time-series results for detailed tracking';

COMMIT;
