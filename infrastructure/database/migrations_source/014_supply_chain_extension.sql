-- =============================================================================
-- Migration 014: Supply Chain BCM Extension
-- =============================================================================
-- Adds supplier management and supply chain resilience tracking
-- Extends BIA module with critical supply chain dependencies
--
-- ISO 22301 Reference: Clause 8.2.2 (BIA) - Extended dependency management
-- Research: Organizations with ISO 22301 recover 20% faster from supply chain disruptions (EY)
--
-- Date: 2025-10-02
-- Dependencies: 005_bia_schema.sql
-- =============================================================================

BEGIN;

-- =============================================================================
-- Table 1: Suppliers
-- =============================================================================

CREATE TABLE IF NOT EXISTS bia.suppliers (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Multi-tenancy
    tenant_id VARCHAR(100) NOT NULL,
    organization_id UUID NOT NULL REFERENCES core.organizations(id) ON DELETE CASCADE,

    -- Basic Information
    supplier_code VARCHAR(50) NOT NULL,
    supplier_name VARCHAR(255) NOT NULL,
    supplier_type VARCHAR(50),  -- manufacturer, distributor, service_provider, logistics

    -- Contact Information
    primary_contact_name VARCHAR(255),
    primary_contact_email VARCHAR(255),
    primary_contact_phone VARCHAR(100),
    address TEXT,
    country VARCHAR(100),

    -- Criticality Assessment
    criticality_level VARCHAR(20) NOT NULL CHECK (criticality_level IN ('critical', 'high', 'medium', 'low')),
    single_point_of_failure BOOLEAN DEFAULT FALSE,  -- SPOF - highest risk indicator

    -- Services/Products (JSONB for flexibility)
    services_provided JSONB DEFAULT '[]'::jsonb,
    /* Structure:
    [
        {
            "service": "Cloud Infrastructure",
            "criticality": "critical",
            "volume": "100% capacity",
            "description": "..."
        }
    ]
    */

    products_supplied JSONB DEFAULT '[]'::jsonb,
    /* Structure:
    [
        {
            "product": "Medical Supplies",
            "criticality": "high",
            "lead_time_days": 30,
            "description": "..."
        }
    ]
    */

    -- BCM Assessment
    has_bcm_program BOOLEAN DEFAULT FALSE,
    has_iso22301_certification BOOLEAN DEFAULT FALSE,
    last_bcm_assessment_date DATE,
    bcm_assessment_score INTEGER CHECK (bcm_assessment_score BETWEEN 0 AND 100),
    bcm_assessment_notes TEXT,

    -- Alternative Suppliers (JSONB)
    alternative_suppliers JSONB DEFAULT '[]'::jsonb,
    /* Structure:
    [
        {
            "supplier_id": "uuid",
            "can_replace": ["service1", "service2"],
            "transition_time_days": 14,
            "capacity_percentage": 80,
            "notes": "..."
        }
    ]
    */

    -- Contractual Obligations
    contract_start_date DATE,
    contract_end_date DATE,
    contractual_rto INTEGER,           -- hours
    contractual_rpo INTEGER,           -- hours
    sla_availability_percentage DECIMAL(5,2),
    penalties_for_breach JSONB,

    -- Dependencies (links to BIA processes)
    dependent_process_ids UUID[],      -- array of bia.processes.id

    -- Risk Assessment
    geographic_risks JSONB DEFAULT '[]'::jsonb,
    /* Structure:
    [
        {
            "risk_type": "political_instability",
            "severity": "high",
            "description": "..."
        }
    ]
    */

    financial_stability VARCHAR(50) CHECK (financial_stability IN ('strong', 'adequate', 'weak', 'at_risk')),
    dependency_level VARCHAR(50) CHECK (dependency_level IN ('exclusive', 'primary', 'secondary', 'backup')),

    -- Performance Tracking
    reliability_score DECIMAL(5,2) CHECK (reliability_score BETWEEN 0 AND 100),
    on_time_delivery_rate DECIMAL(5,2),  -- percentage
    quality_score DECIMAL(5,2) CHECK (quality_score BETWEEN 0 AND 100),

    -- Status
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'at_risk', 'under_review')),

    -- Audit Trail
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL,
    created_by UUID REFERENCES core.users(id),

    -- Constraints
    CONSTRAINT uq_supplier_code_per_org UNIQUE (organization_id, supplier_code),
    CONSTRAINT chk_supplier_rto_rpo CHECK (
        contractual_rto IS NULL OR
        contractual_rpo IS NULL OR
        contractual_rto >= contractual_rpo
    )
);

-- Indexes for suppliers
CREATE INDEX idx_suppliers_tenant ON bia.suppliers(tenant_id);
CREATE INDEX idx_suppliers_org ON bia.suppliers(organization_id);
CREATE INDEX idx_suppliers_criticality ON bia.suppliers(criticality_level);
CREATE INDEX idx_suppliers_spof ON bia.suppliers(single_point_of_failure) WHERE single_point_of_failure = true;
CREATE INDEX idx_suppliers_status ON bia.suppliers(status);
CREATE INDEX idx_suppliers_code ON bia.suppliers(supplier_code);
CREATE INDEX idx_suppliers_country ON bia.suppliers(country);
CREATE INDEX idx_suppliers_bcm_cert ON bia.suppliers(has_iso22301_certification) WHERE has_iso22301_certification = true;
CREATE INDEX idx_suppliers_fin_stability ON bia.suppliers(financial_stability);
CREATE INDEX idx_suppliers_created_at ON bia.suppliers(created_at DESC);

-- Trigger for updated_at
CREATE TRIGGER set_suppliers_updated_at
    BEFORE UPDATE ON bia.suppliers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- Table 2: Supplier Disruptions
-- =============================================================================

CREATE TABLE IF NOT EXISTS bia.supplier_disruptions (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Multi-tenancy
    tenant_id VARCHAR(100) NOT NULL,
    organization_id UUID NOT NULL REFERENCES core.organizations(id) ON DELETE CASCADE,

    -- Foreign Key
    supplier_id UUID NOT NULL REFERENCES bia.suppliers(id) ON DELETE CASCADE,

    -- Disruption Details
    disruption_date TIMESTAMP NOT NULL,
    disruption_type VARCHAR(50) NOT NULL CHECK (disruption_type IN (
        'delivery_delay',
        'quality_issue',
        'outage',
        'bankruptcy',
        'force_majeure',
        'cyber_incident',
        'labor_strike',
        'regulatory_issue',
        'other'
    )),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('minor', 'moderate', 'major', 'critical')),

    -- Impact
    description TEXT NOT NULL,
    impact_description TEXT,
    affected_process_ids UUID[],      -- array of bia.processes.id
    affected_products_services JSONB DEFAULT '[]'::jsonb,

    -- Resolution
    resolution_date TIMESTAMP,
    resolution_description TEXT,
    resolution_time_hours INTEGER GENERATED ALWAYS AS (
        CASE
            WHEN resolution_date IS NOT NULL AND disruption_date IS NOT NULL
            THEN EXTRACT(EPOCH FROM (resolution_date - disruption_date)) / 3600
            ELSE NULL
        END
    ) STORED,

    -- Metrics
    downtime_hours INTEGER,
    financial_impact DECIMAL(15,2),
    customer_impact_count INTEGER,     -- number of customers affected

    -- Lessons Learned
    lessons_learned TEXT,
    corrective_actions JSONB DEFAULT '[]'::jsonb,
    /* Structure:
    [
        {
            "action": "Implement backup supplier",
            "responsible": "Procurement Manager",
            "due_date": "2024-12-31",
            "status": "in_progress",
            "completion_date": null
        }
    ]
    */

    preventive_actions JSONB DEFAULT '[]'::jsonb,

    -- Root Cause Analysis
    root_cause TEXT,
    contributing_factors JSONB DEFAULT '[]'::jsonb,

    -- Audit Trail
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL,
    created_by UUID REFERENCES core.users(id),

    -- Constraints
    CONSTRAINT chk_disruption_resolution_time CHECK (
        resolution_date IS NULL OR
        resolution_date >= disruption_date
    )
);

-- Indexes for supplier_disruptions
CREATE INDEX idx_supplier_disruptions_tenant ON bia.supplier_disruptions(tenant_id);
CREATE INDEX idx_supplier_disruptions_org ON bia.supplier_disruptions(organization_id);
CREATE INDEX idx_supplier_disruptions_supplier ON bia.supplier_disruptions(supplier_id);
CREATE INDEX idx_supplier_disruptions_date ON bia.supplier_disruptions(disruption_date DESC);
CREATE INDEX idx_supplier_disruptions_type ON bia.supplier_disruptions(disruption_type);
CREATE INDEX idx_supplier_disruptions_severity ON bia.supplier_disruptions(severity);
CREATE INDEX idx_supplier_disruptions_resolved ON bia.supplier_disruptions(resolution_date) WHERE resolution_date IS NOT NULL;
CREATE INDEX idx_supplier_disruptions_unresolved ON bia.supplier_disruptions(disruption_date DESC) WHERE resolution_date IS NULL;

-- Trigger for updated_at
CREATE TRIGGER set_supplier_disruptions_updated_at
    BEFORE UPDATE ON bia.supplier_disruptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- RLS Policies
-- =============================================================================

-- Enable RLS
ALTER TABLE bia.suppliers ENABLE ROW LEVEL SECURITY;
ALTER TABLE bia.supplier_disruptions ENABLE ROW LEVEL SECURITY;

-- Suppliers policies
CREATE POLICY suppliers_tenant_isolation
    ON bia.suppliers
    FOR ALL
    USING (
        tenant_id = current_setting('app.current_tenant_id', true)::text
        OR current_setting('app.is_platform_admin', true)::boolean = true
    );

CREATE POLICY suppliers_org_access
    ON bia.suppliers
    FOR SELECT
    USING (
        organization_id IN (
            SELECT organization_id
            FROM core.organization_users
            WHERE user_id = current_setting('app.current_user_id', true)::uuid
        )
    );

-- Supplier disruptions policies
CREATE POLICY supplier_disruptions_tenant_isolation
    ON bia.supplier_disruptions
    FOR ALL
    USING (
        tenant_id = current_setting('app.current_tenant_id', true)::text
        OR current_setting('app.is_platform_admin', true)::boolean = true
    );

CREATE POLICY supplier_disruptions_org_access
    ON bia.supplier_disruptions
    FOR SELECT
    USING (
        organization_id IN (
            SELECT organization_id
            FROM core.organization_users
            WHERE user_id = current_setting('app.current_user_id', true)::uuid
        )
    );

-- =============================================================================
-- Views for Analysis
-- =============================================================================

-- View 1: Critical Suppliers (SPOF Analysis)
CREATE OR REPLACE VIEW bia.v_critical_suppliers AS
SELECT
    s.id,
    s.tenant_id,
    s.organization_id,
    s.supplier_code,
    s.supplier_name,
    s.criticality_level,
    s.single_point_of_failure,
    s.has_iso22301_certification,
    s.bcm_assessment_score,
    s.financial_stability,
    s.reliability_score,

    -- Alternative suppliers count
    COALESCE(jsonb_array_length(s.alternative_suppliers), 0) as alternative_count,

    -- Dependent processes count
    COALESCE(array_length(s.dependent_process_ids, 1), 0) as dependent_process_count,

    -- Disruption statistics (last 12 months)
    COUNT(DISTINCT sd.id) as disruption_count_12m,
    COALESCE(AVG(sd.downtime_hours), 0) as avg_downtime_hours_12m,
    COALESCE(SUM(sd.financial_impact), 0) as total_financial_impact_12m,

    -- Status
    s.status,
    s.created_at,
    s.updated_at

FROM bia.suppliers s
LEFT JOIN bia.supplier_disruptions sd ON sd.supplier_id = s.id
    AND sd.disruption_date >= CURRENT_DATE - INTERVAL '12 months'
WHERE s.status = 'active'
GROUP BY
    s.id, s.tenant_id, s.organization_id, s.supplier_code, s.supplier_name,
    s.criticality_level, s.single_point_of_failure, s.has_iso22301_certification,
    s.bcm_assessment_score, s.financial_stability, s.reliability_score,
    s.alternative_suppliers, s.dependent_process_ids, s.status, s.created_at, s.updated_at;

-- View 2: Supplier Risk Scores
CREATE OR REPLACE VIEW bia.v_supplier_risk_scores AS
WITH disruption_stats AS (
    SELECT
        supplier_id,
        COUNT(*) as disruption_count_12m
    FROM bia.supplier_disruptions
    WHERE disruption_date >= CURRENT_DATE - INTERVAL '12 months'
    GROUP BY supplier_id
)
SELECT
    s.id as supplier_id,
    s.tenant_id,
    s.organization_id,
    s.supplier_name,
    s.supplier_code,

    -- Risk Factors (0-100 scale, higher = more risk)
    CASE s.criticality_level
        WHEN 'critical' THEN 100
        WHEN 'high' THEN 75
        WHEN 'medium' THEN 50
        ELSE 25
    END as criticality_risk,

    CASE WHEN s.single_point_of_failure THEN 100 ELSE 0 END as spof_risk,

    CASE s.financial_stability
        WHEN 'at_risk' THEN 100
        WHEN 'weak' THEN 75
        WHEN 'adequate' THEN 25
        WHEN 'strong' THEN 0
        ELSE 50
    END as financial_risk,

    CASE WHEN s.has_iso22301_certification THEN 0 ELSE 50 END as bcm_maturity_risk,

    CASE
        WHEN s.reliability_score IS NULL THEN 50
        ELSE (100 - s.reliability_score)
    END as reliability_risk,

    CASE
        WHEN jsonb_array_length(s.alternative_suppliers) = 0 THEN 100
        WHEN jsonb_array_length(s.alternative_suppliers) = 1 THEN 50
        WHEN jsonb_array_length(s.alternative_suppliers) >= 2 THEN 25
        ELSE 75
    END as alternative_availability_risk,

    LEAST(COALESCE(ds.disruption_count_12m, 0) * 20, 100) as disruption_frequency_risk,

    -- Overall Risk Score (weighted average)
    ROUND(
        (
            (CASE s.criticality_level WHEN 'critical' THEN 100 WHEN 'high' THEN 75 WHEN 'medium' THEN 50 ELSE 25 END * 0.25) +
            (CASE WHEN s.single_point_of_failure THEN 100 ELSE 0 END * 0.20) +
            (CASE s.financial_stability WHEN 'at_risk' THEN 100 WHEN 'weak' THEN 75 WHEN 'adequate' THEN 25 WHEN 'strong' THEN 0 ELSE 50 END * 0.15) +
            (CASE WHEN s.has_iso22301_certification THEN 0 ELSE 50 END * 0.10) +
            (CASE WHEN s.reliability_score IS NULL THEN 50 ELSE (100 - s.reliability_score) END * 0.15) +
            (CASE WHEN jsonb_array_length(s.alternative_suppliers) = 0 THEN 100
                  WHEN jsonb_array_length(s.alternative_suppliers) = 1 THEN 50
                  WHEN jsonb_array_length(s.alternative_suppliers) >= 2 THEN 25
                  ELSE 75 END * 0.10) +
            (LEAST(COALESCE(ds.disruption_count_12m, 0) * 20, 100) * 0.05)
        ), 2
    ) as overall_risk_score,

    -- Risk Level
    CASE
        WHEN ROUND((
            (CASE s.criticality_level WHEN 'critical' THEN 100 WHEN 'high' THEN 75 WHEN 'medium' THEN 50 ELSE 25 END * 0.25) +
            (CASE WHEN s.single_point_of_failure THEN 100 ELSE 0 END * 0.20) +
            (CASE s.financial_stability WHEN 'at_risk' THEN 100 WHEN 'weak' THEN 75 WHEN 'adequate' THEN 25 WHEN 'strong' THEN 0 ELSE 50 END * 0.15) +
            (CASE WHEN s.has_iso22301_certification THEN 0 ELSE 50 END * 0.10) +
            (CASE WHEN s.reliability_score IS NULL THEN 50 ELSE (100 - s.reliability_score) END * 0.15) +
            (CASE WHEN jsonb_array_length(s.alternative_suppliers) = 0 THEN 100
                  WHEN jsonb_array_length(s.alternative_suppliers) = 1 THEN 50
                  WHEN jsonb_array_length(s.alternative_suppliers) >= 2 THEN 25
                  ELSE 75 END * 0.10) +
            (LEAST(COALESCE(ds.disruption_count_12m, 0) * 20, 100) * 0.05)
        ), 2) >= 75 THEN 'critical'
        WHEN ROUND((
            (CASE s.criticality_level WHEN 'critical' THEN 100 WHEN 'high' THEN 75 WHEN 'medium' THEN 50 ELSE 25 END * 0.25) +
            (CASE WHEN s.single_point_of_failure THEN 100 ELSE 0 END * 0.20) +
            (CASE s.financial_stability WHEN 'at_risk' THEN 100 WHEN 'weak' THEN 75 WHEN 'adequate' THEN 25 WHEN 'strong' THEN 0 ELSE 50 END * 0.15) +
            (CASE WHEN s.has_iso22301_certification THEN 0 ELSE 50 END * 0.10) +
            (CASE WHEN s.reliability_score IS NULL THEN 50 ELSE (100 - s.reliability_score) END * 0.15) +
            (CASE WHEN jsonb_array_length(s.alternative_suppliers) = 0 THEN 100
                  WHEN jsonb_array_length(s.alternative_suppliers) = 1 THEN 50
                  WHEN jsonb_array_length(s.alternative_suppliers) >= 2 THEN 25
                  ELSE 75 END * 0.10) +
            (LEAST(COALESCE(ds.disruption_count_12m, 0) * 20, 100) * 0.05)
        ), 2) >= 50 THEN 'high'
        WHEN ROUND((
            (CASE s.criticality_level WHEN 'critical' THEN 100 WHEN 'high' THEN 75 WHEN 'medium' THEN 50 ELSE 25 END * 0.25) +
            (CASE WHEN s.single_point_of_failure THEN 100 ELSE 0 END * 0.20) +
            (CASE s.financial_stability WHEN 'at_risk' THEN 100 WHEN 'weak' THEN 75 WHEN 'adequate' THEN 25 WHEN 'strong' THEN 0 ELSE 50 END * 0.15) +
            (CASE WHEN s.has_iso22301_certification THEN 0 ELSE 50 END * 0.10) +
            (CASE WHEN s.reliability_score IS NULL THEN 50 ELSE (100 - s.reliability_score) END * 0.15) +
            (CASE WHEN jsonb_array_length(s.alternative_suppliers) = 0 THEN 100
                  WHEN jsonb_array_length(s.alternative_suppliers) = 1 THEN 50
                  WHEN jsonb_array_length(s.alternative_suppliers) >= 2 THEN 25
                  ELSE 75 END * 0.10) +
            (LEAST(COALESCE(ds.disruption_count_12m, 0) * 20, 100) * 0.05)
        ), 2) >= 25 THEN 'medium'
        ELSE 'low'
    END as risk_level

FROM bia.suppliers s
LEFT JOIN disruption_stats ds ON ds.supplier_id = s.id
WHERE s.status = 'active';

-- =============================================================================
-- Comments
-- =============================================================================

COMMENT ON TABLE bia.suppliers IS 'Supply chain supplier management for BCM resilience. Organizations with ISO 22301 recover 20% faster from supply chain disruptions (EY Research).';
COMMENT ON TABLE bia.supplier_disruptions IS 'Historical record of supplier disruptions for lessons learned and continuous improvement.';

COMMENT ON COLUMN bia.suppliers.single_point_of_failure IS 'Critical supplier with no viable alternatives - HIGHEST RISK indicator requiring immediate attention.';
COMMENT ON COLUMN bia.suppliers.bcm_assessment_score IS 'Supplier BCM maturity assessment score (0-100). Scores above 70 indicate good BCM practices.';
COMMENT ON COLUMN bia.suppliers.alternative_suppliers IS 'JSONB array of alternative suppliers that can replace this one, including transition time and capacity percentage.';
COMMENT ON COLUMN bia.suppliers.dependent_process_ids IS 'Array of BIA process UUIDs that depend on this supplier for critical operations.';

COMMENT ON VIEW bia.v_critical_suppliers IS 'Critical suppliers requiring immediate attention - focuses on SPOF, high criticality, and disruption history.';
COMMENT ON VIEW bia.v_supplier_risk_scores IS 'Comprehensive risk scoring for all suppliers based on 7 weighted factors: criticality, SPOF, financial stability, BCM maturity, reliability, alternatives, and disruption history.';

-- =============================================================================
-- Verification
-- =============================================================================

DO $$
DECLARE
    v_suppliers_count INTEGER;
    v_disruptions_count INTEGER;
    v_views_count INTEGER;
BEGIN
    -- Count tables
    SELECT COUNT(*) INTO v_suppliers_count
    FROM information_schema.tables
    WHERE table_schema = 'bia' AND table_name = 'suppliers';

    SELECT COUNT(*) INTO v_disruptions_count
    FROM information_schema.tables
    WHERE table_schema = 'bia' AND table_name = 'supplier_disruptions';

    -- Count views
    SELECT COUNT(*) INTO v_views_count
    FROM information_schema.views
    WHERE table_schema = 'bia' AND table_name IN ('v_critical_suppliers', 'v_supplier_risk_scores');

    -- Report
    RAISE NOTICE '=================================================================';
    RAISE NOTICE 'Migration 014: Supply Chain BCM Extension - COMPLETE';
    RAISE NOTICE '=================================================================';
    RAISE NOTICE 'Tables created:';
    RAISE NOTICE '  - bia.suppliers: %', CASE WHEN v_suppliers_count > 0 THEN '✓' ELSE '✗' END;
    RAISE NOTICE '  - bia.supplier_disruptions: %', CASE WHEN v_disruptions_count > 0 THEN '✓' ELSE '✗' END;
    RAISE NOTICE 'Views created: % of 2', v_views_count;
    RAISE NOTICE '';
    RAISE NOTICE 'Features:';
    RAISE NOTICE '  ✓ SPOF (Single Point of Failure) tracking';
    RAISE NOTICE '  ✓ BCM maturity assessment';
    RAISE NOTICE '  ✓ Disruption history and lessons learned';
    RAISE NOTICE '  ✓ Alternative supplier management';
    RAISE NOTICE '  ✓ Risk scoring (7 weighted factors)';
    RAISE NOTICE '  ✓ Performance tracking';
    RAISE NOTICE '  ✓ RLS multi-tenancy support';
    RAISE NOTICE '=================================================================';
END $$;

COMMIT;
