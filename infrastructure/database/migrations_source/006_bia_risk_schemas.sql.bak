-- ============================================
-- BCM Platform - Unified Database
-- Migration 006: BIA and Risk Schemas
-- ============================================
-- Creates BIA and Risk Management tables per ISO 22301:2019
-- Schemas: bia, risk
-- ============================================

-- =============================================
-- Schema: bia (Business Impact Analysis)
-- ISO 22301:2019 Clause 8.2.2
-- =============================================

-- Table: bia.processes
CREATE TABLE bia.processes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Process identification
    process_name VARCHAR(255) NOT NULL,
    process_code VARCHAR(50),
    process_owner_id UUID REFERENCES auth.users(id),
    department VARCHAR(255),

    -- Description
    description TEXT,
    inputs_outputs JSONB,
    dependencies JSONB DEFAULT '[]'::jsonb,

    -- Critical impact analysis
    rto INTEGER, -- Recovery Time Objective (hours)
    rpo INTEGER, -- Recovery Point Objective (hours)
    mtpd INTEGER, -- Maximum Tolerable Period of Disruption (hours)

    -- Impact ratings (1-5 scale)
    financial_impact INTEGER CHECK (financial_impact BETWEEN 1 AND 5),
    operational_impact INTEGER CHECK (operational_impact BETWEEN 1 AND 5),
    reputational_impact INTEGER CHECK (reputational_impact BETWEEN 1 AND 5),
    regulatory_impact INTEGER CHECK (regulatory_impact BETWEEN 1 AND 5),

    -- Overall criticality
    criticality_level VARCHAR(50),

    -- Resources required
    minimum_resources JSONB,

    -- Status
    is_active BOOLEAN DEFAULT true,
    last_reviewed_at TIMESTAMPTZ,
    reviewed_by UUID REFERENCES auth.users(id),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_bia_processes_org ON bia.processes(organization_id);
CREATE INDEX idx_bia_processes_criticality ON bia.processes(criticality_level);
CREATE INDEX idx_bia_processes_owner ON bia.processes(process_owner_id);

CREATE TRIGGER update_bia_processes_updated_at BEFORE UPDATE ON bia.processes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE bia.processes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "BIA processes visible to org members" ON bia.processes FOR SELECT
    USING (auth.is_org_member(organization_id));

CREATE POLICY "BIA processes manageable by org admins" ON bia.processes FOR ALL
    USING (auth.is_org_admin(organization_id));

COMMENT ON TABLE bia.processes IS 'Business processes with impact analysis per ISO 22301:2019 Clause 8.2.2';

-- Table: bia.templates
CREATE TABLE bia.templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES public.organizations(id), -- NULL = platform template

    template_name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    description TEXT,

    -- Template structure
    sections JSONB,
    questions JSONB,
    impact_scales JSONB,

    is_public BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,

    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_bia_templates_org ON bia.templates(organization_id);
CREATE INDEX idx_bia_templates_industry ON bia.templates(industry) WHERE is_public = true;

ALTER TABLE bia.templates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "BIA templates visible to org or public" ON bia.templates FOR SELECT
    USING (
        is_public = true
        OR organization_id IS NULL
        OR auth.is_org_member(organization_id)
    );

COMMENT ON TABLE bia.templates IS 'BIA templates for different industries';

-- =============================================
-- Schema: risk (Risk Management)
-- ISO 22301:2019 Clause 8.2.3
-- =============================================

-- Table: risk.risks
CREATE TABLE risk.risks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Risk identification
    risk_title VARCHAR(255) NOT NULL,
    risk_code VARCHAR(50),
    risk_category VARCHAR(100),

    -- Description
    description TEXT,
    threat_source VARCHAR(255),
    vulnerabilities TEXT[],

    -- Analysis
    likelihood INTEGER CHECK (likelihood BETWEEN 1 AND 5),
    impact INTEGER CHECK (impact BETWEEN 1 AND 5),
    inherent_risk_score INTEGER GENERATED ALWAYS AS (likelihood * impact) STORED,

    -- Treatment
    treatment_strategy VARCHAR(50),
    residual_likelihood INTEGER CHECK (residual_likelihood BETWEEN 1 AND 5),
    residual_impact INTEGER CHECK (residual_impact BETWEEN 1 AND 5),
    residual_risk_score INTEGER GENERATED ALWAYS AS (
        COALESCE(residual_likelihood, 0) * COALESCE(residual_impact, 0)
    ) STORED,

    -- Ownership
    risk_owner_id UUID REFERENCES auth.users(id),

    -- Related entities
    related_processes JSONB DEFAULT '[]'::jsonb,
    related_assets JSONB DEFAULT '[]'::jsonb,

    -- Status
    status VARCHAR(50) DEFAULT 'identified',

    -- Review
    last_reviewed_at TIMESTAMPTZ,
    next_review_date DATE,

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_risks_org ON risk.risks(organization_id);
CREATE INDEX idx_risks_score ON risk.risks(inherent_risk_score DESC);
CREATE INDEX idx_risks_status ON risk.risks(status);
CREATE INDEX idx_risks_category ON risk.risks(risk_category);
CREATE INDEX idx_risks_owner ON risk.risks(risk_owner_id);

CREATE TRIGGER update_risks_updated_at BEFORE UPDATE ON risk.risks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE risk.risks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Risks visible to org members" ON risk.risks FOR SELECT
    USING (auth.is_org_member(organization_id));

CREATE POLICY "Risks manageable by org admins" ON risk.risks FOR ALL
    USING (auth.is_org_admin(organization_id));

COMMENT ON TABLE risk.risks IS 'Risk register per ISO 22301:2019 Clause 8.2.3';

-- Table: risk.controls
CREATE TABLE risk.controls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    risk_id UUID NOT NULL REFERENCES risk.risks(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id),

    control_name VARCHAR(255) NOT NULL,
    control_type VARCHAR(50),
    description TEXT,

    -- Effectiveness
    effectiveness_rating INTEGER CHECK (effectiveness_rating BETWEEN 1 AND 5),

    -- Implementation
    implementation_status VARCHAR(50),
    implemented_date DATE,

    -- Ownership
    control_owner_id UUID REFERENCES auth.users(id),

    -- Testing
    last_tested_at TIMESTAMPTZ,
    test_frequency VARCHAR(50),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_controls_risk ON risk.controls(risk_id);
CREATE INDEX idx_controls_org ON risk.controls(organization_id);
CREATE INDEX idx_controls_status ON risk.controls(implementation_status);

CREATE TRIGGER update_controls_updated_at BEFORE UPDATE ON risk.controls
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE risk.controls ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Controls visible to org members" ON risk.controls FOR SELECT
    USING (auth.is_org_member(organization_id));

CREATE POLICY "Controls manageable by org admins" ON risk.controls FOR ALL
    USING (auth.is_org_admin(organization_id));

COMMENT ON TABLE risk.controls IS 'Risk controls and mitigation measures';

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 006 completed: BIA and Risk schemas created (4 tables)';
END
$$;
