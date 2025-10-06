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
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

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
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

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
        SELECT id FROM public.organizations
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
        SELECT id FROM public.organizations
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
EXECUTE FUNCTION public.update_updated_at_column();

-- Trigger: Auto-update updated_at timestamp for context_analysis
CREATE TRIGGER update_context_analysis_updated_at
BEFORE UPDATE ON governance.context_analysis
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();

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
