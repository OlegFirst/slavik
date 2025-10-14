-- ============================================
-- BCM Platform - Unified Database
-- Migration 005: Intelligence Schema
-- ============================================
-- Creates Intelligence tables: digital_twins, simulations, metrics
-- Schema: intelligence
-- ============================================

-- Table: intelligence.digital_twins
CREATE TABLE intelligence.digital_twins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Identity
    name VARCHAR(255) NOT NULL,
    twin_type VARCHAR(50),
    description TEXT,

    -- Scope
    scope_definition JSONB,

    -- State
    current_state JSONB DEFAULT '{}'::jsonb,
    confidence_level DECIMAL(5,2),

    -- Update frequency
    sync_frequency VARCHAR(50),
    last_synced_at TIMESTAMPTZ,

    -- Capabilities
    capabilities JSONB DEFAULT '[]'::jsonb,

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_twins_org ON intelligence.digital_twins(organization_id);

CREATE TRIGGER update_digital_twins_updated_at BEFORE UPDATE ON intelligence.digital_twins
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE intelligence.digital_twins ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Digital twins visible to org members" ON intelligence.digital_twins FOR SELECT
    USING (auth.is_org_member(organization_id));

CREATE POLICY "Digital twins manageable by org admins" ON intelligence.digital_twins FOR ALL
    USING (auth.is_org_admin(organization_id));

COMMENT ON TABLE intelligence.digital_twins IS 'Digital twin models for organizations, processes, and systems';

-- Table: intelligence.simulations
CREATE TABLE intelligence.simulations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    digital_twin_id UUID NOT NULL REFERENCES intelligence.digital_twins(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id),

    -- Simulation config
    simulation_name VARCHAR(255),
    scenario_type VARCHAR(50),

    -- Parameters
    input_parameters JSONB,
    assumptions JSONB,

    -- Execution
    status VARCHAR(50) DEFAULT 'pending',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    -- Results
    results JSONB,
    confidence_score DECIMAL(5,2),

    -- Analysis
    key_findings TEXT[],
    recommendations JSONB,

    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_simulations_twin ON intelligence.simulations(digital_twin_id);
CREATE INDEX idx_simulations_status ON intelligence.simulations(status);

ALTER TABLE intelligence.simulations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Simulations visible to org members" ON intelligence.simulations FOR SELECT
    USING (auth.is_org_member(organization_id));

COMMENT ON TABLE intelligence.simulations IS 'Simulation runs for scenario testing and prediction';

-- Table: intelligence.metrics (Partitioned by time)
CREATE TABLE intelligence.metrics (
    id UUID DEFAULT gen_random_uuid(),
    digital_twin_id UUID NOT NULL REFERENCES intelligence.digital_twins(id),
    organization_id UUID NOT NULL REFERENCES public.organizations(id),

    -- Metric info
    metric_name VARCHAR(255) NOT NULL,
    metric_type VARCHAR(50),

    -- Value
    value DECIMAL(15,4),
    unit VARCHAR(50),

    -- Context
    dimensions JSONB DEFAULT '{}'::jsonb,

    -- Timestamp
    recorded_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    PRIMARY KEY (id, recorded_at)
) PARTITION BY RANGE (recorded_at);

-- Create initial partitions (2025 Q1-Q4)
CREATE TABLE intelligence.metrics_2025_q1 PARTITION OF intelligence.metrics
    FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');

CREATE TABLE intelligence.metrics_2025_q2 PARTITION OF intelligence.metrics
    FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');

CREATE TABLE intelligence.metrics_2025_q3 PARTITION OF intelligence.metrics
    FOR VALUES FROM ('2025-07-01') TO ('2025-10-01');

CREATE TABLE intelligence.metrics_2025_q4 PARTITION OF intelligence.metrics
    FOR VALUES FROM ('2025-10-01') TO ('2026-01-01');

CREATE INDEX idx_metrics_twin_time ON intelligence.metrics(digital_twin_id, recorded_at DESC);
CREATE INDEX idx_metrics_name ON intelligence.metrics(metric_name, recorded_at DESC);

ALTER TABLE intelligence.metrics ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Metrics visible to org members" ON intelligence.metrics FOR SELECT
    USING (auth.is_org_member(organization_id));

COMMENT ON TABLE intelligence.metrics IS 'Time-series metrics data (partitioned by quarter)';

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 005 completed: Intelligence schema created (3 tables + 4 partitions)';
END
$$;
