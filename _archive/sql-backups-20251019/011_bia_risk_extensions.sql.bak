-- ============================================
-- BCM Platform - Unified Database
-- Migration 011: BIA/Risk Extensions
-- ============================================
-- Additional tables for BIA and Risk modules
-- Extends migrations 006 (bia.processes, bia.templates, risk.risks, risk.controls)
-- ISO 22301:2019 Clauses 8.2.2 (BIA), 8.2.3 (Risk Assessment)
-- ============================================

-- Table: bia.impact_assessments
CREATE TABLE bia.impact_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_id UUID NOT NULL REFERENCES bia.processes(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Assessment identity
    assessment_code VARCHAR(100),
    assessment_title VARCHAR(255) NOT NULL,

    -- Timeframes (ISO 22301 key concept)
    time_period VARCHAR(50) NOT NULL, -- 0-4h, 4-24h, 1-3d, 3-7d, 1-2w, 2-4w, 1-3m, 3-6m
    time_hours INT, -- Hours from disruption start

    -- Impact categories
    financial_impact DECIMAL(15,2),
    financial_impact_description TEXT,

    operational_impact VARCHAR(50), -- catastrophic, major, moderate, minor, negligible
    operational_impact_description TEXT,

    reputational_impact VARCHAR(50),
    reputational_impact_description TEXT,

    legal_regulatory_impact VARCHAR(50),
    legal_regulatory_impact_description TEXT,

    customer_impact VARCHAR(50),
    customer_impact_description TEXT,
    estimated_customers_affected INT,

    -- Quantitative metrics
    revenue_loss_per_hour DECIMAL(15,2),
    productivity_loss_percent DECIMAL(5,2),
    data_loss_volume VARCHAR(100),

    -- Dependencies affected
    affected_dependencies JSONB DEFAULT '[]'::jsonb, -- UUIDs of bia.dependencies
    cascading_impacts TEXT,

    -- Recovery priorities
    priority_score INT, -- Calculated from impacts
    is_critical_timeframe BOOLEAN DEFAULT FALSE, -- Within MTPD?

    -- Scenario
    disruption_scenario TEXT,
    assumptions TEXT,

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, review, approved, outdated
    assessed_by UUID REFERENCES auth.users(id),
    assessed_at TIMESTAMPTZ DEFAULT NOW(),
    approved_by UUID REFERENCES auth.users(id),
    approved_at TIMESTAMPTZ,

    -- Metadata
    notes TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_impact_assessments_process ON bia.impact_assessments(process_id);
CREATE INDEX idx_impact_assessments_org ON bia.impact_assessments(organization_id);
CREATE INDEX idx_impact_assessments_timeframe ON bia.impact_assessments(time_period);
CREATE INDEX idx_impact_assessments_critical ON bia.impact_assessments(is_critical_timeframe) WHERE is_critical_timeframe = TRUE;

CREATE TRIGGER update_impact_assessments_updated_at BEFORE UPDATE ON bia.impact_assessments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE bia.impact_assessments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Impact assessments visible to org members" ON bia.impact_assessments FOR SELECT
    USING (auth.is_org_member(organization_id));

CREATE POLICY "Impact assessments manageable by org admins" ON bia.impact_assessments FOR ALL
    USING (auth.is_org_admin(organization_id));

COMMENT ON TABLE bia.impact_assessments IS 'Time-based impact assessments per ISO 22301 Clause 8.2.2';

-- Table: bia.dependencies
CREATE TABLE bia.dependencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_id UUID NOT NULL REFERENCES bia.processes(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Dependency identity
    dependency_type VARCHAR(100) NOT NULL, -- people, technology, supplier, facility, information, process, utility, transport
    dependency_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Criticality
    criticality VARCHAR(50) NOT NULL, -- critical, high, medium, low
    impact_if_unavailable TEXT,

    -- For People dependencies
    key_roles JSONB DEFAULT '[]'::jsonb, -- Required roles/skills
    minimum_staff_count INT,
    current_staff_count INT,
    succession_plan_exists BOOLEAN DEFAULT FALSE,

    -- For Technology dependencies
    system_name VARCHAR(255),
    system_owner_id UUID REFERENCES auth.users(id),
    rto_minutes INT, -- Recovery Time Objective
    rpo_minutes INT, -- Recovery Point Objective
    backup_exists BOOLEAN DEFAULT FALSE,
    redundancy_level VARCHAR(50), -- none, partial, full

    -- For Supplier dependencies
    supplier_name VARCHAR(255),
    supplier_contact JSONB, -- {name, email, phone}
    contract_number VARCHAR(100),
    alternative_suppliers JSONB DEFAULT '[]'::jsonb,
    supplier_recovery_plan_exists BOOLEAN DEFAULT FALSE,

    -- For Facility dependencies
    facility_name VARCHAR(255),
    facility_location VARCHAR(255),
    alternate_facility_exists BOOLEAN DEFAULT FALSE,
    alternate_facility_location VARCHAR(255),

    -- Availability requirements
    required_availability_percent DECIMAL(5,2),
    maximum_acceptable_outage_hours DECIMAL(10,2),

    -- Relationships
    depends_on JSONB DEFAULT '[]'::jsonb, -- UUIDs of other dependencies
    supports JSONB DEFAULT '[]'::jsonb, -- UUIDs of processes this supports

    -- Risk mitigation
    single_point_of_failure BOOLEAN DEFAULT FALSE,
    mitigation_measures TEXT,
    backup_arrangements TEXT,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    last_verified_date DATE,
    next_review_date DATE,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_dependencies_process ON bia.dependencies(process_id);
CREATE INDEX idx_dependencies_org ON bia.dependencies(organization_id);
CREATE INDEX idx_dependencies_type ON bia.dependencies(dependency_type);
CREATE INDEX idx_dependencies_criticality ON bia.dependencies(criticality);
CREATE INDEX idx_dependencies_spof ON bia.dependencies(single_point_of_failure) WHERE single_point_of_failure = TRUE;

CREATE TRIGGER update_dependencies_updated_at BEFORE UPDATE ON bia.dependencies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE bia.dependencies ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Dependencies visible to org members" ON bia.dependencies FOR SELECT
    USING (auth.is_org_member(organization_id));

CREATE POLICY "Dependencies manageable by org admins" ON bia.dependencies FOR ALL
    USING (auth.is_org_admin(organization_id));

COMMENT ON TABLE bia.dependencies IS 'Process dependencies per ISO 22301 Clause 8.2.2';

-- Table: bia.workflow_logs
CREATE TABLE bia.workflow_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_id UUID REFERENCES bia.processes(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Workflow event
    event_type VARCHAR(100) NOT NULL, -- created, status_changed, submitted, approved, rejected, updated, commented
    event_description TEXT,

    -- Context
    previous_status VARCHAR(50),
    new_status VARCHAR(50),

    previous_data JSONB, -- Snapshot before change
    new_data JSONB, -- Snapshot after change

    -- Actor
    actor_id UUID REFERENCES auth.users(id),
    actor_name VARCHAR(255),
    actor_role VARCHAR(100),

    -- Approval workflow
    approval_stage INT,
    approver_id UUID REFERENCES auth.users(id),
    approval_decision VARCHAR(50), -- approved, rejected, returned
    approval_comments TEXT,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_bia_workflow_logs_process ON bia.workflow_logs(process_id, created_at DESC);
CREATE INDEX idx_bia_workflow_logs_org ON bia.workflow_logs(organization_id);
CREATE INDEX idx_bia_workflow_logs_event ON bia.workflow_logs(event_type);
CREATE INDEX idx_bia_workflow_logs_actor ON bia.workflow_logs(actor_id);

ALTER TABLE bia.workflow_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "BIA workflow logs visible to org members" ON bia.workflow_logs FOR SELECT
    USING (auth.is_org_member(organization_id));

COMMENT ON TABLE bia.workflow_logs IS 'Audit trail for BIA workflow events';

-- Table: bia.exports
CREATE TABLE bia.exports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Export details
    export_type VARCHAR(100) NOT NULL, -- full_bia, process_report, impact_matrix, dependency_map, summary_report
    export_format VARCHAR(50) NOT NULL, -- pdf, excel, csv, json, docx

    -- Scope
    process_ids JSONB DEFAULT '[]'::jsonb, -- UUIDs of processes to include
    include_confidential BOOLEAN DEFAULT FALSE,

    -- Filters
    filters JSONB DEFAULT '{}'::jsonb, -- Applied filters

    -- File
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    file_size_bytes BIGINT,

    -- Status
    status VARCHAR(50) DEFAULT 'pending', -- pending, generating, completed, failed
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error_message TEXT,

    -- Generation details
    generated_by UUID REFERENCES auth.users(id),
    generation_duration_seconds INT,

    -- Access
    downloaded_count INT DEFAULT 0,
    last_downloaded_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_bia_exports_org ON bia.exports(organization_id, created_at DESC);
CREATE INDEX idx_bia_exports_status ON bia.exports(status);
CREATE INDEX idx_bia_exports_generated_by ON bia.exports(generated_by, created_at DESC);

ALTER TABLE bia.exports ENABLE ROW LEVEL SECURITY;

CREATE POLICY "BIA exports visible to org members" ON bia.exports FOR SELECT
    USING (auth.is_org_member(organization_id));

COMMENT ON TABLE bia.exports IS 'BIA report exports and downloads';

-- ======================
-- RISK SCHEMA EXTENSIONS
-- ======================

-- Table: risk.assessments
CREATE TABLE risk.assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    risk_id UUID NOT NULL REFERENCES risk.risks(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Assessment identity
    assessment_code VARCHAR(100),
    assessment_title VARCHAR(255),

    -- Assessment type
    assessment_type VARCHAR(100) NOT NULL, -- initial, reassessment, post_incident, scheduled, ad_hoc
    methodology VARCHAR(100), -- quantitative, qualitative, semi_quantitative, bow_tie, fmea

    -- ISO 22301 Clause 8.2.3
    likelihood_score INT NOT NULL, -- 1-5 scale
    likelihood_rationale TEXT,

    consequence_score INT NOT NULL, -- 1-5 scale
    consequence_rationale TEXT,

    -- Risk level
    risk_score INT, -- likelihood * consequence
    risk_level VARCHAR(50), -- critical, high, medium, low
    risk_priority INT, -- For prioritization

    -- Timeframe
    assessment_date DATE NOT NULL,
    review_date DATE,
    next_assessment_date DATE,

    -- Assessors
    lead_assessor_id UUID REFERENCES auth.users(id),
    assessment_team JSONB DEFAULT '[]'::jsonb, -- {user_id, role}

    -- Context
    threat_sources JSONB DEFAULT '[]'::jsonb,
    vulnerabilities JSONB DEFAULT '[]'::jsonb,
    existing_controls JSONB DEFAULT '[]'::jsonb, -- UUIDs of risk.controls

    -- Impact analysis
    financial_impact DECIMAL(15,2),
    operational_impact TEXT,
    reputational_impact TEXT,
    compliance_impact TEXT,

    -- Treatment decision
    treatment_decision VARCHAR(100), -- accept, mitigate, transfer, avoid
    treatment_justification TEXT,

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, review, approved, superseded
    approved_by UUID REFERENCES auth.users(id),
    approved_at TIMESTAMPTZ,

    -- Residual risk (after controls)
    residual_likelihood_score INT,
    residual_consequence_score INT,
    residual_risk_score INT,
    residual_risk_level VARCHAR(50),

    -- Metadata
    assumptions TEXT,
    limitations TEXT,
    confidence_level VARCHAR(50), -- high, medium, low
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_risk_assessments_risk ON risk.assessments(risk_id, assessment_date DESC);
CREATE INDEX idx_risk_assessments_org ON risk.assessments(organization_id);
CREATE INDEX idx_risk_assessments_level ON risk.assessments(risk_level);
CREATE INDEX idx_risk_assessments_date ON risk.assessments(assessment_date DESC);

CREATE TRIGGER update_risk_assessments_updated_at BEFORE UPDATE ON risk.assessments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE risk.assessments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Risk assessments visible to org members" ON risk.assessments FOR SELECT
    USING (auth.is_org_member(organization_id));

CREATE POLICY "Risk assessments manageable by org admins" ON risk.assessments FOR ALL
    USING (auth.is_org_admin(organization_id));

COMMENT ON TABLE risk.assessments IS 'Risk assessments per ISO 22301:2019 Clause 8.2.3';

-- Table: risk.treatments
CREATE TABLE risk.treatments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    risk_id UUID NOT NULL REFERENCES risk.risks(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Treatment identity
    treatment_code VARCHAR(100),
    treatment_title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,

    -- Treatment strategy
    strategy VARCHAR(100) NOT NULL, -- mitigate_likelihood, mitigate_consequence, transfer, accept, avoid
    rationale TEXT,

    -- Implementation
    implementation_plan TEXT,
    implementation_steps JSONB DEFAULT '[]'::jsonb, -- {step_number, description, assigned_to, due_date, status}

    -- Assignment
    owner_id UUID REFERENCES auth.users(id) NOT NULL,
    assigned_to_id UUID REFERENCES auth.users(id),
    assigned_to_team_id UUID REFERENCES public.teams(id),

    -- Timeline
    status VARCHAR(50) DEFAULT 'planned', -- planned, in_progress, implemented, verified, ineffective, cancelled
    priority VARCHAR(50) NOT NULL, -- critical, high, medium, low

    planned_start_date DATE,
    planned_completion_date DATE NOT NULL,
    actual_start_date DATE,
    actual_completion_date DATE,

    -- Resources
    estimated_cost DECIMAL(15,2),
    actual_cost DECIMAL(15,2),
    budget_approved BOOLEAN DEFAULT FALSE,
    required_resources TEXT,

    -- Controls to implement
    controls_to_implement JSONB DEFAULT '[]'::jsonb, -- UUIDs of risk.controls

    -- Effectiveness
    expected_risk_reduction TEXT,
    expected_residual_risk_level VARCHAR(50),

    actual_risk_reduction TEXT,
    effectiveness_verified BOOLEAN DEFAULT FALSE,
    verified_by UUID REFERENCES auth.users(id),
    verified_at TIMESTAMPTZ,

    -- Dependencies
    depends_on JSONB DEFAULT '[]'::jsonb, -- UUIDs of other treatments
    blocks JSONB DEFAULT '[]'::jsonb, -- UUIDs of treatments waiting for this

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_risk_treatments_risk ON risk.treatments(risk_id);
CREATE INDEX idx_risk_treatments_org ON risk.treatments(organization_id);
CREATE INDEX idx_risk_treatments_owner ON risk.treatments(owner_id, status);
CREATE INDEX idx_risk_treatments_status ON risk.treatments(status);
CREATE INDEX idx_risk_treatments_overdue ON risk.treatments(planned_completion_date) WHERE status NOT IN ('implemented', 'verified', 'cancelled') AND planned_completion_date < CURRENT_DATE;

CREATE TRIGGER update_risk_treatments_updated_at BEFORE UPDATE ON risk.treatments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE risk.treatments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Risk treatments visible to org members" ON risk.treatments FOR SELECT
    USING (auth.is_org_member(organization_id));

CREATE POLICY "Risk treatments manageable by org admins" ON risk.treatments FOR ALL
    USING (auth.is_org_admin(organization_id));

COMMENT ON TABLE risk.treatments IS 'Risk treatment plans per ISO 22301 Clause 8.2.3';

-- Table: risk.templates
CREATE TABLE risk.templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Template identity
    template_code VARCHAR(100) NOT NULL,
    template_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Template type
    template_type VARCHAR(100) NOT NULL, -- risk, control, assessment, treatment
    category VARCHAR(100), -- cyber, physical, operational, strategic, compliance, financial

    -- Template content (for risks)
    risk_name_template VARCHAR(255),
    risk_description_template TEXT,
    threat_sources_template JSONB DEFAULT '[]'::jsonb,
    vulnerabilities_template JSONB DEFAULT '[]'::jsonb,

    -- Template content (for controls)
    control_name_template VARCHAR(255),
    control_description_template TEXT,
    control_type VARCHAR(100), -- preventive, detective, corrective
    implementation_guidance TEXT,

    -- Suggested ratings
    suggested_likelihood INT,
    suggested_consequence INT,
    suggested_priority VARCHAR(50),

    -- Related standards
    iso_22301_clauses JSONB DEFAULT '[]'::jsonb,
    other_frameworks JSONB DEFAULT '[]'::jsonb, -- NIST, CIS, etc.

    -- Usage
    is_system_template BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INT DEFAULT 0,
    last_used_at TIMESTAMPTZ,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, template_code)
);

CREATE INDEX idx_risk_templates_org ON risk.templates(organization_id);
CREATE INDEX idx_risk_templates_type ON risk.templates(template_type);
CREATE INDEX idx_risk_templates_category ON risk.templates(category);
CREATE INDEX idx_risk_templates_active ON risk.templates(is_active) WHERE is_active = TRUE;

CREATE TRIGGER update_risk_templates_updated_at BEFORE UPDATE ON risk.templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE risk.templates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Risk templates visible to org members" ON risk.templates FOR SELECT
    USING (organization_id IS NULL OR auth.is_org_member(organization_id));

CREATE POLICY "Risk templates manageable by org admins" ON risk.templates FOR ALL
    USING (auth.is_org_admin(organization_id));

COMMENT ON TABLE risk.templates IS 'Risk and control templates for standardization';

-- Table: risk.workflow_logs
CREATE TABLE risk.workflow_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    risk_id UUID REFERENCES risk.risks(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Workflow event
    event_type VARCHAR(100) NOT NULL, -- created, assessment_completed, treatment_planned, status_changed, escalated, review_completed
    event_description TEXT,

    -- Context
    previous_status VARCHAR(50),
    new_status VARCHAR(50),

    previous_risk_level VARCHAR(50),
    new_risk_level VARCHAR(50),

    previous_data JSONB,
    new_data JSONB,

    -- Actor
    actor_id UUID REFERENCES auth.users(id),
    actor_name VARCHAR(255),
    actor_role VARCHAR(100),

    -- Related entities
    related_assessment_id UUID REFERENCES risk.assessments(id),
    related_treatment_id UUID REFERENCES risk.treatments(id),
    related_control_id UUID REFERENCES risk.controls(id),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_risk_workflow_logs_risk ON risk.workflow_logs(risk_id, created_at DESC);
CREATE INDEX idx_risk_workflow_logs_org ON risk.workflow_logs(organization_id);
CREATE INDEX idx_risk_workflow_logs_event ON risk.workflow_logs(event_type);
CREATE INDEX idx_risk_workflow_logs_actor ON risk.workflow_logs(actor_id);

ALTER TABLE risk.workflow_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Risk workflow logs visible to org members" ON risk.workflow_logs FOR SELECT
    USING (auth.is_org_member(organization_id));

COMMENT ON TABLE risk.workflow_logs IS 'Audit trail for risk management workflow events';

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 011 completed: BIA/Risk extensions (8 tables)';
    RAISE NOTICE '   BIA Schema:';
    RAISE NOTICE '   - impact_assessments: Time-based impact analysis';
    RAISE NOTICE '   - dependencies: Process dependencies (people, tech, suppliers, facilities)';
    RAISE NOTICE '   - workflow_logs: BIA workflow audit trail';
    RAISE NOTICE '   - exports: BIA report exports';
    RAISE NOTICE '   Risk Schema:';
    RAISE NOTICE '   - assessments: Risk assessments with likelihood/consequence';
    RAISE NOTICE '   - treatments: Risk treatment plans';
    RAISE NOTICE '   - templates: Risk and control templates';
    RAISE NOTICE '   - workflow_logs: Risk workflow audit trail';
END
$$;
