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
-- =====================================================
-- Migration 015: Compliance - Improvement Initiatives
-- =====================================================
-- Purpose: Integrate Compliance Improvement Initiatives from Stage 2
-- Based on: /BCM/compliance/migrations/002_add_improvement_initiatives.sql
-- Date: 2025-10-02
-- ISO 22301:2019 Clause 10.2 (Continual Improvement)
-- =====================================================

-- =====================================================
-- TABLE: compliance.improvement_initiatives
-- =====================================================

CREATE TABLE IF NOT EXISTS compliance.improvement_initiatives (
    -- Primary Key (UUID)
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Multi-tenancy
    tenant_id VARCHAR(100) NOT NULL,
    organization_id UUID NOT NULL REFERENCES core.organizations(id) ON DELETE CASCADE,

    -- Identification
    initiative_code VARCHAR(50) NOT NULL,  -- IMP-2024-001 (unique per organization)
    title VARCHAR(500) NOT NULL,

    -- Classification
    initiative_type VARCHAR(50) NOT NULL CHECK (initiative_type IN (
        'process_optimization',
        'technology_upgrade',
        'training',
        'documentation',
        'risk_mitigation',
        'compliance',
        'performance',
        'other'
    )),

    source VARCHAR(50) NOT NULL CHECK (source IN (
        'audit_finding',
        'management_review',
        'exercise_lesson',
        'incident_lesson',
        'risk_assessment',
        'stakeholder_feedback',
        'internal_suggestion',
        'regulatory_change'
    )),

    source_reference VARCHAR(255),  -- Reference to audit finding, exercise, etc.

    -- Description
    description TEXT NOT NULL,
    current_state TEXT,
    desired_state TEXT,
    gap_analysis TEXT,

    -- Benefits & ROI
    expected_benefits JSONB DEFAULT '[]'::jsonb,  -- [{benefit: "...", metric: "...", target: "..."}]
    cost_estimate DECIMAL(15,2),
    roi DECIMAL(10,2),  -- ROI percentage
    benefits_realized JSONB DEFAULT '[]'::jsonb,  -- [{benefit: "...", actual: "...", date: "..."}]
    actual_cost DECIMAL(15,2),

    -- Priority & Impact
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    impact_level VARCHAR(20) CHECK (impact_level IN ('low', 'medium', 'high')),
    urgency VARCHAR(20) CHECK (urgency IN ('low', 'medium', 'high')),

    -- Ownership & Accountability
    owner VARCHAR(255) NOT NULL,
    sponsor VARCHAR(255),
    assigned_team JSONB DEFAULT '[]'::jsonb,  -- [{"name": "...", "role": "..."}]

    -- Planning
    planned_start_date DATE,
    planned_end_date DATE,
    estimated_effort_hours INTEGER,

    -- Execution
    actual_start_date DATE,
    actual_end_date DATE,
    actual_effort_hours INTEGER,

    -- Status & Progress
    status VARCHAR(50) DEFAULT 'identified' CHECK (status IN (
        'identified',
        'approved',
        'planned',
        'in_progress',
        'on_hold',
        'completed',
        'verified',
        'closed',
        'cancelled'
    )),

    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    milestones JSONB DEFAULT '[]'::jsonb,  -- [{name: "...", date: "...", status: "..."}]

    -- Implementation Details
    implementation_plan TEXT,
    resources_required JSONB DEFAULT '{}'::jsonb,
    dependencies JSONB DEFAULT '[]'::jsonb,
    risks JSONB DEFAULT '[]'::jsonb,

    -- Verification & Effectiveness
    verification_method VARCHAR(255),
    verification_criteria TEXT,
    verification_date DATE,
    verified_by VARCHAR(255),
    verification_status VARCHAR(20) CHECK (verification_status IN ('pending', 'passed', 'failed', 'partial')),
    verification_notes TEXT,

    effectiveness_criteria TEXT,
    effectiveness_review_date DATE,
    effectiveness_rating INTEGER CHECK (effectiveness_rating BETWEEN 1 AND 5),
    effectiveness_notes TEXT,

    -- Approval Workflow
    approval_status VARCHAR(20) DEFAULT 'pending' CHECK (approval_status IN ('pending', 'approved', 'rejected')),
    approved_by VARCHAR(255),
    approved_at TIMESTAMP WITH TIME ZONE,
    approval_notes TEXT,

    -- Change Management
    change_impact_assessment TEXT,
    communication_plan TEXT,
    training_required BOOLEAN DEFAULT false,
    training_completed BOOLEAN DEFAULT false,

    -- Integration with other modules (UUID arrays for relationships)
    related_risks UUID[],
    related_findings UUID[],
    related_incidents UUID[],
    related_exercises UUID[],

    -- Document Management
    attachments JSONB DEFAULT '[]'::jsonb,
    related_documents JSONB DEFAULT '[]'::jsonb,

    -- Audit Trail
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,  -- User ID
    updated_by UUID,  -- User ID

    -- Additional Notes
    notes TEXT,
    lessons_learned TEXT,
    closure_notes TEXT,

    -- Constraints
    CONSTRAINT uq_improvement_code_per_org UNIQUE (organization_id, initiative_code)
);

-- =====================================================
-- INDEXES
-- =====================================================

-- Primary lookups
CREATE INDEX idx_improvements_tenant ON compliance.improvement_initiatives(tenant_id);
CREATE INDEX idx_improvements_organization ON compliance.improvement_initiatives(organization_id);
CREATE INDEX idx_improvements_code ON compliance.improvement_initiatives(initiative_code);

-- Filtering & search
CREATE INDEX idx_improvements_type ON compliance.improvement_initiatives(initiative_type);
CREATE INDEX idx_improvements_source ON compliance.improvement_initiatives(source);
CREATE INDEX idx_improvements_status ON compliance.improvement_initiatives(status);
CREATE INDEX idx_improvements_priority ON compliance.improvement_initiatives(priority);
CREATE INDEX idx_improvements_owner ON compliance.improvement_initiatives(owner);

-- Date-based queries
CREATE INDEX idx_improvements_planned_end ON compliance.improvement_initiatives(planned_end_date);
CREATE INDEX idx_improvements_created ON compliance.improvement_initiatives(created_at);

-- Verification & effectiveness
CREATE INDEX idx_improvements_verification ON compliance.improvement_initiatives(verification_status);
CREATE INDEX idx_improvements_effectiveness ON compliance.improvement_initiatives(effectiveness_rating);

-- Composite indexes for common queries
CREATE INDEX idx_improvements_tenant_status ON compliance.improvement_initiatives(tenant_id, status);
CREATE INDEX idx_improvements_tenant_priority ON compliance.improvement_initiatives(tenant_id, priority);
CREATE INDEX idx_improvements_org_status ON compliance.improvement_initiatives(organization_id, status);

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================================

ALTER TABLE compliance.improvement_initiatives ENABLE ROW LEVEL SECURITY;

-- Policy: Tenant isolation
CREATE POLICY improvement_initiatives_tenant_isolation
ON compliance.improvement_initiatives
USING (
    tenant_id = current_setting('app.current_tenant_id', true)::text
);

-- Policy: Organization-level access
CREATE POLICY improvement_initiatives_org_access
ON compliance.improvement_initiatives
USING (
    organization_id IN (
        SELECT id FROM core.organizations
        WHERE tenant_id = current_setting('app.current_tenant_id', true)::text
    )
);

-- Policy: Platform admin full access
CREATE POLICY improvement_initiatives_platform_admin
ON compliance.improvement_initiatives
USING (
    current_setting('app.is_platform_admin', true)::boolean = true
);

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger: Auto-update updated_at timestamp
CREATE TRIGGER update_improvements_updated_at
BEFORE UPDATE ON compliance.improvement_initiatives
FOR EACH ROW
EXECUTE FUNCTION core.update_updated_at_column();

-- Trigger: Auto-generate initiative_code if not provided
CREATE OR REPLACE FUNCTION compliance.generate_improvement_code()
RETURNS TRIGGER AS $$
DECLARE
    next_num INTEGER;
    new_code VARCHAR(50);
    current_year INTEGER;
BEGIN
    IF NEW.initiative_code IS NULL OR NEW.initiative_code = '' THEN
        current_year := EXTRACT(YEAR FROM CURRENT_DATE);

        -- Get next sequential number for this organization and year
        SELECT COALESCE(
            MAX(
                CAST(
                    SPLIT_PART(initiative_code, '-', 3) AS INTEGER
                )
            ), 0
        ) + 1
        INTO next_num
        FROM compliance.improvement_initiatives
        WHERE organization_id = NEW.organization_id
          AND initiative_code LIKE 'IMP-' || current_year || '-%';

        -- Generate code: IMP-2024-001
        new_code := 'IMP-' || current_year || '-' || LPAD(next_num::TEXT, 3, '0');
        NEW.initiative_code := new_code;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER generate_improvement_code_trigger
BEFORE INSERT ON compliance.improvement_initiatives
FOR EACH ROW
EXECUTE FUNCTION compliance.generate_improvement_code();

-- =====================================================
-- ANALYTICAL VIEWS
-- =====================================================

-- View: Active improvement initiatives summary
CREATE OR REPLACE VIEW compliance.v_active_improvements AS
SELECT
    i.id,
    i.organization_id,
    i.tenant_id,
    i.initiative_code,
    i.title,
    i.initiative_type,
    i.source,
    i.status,
    i.priority,
    i.progress_percentage,
    i.owner,
    i.planned_start_date,
    i.planned_end_date,
    i.actual_start_date,
    i.actual_end_date,

    -- Calculated fields
    CASE
        WHEN i.actual_end_date IS NOT NULL THEN
            i.actual_end_date - i.actual_start_date
        WHEN i.actual_start_date IS NOT NULL THEN
            CURRENT_DATE - i.actual_start_date
        ELSE NULL
    END AS days_in_progress,

    CASE
        WHEN i.planned_end_date < CURRENT_DATE AND i.status NOT IN ('completed', 'verified', 'closed', 'cancelled')
        THEN true
        ELSE false
    END AS is_overdue,

    i.verification_status,
    i.effectiveness_rating,
    i.created_at
FROM compliance.improvement_initiatives i
WHERE i.status NOT IN ('cancelled', 'closed');

-- View: Improvement initiatives by source
CREATE OR REPLACE VIEW compliance.v_improvements_by_source AS
SELECT
    organization_id,
    tenant_id,
    source,
    COUNT(*) AS total_initiatives,
    COUNT(*) FILTER (WHERE status = 'completed') AS completed_count,
    COUNT(*) FILTER (WHERE status IN ('in_progress', 'planned')) AS active_count,
    COUNT(*) FILTER (WHERE verification_status = 'passed') AS verified_count,
    AVG(effectiveness_rating) AS avg_effectiveness,
    SUM(cost_estimate) AS total_estimated_cost,
    SUM(actual_cost) AS total_actual_cost
FROM compliance.improvement_initiatives
GROUP BY organization_id, tenant_id, source
ORDER BY total_initiatives DESC;

-- View: Improvement initiatives requiring attention
CREATE OR REPLACE VIEW compliance.v_improvements_requiring_attention AS
SELECT
    i.id,
    i.organization_id,
    i.tenant_id,
    i.initiative_code,
    i.title,
    i.priority,
    i.status,
    i.progress_percentage,
    i.planned_end_date,
    i.owner,

    -- Attention reasons
    CASE
        WHEN i.planned_end_date < CURRENT_DATE AND i.status NOT IN ('completed', 'verified', 'closed', 'cancelled')
        THEN 'Overdue'
        WHEN i.verification_status = 'failed'
        THEN 'Verification failed'
        WHEN i.status = 'on_hold' AND (CURRENT_DATE - i.updated_at::date) > 30
        THEN 'On hold for 30+ days'
        WHEN i.priority = 'critical' AND i.status = 'identified'
        THEN 'Critical priority not started'
        WHEN i.effectiveness_rating < 3 AND i.status = 'verified'
        THEN 'Low effectiveness rating'
        ELSE 'Other'
    END AS attention_reason
FROM compliance.improvement_initiatives i
WHERE
    (i.planned_end_date < CURRENT_DATE AND i.status NOT IN ('completed', 'verified', 'closed', 'cancelled'))
    OR i.verification_status = 'failed'
    OR (i.status = 'on_hold' AND (CURRENT_DATE - i.updated_at::date) > 30)
    OR (i.priority = 'critical' AND i.status = 'identified')
    OR (i.effectiveness_rating < 3 AND i.status = 'verified');

-- =====================================================
-- COMMENTS (Documentation)
-- =====================================================

COMMENT ON TABLE compliance.improvement_initiatives IS 'ISO 22301 Clause 10.2 - Continual improvement initiatives tracking';
COMMENT ON COLUMN compliance.improvement_initiatives.initiative_code IS 'Unique code per organization (IMP-2024-001)';
COMMENT ON COLUMN compliance.improvement_initiatives.source IS 'Origin of improvement initiative (audit, review, incident, etc.)';
COMMENT ON COLUMN compliance.improvement_initiatives.verification_status IS 'Verification outcome after implementation';
COMMENT ON COLUMN compliance.improvement_initiatives.effectiveness_rating IS 'Rating 1-5 of actual effectiveness after implementation';
COMMENT ON COLUMN compliance.improvement_initiatives.roi IS 'Return on Investment percentage';

-- =====================================================
-- VERIFICATION
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Migration 015: Compliance Improvement Initiatives - COMPLETE';
    RAISE NOTICE 'Tables created: 1';
    RAISE NOTICE 'Views created: 3';
    RAISE NOTICE 'Indexes created: 15';
    RAISE NOTICE 'RLS policies: 3';
    RAISE NOTICE 'Triggers: 2';
END $$;
-- =====================================================
-- Migration 016: Governance - Context Analysis & Stakeholder Management
-- =====================================================
-- Purpose: Integrate Context Analysis & Stakeholder Management from Stage 2
-- Based on: /BCM/governance/database/migrations/003_add_context_stakeholders.sql
-- Date: 2025-10-02
-- ISO 22301:2019 Clauses 4.1 (Understanding organization and context) & 4.2 (Stakeholder needs)
-- =====================================================

-- =====================================================
-- TABLE 1: governance.stakeholders
-- =====================================================

CREATE TABLE IF NOT EXISTS governance.stakeholders (
    -- Primary Key (UUID)
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Multi-tenancy
    tenant_id VARCHAR(100) NOT NULL,
    organization_id UUID NOT NULL REFERENCES core.organizations(id) ON DELETE CASCADE,

    -- Identification
    stakeholder_name VARCHAR(255) NOT NULL,
    stakeholder_type VARCHAR(50) NOT NULL CHECK (stakeholder_type IN ('internal', 'external', 'regulatory')),
    category VARCHAR(100),

    -- Power/Interest Matrix (Mendelow Matrix)
    influence_level VARCHAR(20) NOT NULL CHECK (influence_level IN ('low', 'medium', 'high')),
    interest_level VARCHAR(20) NOT NULL CHECK (interest_level IN ('low', 'medium', 'high')),

    -- Requirements & Expectations
    requirements JSONB DEFAULT '[]'::jsonb,
    expectations JSONB DEFAULT '[]'::jsonb,
    needs_assessment JSONB DEFAULT '{}'::jsonb,

    -- Contact Information
    contact_person VARCHAR(255),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    department VARCHAR(255),

    -- Engagement Strategy
    engagement_strategy TEXT,
    communication_plan JSONB DEFAULT '{}'::jsonb,
    engagement_frequency VARCHAR(50),

    -- Status & Tracking
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'archived')),
    priority_score INTEGER DEFAULT 0,
    satisfaction_score INTEGER CHECK (satisfaction_score BETWEEN 1 AND 5),

    -- Integration (UUID arrays for relationships)
    related_risks UUID[],
    related_objectives UUID[],

    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,  -- User ID
    updated_by UUID,  -- User ID
    notes TEXT
);

-- =====================================================
-- TABLE 2: governance.context_analysis
-- =====================================================

CREATE TABLE IF NOT EXISTS governance.context_analysis (
    -- Primary Key (UUID)
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Multi-tenancy
    tenant_id VARCHAR(100) NOT NULL,
    organization_id UUID NOT NULL REFERENCES core.organizations(id) ON DELETE CASCADE,

    -- Analysis Type & Identification
    analysis_type VARCHAR(50) NOT NULL CHECK (analysis_type IN ('PESTLE', 'SWOT', 'PORTER', 'VUCA', 'OTHER')),
    analysis_name VARCHAR(255) NOT NULL,

    -- Analysis Data (JSONB for flexibility)
    analysis_data JSONB NOT NULL,
    /*
    Example for PESTLE:
    {
        "political": ["Factor 1", "Factor 2"],
        "economic": ["Factor 1"],
        "social": ["Factor 1"],
        "technological": ["Factor 1"],
        "legal": ["Factor 1"],
        "environmental": ["Factor 1"]
    }

    Example for SWOT:
    {
        "strengths": ["Strength 1", "Strength 2"],
        "weaknesses": ["Weakness 1"],
        "opportunities": ["Opportunity 1"],
        "threats": ["Threat 1"]
    }
    */

    -- Outputs
    insights JSONB DEFAULT '[]'::jsonb,
    action_items JSONB DEFAULT '[]'::jsonb,
    opportunities JSONB DEFAULT '[]'::jsonb,
    threats JSONB DEFAULT '[]'::jsonb,

    -- Scoring & Priority
    overall_score DECIMAL(10,2),
    priority_level VARCHAR(20) CHECK (priority_level IN ('low', 'medium', 'high', 'critical')),

    -- Review & Approval
    review_status VARCHAR(20) DEFAULT 'draft' CHECK (review_status IN ('draft', 'in_review', 'approved', 'archived')),
    reviewed_by VARCHAR(255),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    approval_status VARCHAR(20) CHECK (approval_status IN ('pending', 'approved', 'rejected')),
    approved_by VARCHAR(255),
    approved_at TIMESTAMP WITH TIME ZONE,

    -- Validity & Scheduling
    validity_period_months INTEGER DEFAULT 12,
    next_review_date DATE,

    -- Integration (UUID arrays for relationships)
    related_risks UUID[],
    related_objectives UUID[],

    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,  -- User ID
    updated_by UUID,  -- User ID
    notes TEXT
);

-- =====================================================
-- INDEXES - Stakeholders
-- =====================================================

-- Primary lookups
CREATE INDEX idx_stakeholders_tenant ON governance.stakeholders(tenant_id);
CREATE INDEX idx_stakeholders_organization ON governance.stakeholders(organization_id);

-- Filtering & search
CREATE INDEX idx_stakeholders_type ON governance.stakeholders(stakeholder_type);
CREATE INDEX idx_stakeholders_status ON governance.stakeholders(status);
CREATE INDEX idx_stakeholders_created ON governance.stakeholders(created_at);

-- Power/Interest Matrix queries
CREATE INDEX idx_stakeholders_influence ON governance.stakeholders(influence_level);
CREATE INDEX idx_stakeholders_interest ON governance.stakeholders(interest_level);
CREATE INDEX idx_stakeholders_influence_interest ON governance.stakeholders(influence_level, interest_level);

-- Composite indexes
CREATE INDEX idx_stakeholders_org_status ON governance.stakeholders(organization_id, status);
CREATE INDEX idx_stakeholders_tenant_type ON governance.stakeholders(tenant_id, stakeholder_type);

-- =====================================================
-- INDEXES - Context Analysis
-- =====================================================

-- Primary lookups
CREATE INDEX idx_context_tenant ON governance.context_analysis(tenant_id);
CREATE INDEX idx_context_organization ON governance.context_analysis(organization_id);

-- Filtering & search
CREATE INDEX idx_context_type ON governance.context_analysis(analysis_type);
CREATE INDEX idx_context_status ON governance.context_analysis(review_status);
CREATE INDEX idx_context_priority ON governance.context_analysis(priority_level);
CREATE INDEX idx_context_created ON governance.context_analysis(created_at);

-- Date-based queries
CREATE INDEX idx_context_next_review ON governance.context_analysis(next_review_date);
CREATE INDEX idx_context_next_review_due ON governance.context_analysis(next_review_date)
WHERE review_status = 'approved' AND next_review_date IS NOT NULL;

-- Composite indexes
CREATE INDEX idx_context_org_status ON governance.context_analysis(organization_id, review_status);
CREATE INDEX idx_context_tenant_type ON governance.context_analysis(tenant_id, analysis_type);

-- =====================================================
-- ROW LEVEL SECURITY (RLS) - Stakeholders
-- =====================================================

ALTER TABLE governance.stakeholders ENABLE ROW LEVEL SECURITY;

-- Policy: Tenant isolation
CREATE POLICY stakeholders_tenant_isolation
ON governance.stakeholders
USING (
    tenant_id = current_setting('app.current_tenant_id', true)::text
);

-- Policy: Organization-level access
CREATE POLICY stakeholders_org_access
ON governance.stakeholders
USING (
    organization_id IN (
        SELECT id FROM core.organizations
        WHERE tenant_id = current_setting('app.current_tenant_id', true)::text
    )
);

-- Policy: Platform admin full access
CREATE POLICY stakeholders_platform_admin
ON governance.stakeholders
USING (
    current_setting('app.is_platform_admin', true)::boolean = true
);

-- =====================================================
-- ROW LEVEL SECURITY (RLS) - Context Analysis
-- =====================================================

ALTER TABLE governance.context_analysis ENABLE ROW LEVEL SECURITY;

-- Policy: Tenant isolation
CREATE POLICY context_analysis_tenant_isolation
ON governance.context_analysis
USING (
    tenant_id = current_setting('app.current_tenant_id', true)::text
);

-- Policy: Organization-level access
CREATE POLICY context_analysis_org_access
ON governance.context_analysis
USING (
    organization_id IN (
        SELECT id FROM core.organizations
        WHERE tenant_id = current_setting('app.current_tenant_id', true)::text
    )
);

-- Policy: Platform admin full access
CREATE POLICY context_analysis_platform_admin
ON governance.context_analysis
USING (
    current_setting('app.is_platform_admin', true)::boolean = true
);

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger: Auto-update updated_at timestamp for stakeholders
CREATE TRIGGER update_stakeholders_updated_at
BEFORE UPDATE ON governance.stakeholders
FOR EACH ROW
EXECUTE FUNCTION core.update_updated_at_column();

-- Trigger: Auto-update updated_at timestamp for context_analysis
CREATE TRIGGER update_context_analysis_updated_at
BEFORE UPDATE ON governance.context_analysis
FOR EACH ROW
EXECUTE FUNCTION core.update_updated_at_column();

-- =====================================================
-- ANALYTICAL VIEWS
-- =====================================================

-- View: Stakeholder Power/Interest Matrix
CREATE OR REPLACE VIEW governance.v_stakeholder_matrix AS
SELECT
    organization_id,
    tenant_id,
    influence_level,
    interest_level,

    -- Quadrant classification (Mendelow Matrix)
    CASE
        WHEN influence_level = 'high' AND interest_level = 'high' THEN 'Manage Closely'
        WHEN influence_level = 'high' AND interest_level IN ('medium', 'low') THEN 'Keep Satisfied'
        WHEN influence_level IN ('medium', 'low') AND interest_level = 'high' THEN 'Keep Informed'
        ELSE 'Monitor'
    END AS management_strategy,

    COUNT(*) AS stakeholder_count,
    AVG(satisfaction_score) AS avg_satisfaction,
    AVG(priority_score) AS avg_priority,

    ARRAY_AGG(
        jsonb_build_object(
            'id', id,
            'name', stakeholder_name,
            'type', stakeholder_type,
            'category', category
        ) ORDER BY priority_score DESC
    ) AS stakeholders
FROM governance.stakeholders
WHERE status = 'active'
GROUP BY organization_id, tenant_id, influence_level, interest_level
ORDER BY
    CASE influence_level WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
    CASE interest_level WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END;

-- View: Context analyses requiring review
CREATE OR REPLACE VIEW governance.v_context_review_due AS
SELECT
    c.id,
    c.organization_id,
    c.tenant_id,
    c.analysis_type,
    c.analysis_name,
    c.review_status,
    c.next_review_date,
    c.validity_period_months,
    c.updated_at,

    -- Days until review
    CASE
        WHEN c.next_review_date IS NOT NULL
        THEN c.next_review_date - CURRENT_DATE
        ELSE NULL
    END AS days_until_review,

    -- Overdue flag
    CASE
        WHEN c.next_review_date < CURRENT_DATE THEN true
        ELSE false
    END AS is_overdue
FROM governance.context_analysis c
WHERE c.review_status = 'approved'
  AND c.next_review_date IS NOT NULL
  AND c.next_review_date <= CURRENT_DATE + INTERVAL '30 days'
ORDER BY c.next_review_date ASC;

-- View: Active context summary by organization
CREATE OR REPLACE VIEW governance.v_context_summary AS
SELECT
    organization_id,
    tenant_id,

    COUNT(*) AS total_analyses,
    COUNT(*) FILTER (WHERE analysis_type = 'PESTLE') AS pestle_count,
    COUNT(*) FILTER (WHERE analysis_type = 'SWOT') AS swot_count,
    COUNT(*) FILTER (WHERE analysis_type = 'PORTER') AS porter_count,
    COUNT(*) FILTER (WHERE analysis_type = 'VUCA') AS vuca_count,

    COUNT(*) FILTER (WHERE review_status = 'draft') AS draft_count,
    COUNT(*) FILTER (WHERE review_status = 'in_review') AS in_review_count,
    COUNT(*) FILTER (WHERE review_status = 'approved') AS approved_count,

    COUNT(*) FILTER (WHERE next_review_date < CURRENT_DATE) AS overdue_reviews,

    MAX(updated_at) AS last_updated
FROM governance.context_analysis
WHERE review_status != 'archived'
GROUP BY organization_id, tenant_id;

-- =====================================================
-- COMMENTS (Documentation)
-- =====================================================

COMMENT ON TABLE governance.stakeholders IS 'ISO 22301 Clause 4.2 - Stakeholder needs and expectations';
COMMENT ON TABLE governance.context_analysis IS 'ISO 22301 Clause 4.1 - Understanding organization and its context';

COMMENT ON COLUMN governance.stakeholders.influence_level IS 'Stakeholder power/influence (Mendelow Matrix)';
COMMENT ON COLUMN governance.stakeholders.interest_level IS 'Stakeholder interest in BCMS (Mendelow Matrix)';
COMMENT ON COLUMN governance.stakeholders.satisfaction_score IS 'Stakeholder satisfaction rating 1-5';

COMMENT ON COLUMN governance.context_analysis.analysis_type IS 'Type of context analysis (PESTLE, SWOT, PORTER, VUCA)';
COMMENT ON COLUMN governance.context_analysis.analysis_data IS 'Structured analysis data in JSONB format';
COMMENT ON COLUMN governance.context_analysis.validity_period_months IS 'How long analysis remains valid before review required';

COMMENT ON VIEW governance.v_stakeholder_matrix IS 'Mendelow Matrix visualization - stakeholder power/interest quadrants';

-- =====================================================
-- VERIFICATION
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Migration 016: Governance Context & Stakeholders - COMPLETE';
    RAISE NOTICE 'Tables created: 2';
    RAISE NOTICE 'Views created: 3';
    RAISE NOTICE 'Indexes created: 20';
    RAISE NOTICE 'RLS policies: 6';
    RAISE NOTICE 'Triggers: 2';
END $$;
-- =====================================================
-- Migration 017: Governance - Domain Intelligence System
-- =====================================================
-- Purpose: Industry-specific knowledge base and domain classification
-- Based on: /BCM/governance/database/migrations/004_add_domain_intelligence.sql
-- Date: 2025-10-02
-- Stage 4: Domain Classification & Industry Knowledge
-- Makes the platform intelligent with industry-specific recommendations
-- =====================================================

-- =====================================================
-- PART 1: CREATE DOMAIN_INTELLIGENCE SCHEMA
-- =====================================================

CREATE SCHEMA IF NOT EXISTS domain_intelligence;

COMMENT ON SCHEMA domain_intelligence IS 'Industry knowledge and domain classification system - shared across tenants';

-- =====================================================
-- PART 2: EXTEND ORGANIZATIONS TABLE (for domain classification)
-- =====================================================

-- Add domain classification columns to core.organizations
ALTER TABLE core.organizations
    ADD COLUMN IF NOT EXISTS organizational_type VARCHAR(50) CHECK (
        organizational_type IS NULL OR organizational_type IN (
            'for_profit', 'non_profit', 'government', 'educational',
            'healthcare_provider', 'financial_institution', 'other'
        )
    ),
    ADD COLUMN IF NOT EXISTS industry_domain VARCHAR(50),
    ADD COLUMN IF NOT EXISTS sub_domain VARCHAR(100),
    ADD COLUMN IF NOT EXISTS company_size VARCHAR(50) CHECK (
        company_size IS NULL OR company_size IN (
            'micro', 'small', 'medium', 'large', 'enterprise'
        )
    ),
    ADD COLUMN IF NOT EXISTS geographic_scope VARCHAR(50),
    ADD COLUMN IF NOT EXISTS regulatory_requirements JSONB DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS domain_classified_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS domain_classified_by UUID;  -- User ID

-- Create indexes for domain classification
CREATE INDEX IF NOT EXISTS idx_orgs_org_type ON core.organizations(organizational_type);
CREATE INDEX IF NOT EXISTS idx_orgs_industry ON core.organizations(industry_domain);
CREATE INDEX IF NOT EXISTS idx_orgs_subdomain ON core.organizations(sub_domain);
CREATE INDEX IF NOT EXISTS idx_orgs_company_size ON core.organizations(company_size);

-- Comments
COMMENT ON COLUMN core.organizations.industry_domain IS 'Primary industry classification (healthcare, financial, manufacturing, etc.)';
COMMENT ON COLUMN core.organizations.sub_domain IS 'Industry sub-domain (hospital, bank, automotive, etc.)';
COMMENT ON COLUMN core.organizations.organizational_type IS 'Organization type (for_profit, non_profit, government, etc.)';
COMMENT ON COLUMN core.organizations.company_size IS 'Organization size (micro, small, medium, large, enterprise)';
COMMENT ON COLUMN core.organizations.regulatory_requirements IS 'Applicable regulations (HIPAA, SOX, GDPR, etc.)';

-- =====================================================
-- TABLE 1: INDUSTRY KNOWLEDGE
-- =====================================================

CREATE TABLE IF NOT EXISTS domain_intelligence.industry_knowledge (
    -- Primary Key (UUID)
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Classification
    industry VARCHAR(50) NOT NULL,  -- healthcare, financial, manufacturing, etc.
    sub_domain VARCHAR(100),        -- hospital, bank, automotive, etc.
    knowledge_type VARCHAR(50) NOT NULL CHECK (knowledge_type IN (
        'typical_rto',
        'typical_rpo',
        'common_risk',
        'regulatory_requirement',
        'best_practice',
        'critical_process',
        'seasonal_factor',
        'compliance_standard',
        'other'
    )),

    -- Knowledge Content
    title VARCHAR(255) NOT NULL,
    description TEXT,
    knowledge_data JSONB NOT NULL,
    /*
    Examples of knowledge_data structure:

    For typical_rto:
    {
        "process": "EHR System",
        "typical_rto_hours": 4,
        "range_min": 2,
        "range_max": 8,
        "percentile_25": 2,
        "percentile_50": 4,
        "percentile_75": 6,
        "reasoning": "Patient care continuity requirements"
    }

    For regulatory_requirement:
    {
        "regulation": "HIPAA",
        "requirement": "Emergency access to patient data",
        "consequence": "Criminal penalties up to $250,000",
        "reference_url": "https://..."
    }

    For common_risk:
    {
        "risk_name": "Ransomware Attack",
        "likelihood": "high",
        "typical_impact": "critical",
        "mitigation_strategies": ["Offline backups", "MFA", "Security training"]
    }
    */

    -- Applicability
    applies_to_org_types JSONB DEFAULT '[]'::jsonb,  -- ['for_profit', 'non_profit']
    applies_to_sizes JSONB DEFAULT '[]'::jsonb,      -- ['large', 'enterprise']
    geographic_relevance JSONB DEFAULT '[]'::jsonb,  -- ['US', 'EU', 'global']

    -- Source & Confidence
    source VARCHAR(255),           -- "BCI GPG 7.0", "ISO 22301:2019", "Internal research"
    source_url TEXT,
    confidence_level VARCHAR(20) CHECK (confidence_level IN ('low', 'medium', 'high', 'verified')),
    verified_by VARCHAR(255),
    verified_at TIMESTAMP WITH TIME ZONE,

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,      -- Track how often this knowledge is used
    last_used_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,  -- User ID

    -- Tags for search
    tags JSONB DEFAULT '[]'::jsonb
);

-- =====================================================
-- TABLE 2: DOMAIN TEMPLATES
-- =====================================================

CREATE TABLE IF NOT EXISTS domain_intelligence.domain_templates (
    -- Primary Key (UUID)
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Classification
    industry VARCHAR(50) NOT NULL,
    sub_domain VARCHAR(100),
    template_type VARCHAR(50) NOT NULL CHECK (template_type IN (
        'bcp_plan',
        'bia_process',
        'risk_catalog',
        'exercise_scenario',
        'policy_template',
        'checklist',
        'communication_plan',
        'other'
    )),

    -- Template Details
    template_name VARCHAR(255) NOT NULL,
    template_code VARCHAR(100) NOT NULL,  -- healthcare_ehr_bcp, financial_payment_risk
    description TEXT,
    complexity_level VARCHAR(20) CHECK (complexity_level IN ('basic', 'intermediate', 'advanced')),

    -- Template Content (JSONB for flexibility)
    template_data JSONB NOT NULL,
    /*
    Example for exercise_scenario:
    {
        "scenario_name": "Ransomware Attack - Healthcare",
        "duration_hours": 3,
        "participants": ["IT", "Security", "Clinical", "Executive"],
        "injects": [
            {
                "time_minutes": 0,
                "inject": "Encryption detected on EHR servers",
                "expected_response": "Activate incident response team"
            }
        ],
        "success_criteria": [
            "EHR restored from backups within RTO"
        ]
    }
    */

    -- Applicability
    applies_to_org_types JSONB DEFAULT '[]'::jsonb,
    applies_to_sizes JSONB DEFAULT '[]'::jsonb,

    -- Usage Statistics
    usage_count INTEGER DEFAULT 0,
    rating DECIMAL(3,2) CHECK (rating IS NULL OR (rating >= 0 AND rating <= 5)),  -- Average rating 0.00-5.00
    rating_count INTEGER DEFAULT 0,

    -- Metadata
    version VARCHAR(50) DEFAULT '1.0',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,  -- User ID

    tags JSONB DEFAULT '[]'::jsonb,

    -- Constraints
    CONSTRAINT uq_template_code UNIQUE (template_code)
);

-- =====================================================
-- TABLE 3: INDUSTRY BENCHMARKS
-- =====================================================
-- Cross-tenant anonymous aggregates for competitive intelligence

CREATE TABLE IF NOT EXISTS domain_intelligence.industry_benchmarks (
    -- Primary Key (UUID)
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Classification
    industry VARCHAR(50) NOT NULL,
    sub_domain VARCHAR(100),
    metric_name VARCHAR(100) NOT NULL,  -- rto_ehr_system, plan_currency_rate, exercise_frequency

    -- Statistical Data
    sample_size INTEGER NOT NULL,           -- Number of organizations in sample

    mean_value DECIMAL(15,2),
    median_value DECIMAL(15,2),
    percentile_25 DECIMAL(15,2),
    percentile_50 DECIMAL(15,2),
    percentile_75 DECIMAL(15,2),
    percentile_90 DECIMAL(15,2),
    std_deviation DECIMAL(15,2),

    min_value DECIMAL(15,2),
    max_value DECIMAL(15,2),

    -- Unit & Context
    unit_of_measure VARCHAR(50),        -- hours, percentage, days, count
    metric_description TEXT,
    calculation_method TEXT,

    -- Data Quality
    data_collection_period_start DATE NOT NULL,
    data_collection_period_end DATE NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    confidence_level VARCHAR(20) CHECK (confidence_level IN ('low', 'medium', 'high')),
    data_quality_score INTEGER CHECK (data_quality_score BETWEEN 0 AND 100),

    -- Filtering (for more specific benchmarks)
    company_size_filter VARCHAR(50),    -- Only large companies, etc.
    geographic_filter VARCHAR(50),      -- US only, EU only, etc.

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID,  -- User ID

    -- Ensure unique benchmarks
    CONSTRAINT uq_benchmark UNIQUE (
        industry, sub_domain, metric_name,
        company_size_filter, geographic_filter,
        data_collection_period_end
    )
);

-- =====================================================
-- INDEXES - Industry Knowledge
-- =====================================================

CREATE INDEX idx_knowledge_industry ON domain_intelligence.industry_knowledge(industry);
CREATE INDEX idx_knowledge_subdomain ON domain_intelligence.industry_knowledge(sub_domain);
CREATE INDEX idx_knowledge_type ON domain_intelligence.industry_knowledge(knowledge_type);
CREATE INDEX idx_knowledge_active ON domain_intelligence.industry_knowledge(is_active);
CREATE INDEX idx_knowledge_industry_type ON domain_intelligence.industry_knowledge(industry, knowledge_type);
CREATE INDEX idx_knowledge_tags ON domain_intelligence.industry_knowledge USING gin(tags);

-- =====================================================
-- INDEXES - Domain Templates
-- =====================================================

CREATE INDEX idx_template_industry ON domain_intelligence.domain_templates(industry);
CREATE INDEX idx_template_subdomain ON domain_intelligence.domain_templates(sub_domain);
CREATE INDEX idx_template_type ON domain_intelligence.domain_templates(template_type);
CREATE INDEX idx_template_code ON domain_intelligence.domain_templates(template_code);
CREATE INDEX idx_template_active ON domain_intelligence.domain_templates(is_active);
CREATE INDEX idx_template_rating ON domain_intelligence.domain_templates(rating DESC NULLS LAST);
CREATE INDEX idx_template_industry_type ON domain_intelligence.domain_templates(industry, template_type);

-- =====================================================
-- INDEXES - Industry Benchmarks
-- =====================================================

CREATE INDEX idx_benchmark_industry ON domain_intelligence.industry_benchmarks(industry);
CREATE INDEX idx_benchmark_metric ON domain_intelligence.industry_benchmarks(metric_name);
CREATE INDEX idx_benchmark_active ON domain_intelligence.industry_benchmarks(is_active);
CREATE INDEX idx_benchmark_period ON domain_intelligence.industry_benchmarks(data_collection_period_end DESC);
CREATE INDEX idx_benchmark_industry_metric ON domain_intelligence.industry_benchmarks(industry, metric_name);

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION domain_intelligence.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_industry_knowledge_updated_at
BEFORE UPDATE ON domain_intelligence.industry_knowledge
FOR EACH ROW
EXECUTE FUNCTION domain_intelligence.update_updated_at();

CREATE TRIGGER update_domain_templates_updated_at
BEFORE UPDATE ON domain_intelligence.domain_templates
FOR EACH ROW
EXECUTE FUNCTION domain_intelligence.update_updated_at();

-- =====================================================
-- ANALYTICAL VIEWS
-- =====================================================

-- View: Available Industries
CREATE OR REPLACE VIEW domain_intelligence.v_available_industries AS
SELECT DISTINCT
    industry,
    COUNT(DISTINCT id) AS knowledge_items,
    COUNT(DISTINCT CASE WHEN knowledge_type = 'typical_rto' THEN id END) AS rto_recommendations,
    COUNT(DISTINCT CASE WHEN knowledge_type = 'common_risk' THEN id END) AS risk_items,
    COUNT(DISTINCT CASE WHEN knowledge_type = 'regulatory_requirement' THEN id END) AS regulatory_items,
    COUNT(DISTINCT CASE WHEN knowledge_type = 'best_practice' THEN id END) AS best_practices
FROM domain_intelligence.industry_knowledge
WHERE is_active = TRUE
GROUP BY industry
ORDER BY knowledge_items DESC;

-- View: Industry Knowledge Summary
CREATE OR REPLACE VIEW domain_intelligence.v_industry_summary AS
SELECT
    k.industry,
    k.sub_domain,
    COUNT(DISTINCT k.id) AS total_knowledge_items,
    COUNT(DISTINCT t.id) AS total_templates,
    COUNT(DISTINCT b.id) AS total_benchmarks,
    MAX(k.updated_at) AS last_knowledge_update,
    SUM(k.usage_count) AS total_knowledge_usage,
    AVG(t.rating) AS avg_template_rating
FROM domain_intelligence.industry_knowledge k
LEFT JOIN domain_intelligence.domain_templates t
    ON t.industry = k.industry
    AND (t.sub_domain = k.sub_domain OR t.sub_domain IS NULL OR k.sub_domain IS NULL)
LEFT JOIN domain_intelligence.industry_benchmarks b
    ON b.industry = k.industry
    AND (b.sub_domain = k.sub_domain OR b.sub_domain IS NULL OR k.sub_domain IS NULL)
WHERE k.is_active = TRUE
GROUP BY k.industry, k.sub_domain
ORDER BY total_knowledge_items DESC;

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function: Get domain recommendations for an organization
CREATE OR REPLACE FUNCTION domain_intelligence.get_organization_recommendations(
    p_organization_id UUID,
    p_context_type VARCHAR(50) DEFAULT NULL  -- 'bia', 'risk', 'planning', etc.
)
RETURNS TABLE (
    knowledge_id UUID,
    title VARCHAR(255),
    knowledge_type VARCHAR(50),
    description TEXT,
    knowledge_data JSONB,
    relevance_score DECIMAL(5,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        k.id,
        k.title,
        k.knowledge_type,
        k.description,
        k.knowledge_data,
        -- Relevance score based on confidence level
        CASE
            WHEN k.confidence_level = 'verified' THEN 100.0
            WHEN k.confidence_level = 'high' THEN 85.0
            WHEN k.confidence_level = 'medium' THEN 70.0
            ELSE 50.0
        END AS relevance_score
    FROM domain_intelligence.industry_knowledge k
    INNER JOIN core.organizations o ON
        o.id = p_organization_id
        AND k.industry = o.industry_domain
        AND (k.sub_domain IS NULL OR k.sub_domain = o.sub_domain)
    WHERE k.is_active = TRUE
      AND (p_context_type IS NULL OR k.knowledge_type LIKE '%' || p_context_type || '%')
    ORDER BY relevance_score DESC, k.usage_count DESC
    LIMIT 20;
END;
$$ LANGUAGE plpgsql;

-- Function: Track knowledge usage
CREATE OR REPLACE FUNCTION domain_intelligence.track_knowledge_usage(
    p_knowledge_id UUID
)
RETURNS VOID AS $$
BEGIN
    UPDATE domain_intelligence.industry_knowledge
    SET
        usage_count = usage_count + 1,
        last_used_at = CURRENT_TIMESTAMP
    WHERE id = p_knowledge_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Track template usage
CREATE OR REPLACE FUNCTION domain_intelligence.track_template_usage(
    p_template_id UUID
)
RETURNS VOID AS $$
BEGIN
    UPDATE domain_intelligence.domain_templates
    SET usage_count = usage_count + 1
    WHERE id = p_template_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Rate template
CREATE OR REPLACE FUNCTION domain_intelligence.rate_template(
    p_template_id UUID,
    p_rating DECIMAL(3,2)
)
RETURNS VOID AS $$
BEGIN
    UPDATE domain_intelligence.domain_templates
    SET
        rating = CASE
            WHEN rating IS NULL THEN p_rating
            ELSE ((rating * rating_count) + p_rating) / (rating_count + 1)
        END,
        rating_count = rating_count + 1
    WHERE id = p_template_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- ROW LEVEL SECURITY
-- =====================================================

-- Note: Domain intelligence tables are SHARED across all tenants
-- No RLS policies needed - this is platform-wide knowledge
-- Access control is managed at application level

-- Organizations table already has RLS from previous migrations

-- =====================================================
-- COMMENTS (Documentation)
-- =====================================================

COMMENT ON TABLE domain_intelligence.industry_knowledge IS 'Industry-specific knowledge base (RTOs, risks, regulations, best practices) - shared across tenants';
COMMENT ON TABLE domain_intelligence.domain_templates IS 'Reusable templates for BCPs, BIAs, risks, exercises by industry - shared across tenants';
COMMENT ON TABLE domain_intelligence.industry_benchmarks IS 'Anonymous cross-tenant benchmarks for competitive intelligence';

COMMENT ON COLUMN domain_intelligence.industry_knowledge.knowledge_data IS 'Structured knowledge content in JSONB format';
COMMENT ON COLUMN domain_intelligence.industry_knowledge.confidence_level IS 'Confidence in knowledge accuracy (verified > high > medium > low)';
COMMENT ON COLUMN domain_intelligence.industry_knowledge.usage_count IS 'How many times this knowledge has been accessed/applied';

COMMENT ON COLUMN domain_intelligence.domain_templates.template_data IS 'Template content structure in JSONB format';
COMMENT ON COLUMN domain_intelligence.domain_templates.rating IS 'Average user rating 0.00-5.00';

COMMENT ON FUNCTION domain_intelligence.get_organization_recommendations IS 'Get recommended knowledge items for an organization based on their domain classification';

-- =====================================================
-- VERIFICATION
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Migration 017: Governance Domain Intelligence - COMPLETE';
    RAISE NOTICE 'Schema created: domain_intelligence';
    RAISE NOTICE 'Tables created: 3';
    RAISE NOTICE 'Views created: 2';
    RAISE NOTICE 'Functions created: 4';
    RAISE NOTICE 'Indexes created: 19';
    RAISE NOTICE 'Triggers: 2';
    RAISE NOTICE 'Note: No RLS - shared knowledge across tenants';
END $$;
-- =====================================================
-- Migration 018: Validation - KPI Alerts
-- =====================================================
-- Purpose: Automated alerting system for KPI threshold breaches
-- Based on: /BCM/validation/database/migrations/003_add_kpi_alerts.sql
-- Date: 2025-10-02
-- Stage 2: KPI Auto-Alerting System
-- =====================================================

-- =====================================================
-- TABLE: validation.kpi_alerts
-- =====================================================

CREATE TABLE IF NOT EXISTS validation.kpi_alerts (
    -- Primary Key (UUID)
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Multi-tenancy
    tenant_id VARCHAR(100) NOT NULL,
    organization_id UUID NOT NULL REFERENCES core.organizations(id) ON DELETE CASCADE,

    -- KPI Reference (FK to validation.kpis)
    kpi_id UUID NOT NULL REFERENCES validation.kpis(id) ON DELETE CASCADE,

    -- Alert Identification
    alert_code VARCHAR(50) NOT NULL,  -- ALERT-KPI-2024-001 (unique per organization)

    -- Alert Severity
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('critical', 'warning', 'info')),

    -- Trigger Information
    triggered_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    triggered_value DECIMAL(15,2) NOT NULL,
    threshold_breached DECIMAL(15,2),
    threshold_type VARCHAR(20) CHECK (threshold_type IN ('critical', 'warning')),

    -- Message
    alert_title VARCHAR(500) NOT NULL,
    alert_message TEXT NOT NULL,

    -- Status & Lifecycle
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN (
        'active',
        'acknowledged',
        'resolved',
        'auto_resolved'
    )),

    -- Acknowledgement
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    acknowledged_by UUID,  -- User ID
    acknowledged_by_name VARCHAR(255),
    acknowledgement_notes TEXT,

    -- Resolution
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID,  -- User ID
    resolved_by_name VARCHAR(255),
    resolution_notes TEXT,
    resolved_value DECIMAL(15,2),
    auto_resolved BOOLEAN DEFAULT false,

    -- Notification
    notification_sent BOOLEAN DEFAULT false,
    notification_sent_at TIMESTAMP WITH TIME ZONE,
    recipients JSONB DEFAULT '[]'::jsonb,
    notification_error TEXT,

    -- Escalation
    escalated BOOLEAN DEFAULT false,
    escalated_at TIMESTAMP WITH TIME ZONE,
    escalated_to JSONB DEFAULT '[]'::jsonb,

    -- Related Data
    measurement_id UUID,  -- Link to specific KPI measurement
    related_incidents UUID[],

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT uq_alert_code_per_org UNIQUE (organization_id, alert_code)
);

-- =====================================================
-- INDEXES
-- =====================================================

-- Primary lookups
CREATE INDEX idx_kpi_alerts_tenant ON validation.kpi_alerts(tenant_id);
CREATE INDEX idx_kpi_alerts_organization ON validation.kpi_alerts(organization_id);
CREATE INDEX idx_kpi_alerts_kpi ON validation.kpi_alerts(kpi_id);

-- Filtering & search
CREATE INDEX idx_kpi_alerts_status ON validation.kpi_alerts(status);
CREATE INDEX idx_kpi_alerts_severity ON validation.kpi_alerts(severity);
CREATE INDEX idx_kpi_alerts_triggered ON validation.kpi_alerts(triggered_at);

-- Active alerts (most common query)
CREATE INDEX idx_kpi_alerts_active ON validation.kpi_alerts(status, severity)
WHERE status = 'active';

-- Composite indexes for common queries
CREATE INDEX idx_kpi_alerts_tenant_status ON validation.kpi_alerts(tenant_id, status);
CREATE INDEX idx_kpi_alerts_org_status ON validation.kpi_alerts(organization_id, status);
CREATE INDEX idx_kpi_alerts_kpi_status ON validation.kpi_alerts(kpi_id, status);

-- Notification tracking
CREATE INDEX idx_kpi_alerts_notification ON validation.kpi_alerts(notification_sent, notification_sent_at);

-- Escalation tracking
CREATE INDEX idx_kpi_alerts_escalation ON validation.kpi_alerts(escalated, escalated_at);

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================================

ALTER TABLE validation.kpi_alerts ENABLE ROW LEVEL SECURITY;

-- Policy: Tenant isolation
CREATE POLICY kpi_alerts_tenant_isolation
ON validation.kpi_alerts
USING (
    tenant_id = current_setting('app.current_tenant_id', true)::text
);

-- Policy: Organization-level access
CREATE POLICY kpi_alerts_org_access
ON validation.kpi_alerts
USING (
    organization_id IN (
        SELECT id FROM core.organizations
        WHERE tenant_id = current_setting('app.current_tenant_id', true)::text
    )
);

-- Policy: Platform admin full access
CREATE POLICY kpi_alerts_platform_admin
ON validation.kpi_alerts
USING (
    current_setting('app.is_platform_admin', true)::boolean = true
);

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger: Auto-update updated_at timestamp
CREATE TRIGGER update_kpi_alerts_updated_at
BEFORE UPDATE ON validation.kpi_alerts
FOR EACH ROW
EXECUTE FUNCTION core.update_updated_at_column();

-- Trigger: Auto-generate alert_code if not provided
CREATE OR REPLACE FUNCTION validation.generate_alert_code()
RETURNS TRIGGER AS $$
DECLARE
    next_num INTEGER;
    new_code VARCHAR(50);
    current_year INTEGER;
BEGIN
    IF NEW.alert_code IS NULL OR NEW.alert_code = '' THEN
        current_year := EXTRACT(YEAR FROM CURRENT_DATE);

        -- Get next sequential number for this organization and year
        SELECT COALESCE(
            MAX(
                CAST(
                    SPLIT_PART(alert_code, '-', 4) AS INTEGER
                )
            ), 0
        ) + 1
        INTO next_num
        FROM validation.kpi_alerts
        WHERE organization_id = NEW.organization_id
          AND alert_code LIKE 'ALERT-KPI-' || current_year || '-%';

        -- Generate code: ALERT-KPI-2024-001
        new_code := 'ALERT-KPI-' || current_year || '-' || LPAD(next_num::TEXT, 3, '0');
        NEW.alert_code := new_code;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER generate_alert_code_trigger
BEFORE INSERT ON validation.kpi_alerts
FOR EACH ROW
EXECUTE FUNCTION validation.generate_alert_code();

-- =====================================================
-- ANALYTICAL VIEWS
-- =====================================================

-- View: Active alerts summary
CREATE OR REPLACE VIEW validation.v_active_alerts AS
SELECT
    a.id,
    a.organization_id,
    a.tenant_id,
    a.alert_code,
    a.severity,
    a.triggered_at,
    a.status,

    -- KPI details
    k.kpi_code,
    k.kpi_name,
    k.category,
    k.owner,

    -- Alert details
    a.alert_title,
    a.triggered_value,
    a.threshold_breached,
    a.threshold_type,

    -- Time metrics
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - a.triggered_at)) / 3600 AS hours_since_triggered,

    -- Acknowledgement
    a.acknowledged_at,
    a.acknowledged_by_name,

    -- Escalation
    a.escalated,
    a.escalated_at
FROM validation.kpi_alerts a
INNER JOIN validation.kpis k ON k.id = a.kpi_id
WHERE a.status IN ('active', 'acknowledged')
ORDER BY
    CASE a.severity
        WHEN 'critical' THEN 1
        WHEN 'warning' THEN 2
        ELSE 3
    END,
    a.triggered_at DESC;

-- View: Alert statistics by KPI
CREATE OR REPLACE VIEW validation.v_alert_stats_by_kpi AS
SELECT
    a.kpi_id,
    k.kpi_code,
    k.kpi_name,
    k.organization_id,
    k.tenant_id,

    COUNT(*) AS total_alerts,
    COUNT(*) FILTER (WHERE a.severity = 'critical') AS critical_alerts,
    COUNT(*) FILTER (WHERE a.severity = 'warning') AS warning_alerts,
    COUNT(*) FILTER (WHERE a.status = 'active') AS active_alerts,
    COUNT(*) FILTER (WHERE a.status = 'acknowledged') AS acknowledged_alerts,
    COUNT(*) FILTER (WHERE a.status IN ('resolved', 'auto_resolved')) AS resolved_alerts,

    -- Average time to acknowledge (hours)
    AVG(
        EXTRACT(EPOCH FROM (a.acknowledged_at - a.triggered_at)) / 3600
    ) FILTER (WHERE a.acknowledged_at IS NOT NULL) AS avg_hours_to_acknowledge,

    -- Average time to resolve (hours)
    AVG(
        EXTRACT(EPOCH FROM (a.resolved_at - a.triggered_at)) / 3600
    ) FILTER (WHERE a.resolved_at IS NOT NULL) AS avg_hours_to_resolve,

    MAX(a.triggered_at) AS last_alert_triggered
FROM validation.kpi_alerts a
INNER JOIN validation.kpis k ON k.id = a.kpi_id
GROUP BY a.kpi_id, k.kpi_code, k.kpi_name, k.organization_id, k.tenant_id
ORDER BY total_alerts DESC;

-- View: Unacknowledged critical alerts
CREATE OR REPLACE VIEW validation.v_critical_unacknowledged AS
SELECT
    a.id,
    a.organization_id,
    a.tenant_id,
    a.alert_code,
    a.triggered_at,

    -- KPI details
    k.kpi_code,
    k.kpi_name,
    k.owner,

    -- Alert details
    a.alert_title,
    a.triggered_value,
    a.threshold_breached,

    -- Time metrics
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - a.triggered_at)) / 3600 AS hours_unacknowledged,

    -- Escalation
    a.escalated,
    a.escalated_at,

    -- Urgency score (higher = more urgent)
    CASE
        WHEN EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - a.triggered_at)) / 3600 > 24
        THEN 100
        WHEN EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - a.triggered_at)) / 3600 > 12
        THEN 75
        WHEN EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - a.triggered_at)) / 3600 > 4
        THEN 50
        ELSE 25
    END AS urgency_score
FROM validation.kpi_alerts a
INNER JOIN validation.kpis k ON k.id = a.kpi_id
WHERE a.severity = 'critical'
  AND a.status = 'active'
  AND a.acknowledged_at IS NULL
ORDER BY a.triggered_at ASC;

-- View: Alert trends (last 30 days)
CREATE OR REPLACE VIEW validation.v_alert_trends AS
SELECT
    DATE_TRUNC('day', a.triggered_at)::date AS alert_date,
    a.organization_id,
    a.tenant_id,

    COUNT(*) AS total_alerts,
    COUNT(*) FILTER (WHERE a.severity = 'critical') AS critical_count,
    COUNT(*) FILTER (WHERE a.severity = 'warning') AS warning_count,
    COUNT(*) FILTER (WHERE a.severity = 'info') AS info_count,

    COUNT(DISTINCT a.kpi_id) AS unique_kpis_triggered,

    AVG(
        EXTRACT(EPOCH FROM (a.resolved_at - a.triggered_at)) / 3600
    ) FILTER (WHERE a.resolved_at IS NOT NULL) AS avg_resolution_hours
FROM validation.kpi_alerts a
WHERE a.triggered_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', a.triggered_at)::date, a.organization_id, a.tenant_id
ORDER BY alert_date DESC;

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function: Create KPI alert
CREATE OR REPLACE FUNCTION validation.create_kpi_alert(
    p_kpi_id UUID,
    p_severity VARCHAR(20),
    p_triggered_value DECIMAL(15,2),
    p_threshold_breached DECIMAL(15,2),
    p_threshold_type VARCHAR(20),
    p_alert_title VARCHAR(500),
    p_alert_message TEXT
)
RETURNS UUID AS $$
DECLARE
    v_alert_id UUID;
    v_tenant_id VARCHAR(100);
    v_organization_id UUID;
BEGIN
    -- Get tenant and organization from KPI
    SELECT tenant_id, organization_id
    INTO v_tenant_id, v_organization_id
    FROM validation.kpis
    WHERE id = p_kpi_id;

    -- Create alert
    INSERT INTO validation.kpi_alerts (
        tenant_id,
        organization_id,
        kpi_id,
        severity,
        triggered_value,
        threshold_breached,
        threshold_type,
        alert_title,
        alert_message
    ) VALUES (
        v_tenant_id,
        v_organization_id,
        p_kpi_id,
        p_severity,
        p_triggered_value,
        p_threshold_breached,
        p_threshold_type,
        p_alert_title,
        p_alert_message
    )
    RETURNING id INTO v_alert_id;

    RETURN v_alert_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Acknowledge alert
CREATE OR REPLACE FUNCTION validation.acknowledge_alert(
    p_alert_id UUID,
    p_user_id UUID,
    p_user_name VARCHAR(255),
    p_notes TEXT DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    UPDATE validation.kpi_alerts
    SET
        status = 'acknowledged',
        acknowledged_at = CURRENT_TIMESTAMP,
        acknowledged_by = p_user_id,
        acknowledged_by_name = p_user_name,
        acknowledgement_notes = p_notes
    WHERE id = p_alert_id
      AND status = 'active';
END;
$$ LANGUAGE plpgsql;

-- Function: Resolve alert
CREATE OR REPLACE FUNCTION validation.resolve_alert(
    p_alert_id UUID,
    p_user_id UUID,
    p_user_name VARCHAR(255),
    p_resolution_notes TEXT DEFAULT NULL,
    p_resolved_value DECIMAL(15,2) DEFAULT NULL,
    p_auto_resolved BOOLEAN DEFAULT false
)
RETURNS VOID AS $$
BEGIN
    UPDATE validation.kpi_alerts
    SET
        status = CASE WHEN p_auto_resolved THEN 'auto_resolved' ELSE 'resolved' END,
        resolved_at = CURRENT_TIMESTAMP,
        resolved_by = p_user_id,
        resolved_by_name = p_user_name,
        resolution_notes = p_resolution_notes,
        resolved_value = p_resolved_value,
        auto_resolved = p_auto_resolved
    WHERE id = p_alert_id
      AND status IN ('active', 'acknowledged');
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- COMMENTS (Documentation)
-- =====================================================

COMMENT ON TABLE validation.kpi_alerts IS 'Automated alerting for KPI threshold breaches - ISO 22301 Clause 9.1';
COMMENT ON COLUMN validation.kpi_alerts.alert_code IS 'Unique alert code per organization (ALERT-KPI-2024-001)';
COMMENT ON COLUMN validation.kpi_alerts.severity IS 'Alert severity: critical, warning, info';
COMMENT ON COLUMN validation.kpi_alerts.threshold_type IS 'Which threshold was breached: critical or warning';
COMMENT ON COLUMN validation.kpi_alerts.auto_resolved IS 'True if alert was automatically resolved (e.g., KPI back in threshold)';

COMMENT ON VIEW validation.v_active_alerts IS 'Real-time view of active and acknowledged alerts';
COMMENT ON VIEW validation.v_critical_unacknowledged IS 'Critical alerts requiring immediate attention';
COMMENT ON VIEW validation.v_alert_trends IS 'Daily alert trends for last 30 days';

COMMENT ON FUNCTION validation.create_kpi_alert IS 'Create a new KPI alert when threshold is breached';
COMMENT ON FUNCTION validation.acknowledge_alert IS 'Acknowledge an active alert';
COMMENT ON FUNCTION validation.resolve_alert IS 'Resolve an alert (manual or automatic)';

-- =====================================================
-- VERIFICATION
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Migration 018: Validation KPI Alerts - COMPLETE';
    RAISE NOTICE 'Tables created: 1';
    RAISE NOTICE 'Views created: 4';
    RAISE NOTICE 'Functions created: 3';
    RAISE NOTICE 'Indexes created: 13';
    RAISE NOTICE 'RLS policies: 3';
    RAISE NOTICE 'Triggers: 2';
END $$;
