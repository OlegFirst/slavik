-- Migration 004: Add Simulation Schema
-- Adds simulation tables for What-If, Monte Carlo, and Scenario simulations

-- Create simulation schema
CREATE SCHEMA IF NOT EXISTS simulation;

-- =============================================================================
-- Simulations Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS simulation.simulations (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,

    -- Simulation configuration
    simulation_type VARCHAR(50) NOT NULL, -- what_if, monte_carlo, scenario, optimization
    engine VARCHAR(50), -- internal, jaamsim, external
    parameters JSONB NOT NULL DEFAULT '{}',

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, ready, running, completed, failed
    created_by VARCHAR(255),

    -- Metadata (renamed from metadata to sim_metadata to avoid SQLAlchemy reserved name)
    sim_metadata JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    -- Indexes
    CONSTRAINT chk_simulation_type CHECK (simulation_type IN ('what_if', 'monte_carlo', 'scenario', 'optimization')),
    CONSTRAINT chk_simulation_status CHECK (status IN ('draft', 'ready', 'running', 'completed', 'failed'))
);

CREATE INDEX idx_simulations_tenant ON simulation.simulations(tenant_id);
CREATE INDEX idx_simulations_type ON simulation.simulations(simulation_type);
CREATE INDEX idx_simulations_status ON simulation.simulations(status);
CREATE INDEX idx_simulations_created ON simulation.simulations(created_at DESC);

-- =============================================================================
-- Scenarios Table (BCM Exercise Scenarios)
-- =============================================================================
CREATE TABLE IF NOT EXISTS simulation.scenarios (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255),
    title VARCHAR(255) NOT NULL,

    -- Scenario metadata
    category VARCHAR(50), -- cyber, pandemic, disaster, etc.
    complexity INT CHECK (complexity BETWEEN 1 AND 5), -- 1-5
    scenario_type VARCHAR(50), -- tabletop, functional, full_scale

    -- Content
    content TEXT, -- Markdown description
    timeline JSONB, -- Hour-by-hour timeline
    injects JSONB, -- Exercise injects
    success_metrics JSONB,

    -- AI generation
    is_ai_generated BOOLEAN DEFAULT FALSE,
    ai_generation_params JSONB,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_scenarios_tenant ON simulation.scenarios(tenant_id);
CREATE INDEX idx_scenarios_category ON simulation.scenarios(category);
CREATE INDEX idx_scenarios_type ON simulation.scenarios(scenario_type);

-- =============================================================================
-- Simulation Executions Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS simulation.executions (
    id SERIAL PRIMARY KEY,
    simulation_id INT NOT NULL REFERENCES simulation.simulations(id) ON DELETE CASCADE,
    execution_number INT,

    -- Execution parameters (can override simulation params)
    parameters JSONB,

    -- Status
    status VARCHAR(50), -- running, completed, failed
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    -- Results
    results JSONB,
    error_message TEXT,

    CONSTRAINT chk_execution_status CHECK (status IN ('running', 'completed', 'failed'))
);

CREATE INDEX idx_executions_sim ON simulation.executions(simulation_id);
CREATE INDEX idx_executions_status ON simulation.executions(status);

-- =============================================================================
-- Simulation Results Table (Time-series data)
-- =============================================================================
CREATE TABLE IF NOT EXISTS simulation.results (
    id SERIAL PRIMARY KEY,
    simulation_id INT NOT NULL REFERENCES simulation.simulations(id) ON DELETE CASCADE,

    -- Result data
    result_type VARCHAR(50), -- final, intermediate, metric
    result_data JSONB NOT NULL,
    confidence_score FLOAT,

    -- Metadata (renamed from metadata to result_metadata)
    result_metadata JSONB DEFAULT '{}',

    -- Timestamp
    recorded_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_result_type CHECK (result_type IN ('final', 'intermediate', 'metric'))
);

CREATE INDEX idx_results_sim ON simulation.results(simulation_id);
CREATE INDEX idx_results_type ON simulation.results(result_type);
CREATE INDEX idx_results_recorded ON simulation.results(recorded_at DESC);

-- =============================================================================
-- Comments
-- =============================================================================
COMMENT ON SCHEMA simulation IS 'Simulation engine tables for BCM simulations';
COMMENT ON TABLE simulation.simulations IS 'Main simulation configurations';
COMMENT ON TABLE simulation.scenarios IS 'BCM exercise scenarios (tabletop, functional, etc.)';
COMMENT ON TABLE simulation.executions IS 'Individual execution runs of simulations';
COMMENT ON TABLE simulation.results IS 'Time-series results data from simulations';

-- =============================================================================
-- Grant permissions (adjust based on your user setup)
-- =============================================================================
-- GRANT USAGE ON SCHEMA simulation TO bcm_user;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA simulation TO bcm_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA simulation TO bcm_user;
