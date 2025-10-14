-- ============================================
-- BCM Platform - Unified Database
-- Migration 012: Governance & Compliance Extensions
-- ============================================
-- Extends migration 007 (governance.policies, governance.roles, governance.objectives)
-- ISO 22301:2019 Clauses:
--   5 (Leadership)
--   6 (Planning)
--   7 (Support)
--   4.4 (BCMS and its processes)
-- Schemas: governance, bcm
-- ============================================

-- Table: governance.policy_versions
CREATE TABLE governance.policy_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_id UUID NOT NULL REFERENCES governance.policies(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Version details
    version_number VARCHAR(50) NOT NULL,
    version_date DATE NOT NULL,

    -- Content snapshot
    policy_name VARCHAR(255) NOT NULL,
    policy_content TEXT NOT NULL,

    -- Approval
    approved_by UUID REFERENCES auth.users(id),
    approved_at TIMESTAMPTZ,
    approval_notes TEXT,

    -- Change tracking
    change_summary TEXT,
    changed_sections JSONB DEFAULT '[]'::jsonb,
    change_reason VARCHAR(100), -- scheduled_review, regulatory_change, incident, improvement, correction

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, approved, superseded, archived
    effective_date DATE,
    expiry_date DATE,

    -- Files
    file_path VARCHAR(500),
    file_hash VARCHAR(128), -- SHA-256 for integrity

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_policy_versions_policy ON governance.policy_versions(policy_id, version_date DESC);
CREATE INDEX idx_policy_versions_org ON governance.policy_versions(organization_id);
CREATE INDEX idx_policy_versions_status ON governance.policy_versions(status);

ALTER TABLE governance.policy_versions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Policy versions visible to org members" ON governance.policy_versions FOR SELECT
    USING (auth.is_org_member(organization_id));

COMMENT ON TABLE governance.policy_versions IS 'Policy version history for audit trail';

-- Table: bcm.resources
CREATE TABLE bcm.resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Resource identity
    resource_code VARCHAR(100) NOT NULL,
    resource_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- ISO 22301 Clause 7.1 (Resources)
    resource_type VARCHAR(100) NOT NULL, -- financial, people, equipment, facility, technology, knowledge, suppliers, partners
    resource_category VARCHAR(100), -- critical, important, standard, backup

    -- For People resources
    role_title VARCHAR(255),
    required_skills JSONB DEFAULT '[]'::jsonb,
    current_staff_count INT,
    required_staff_count INT,
    training_required TEXT,

    -- For Equipment/Technology resources
    equipment_type VARCHAR(100),
    quantity_available INT,
    quantity_required INT,
    location VARCHAR(255),
    maintenance_schedule TEXT,
    replacement_cost DECIMAL(15,2),

    -- For Facility resources
    facility_name VARCHAR(255),
    facility_type VARCHAR(100), -- office, datacenter, warehouse, alternate_site
    capacity VARCHAR(100),
    access_requirements TEXT,

    -- For Financial resources
    annual_budget DECIMAL(15,2),
    allocated_budget DECIMAL(15,2),
    spent_budget DECIMAL(15,2),

    -- Availability
    availability_status VARCHAR(50) DEFAULT 'available', -- available, in_use, unavailable, maintenance
    is_shared_resource BOOLEAN DEFAULT FALSE,
    shared_with JSONB DEFAULT '[]'::jsonb, -- Which processes/teams share this

    -- Owner and responsibility
    owner_id UUID REFERENCES auth.users(id),
    custodian_id UUID REFERENCES auth.users(id),
    responsible_team_id UUID REFERENCES public.teams(id),

    -- Allocation
    allocated_to_processes JSONB DEFAULT '[]'::jsonb, -- UUIDs of bia.processes
    allocated_to_teams JSONB DEFAULT '[]'::jsonb, -- UUIDs of teams

    -- Procurement
    procurement_status VARCHAR(50), -- approved, pending, procured, delivered
    vendor_name VARCHAR(255),
    vendor_contact JSONB,
    procurement_lead_time_days INT,

    -- Criticality for BCM
    is_critical_resource BOOLEAN DEFAULT FALSE,
    single_point_of_failure BOOLEAN DEFAULT FALSE,
    backup_available BOOLEAN DEFAULT FALSE,
    backup_resource_id UUID REFERENCES bcm.resources(id),

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
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, resource_code)
);

CREATE INDEX idx_bcm_resources_org ON bcm.resources(organization_id);
CREATE INDEX idx_bcm_resources_code ON bcm.resources(resource_code);
CREATE INDEX idx_bcm_resources_type ON bcm.resources(resource_type);
CREATE INDEX idx_bcm_resources_critical ON bcm.resources(is_critical_resource) WHERE is_critical_resource = TRUE;
CREATE INDEX idx_bcm_resources_spof ON bcm.resources(single_point_of_failure) WHERE single_point_of_failure = TRUE;

CREATE TRIGGER update_bcm_resources_updated_at BEFORE UPDATE ON bcm.resources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE bcm.resources ENABLE ROW LEVEL SECURITY;

CREATE POLICY "BCM resources visible to org members" ON bcm.resources FOR SELECT
    USING (auth.is_org_member(organization_id));

CREATE POLICY "BCM resources manageable by org admins" ON bcm.resources FOR ALL
    USING (auth.is_org_admin(organization_id));

COMMENT ON TABLE bcm.resources IS 'BCM resources per ISO 22301:2019 Clause 7.1';

-- Table: bcm.competence_records
CREATE TABLE bcm.competence_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Person
    user_id UUID NOT NULL REFERENCES auth.users(id),
    user_name VARCHAR(255),
    user_role VARCHAR(100),

    -- ISO 22301 Clause 7.2 (Competence)
    competency_area VARCHAR(100) NOT NULL, -- bcm_planning, bia, risk_assessment, incident_response, crisis_management, exercise_facilitation, audit

    -- Competency level
    competency_level VARCHAR(50) NOT NULL, -- novice, intermediate, advanced, expert
    assessment_method VARCHAR(100), -- training, certification, experience, exercise_performance, manager_assessment

    -- Evidence
    evidence_type VARCHAR(100), -- certification, training_completion, work_experience, exercise_participation, assessment
    evidence_description TEXT,
    evidence_file_path VARCHAR(500),

    -- Certification details
    certification_name VARCHAR(255),
    certification_body VARCHAR(255),
    certification_number VARCHAR(100),
    certification_date DATE,
    certification_expiry_date DATE,

    -- Training details
    training_course_name VARCHAR(255),
    training_provider VARCHAR(255),
    training_completion_date DATE,
    training_hours DECIMAL(10,2),

    -- Experience details
    years_of_experience DECIMAL(5,2),
    relevant_roles JSONB DEFAULT '[]'::jsonb,

    -- Status
    status VARCHAR(50) DEFAULT 'current', -- current, expiring_soon, expired, pending_renewal
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by UUID REFERENCES auth.users(id),
    verified_at TIMESTAMPTZ,

    -- Renewal
    renewal_required BOOLEAN DEFAULT FALSE,
    renewal_due_date DATE,
    renewal_reminder_sent BOOLEAN DEFAULT FALSE,

    -- Metadata
    notes TEXT,
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_competence_records_org ON bcm.competence_records(organization_id);
CREATE INDEX idx_competence_records_user ON bcm.competence_records(user_id);
CREATE INDEX idx_competence_records_area ON bcm.competence_records(competency_area);
CREATE INDEX idx_competence_records_status ON bcm.competence_records(status);
CREATE INDEX idx_competence_records_expiring ON bcm.competence_records(certification_expiry_date) WHERE certification_expiry_date IS NOT NULL AND status = 'current';

CREATE TRIGGER update_competence_records_updated_at BEFORE UPDATE ON bcm.competence_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE bcm.competence_records ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Competence records visible to org members" ON bcm.competence_records FOR SELECT
    USING (auth.is_org_member(organization_id));

CREATE POLICY "Users see their own competence records" ON bcm.competence_records FOR SELECT
    USING (user_id = auth.uid());

COMMENT ON TABLE bcm.competence_records IS 'Competency evidence per ISO 22301:2019 Clause 7.2';

-- Table: bcm.communication_plans
CREATE TABLE bcm.communication_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Plan identity
    plan_code VARCHAR(100) NOT NULL,
    plan_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- ISO 22301 Clause 7.4 (Communication)
    plan_type VARCHAR(100) NOT NULL, -- stakeholder_engagement, incident_communication, awareness, training, reporting

    -- Stakeholder groups
    stakeholder_groups JSONB NOT NULL, -- Array of {group_name, type, priority, contact_method}

    -- Communication matrix
    what_to_communicate JSONB DEFAULT '[]'::jsonb, -- Topics/information to communicate
    when_to_communicate JSONB DEFAULT '[]'::jsonb, -- Timing/triggers
    how_to_communicate JSONB DEFAULT '[]'::jsonb, -- Channels/methods
    who_communicates JSONB DEFAULT '[]'::jsonb, -- Roles responsible

    -- Channels
    primary_channels JSONB DEFAULT '[]'::jsonb, -- email, sms, phone, teams, slack, website, social_media
    backup_channels JSONB DEFAULT '[]'::jsonb,

    -- Templates
    message_templates JSONB DEFAULT '[]'::jsonb, -- {template_name, audience, content}

    -- Approval requirements
    requires_approval BOOLEAN DEFAULT FALSE,
    approval_authority VARCHAR(100),
    approval_workflow JSONB,

    -- Frequency
    communication_frequency VARCHAR(50), -- as_needed, daily, weekly, monthly, quarterly, annual
    scheduled_communications JSONB DEFAULT '[]'::jsonb,

    -- Effectiveness
    effectiveness_measures JSONB DEFAULT '[]'::jsonb, -- How to measure success
    last_effectiveness_review_date DATE,
    effectiveness_rating VARCHAR(50), -- highly_effective, effective, needs_improvement, ineffective

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, approved, active, under_review, archived
    approved_by UUID REFERENCES auth.users(id),
    approved_at TIMESTAMPTZ,

    is_active BOOLEAN DEFAULT TRUE,
    activation_triggers JSONB DEFAULT '[]'::jsonb, -- When this plan activates

    -- Maintenance
    owner_id UUID REFERENCES auth.users(id),
    last_reviewed_date DATE,
    next_review_date DATE,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, plan_code)
);

CREATE INDEX idx_comm_plans_org ON bcm.communication_plans(organization_id);
CREATE INDEX idx_comm_plans_code ON bcm.communication_plans(plan_code);
CREATE INDEX idx_comm_plans_type ON bcm.communication_plans(plan_type);
CREATE INDEX idx_comm_plans_status ON bcm.communication_plans(status);
CREATE INDEX idx_comm_plans_active ON bcm.communication_plans(is_active) WHERE is_active = TRUE;

CREATE TRIGGER update_comm_plans_updated_at BEFORE UPDATE ON bcm.communication_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE bcm.communication_plans ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Communication plans visible to org members" ON bcm.communication_plans FOR SELECT
    USING (auth.is_org_member(organization_id));

CREATE POLICY "Communication plans manageable by org admins" ON bcm.communication_plans FOR ALL
    USING (auth.is_org_admin(organization_id));

COMMENT ON TABLE bcm.communication_plans IS 'Communication plans per ISO 22301:2019 Clause 7.4';

-- =========================
-- COMPLIANCE SCHEMA
-- =========================

CREATE SCHEMA IF NOT EXISTS compliance;
COMMENT ON SCHEMA compliance IS 'Compliance management and tracking';

-- Table: compliance.requirements
CREATE TABLE compliance.requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Requirement identity
    requirement_code VARCHAR(100) NOT NULL,
    requirement_title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,

    -- Source
    framework VARCHAR(100) NOT NULL, -- ISO_22301, ISO_27001, GDPR, SOC2, HIPAA, PCI_DSS, custom
    framework_version VARCHAR(50),
    clause_reference VARCHAR(50), -- e.g., "8.2.2" for ISO 22301

    -- Classification
    requirement_type VARCHAR(100), -- mandatory, recommended, optional, best_practice
    category VARCHAR(100), -- governance, risk, operations, technical, documentation

    -- Applicability
    applies_to VARCHAR(100), -- entire_organization, specific_processes, specific_systems
    applicable_processes JSONB DEFAULT '[]'::jsonb, -- UUIDs of bia.processes
    applicable_systems JSONB DEFAULT '[]'::jsonb,

    is_applicable BOOLEAN DEFAULT TRUE,
    applicability_rationale TEXT,

    -- Compliance status
    compliance_status VARCHAR(50) NOT NULL DEFAULT 'not_assessed', -- compliant, partially_compliant, non_compliant, not_applicable, not_assessed
    compliance_percentage DECIMAL(5,2),

    -- Evidence
    evidence_required TEXT,
    evidence_description TEXT,

    -- Implementation
    implementation_guidance TEXT,
    control_objectives TEXT,

    -- Ownership
    owner_id UUID REFERENCES auth.users(id),
    responsible_team_id UUID REFERENCES public.teams(id),

    -- Related entities
    related_policies JSONB DEFAULT '[]'::jsonb, -- UUIDs of governance.policies
    related_controls JSONB DEFAULT '[]'::jsonb, -- UUIDs of risk.controls
    related_procedures JSONB DEFAULT '[]'::jsonb,

    -- Assessment
    last_assessment_date DATE,
    next_assessment_date DATE,
    assessment_frequency_months INT DEFAULT 12,

    -- Priority
    priority VARCHAR(50), -- critical, high, medium, low
    regulatory_deadline DATE,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Full-text search
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english',
            coalesce(requirement_code,'') || ' ' ||
            coalesce(requirement_title,'') || ' ' ||
            coalesce(description,'') || ' ' ||
            coalesce(framework,'')
        )
    ) STORED,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, requirement_code)
);

CREATE INDEX idx_compliance_requirements_org ON compliance.requirements(organization_id);
CREATE INDEX idx_compliance_requirements_code ON compliance.requirements(requirement_code);
CREATE INDEX idx_compliance_requirements_framework ON compliance.requirements(framework);
CREATE INDEX idx_compliance_requirements_status ON compliance.requirements(compliance_status);
CREATE INDEX idx_compliance_requirements_search ON compliance.requirements USING GIN(search_vector);
CREATE INDEX idx_compliance_requirements_non_compliant ON compliance.requirements(compliance_status) WHERE compliance_status IN ('non_compliant', 'partially_compliant');

CREATE TRIGGER update_compliance_requirements_updated_at BEFORE UPDATE ON compliance.requirements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE compliance.requirements ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Compliance requirements visible to org members" ON compliance.requirements FOR SELECT
    USING (auth.is_org_member(organization_id));

CREATE POLICY "Compliance requirements manageable by org admins" ON compliance.requirements FOR ALL
    USING (auth.is_org_admin(organization_id));

COMMENT ON TABLE compliance.requirements IS 'Compliance requirements from various frameworks';

-- Table: compliance.evidence
CREATE TABLE compliance.evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID NOT NULL REFERENCES compliance.requirements(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Evidence identity
    evidence_code VARCHAR(100),
    evidence_title VARCHAR(255) NOT NULL,
    description TEXT,

    -- Evidence type
    evidence_type VARCHAR(100) NOT NULL, -- document, screenshot, log_export, report, certificate, attestation, interview_notes, observation
    evidence_source VARCHAR(100), -- manual_upload, automated_collection, system_export, audit

    -- File details
    file_name VARCHAR(255),
    file_path VARCHAR(500),
    file_type VARCHAR(50),
    file_size_bytes BIGINT,
    file_hash VARCHAR(128), -- SHA-256

    -- Content
    evidence_content TEXT, -- For text-based evidence
    evidence_url VARCHAR(500), -- For external evidence

    -- Collection
    collected_date DATE NOT NULL,
    collection_method VARCHAR(100), -- manual, automated, screenshot, export
    collected_by UUID REFERENCES auth.users(id),

    -- Validity
    valid_from DATE NOT NULL,
    valid_until DATE,
    is_current BOOLEAN DEFAULT TRUE,

    -- Verification
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by UUID REFERENCES auth.users(id),
    verified_at TIMESTAMPTZ,
    verification_notes TEXT,

    -- Retention
    retention_period_years INT,
    disposal_date DATE,

    -- Related entities
    related_audit_id UUID, -- UUID of validation.audit_plans
    related_assessment_id UUID, -- UUID of compliance.assessments

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_compliance_evidence_requirement ON compliance.evidence(requirement_id);
CREATE INDEX idx_compliance_evidence_org ON compliance.evidence(organization_id);
CREATE INDEX idx_compliance_evidence_type ON compliance.evidence(evidence_type);
CREATE INDEX idx_compliance_evidence_current ON compliance.evidence(is_current) WHERE is_current = TRUE;
CREATE INDEX idx_compliance_evidence_expiring ON compliance.evidence(valid_until) WHERE is_current = TRUE AND valid_until IS NOT NULL;

CREATE TRIGGER update_compliance_evidence_updated_at BEFORE UPDATE ON compliance.evidence
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE compliance.evidence ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Compliance evidence visible to org members" ON compliance.evidence FOR SELECT
    USING (auth.is_org_member(organization_id));

COMMENT ON TABLE compliance.evidence IS 'Evidence of compliance with requirements';

-- Table: compliance.assessments
CREATE TABLE compliance.assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID NOT NULL REFERENCES compliance.requirements(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Assessment details
    assessment_code VARCHAR(100),
    assessment_date DATE NOT NULL,
    assessment_type VARCHAR(100) NOT NULL, -- self_assessment, internal_audit, external_audit, certification, continuous_monitoring

    -- Assessor
    assessor_id UUID REFERENCES auth.users(id),
    assessor_name VARCHAR(255),
    assessor_role VARCHAR(100),

    -- Findings
    compliance_status VARCHAR(50) NOT NULL, -- compliant, partially_compliant, non_compliant, not_applicable
    compliance_score DECIMAL(5,2), -- 0-100

    findings TEXT,
    strengths TEXT,
    weaknesses TEXT,
    recommendations TEXT,

    -- Evidence reviewed
    evidence_reviewed JSONB DEFAULT '[]'::jsonb, -- UUIDs of compliance.evidence

    -- Gaps identified
    gaps_identified JSONB DEFAULT '[]'::jsonb, -- {gap_description, severity, impact}

    -- Actions required
    corrective_actions_required BOOLEAN DEFAULT FALSE,
    action_items JSONB DEFAULT '[]'::jsonb,

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, in_review, completed, approved
    approved_by UUID REFERENCES auth.users(id),
    approved_at TIMESTAMPTZ,

    -- Next assessment
    next_assessment_date DATE,

    -- Metadata
    notes TEXT,
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_compliance_assessments_requirement ON compliance.assessments(requirement_id, assessment_date DESC);
CREATE INDEX idx_compliance_assessments_org ON compliance.assessments(organization_id);
CREATE INDEX idx_compliance_assessments_status ON compliance.assessments(compliance_status);
CREATE INDEX idx_compliance_assessments_date ON compliance.assessments(assessment_date DESC);

CREATE TRIGGER update_compliance_assessments_updated_at BEFORE UPDATE ON compliance.assessments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE compliance.assessments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Compliance assessments visible to org members" ON compliance.assessments FOR SELECT
    USING (auth.is_org_member(organization_id));

COMMENT ON TABLE compliance.assessments IS 'Compliance assessments for requirements';

-- Table: compliance.gaps
CREATE TABLE compliance.gaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID NOT NULL REFERENCES compliance.requirements(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Gap identity
    gap_code VARCHAR(100),
    gap_title VARCHAR(500) NOT NULL,
    gap_description TEXT NOT NULL,

    -- Source
    identified_by VARCHAR(100), -- self_assessment, audit, incident, exercise, risk_assessment
    identified_date DATE NOT NULL,
    identified_by_user_id UUID REFERENCES auth.users(id),

    related_assessment_id UUID REFERENCES compliance.assessments(id),

    -- Severity
    severity VARCHAR(50) NOT NULL, -- critical, high, medium, low
    priority VARCHAR(50) NOT NULL, -- immediate, urgent, high, medium, low

    -- Impact
    impact_description TEXT,
    potential_consequences TEXT,
    regulatory_risk TEXT,

    -- Remediation
    remediation_plan TEXT,
    remediation_owner_id UUID REFERENCES auth.users(id),
    target_closure_date DATE NOT NULL,
    actual_closure_date DATE,

    -- Status
    status VARCHAR(50) DEFAULT 'open', -- open, action_planned, in_progress, verification_pending, closed, accepted_risk
    resolution_notes TEXT,

    -- Related CAPA
    related_capa_id UUID, -- UUID of validation.capa

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_compliance_gaps_requirement ON compliance.gaps(requirement_id);
CREATE INDEX idx_compliance_gaps_org ON compliance.gaps(organization_id);
CREATE INDEX idx_compliance_gaps_severity ON compliance.gaps(severity);
CREATE INDEX idx_compliance_gaps_status ON compliance.gaps(status);
CREATE INDEX idx_compliance_gaps_open ON compliance.gaps(status) WHERE status NOT IN ('closed', 'accepted_risk');
CREATE INDEX idx_compliance_gaps_overdue ON compliance.gaps(target_closure_date) WHERE status NOT IN ('closed', 'accepted_risk') AND target_closure_date < CURRENT_DATE;

CREATE TRIGGER update_compliance_gaps_updated_at BEFORE UPDATE ON compliance.gaps
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE compliance.gaps ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Compliance gaps visible to org members" ON compliance.gaps FOR SELECT
    USING (auth.is_org_member(organization_id));

COMMENT ON TABLE compliance.gaps IS 'Compliance gaps and remediation tracking';

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 012 completed: Governance & Compliance (9 tables)';
    RAISE NOTICE '   Governance Schema Extensions:';
    RAISE NOTICE '   - policy_versions: Policy version history';
    RAISE NOTICE '   BCM Schema:';
    RAISE NOTICE '   - resources: BCM resources (ISO 22301 Clause 7.1)';
    RAISE NOTICE '   - competence_records: Competency tracking (ISO 22301 Clause 7.2)';
    RAISE NOTICE '   - communication_plans: Communication planning (ISO 22301 Clause 7.4)';
    RAISE NOTICE '   Compliance Schema (NEW):';
    RAISE NOTICE '   - requirements: Compliance requirements from frameworks';
    RAISE NOTICE '   - evidence: Evidence of compliance';
    RAISE NOTICE '   - assessments: Compliance assessments';
    RAISE NOTICE '   - gaps: Compliance gaps and remediation';
END
$$;
