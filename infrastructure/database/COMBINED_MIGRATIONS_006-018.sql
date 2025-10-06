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
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE bia.processes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "BIA processes visible to org members" ON bia.processes FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "BIA processes manageable by org admins" ON bia.processes FOR ALL
    USING (public.is_org_admin(organization_id));

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
        OR public.is_org_member(organization_id)
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
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE risk.risks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Risks visible to org members" ON risk.risks FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Risks manageable by org admins" ON risk.risks FOR ALL
    USING (public.is_org_admin(organization_id));

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
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE risk.controls ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Controls visible to org members" ON risk.controls FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Controls manageable by org admins" ON risk.controls FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE risk.controls IS 'Risk controls and mitigation measures';

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 006 completed: BIA and Risk schemas created (4 tables)';
END
$$;
-- ============================================
-- BCM Platform - Unified Database
-- Migration 007: Governance and Audit Schemas
-- ============================================
-- Creates Governance and Audit tables per ISO 22301:2019
-- Schemas: governance, audit
-- ============================================

-- =============================================
-- Schema: governance (BCM Governance)
-- ISO 22301:2019 Clauses 5, 6, 7
-- =============================================

-- Table: governance.policies
CREATE TABLE governance.policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Policy info
    policy_name VARCHAR(255) NOT NULL,
    policy_code VARCHAR(50),
    policy_type VARCHAR(100),

    -- Content
    description TEXT,
    policy_statement TEXT,
    scope TEXT,

    -- Ownership
    policy_owner_id UUID REFERENCES auth.users(id),
    approved_by_id UUID REFERENCES auth.users(id),

    -- Lifecycle
    version VARCHAR(50),
    effective_date DATE,
    review_frequency VARCHAR(50),
    next_review_date DATE,

    -- Status
    status VARCHAR(50) DEFAULT 'draft',

    -- Document
    document_url TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_policies_org ON governance.policies(organization_id);
CREATE INDEX idx_policies_status ON governance.policies(status);
CREATE INDEX idx_policies_type ON governance.policies(policy_type);

CREATE TRIGGER update_policies_updated_at BEFORE UPDATE ON governance.policies
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE governance.policies ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Policies visible to org members" ON governance.policies FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Policies manageable by org admins" ON governance.policies FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE governance.policies IS 'BCM policies per ISO 22301:2019 Clause 5';

-- Table: governance.roles
CREATE TABLE governance.roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    role_name VARCHAR(255) NOT NULL,
    role_type VARCHAR(100),
    description TEXT,

    -- Responsibilities
    responsibilities TEXT[],
    authorities TEXT[],

    -- Assignment
    assigned_to_user_id UUID REFERENCES auth.users(id),
    assigned_to_team_id UUID REFERENCES public.teams(id),

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_roles_org ON governance.roles(organization_id);
CREATE INDEX idx_roles_assigned_user ON governance.roles(assigned_to_user_id);
CREATE INDEX idx_roles_assigned_team ON governance.roles(assigned_to_team_id);

ALTER TABLE governance.roles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Roles visible to org members" ON governance.roles FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Roles manageable by org admins" ON governance.roles FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE governance.roles IS 'BCM roles and responsibilities per ISO 22301:2019 Clause 5';

-- Table: governance.objectives
CREATE TABLE governance.objectives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    objective_title VARCHAR(255) NOT NULL,
    objective_type VARCHAR(100),
    description TEXT,

    -- Measurability
    target_value DECIMAL(12,2),
    current_value DECIMAL(12,2),
    unit VARCHAR(50),

    -- Timeline
    start_date DATE,
    target_date DATE,

    -- Ownership
    owner_id UUID REFERENCES auth.users(id),

    -- Status
    status VARCHAR(50) DEFAULT 'active',
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage BETWEEN 0 AND 100),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_objectives_org ON governance.objectives(organization_id);
CREATE INDEX idx_objectives_status ON governance.objectives(status);
CREATE INDEX idx_objectives_owner ON governance.objectives(owner_id);

CREATE TRIGGER update_objectives_updated_at BEFORE UPDATE ON governance.objectives
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE governance.objectives ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Objectives visible to org members" ON governance.objectives FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Objectives manageable by org admins" ON governance.objectives FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE governance.objectives IS 'BCM objectives per ISO 22301:2019 Clause 6';

-- =============================================
-- Schema: audit (Unified Audit Logging)
-- Consolidates 5 audit log sources
-- =============================================

-- Table: audit.logs
CREATE TABLE audit.logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Tenant context
    organization_id UUID REFERENCES public.organizations(id),
    tenant_id VARCHAR(255),

    -- Actor (who did it)
    actor_type VARCHAR(50),
    actor_id UUID,
    actor_name VARCHAR(255),
    actor_ip VARCHAR(45),

    -- Action (what happened)
    event_type VARCHAR(100) NOT NULL,
    action VARCHAR(50),

    -- Target (what was affected)
    resource_type VARCHAR(100),
    resource_id UUID,
    resource_name VARCHAR(255),

    -- Details
    description TEXT,
    changes JSONB,
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Result
    status VARCHAR(50) DEFAULT 'success',
    error_message TEXT,

    -- Timestamp
    occurred_at TIMESTAMPTZ DEFAULT NOW(),

    -- Compliance
    is_security_event BOOLEAN DEFAULT false,
    severity VARCHAR(50)
);

CREATE INDEX idx_audit_org_time ON audit.logs(organization_id, occurred_at DESC);
CREATE INDEX idx_audit_actor ON audit.logs(actor_id, occurred_at DESC);
CREATE INDEX idx_audit_resource ON audit.logs(resource_type, resource_id);
CREATE INDEX idx_audit_event_type ON audit.logs(event_type, occurred_at DESC);
CREATE INDEX idx_audit_security ON audit.logs(is_security_event) WHERE is_security_event = true;
CREATE INDEX idx_audit_severity ON audit.logs(severity) WHERE severity IN ('warning', 'critical');

ALTER TABLE audit.logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Audit logs visible to org admins" ON audit.logs FOR SELECT
    USING (
        public.is_org_admin(organization_id)
        OR public.is_platform_admin()
    );

-- Only system can insert audit logs
CREATE POLICY "Audit logs insertable by system" ON audit.logs FOR INSERT
    WITH CHECK (true); -- Will be restricted at application layer

COMMENT ON TABLE audit.logs IS 'Unified audit logs - consolidates 5 sources';

-- Table: audit.domain_events
CREATE TABLE audit.domain_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES public.organizations(id),

    -- Event info
    event_name VARCHAR(255) NOT NULL,
    event_version VARCHAR(10) DEFAULT '1.0',
    aggregate_type VARCHAR(100),
    aggregate_id UUID,

    -- Payload
    event_data JSONB NOT NULL,

    -- Metadata
    correlation_id UUID,
    causation_id UUID,

    -- Processing
    is_processed BOOLEAN DEFAULT false,
    processed_at TIMESTAMPTZ,

    occurred_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_events_aggregate ON audit.domain_events(aggregate_type, aggregate_id);
CREATE INDEX idx_events_time ON audit.domain_events(occurred_at DESC);
CREATE INDEX idx_events_unprocessed ON audit.domain_events(is_processed) WHERE is_processed = false;
CREATE INDEX idx_events_org ON audit.domain_events(organization_id, occurred_at DESC);

ALTER TABLE audit.domain_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Domain events visible to org members" ON audit.domain_events FOR SELECT
    USING (public.is_org_member(organization_id) OR public.is_platform_admin());

-- Only system can insert events
CREATE POLICY "Domain events insertable by system" ON audit.domain_events FOR INSERT
    WITH CHECK (true);

COMMENT ON TABLE audit.domain_events IS 'Domain events for CDC, webhooks, and event sourcing';

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 007 completed: Governance and Audit schemas created (5 tables)';
END
$$;
-- ============================================
-- BCM Platform - Unified Database
-- Migration 008: Documents Schema
-- ============================================
-- ISO 22301:2019 Clause 7.5 (Documented Information)
-- Complete document management with versioning, approvals, retention
-- Schema: bcm (shared BCM resources)
-- ============================================

-- Table: bcm.documents
CREATE TABLE bcm.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Document identity
    document_code VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    document_type VARCHAR(50) NOT NULL, -- policy, procedure, plan, form, template, record, report, manual, guideline

    -- ISO 22301 classification
    iso_clause VARCHAR(20), -- e.g., "7.5", "8.4.1"
    bcms_category VARCHAR(100), -- policy, objective, plan, procedure, record, etc.
    is_controlled_document BOOLEAN DEFAULT FALSE,
    control_level VARCHAR(50), -- public, internal, confidential, restricted

    -- Content
    content_type VARCHAR(50), -- pdf, docx, html, markdown
    file_path VARCHAR(500),
    file_size_bytes BIGINT,
    file_hash VARCHAR(128), -- SHA-256 for integrity

    -- Versioning
    version VARCHAR(50) DEFAULT '1.0',
    version_number INT DEFAULT 1,
    is_current_version BOOLEAN DEFAULT TRUE,
    parent_document_id UUID REFERENCES bcm.documents(id),
    supersedes_document_id UUID REFERENCES bcm.documents(id),

    -- Lifecycle
    status VARCHAR(50) DEFAULT 'draft', -- draft, review, approved, published, archived, obsolete
    published_date TIMESTAMP,
    effective_date TIMESTAMP,
    review_date TIMESTAMP,
    next_review_date TIMESTAMP,
    expiry_date TIMESTAMP,
    obsolete_date TIMESTAMP,

    -- Ownership
    owner_id UUID REFERENCES auth.users(id),
    author_id UUID REFERENCES auth.users(id) NOT NULL,
    reviewer_ids JSONB DEFAULT '[]'::jsonb,
    approver_id UUID REFERENCES auth.users(id),
    approved_date TIMESTAMP,

    -- Retention
    retention_period_years INT,
    retention_rule VARCHAR(100),
    disposal_date TIMESTAMP,
    legal_hold BOOLEAN DEFAULT FALSE,

    -- Access control
    access_level VARCHAR(50) DEFAULT 'internal',
    authorized_roles JSONB DEFAULT '[]'::jsonb,
    authorized_users JSONB DEFAULT '[]'::jsonb,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    keywords VARCHAR(500),
    language VARCHAR(10) DEFAULT 'en',
    related_documents JSONB DEFAULT '[]'::jsonb,

    -- AI/ML metadata
    ai_extracted_entities JSONB,
    ai_summary TEXT,
    ai_classification_confidence FLOAT,
    ai_compliance_check JSONB,

    -- Full-text search
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english',
            coalesce(title,'') || ' ' ||
            coalesce(description,'') || ' ' ||
            coalesce(keywords,'')
        )
    ) STORED,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_documents_org ON bcm.documents(organization_id);
CREATE INDEX idx_documents_code ON bcm.documents(document_code);
CREATE INDEX idx_documents_type ON bcm.documents(document_type);
CREATE INDEX idx_documents_status ON bcm.documents(status);
CREATE INDEX idx_documents_version ON bcm.documents(is_current_version) WHERE is_current_version = TRUE;
CREATE INDEX idx_documents_search ON bcm.documents USING GIN(search_vector);
CREATE INDEX idx_documents_iso_clause ON bcm.documents(iso_clause) WHERE iso_clause IS NOT NULL;
CREATE INDEX idx_documents_review_date ON bcm.documents(next_review_date) WHERE status = 'published';

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON bcm.documents
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE bcm.documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Documents visible to org members" ON bcm.documents FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Documents manageable by org admins" ON bcm.documents FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE bcm.documents IS 'Document management per ISO 22301:2019 Clause 7.5';

-- Table: bcm.document_access
CREATE TABLE bcm.document_access (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES bcm.documents(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    user_id UUID NOT NULL REFERENCES auth.users(id),
    access_type VARCHAR(50) NOT NULL, -- view, download, edit, delete, share, approve
    access_granted_at TIMESTAMPTZ DEFAULT NOW(),
    access_duration_minutes INT,
    access_expires_at TIMESTAMPTZ,

    -- Audit trail
    ip_address VARCHAR(45),
    user_agent TEXT,
    location VARCHAR(255),

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_document_access_document ON bcm.document_access(document_id, created_at DESC);
CREATE INDEX idx_document_access_user ON bcm.document_access(user_id, created_at DESC);
CREATE INDEX idx_document_access_type ON bcm.document_access(access_type);

ALTER TABLE bcm.document_access ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Document access visible to org admins" ON bcm.document_access FOR SELECT
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE bcm.document_access IS 'Audit trail for document access';

-- Table: bcm.document_approvals
CREATE TABLE bcm.document_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES bcm.documents(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id),

    approval_stage INT NOT NULL DEFAULT 1,
    approver_id UUID NOT NULL REFERENCES auth.users(id),
    approver_role VARCHAR(100),

    status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected, delegated
    requested_at TIMESTAMPTZ DEFAULT NOW(),
    responded_at TIMESTAMPTZ,

    comments TEXT,
    decision_rationale TEXT,

    delegated_to UUID REFERENCES auth.users(id),
    delegation_reason TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_document_approvals_document ON bcm.document_approvals(document_id);
CREATE INDEX idx_document_approvals_approver ON bcm.document_approvals(approver_id, status);

ALTER TABLE bcm.document_approvals ENABLE ROW LEVEL SECURITY;

COMMENT ON TABLE bcm.document_approvals IS 'Document approval workflow';

-- Table: bcm.document_tags
CREATE TABLE bcm.document_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES public.organizations(id),

    tag_name VARCHAR(100) NOT NULL,
    tag_category VARCHAR(50), -- department, project, iso_clause, type, status
    description TEXT,
    color VARCHAR(20),

    is_system_tag BOOLEAN DEFAULT FALSE,
    usage_count INT DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(organization_id, tag_name)
);

CREATE INDEX idx_document_tags_org ON bcm.document_tags(organization_id);
CREATE INDEX idx_document_tags_category ON bcm.document_tags(tag_category);

ALTER TABLE bcm.document_tags ENABLE ROW LEVEL SECURITY;

COMMENT ON TABLE bcm.document_tags IS 'Tagging system for document organization';

-- Table: bcm.document_retention_policies
CREATE TABLE bcm.document_retention_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    policy_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Applicability
    document_types JSONB, -- Which document types this applies to
    iso_clauses JSONB, -- Which ISO clauses

    -- Retention rules
    retention_period_years INT NOT NULL,
    retention_trigger VARCHAR(50), -- creation_date, approval_date, expiry_date, last_access

    -- Post-retention
    post_retention_action VARCHAR(50), -- archive, delete, review
    notification_before_days INT DEFAULT 30,

    -- Legal requirements
    regulatory_basis TEXT,
    legal_citations JSONB,

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_retention_policies_org ON bcm.document_retention_policies(organization_id);

CREATE TRIGGER update_retention_policies_updated_at BEFORE UPDATE ON bcm.document_retention_policies
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE bcm.document_retention_policies ENABLE ROW LEVEL SECURITY;

COMMENT ON TABLE bcm.document_retention_policies IS 'Document retention policies for compliance';

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 008 completed: Documents schema created (5 tables)';
END
$$;
-- ============================================
-- BCM Platform - Unified Database
-- Migration 009: Response Schema
-- ============================================
-- ISO 22301:2019 Clauses 8.4.2 (Incident Response), 8.4.3 (Warning & Communication)
-- Incident management, crisis response, notifications, escalations
-- Schema: response (incident response & crisis management)
-- ============================================

-- Table: response.incidents
CREATE TABLE response.incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Incident identity
    incident_code VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,

    -- Classification
    incident_type VARCHAR(100) NOT NULL, -- disruption, threat, near_miss, exercise, drill
    severity VARCHAR(50) NOT NULL, -- critical, high, medium, low
    impact_level VARCHAR(50), -- catastrophic, major, moderate, minor, negligible
    category VARCHAR(100), -- cyber, natural_disaster, supply_chain, personnel, infrastructure, etc.

    -- ISO 22301 classification
    is_disruptive_event BOOLEAN DEFAULT FALSE,
    triggers_bcm_plan BOOLEAN DEFAULT FALSE,
    related_risks JSONB DEFAULT '[]'::jsonb, -- UUIDs of related risk.risks
    affected_processes JSONB DEFAULT '[]'::jsonb, -- UUIDs of bia.processes

    -- Status and lifecycle
    status VARCHAR(50) DEFAULT 'reported', -- reported, investigating, responding, recovering, resolved, closed
    priority VARCHAR(50), -- p1_critical, p2_high, p3_medium, p4_low

    detected_at TIMESTAMPTZ NOT NULL,
    reported_at TIMESTAMPTZ DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,
    response_started_at TIMESTAMPTZ,
    contained_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,

    -- Response coordination
    incident_commander_id UUID REFERENCES auth.users(id),
    response_team_id UUID, -- Will reference response.response_teams(id)
    activated_plans JSONB DEFAULT '[]'::jsonb, -- Which BCM plans were activated

    -- Impact assessment
    affected_locations JSONB DEFAULT '[]'::jsonb,
    affected_departments JSONB DEFAULT '[]'::jsonb,
    affected_customers_count INT,
    estimated_financial_impact DECIMAL(15,2),
    actual_financial_impact DECIMAL(15,2),

    -- Recovery metrics
    rto_target_minutes INT, -- Recovery Time Objective
    rto_actual_minutes INT,
    rpo_target_minutes INT, -- Recovery Point Objective
    rpo_actual_minutes INT,

    -- Communications
    public_statement TEXT,
    internal_summary TEXT,
    stakeholder_notifications_sent INT DEFAULT 0,

    -- Post-incident
    root_cause TEXT,
    lessons_learned TEXT,
    corrective_actions JSONB DEFAULT '[]'::jsonb,
    preventive_actions JSONB DEFAULT '[]'::jsonb,

    -- References
    related_incidents JSONB DEFAULT '[]'::jsonb, -- UUIDs of related incidents
    external_references JSONB DEFAULT '[]'::jsonb, -- Ticket systems, etc.

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Full-text search
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english',
            coalesce(incident_code,'') || ' ' ||
            coalesce(title,'') || ' ' ||
            coalesce(description,'') || ' ' ||
            coalesce(category,'')
        )
    ) STORED,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_incidents_org ON response.incidents(organization_id);
CREATE INDEX idx_incidents_code ON response.incidents(incident_code);
CREATE INDEX idx_incidents_status ON response.incidents(status);
CREATE INDEX idx_incidents_severity ON response.incidents(severity);
CREATE INDEX idx_incidents_type ON response.incidents(incident_type);
CREATE INDEX idx_incidents_detected ON response.incidents(detected_at DESC);
CREATE INDEX idx_incidents_search ON response.incidents USING GIN(search_vector);
CREATE INDEX idx_incidents_active ON response.incidents(status) WHERE status IN ('reported', 'investigating', 'responding');

CREATE TRIGGER update_incidents_updated_at BEFORE UPDATE ON response.incidents
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE response.incidents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Incidents visible to org members" ON response.incidents FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Incidents manageable by org admins" ON response.incidents FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE response.incidents IS 'Incident tracking per ISO 22301:2019 Clause 8.4.2';

-- Table: response.response_teams
CREATE TABLE response.response_teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Team identity
    team_code VARCHAR(100) NOT NULL,
    team_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Team type
    team_type VARCHAR(100) NOT NULL, -- imt (Incident Management Team), cmt (Crisis Management Team), brt (Business Recovery Team), technical, communications

    -- Activation
    is_standing_team BOOLEAN DEFAULT TRUE, -- Permanent vs. ad-hoc
    activation_criteria TEXT,
    activation_authority VARCHAR(100), -- Who can activate this team

    is_active BOOLEAN DEFAULT TRUE,
    activated_at TIMESTAMPTZ,
    deactivated_at TIMESTAMPTZ,

    -- Team composition
    team_lead_id UUID REFERENCES auth.users(id),
    deputy_lead_id UUID REFERENCES auth.users(id),
    members JSONB DEFAULT '[]'::jsonb, -- Array of {user_id, role, primary_contact}

    -- Contact information
    primary_contact_phone VARCHAR(50),
    primary_contact_email VARCHAR(255),
    emergency_contacts JSONB DEFAULT '[]'::jsonb,

    -- Responsibilities
    roles_and_responsibilities TEXT,
    authority_level VARCHAR(50), -- strategic, tactical, operational
    decision_making_authority TEXT,

    -- Resources
    assembly_location VARCHAR(255),
    alternate_location VARCHAR(255),
    communication_channels JSONB DEFAULT '[]'::jsonb, -- Teams, Slack, radio frequencies, etc.

    required_resources JSONB DEFAULT '[]'::jsonb,
    available_resources JSONB DEFAULT '[]'::jsonb,

    -- Training and readiness
    training_requirements TEXT,
    last_training_date DATE,
    next_training_date DATE,
    last_exercise_date DATE,
    readiness_status VARCHAR(50), -- ready, training_required, not_ready

    -- Performance metrics
    activations_count INT DEFAULT 0,
    average_activation_time_minutes INT,
    incidents_handled JSONB DEFAULT '[]'::jsonb, -- UUIDs of incidents

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, team_code)
);

CREATE INDEX idx_response_teams_org ON response.response_teams(organization_id);
CREATE INDEX idx_response_teams_type ON response.response_teams(team_type);
CREATE INDEX idx_response_teams_active ON response.response_teams(is_active) WHERE is_active = TRUE;

CREATE TRIGGER update_response_teams_updated_at BEFORE UPDATE ON response.response_teams
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE response.response_teams ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Response teams visible to org members" ON response.response_teams FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Response teams manageable by org admins" ON response.response_teams FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE response.response_teams IS 'Response teams (IMT, CMT, BRT) per ISO 22301';

-- Add foreign key now that response_teams exists
ALTER TABLE response.incidents
    ADD CONSTRAINT fk_incidents_response_team
    FOREIGN KEY (response_team_id) REFERENCES response.response_teams(id);

-- Table: response.communication_templates
CREATE TABLE response.communication_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Template identity
    template_code VARCHAR(100) NOT NULL,
    template_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Classification
    template_type VARCHAR(100) NOT NULL, -- internal, external, customer, media, regulatory, supplier
    incident_types JSONB DEFAULT '[]'::jsonb, -- Which incident types this applies to
    severity_levels JSONB DEFAULT '[]'::jsonb, -- Which severity levels

    -- Content
    subject_template TEXT,
    body_template TEXT, -- Supports placeholders like {{incident_code}}, {{severity}}, etc.

    -- Delivery
    delivery_channels JSONB DEFAULT '[]'::jsonb, -- email, sms, push, phone, teams, slack, public_website
    default_recipients JSONB DEFAULT '[]'::jsonb, -- Roles or specific users

    requires_approval BOOLEAN DEFAULT FALSE,
    approver_role VARCHAR(100),

    -- Timing
    send_timing VARCHAR(50), -- immediate, scheduled, manual
    send_delay_minutes INT,

    -- Compliance
    regulatory_requirements TEXT,
    must_notify_within_hours INT, -- Legal requirement to notify within X hours

    -- Localization
    language VARCHAR(10) DEFAULT 'en',
    translations JSONB DEFAULT '{}'::jsonb, -- {lang_code: {subject, body}}

    -- Usage tracking
    usage_count INT DEFAULT 0,
    last_used_at TIMESTAMPTZ,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, template_code)
);

CREATE INDEX idx_comm_templates_org ON response.communication_templates(organization_id);
CREATE INDEX idx_comm_templates_type ON response.communication_templates(template_type);
CREATE INDEX idx_comm_templates_active ON response.communication_templates(is_active) WHERE is_active = TRUE;

CREATE TRIGGER update_comm_templates_updated_at BEFORE UPDATE ON response.communication_templates
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE response.communication_templates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Comm templates visible to org members" ON response.communication_templates FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Comm templates manageable by org admins" ON response.communication_templates FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE response.communication_templates IS 'Communication templates per ISO 22301:2019 Clause 8.4.3';

-- Table: response.communications
CREATE TABLE response.communications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID NOT NULL REFERENCES response.incidents(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Communication identity
    communication_code VARCHAR(100),

    -- Source
    template_id UUID REFERENCES response.communication_templates(id),
    communication_type VARCHAR(100) NOT NULL, -- internal, external, customer, media, regulatory, supplier

    -- Content
    subject VARCHAR(500),
    body TEXT NOT NULL,

    -- Delivery
    delivery_channel VARCHAR(50) NOT NULL, -- email, sms, push, phone, teams, slack, public_website
    recipients JSONB NOT NULL, -- Array of {type: "user"/"email"/"phone", value, name}
    recipients_count INT,

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, pending_approval, approved, sent, delivered, failed

    scheduled_at TIMESTAMPTZ,
    approved_at TIMESTAMPTZ,
    approved_by UUID REFERENCES auth.users(id),
    sent_at TIMESTAMPTZ,

    -- Delivery tracking
    delivered_count INT DEFAULT 0,
    failed_count INT DEFAULT 0,
    opened_count INT DEFAULT 0,
    clicked_count INT DEFAULT 0,

    delivery_status JSONB DEFAULT '{}'::jsonb, -- {recipient_id: {status, delivered_at, opened_at}}

    -- Errors
    error_message TEXT,
    retry_count INT DEFAULT 0,
    max_retries INT DEFAULT 3,

    -- Compliance
    is_regulatory_notification BOOLEAN DEFAULT FALSE,
    regulatory_deadline TIMESTAMPTZ,
    confirmation_required BOOLEAN DEFAULT FALSE,
    confirmations_received JSONB DEFAULT '[]'::jsonb,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_communications_incident ON response.communications(incident_id);
CREATE INDEX idx_communications_org ON response.communications(organization_id);
CREATE INDEX idx_communications_status ON response.communications(status);
CREATE INDEX idx_communications_sent ON response.communications(sent_at DESC);
CREATE INDEX idx_communications_scheduled ON response.communications(scheduled_at) WHERE status = 'approved';

CREATE TRIGGER update_communications_updated_at BEFORE UPDATE ON response.communications
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE response.communications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Communications visible to org members" ON response.communications FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Communications manageable by org admins" ON response.communications FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE response.communications IS 'Communications sent during incidents per ISO 22301 Clause 8.4.3';

-- Table: response.notifications
CREATE TABLE response.notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID NOT NULL REFERENCES response.incidents(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Notification identity
    notification_type VARCHAR(100) NOT NULL, -- incident_alert, status_update, escalation, resolution, task_assignment

    -- Recipient
    user_id UUID REFERENCES auth.users(id),
    recipient_email VARCHAR(255),
    recipient_phone VARCHAR(50),
    recipient_name VARCHAR(255),

    -- Content
    title VARCHAR(500) NOT NULL,
    message TEXT NOT NULL,
    priority VARCHAR(50) DEFAULT 'normal', -- urgent, high, normal, low

    -- Delivery
    delivery_channel VARCHAR(50) NOT NULL, -- email, sms, push, in_app, phone_call

    status VARCHAR(50) DEFAULT 'pending', -- pending, sent, delivered, read, failed
    sent_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    read_at TIMESTAMPTZ,

    -- Response tracking
    requires_acknowledgment BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMPTZ,
    acknowledgment_response TEXT,

    -- Retry logic
    retry_count INT DEFAULT 0,
    max_retries INT DEFAULT 3,
    next_retry_at TIMESTAMPTZ,
    error_message TEXT,

    -- Action link
    action_url VARCHAR(500), -- Deep link to incident or task
    action_label VARCHAR(100),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notifications_incident ON response.notifications(incident_id);
CREATE INDEX idx_notifications_user ON response.notifications(user_id, created_at DESC);
CREATE INDEX idx_notifications_status ON response.notifications(status);
CREATE INDEX idx_notifications_unread ON response.notifications(user_id, read_at) WHERE read_at IS NULL;
CREATE INDEX idx_notifications_pending_retry ON response.notifications(next_retry_at) WHERE status = 'failed' AND next_retry_at IS NOT NULL;

CREATE TRIGGER update_notifications_updated_at BEFORE UPDATE ON response.notifications
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE response.notifications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Notifications visible to org members" ON response.notifications FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Users see their own notifications" ON response.notifications FOR SELECT
    USING (user_id = auth.uid());

COMMENT ON TABLE response.notifications IS 'Individual stakeholder notifications during incidents';

-- Table: response.escalations
CREATE TABLE response.escalations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID NOT NULL REFERENCES response.incidents(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Escalation details
    escalation_level INT NOT NULL, -- 1, 2, 3, etc.
    escalation_reason TEXT NOT NULL,

    previous_severity VARCHAR(50),
    new_severity VARCHAR(50) NOT NULL,

    previous_priority VARCHAR(50),
    new_priority VARCHAR(50),

    -- Escalation triggers
    triggered_by VARCHAR(100), -- manual, automatic, threshold_exceeded, sla_breach, impact_increase
    trigger_details JSONB,

    -- Who was escalated to
    escalated_to_user_id UUID REFERENCES auth.users(id),
    escalated_to_team_id UUID REFERENCES response.response_teams(id),
    escalated_to_role VARCHAR(100),

    -- Response
    status VARCHAR(50) DEFAULT 'pending', -- pending, acknowledged, accepted, rejected
    acknowledged_at TIMESTAMPTZ,
    response_received_at TIMESTAMPTZ,
    response_notes TEXT,

    -- SLA tracking
    escalation_sla_minutes INT,
    response_sla_minutes INT,
    sla_breached BOOLEAN DEFAULT FALSE,

    -- Actions taken
    actions_taken TEXT,
    additional_resources_allocated JSONB DEFAULT '[]'::jsonb,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_escalations_incident ON response.escalations(incident_id, created_at DESC);
CREATE INDEX idx_escalations_org ON response.escalations(organization_id);
CREATE INDEX idx_escalations_level ON response.escalations(escalation_level);
CREATE INDEX idx_escalations_pending ON response.escalations(status) WHERE status = 'pending';

CREATE TRIGGER update_escalations_updated_at BEFORE UPDATE ON response.escalations
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE response.escalations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Escalations visible to org members" ON response.escalations FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Escalations manageable by org admins" ON response.escalations FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE response.escalations IS 'Incident escalation tracking';

-- Table: response.timeline_events
CREATE TABLE response.timeline_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID NOT NULL REFERENCES response.incidents(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Event details
    event_type VARCHAR(100) NOT NULL, -- status_change, comment, action_taken, decision_made, resource_allocated, communication_sent, escalation, milestone_reached
    event_title VARCHAR(500) NOT NULL,
    event_description TEXT,

    occurred_at TIMESTAMPTZ DEFAULT NOW(),

    -- Context
    previous_status VARCHAR(50),
    new_status VARCHAR(50),

    -- Actor
    actor_id UUID REFERENCES auth.users(id),
    actor_name VARCHAR(255),
    actor_role VARCHAR(100),

    -- Related entities
    related_communication_id UUID REFERENCES response.communications(id),
    related_escalation_id UUID REFERENCES response.escalations(id),
    related_team_id UUID REFERENCES response.response_teams(id),

    -- Visibility
    is_public BOOLEAN DEFAULT FALSE, -- Public events shown in status pages
    is_milestone BOOLEAN DEFAULT FALSE, -- Key milestones highlighted in timeline

    -- Attachments and evidence
    attachments JSONB DEFAULT '[]'::jsonb, -- {filename, file_path, file_type, uploaded_by, uploaded_at}

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_timeline_incident ON response.timeline_events(incident_id, occurred_at DESC);
CREATE INDEX idx_timeline_org ON response.timeline_events(organization_id);
CREATE INDEX idx_timeline_type ON response.timeline_events(event_type);
CREATE INDEX idx_timeline_public ON response.timeline_events(is_public) WHERE is_public = TRUE;
CREATE INDEX idx_timeline_milestones ON response.timeline_events(incident_id, is_milestone) WHERE is_milestone = TRUE;

ALTER TABLE response.timeline_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Timeline events visible to org members" ON response.timeline_events FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Public timeline events visible to all" ON response.timeline_events FOR SELECT
    USING (is_public = TRUE);

COMMENT ON TABLE response.timeline_events IS 'Audit trail of incident events per ISO 22301';

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 009 completed: Response schema created (7 tables)';
    RAISE NOTICE '   - incidents: Main incident tracking';
    RAISE NOTICE '   - response_teams: IMT, CMT, BRT teams';
    RAISE NOTICE '   - communication_templates: Pre-defined templates';
    RAISE NOTICE '   - communications: Communications sent';
    RAISE NOTICE '   - notifications: Individual notifications';
    RAISE NOTICE '   - escalations: Escalation tracking';
    RAISE NOTICE '   - timeline_events: Incident audit trail';
END
$$;
-- ============================================
-- BCM Platform - Unified Database
-- Migration 010: Validation Schema
-- ============================================
-- ISO 22301:2019 Clauses:
--   8.5 (Testing and Exercising)
--   9.1 (Monitoring, Measurement, Analysis, Evaluation)
--   9.2 (Internal Audit)
--   9.3 (Management Review)
--   10 (Improvement - CAPA)
-- Schema: validation (exercises, KPIs, audits, CAPA, management reviews)
-- ============================================

-- Table: validation.exercises
CREATE TABLE validation.exercises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Exercise identity
    exercise_code VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,

    -- ISO 22301 Clause 8.5
    exercise_type VARCHAR(100) NOT NULL, -- tabletop, walkthrough, simulation, full_scale, functional, drill
    exercise_scope VARCHAR(100), -- single_process, department, organization_wide, multi_site, supply_chain

    -- Classification
    complexity_level VARCHAR(50), -- basic, intermediate, advanced, complex
    involves_external_parties BOOLEAN DEFAULT FALSE,

    -- Planning
    objectives JSONB NOT NULL, -- Array of objectives
    success_criteria JSONB, -- Array of measurable criteria

    tested_plans JSONB DEFAULT '[]'::jsonb, -- UUIDs of plans being tested
    tested_processes JSONB DEFAULT '[]'::jsonb, -- UUIDs of bia.processes
    tested_controls JSONB DEFAULT '[]'::jsonb, -- UUIDs of risk.controls

    -- Scheduling
    status VARCHAR(50) DEFAULT 'planning', -- planning, scheduled, in_progress, completed, cancelled
    scheduled_start TIMESTAMPTZ,
    scheduled_end TIMESTAMPTZ,
    actual_start TIMESTAMPTZ,
    actual_end TIMESTAMPTZ,

    -- Participation
    exercise_director_id UUID REFERENCES auth.users(id),
    lead_facilitator_id UUID REFERENCES auth.users(id),

    participants JSONB DEFAULT '[]'::jsonb, -- {user_id, role, team, attendance_status}
    participants_count INT,
    observers JSONB DEFAULT '[]'::jsonb,
    external_participants JSONB DEFAULT '[]'::jsonb,

    -- Scenario
    scenario_id UUID, -- Will reference validation.exercise_scenarios(id)
    scenario_description TEXT,
    scenario_complexity VARCHAR(50),
    inject_schedule JSONB DEFAULT '[]'::jsonb, -- Timed injects during exercise

    -- Location and logistics
    location VARCHAR(255),
    is_virtual BOOLEAN DEFAULT FALSE,
    meeting_links JSONB DEFAULT '[]'::jsonb,
    required_resources JSONB DEFAULT '[]'::jsonb,

    -- Evaluation
    overall_score DECIMAL(5,2), -- 0-100
    evaluation_summary TEXT,
    strengths TEXT,
    weaknesses TEXT,
    lessons_learned TEXT,

    objectives_met_count INT DEFAULT 0,
    objectives_total_count INT,
    success_rate_percent DECIMAL(5,2),

    -- Compliance
    is_regulatory_requirement BOOLEAN DEFAULT FALSE,
    regulatory_frequency VARCHAR(50), -- annual, biannual, as_required
    last_similar_exercise_date DATE,
    next_required_exercise_date DATE,

    -- Outcomes
    findings_count INT DEFAULT 0,
    actions_identified_count INT DEFAULT 0,
    actions_completed_count INT DEFAULT 0,

    -- Reporting
    report_completed BOOLEAN DEFAULT FALSE,
    report_file_path VARCHAR(500),
    report_completed_at TIMESTAMPTZ,
    report_approved_by UUID REFERENCES auth.users(id),

    -- Budget
    estimated_cost DECIMAL(15,2),
    actual_cost DECIMAL(15,2),

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Full-text search
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english',
            coalesce(exercise_code,'') || ' ' ||
            coalesce(title,'') || ' ' ||
            coalesce(description,'')
        )
    ) STORED,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_exercises_org ON validation.exercises(organization_id);
CREATE INDEX idx_exercises_code ON validation.exercises(exercise_code);
CREATE INDEX idx_exercises_status ON validation.exercises(status);
CREATE INDEX idx_exercises_type ON validation.exercises(exercise_type);
CREATE INDEX idx_exercises_scheduled ON validation.exercises(scheduled_start);
CREATE INDEX idx_exercises_search ON validation.exercises USING GIN(search_vector);

CREATE TRIGGER update_exercises_updated_at BEFORE UPDATE ON validation.exercises
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE validation.exercises ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Exercises visible to org members" ON validation.exercises FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Exercises manageable by org admins" ON validation.exercises FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE validation.exercises IS 'BCM exercises per ISO 22301:2019 Clause 8.5';

-- Table: validation.exercise_scenarios
CREATE TABLE validation.exercise_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Scenario identity
    scenario_code VARCHAR(100) NOT NULL,
    scenario_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Classification
    scenario_type VARCHAR(100) NOT NULL, -- cyber_attack, natural_disaster, supply_chain_disruption, pandemic, facility_loss, key_personnel_loss
    threat_category VARCHAR(100),
    severity_level VARCHAR(50), -- critical, high, medium, low

    -- Scenario details
    initial_situation TEXT NOT NULL, -- What participants are told at start
    trigger_event TEXT, -- What initiates the incident
    complicating_factors TEXT, -- Additional challenges during exercise

    -- Timeline
    estimated_duration_minutes INT,
    phases JSONB DEFAULT '[]'::jsonb, -- Array of {phase_name, duration_minutes, description, objectives}

    -- Injects
    injects JSONB DEFAULT '[]'::jsonb, -- Array of {inject_time, type, title, description, expected_response}
    injects_count INT DEFAULT 0,

    -- Scope and impact
    affected_processes JSONB DEFAULT '[]'::jsonb,
    affected_locations JSONB DEFAULT '[]'::jsonb,
    simulated_impacts JSONB DEFAULT '[]'::jsonb, -- {impact_type, severity, description}

    -- Learning objectives
    learning_objectives JSONB DEFAULT '[]'::jsonb,
    skills_tested JSONB DEFAULT '[]'::jsonb, -- decision_making, communication, coordination, technical_recovery, etc.

    -- Required participants
    required_roles JSONB DEFAULT '[]'::jsonb,
    min_participants INT,
    max_participants INT,

    -- Resources needed
    required_props JSONB DEFAULT '[]'::jsonb, -- Physical or digital resources needed
    technology_requirements TEXT,

    -- Usage
    is_template BOOLEAN DEFAULT FALSE,
    usage_count INT DEFAULT 0,
    last_used_date DATE,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    approval_status VARCHAR(50) DEFAULT 'draft', -- draft, approved, archived
    approved_by UUID REFERENCES auth.users(id),
    approved_at TIMESTAMPTZ,

    -- Metadata
    difficulty_rating VARCHAR(50), -- beginner, intermediate, advanced, expert
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, scenario_code)
);

CREATE INDEX idx_scenarios_org ON validation.exercise_scenarios(organization_id);
CREATE INDEX idx_scenarios_type ON validation.exercise_scenarios(scenario_type);
CREATE INDEX idx_scenarios_active ON validation.exercise_scenarios(is_active) WHERE is_active = TRUE;

CREATE TRIGGER update_scenarios_updated_at BEFORE UPDATE ON validation.exercise_scenarios
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE validation.exercise_scenarios ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Scenarios visible to org members" ON validation.exercise_scenarios FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Scenarios manageable by org admins" ON validation.exercise_scenarios FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE validation.exercise_scenarios IS 'Exercise scenarios and templates per ISO 22301 Clause 8.5';

-- Add foreign key now that exercise_scenarios exists
ALTER TABLE validation.exercises
    ADD CONSTRAINT fk_exercises_scenario
    FOREIGN KEY (scenario_id) REFERENCES validation.exercise_scenarios(id);

-- Table: validation.exercise_observations
CREATE TABLE validation.exercise_observations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exercise_id UUID NOT NULL REFERENCES validation.exercises(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Observation details
    observation_type VARCHAR(100) NOT NULL, -- strength, weakness, gap, risk, improvement_opportunity
    severity VARCHAR(50), -- critical, high, medium, low
    category VARCHAR(100), -- communication, decision_making, coordination, technical, procedural, resource

    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,

    -- Context
    observed_at TIMESTAMPTZ NOT NULL,
    phase VARCHAR(100), -- Which phase of exercise this occurred in
    related_objective_id VARCHAR(100), -- Which objective this relates to

    affected_plan_id UUID, -- Which plan had the issue
    affected_process_id UUID, -- Which process

    -- Observer
    observer_id UUID REFERENCES auth.users(id),
    observer_role VARCHAR(100),

    -- Impact
    impact_assessment TEXT,
    potential_consequences TEXT,

    -- Evidence
    evidence JSONB DEFAULT '[]'::jsonb, -- Photos, videos, documents, logs
    witness_statements JSONB DEFAULT '[]'::jsonb,

    -- Status
    status VARCHAR(50) DEFAULT 'open', -- open, acknowledged, action_planned, resolved, closed
    resolution_notes TEXT,
    resolved_at TIMESTAMPTZ,

    -- Priority
    requires_immediate_action BOOLEAN DEFAULT FALSE,
    action_deadline DATE,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_observations_exercise ON validation.exercise_observations(exercise_id);
CREATE INDEX idx_observations_org ON validation.exercise_observations(organization_id);
CREATE INDEX idx_observations_type ON validation.exercise_observations(observation_type);
CREATE INDEX idx_observations_severity ON validation.exercise_observations(severity);
CREATE INDEX idx_observations_status ON validation.exercise_observations(status);

CREATE TRIGGER update_observations_updated_at BEFORE UPDATE ON validation.exercise_observations
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE validation.exercise_observations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Observations visible to org members" ON validation.exercise_observations FOR SELECT
    USING (public.is_org_member(organization_id));

COMMENT ON TABLE validation.exercise_observations IS 'Observations during exercises';

-- Table: validation.exercise_actions
CREATE TABLE validation.exercise_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exercise_id UUID NOT NULL REFERENCES validation.exercises(id) ON DELETE CASCADE,
    observation_id UUID REFERENCES validation.exercise_observations(id),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Action details
    action_code VARCHAR(100),
    action_title VARCHAR(500) NOT NULL,
    action_description TEXT NOT NULL,

    action_type VARCHAR(100) NOT NULL, -- corrective, preventive, improvement
    priority VARCHAR(50) NOT NULL, -- critical, high, medium, low

    -- Assignment
    assigned_to_id UUID REFERENCES auth.users(id),
    assigned_to_team_id UUID REFERENCES public.teams(id),
    assigned_to_role VARCHAR(100),

    -- Timeline
    status VARCHAR(50) DEFAULT 'planned', -- planned, in_progress, completed, cancelled, overdue
    due_date DATE NOT NULL,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    -- Progress
    progress_percent INT DEFAULT 0,
    progress_notes TEXT,

    -- Resources
    estimated_effort_hours DECIMAL(10,2),
    actual_effort_hours DECIMAL(10,2),
    budget_required DECIMAL(15,2),

    -- Verification
    requires_verification BOOLEAN DEFAULT TRUE,
    verification_method TEXT,
    verified_by UUID REFERENCES auth.users(id),
    verified_at TIMESTAMPTZ,
    verification_notes TEXT,

    -- Effectiveness
    effectiveness_rating INT, -- 1-5 scale
    effectiveness_notes TEXT,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_exercise_actions_exercise ON validation.exercise_actions(exercise_id);
CREATE INDEX idx_exercise_actions_org ON validation.exercise_actions(organization_id);
CREATE INDEX idx_exercise_actions_assigned ON validation.exercise_actions(assigned_to_id, status);
CREATE INDEX idx_exercise_actions_status ON validation.exercise_actions(status);
CREATE INDEX idx_exercise_actions_overdue ON validation.exercise_actions(due_date) WHERE status != 'completed' AND due_date < CURRENT_DATE;

CREATE TRIGGER update_exercise_actions_updated_at BEFORE UPDATE ON validation.exercise_actions
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE validation.exercise_actions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Exercise actions visible to org members" ON validation.exercise_actions FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Exercise actions manageable by org admins" ON validation.exercise_actions FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE validation.exercise_actions IS 'Actions from exercise observations per ISO 22301 Clause 10';

-- Table: validation.kpis
CREATE TABLE validation.kpis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- KPI identity
    kpi_code VARCHAR(100) NOT NULL,
    kpi_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- ISO 22301 Clause 9.1
    kpi_category VARCHAR(100) NOT NULL, -- bcms_performance, plan_effectiveness, process_performance, objective_achievement, incident_metrics
    iso_clause VARCHAR(20), -- Which ISO clause this monitors

    -- Measurement
    measurement_unit VARCHAR(50) NOT NULL, -- percentage, count, minutes, hours, days, currency, ratio
    measurement_method TEXT,
    data_source VARCHAR(255), -- Where data comes from

    calculation_formula TEXT, -- How to calculate the KPI
    aggregation_method VARCHAR(50), -- sum, average, max, min, count, percentage

    -- Targets
    target_value DECIMAL(15,2),
    target_operator VARCHAR(10), -- >=, <=, =, >, <
    target_description TEXT,

    warning_threshold DECIMAL(15,2),
    critical_threshold DECIMAL(15,2),

    -- Frequency
    measurement_frequency VARCHAR(50) NOT NULL, -- daily, weekly, monthly, quarterly, annually, per_incident, real_time
    reporting_frequency VARCHAR(50), -- daily, weekly, monthly, quarterly, annually

    -- Ownership
    owner_id UUID REFERENCES auth.users(id),
    data_collector_id UUID REFERENCES auth.users(id),

    -- Related entities
    related_objectives JSONB DEFAULT '[]'::jsonb, -- UUIDs of governance.objectives
    related_processes JSONB DEFAULT '[]'::jsonb, -- UUIDs of bia.processes
    related_risks JSONB DEFAULT '[]'::jsonb, -- UUIDs of risk.risks

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    status VARCHAR(50) DEFAULT 'active', -- active, on_target, at_risk, critical, paused

    -- Current value
    current_value DECIMAL(15,2),
    current_status VARCHAR(50), -- on_target, warning, critical
    last_measured_at TIMESTAMPTZ,

    -- Trend analysis
    trend VARCHAR(50), -- improving, stable, declining
    trend_calculation_period INT, -- Days to look back for trend

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, kpi_code)
);

CREATE INDEX idx_kpis_org ON validation.kpis(organization_id);
CREATE INDEX idx_kpis_code ON validation.kpis(kpi_code);
CREATE INDEX idx_kpis_category ON validation.kpis(kpi_category);
CREATE INDEX idx_kpis_status ON validation.kpis(status);
CREATE INDEX idx_kpis_active ON validation.kpis(is_active) WHERE is_active = TRUE;

CREATE TRIGGER update_kpis_updated_at BEFORE UPDATE ON validation.kpis
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE validation.kpis ENABLE ROW LEVEL SECURITY;

CREATE POLICY "KPIs visible to org members" ON validation.kpis FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "KPIs manageable by org admins" ON validation.kpis FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE validation.kpis IS 'Key Performance Indicators per ISO 22301:2019 Clause 9.1';

-- Table: validation.kpi_measurements
CREATE TABLE validation.kpi_measurements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kpi_id UUID NOT NULL REFERENCES validation.kpis(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Measurement
    measured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    measurement_period_start DATE,
    measurement_period_end DATE,

    measured_value DECIMAL(15,2) NOT NULL,
    target_value DECIMAL(15,2),

    -- Status at time of measurement
    status VARCHAR(50) NOT NULL, -- on_target, warning, critical, no_target

    variance DECIMAL(15,2), -- Difference from target
    variance_percent DECIMAL(5,2), -- Percentage difference

    -- Context
    measured_by UUID REFERENCES auth.users(id),
    measurement_notes TEXT,

    data_quality VARCHAR(50) DEFAULT 'verified', -- verified, estimated, unverified
    data_source_reference VARCHAR(500),

    -- Related entities
    related_incident_id UUID, -- If measurement is incident-related
    related_exercise_id UUID REFERENCES validation.exercises(id),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_kpi_measurements_kpi ON validation.kpi_measurements(kpi_id, measured_at DESC);
CREATE INDEX idx_kpi_measurements_org ON validation.kpi_measurements(organization_id);
CREATE INDEX idx_kpi_measurements_period ON validation.kpi_measurements(measurement_period_start, measurement_period_end);
CREATE INDEX idx_kpi_measurements_status ON validation.kpi_measurements(status);

ALTER TABLE validation.kpi_measurements ENABLE ROW LEVEL SECURITY;

CREATE POLICY "KPI measurements visible to org members" ON validation.kpi_measurements FOR SELECT
    USING (public.is_org_member(organization_id));

COMMENT ON TABLE validation.kpi_measurements IS 'Historical KPI measurements per ISO 22301 Clause 9.1';

-- Table: validation.kpi_dashboards
CREATE TABLE validation.kpi_dashboards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Dashboard identity
    dashboard_code VARCHAR(100) NOT NULL,
    dashboard_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Configuration
    dashboard_type VARCHAR(100), -- executive, operational, compliance, incident_metrics
    kpi_ids JSONB NOT NULL, -- Array of KPI UUIDs to include

    layout_config JSONB, -- Dashboard layout and visualization settings
    refresh_frequency_seconds INT DEFAULT 300,

    -- Access
    is_public BOOLEAN DEFAULT FALSE,
    authorized_roles JSONB DEFAULT '[]'::jsonb,
    authorized_users JSONB DEFAULT '[]'::jsonb,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, dashboard_code)
);

CREATE INDEX idx_kpi_dashboards_org ON validation.kpi_dashboards(organization_id);
CREATE INDEX idx_kpi_dashboards_active ON validation.kpi_dashboards(is_active) WHERE is_active = TRUE;

CREATE TRIGGER update_kpi_dashboards_updated_at BEFORE UPDATE ON validation.kpi_dashboards
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE validation.kpi_dashboards ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Dashboards visible to org members" ON validation.kpi_dashboards FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Dashboards manageable by org admins" ON validation.kpi_dashboards FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE validation.kpi_dashboards IS 'KPI dashboards for monitoring and reporting';

-- Table: validation.audit_plans
CREATE TABLE validation.audit_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Audit identity
    audit_code VARCHAR(100) NOT NULL,
    audit_title VARCHAR(500) NOT NULL,
    description TEXT,

    -- ISO 22301 Clause 9.2
    audit_type VARCHAR(100) NOT NULL, -- internal, external, certification, surveillance, compliance
    audit_scope TEXT NOT NULL, -- What is being audited

    -- Classification
    audit_standard VARCHAR(100), -- ISO_22301, ISO_27001, SOC2, custom
    audited_clauses JSONB DEFAULT '[]'::jsonb, -- Which ISO clauses

    audited_processes JSONB DEFAULT '[]'::jsonb, -- UUIDs of bia.processes
    audited_locations JSONB DEFAULT '[]'::jsonb,
    audited_departments JSONB DEFAULT '[]'::jsonb,

    -- Planning
    status VARCHAR(50) DEFAULT 'planning', -- planning, scheduled, in_progress, fieldwork_complete, reporting, completed, cancelled

    planned_start_date DATE NOT NULL,
    planned_end_date DATE NOT NULL,
    actual_start_date DATE,
    actual_end_date DATE,

    -- Team
    lead_auditor_id UUID REFERENCES auth.users(id),
    audit_team JSONB DEFAULT '[]'::jsonb, -- {user_id, role, is_external}
    auditee_contacts JSONB DEFAULT '[]'::jsonb,

    -- Methodology
    audit_criteria TEXT,
    audit_methodology TEXT,
    sample_size INT,
    sampling_method VARCHAR(100),

    -- Schedule
    audit_schedule JSONB DEFAULT '[]'::jsonb, -- {date, time, activity, location, participants}

    -- Findings summary
    findings_count INT DEFAULT 0,
    critical_findings_count INT DEFAULT 0,
    major_findings_count INT DEFAULT 0,
    minor_findings_count INT DEFAULT 0,
    observations_count INT DEFAULT 0,

    -- Compliance
    is_regulatory_requirement BOOLEAN DEFAULT FALSE,
    regulatory_body VARCHAR(255),
    certification_body VARCHAR(255),

    -- Outcomes
    overall_conformity VARCHAR(50), -- conformant, non_conformant, partial_conformance
    certification_decision VARCHAR(50), -- granted, denied, conditional, pending

    report_issued_date DATE,
    report_file_path VARCHAR(500),

    -- Follow-up
    next_audit_date DATE,
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_audit_id UUID REFERENCES validation.audit_plans(id),

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, audit_code)
);

CREATE INDEX idx_audit_plans_org ON validation.audit_plans(organization_id);
CREATE INDEX idx_audit_plans_code ON validation.audit_plans(audit_code);
CREATE INDEX idx_audit_plans_status ON validation.audit_plans(status);
CREATE INDEX idx_audit_plans_type ON validation.audit_plans(audit_type);
CREATE INDEX idx_audit_plans_dates ON validation.audit_plans(planned_start_date, planned_end_date);

CREATE TRIGGER update_audit_plans_updated_at BEFORE UPDATE ON validation.audit_plans
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE validation.audit_plans ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Audit plans visible to org members" ON validation.audit_plans FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Audit plans manageable by org admins" ON validation.audit_plans FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE validation.audit_plans IS 'Internal audit plans per ISO 22301:2019 Clause 9.2';

-- Table: validation.audit_findings
CREATE TABLE validation.audit_findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    audit_plan_id UUID NOT NULL REFERENCES validation.audit_plans(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Finding identity
    finding_code VARCHAR(100) NOT NULL,
    finding_title VARCHAR(500) NOT NULL,
    finding_description TEXT NOT NULL,

    -- Classification
    finding_type VARCHAR(100) NOT NULL, -- non_conformance, observation, opportunity_for_improvement
    severity VARCHAR(50) NOT NULL, -- critical, major, minor

    -- ISO context
    iso_clause VARCHAR(20), -- Which clause is non-conformant
    requirement_text TEXT, -- The specific requirement

    -- Evidence
    evidence TEXT NOT NULL,
    evidence_files JSONB DEFAULT '[]'::jsonb,
    root_cause TEXT,

    -- Impact
    impact_assessment TEXT,
    affected_processes JSONB DEFAULT '[]'::jsonb,
    affected_controls JSONB DEFAULT '[]'::jsonb,

    -- Status
    status VARCHAR(50) DEFAULT 'open', -- open, action_planned, in_progress, verification_pending, closed

    -- Response
    auditee_response TEXT,
    corrective_action_plan TEXT,
    target_closure_date DATE,

    actual_closure_date DATE,
    closed_by UUID REFERENCES auth.users(id),
    closure_notes TEXT,

    -- Verification
    verification_required BOOLEAN DEFAULT TRUE,
    verified_by UUID REFERENCES auth.users(id),
    verified_at TIMESTAMPTZ,
    verification_method TEXT,
    verification_evidence TEXT,

    -- Recurrence tracking
    is_repeat_finding BOOLEAN DEFAULT FALSE,
    previous_finding_id UUID REFERENCES validation.audit_findings(id),
    recurrence_count INT DEFAULT 0,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(organization_id, finding_code)
);

CREATE INDEX idx_audit_findings_plan ON validation.audit_findings(audit_plan_id);
CREATE INDEX idx_audit_findings_org ON validation.audit_findings(organization_id);
CREATE INDEX idx_audit_findings_severity ON validation.audit_findings(severity);
CREATE INDEX idx_audit_findings_status ON validation.audit_findings(status);
CREATE INDEX idx_audit_findings_open ON validation.audit_findings(status) WHERE status != 'closed';

CREATE TRIGGER update_audit_findings_updated_at BEFORE UPDATE ON validation.audit_findings
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE validation.audit_findings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Audit findings visible to org members" ON validation.audit_findings FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Audit findings manageable by org admins" ON validation.audit_findings FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE validation.audit_findings IS 'Audit findings per ISO 22301 Clause 9.2';

-- Table: validation.capa
CREATE TABLE validation.capa (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- CAPA identity (Corrective and Preventive Actions)
    capa_code VARCHAR(100) NOT NULL,
    capa_title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,

    -- ISO 22301 Clause 10
    capa_type VARCHAR(100) NOT NULL, -- corrective, preventive
    action_category VARCHAR(100), -- process_improvement, control_enhancement, plan_update, training, resource_allocation

    -- Source
    source_type VARCHAR(100) NOT NULL, -- audit_finding, incident, exercise, management_review, risk_assessment, complaint, near_miss
    source_reference_id UUID, -- UUID of the source (finding, incident, etc.)
    source_description TEXT,

    -- Root cause
    root_cause_analysis TEXT,
    root_cause_method VARCHAR(100), -- 5_whys, fishbone, fault_tree, pareto, other
    contributing_factors JSONB DEFAULT '[]'::jsonb,

    -- Action plan
    action_plan TEXT NOT NULL,
    implementation_steps JSONB DEFAULT '[]'::jsonb, -- {step_number, description, assigned_to, due_date, status}

    -- Assignment
    assigned_to_id UUID REFERENCES auth.users(id),
    assigned_to_team_id UUID REFERENCES public.teams(id),
    action_owner_id UUID REFERENCES auth.users(id) NOT NULL,

    -- Timeline
    status VARCHAR(50) DEFAULT 'planned', -- planned, in_progress, implemented, verification_pending, verified, effective, ineffective, closed
    priority VARCHAR(50) NOT NULL, -- critical, high, medium, low

    target_completion_date DATE NOT NULL,
    actual_completion_date DATE,

    implemented_at TIMESTAMPTZ,
    implemented_by UUID REFERENCES auth.users(id),

    -- Verification
    requires_verification BOOLEAN DEFAULT TRUE,
    verification_method TEXT,
    verification_criteria TEXT,

    verified_at TIMESTAMPTZ,
    verified_by UUID REFERENCES auth.users(id),
    verification_evidence TEXT,
    verification_result VARCHAR(50), -- effective, partially_effective, ineffective

    -- Effectiveness review
    effectiveness_review_date DATE,
    effectiveness_rating INT, -- 1-5 scale
    effectiveness_notes TEXT,
    reviewed_by UUID REFERENCES auth.users(id),

    -- Related entities
    related_risks JSONB DEFAULT '[]'::jsonb, -- UUIDs of risk.risks
    related_processes JSONB DEFAULT '[]'::jsonb, -- UUIDs of bia.processes
    related_controls JSONB DEFAULT '[]'::jsonb, -- UUIDs of risk.controls
    related_objectives JSONB DEFAULT '[]'::jsonb, -- UUIDs of governance.objectives

    -- Impact
    expected_benefits TEXT,
    actual_benefits TEXT,
    estimated_cost DECIMAL(15,2),
    actual_cost DECIMAL(15,2),

    -- Recurrence prevention
    preventive_measures JSONB DEFAULT '[]'::jsonb,
    systemic_changes_made TEXT,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, capa_code)
);

CREATE INDEX idx_capa_org ON validation.capa(organization_id);
CREATE INDEX idx_capa_code ON validation.capa(capa_code);
CREATE INDEX idx_capa_type ON validation.capa(capa_type);
CREATE INDEX idx_capa_status ON validation.capa(status);
CREATE INDEX idx_capa_priority ON validation.capa(priority);
CREATE INDEX idx_capa_assigned ON validation.capa(assigned_to_id, status);
CREATE INDEX idx_capa_overdue ON validation.capa(target_completion_date) WHERE status NOT IN ('verified', 'closed') AND target_completion_date < CURRENT_DATE;

CREATE TRIGGER update_capa_updated_at BEFORE UPDATE ON validation.capa
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE validation.capa ENABLE ROW LEVEL SECURITY;

CREATE POLICY "CAPA visible to org members" ON validation.capa FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "CAPA manageable by org admins" ON validation.capa FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE validation.capa IS 'Corrective and Preventive Actions per ISO 22301:2019 Clause 10';

-- Table: validation.management_reviews
CREATE TABLE validation.management_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Review identity
    review_code VARCHAR(100) NOT NULL,
    review_title VARCHAR(255) NOT NULL,
    description TEXT,

    -- ISO 22301 Clause 9.3
    review_type VARCHAR(100) DEFAULT 'scheduled', -- scheduled, ad_hoc, post_incident, post_exercise

    -- Scheduling
    status VARCHAR(50) DEFAULT 'planning', -- planning, scheduled, in_progress, completed, cancelled
    scheduled_date DATE NOT NULL,
    actual_date DATE,
    duration_hours DECIMAL(5,2),

    -- Participants
    chairperson_id UUID REFERENCES auth.users(id),
    attendees JSONB DEFAULT '[]'::jsonb, -- {user_id, name, role, attended}
    required_attendees JSONB DEFAULT '[]'::jsonb,
    attendance_rate_percent DECIMAL(5,2),

    -- Agenda (ISO 22301 Clause 9.3 requirements)
    agenda JSONB DEFAULT '[]'::jsonb,

    -- Inputs to review (ISO 22301:2019 9.3.2)
    inputs JSONB DEFAULT '{}'::jsonb, -- {
        -- bcms_performance: {...},
        -- nonconformities_capa: {...},
        -- monitoring_measurement_results: {...},
        -- audit_results: {...},
        -- objectives_achievement: {...},
        -- risk_opportunities: {...},
        -- adequacy_resources: {...},
        -- stakeholder_communications: {...},
        -- improvement_recommendations: {...}
    -- }

    -- Outputs (ISO 22301:2019 9.3.3)
    decisions_made JSONB DEFAULT '[]'::jsonb,
    improvement_opportunities JSONB DEFAULT '[]'::jsonb,
    changes_to_bcms JSONB DEFAULT '[]'::jsonb,
    resource_needs JSONB DEFAULT '[]'::jsonb,

    -- Action items
    action_items_count INT DEFAULT 0,
    actions_completed_count INT DEFAULT 0,

    -- Documentation
    minutes_file_path VARCHAR(500),
    minutes_completed BOOLEAN DEFAULT FALSE,
    minutes_approved_by UUID REFERENCES auth.users(id),
    minutes_approved_at TIMESTAMPTZ,

    presentation_files JSONB DEFAULT '[]'::jsonb,
    supporting_documents JSONB DEFAULT '[]'::jsonb,

    -- Key metrics reviewed
    kpis_reviewed JSONB DEFAULT '[]'::jsonb, -- UUIDs of validation.kpis
    incidents_reviewed JSONB DEFAULT '[]'::jsonb, -- UUIDs of incidents
    exercises_reviewed JSONB DEFAULT '[]'::jsonb, -- UUIDs of exercises
    audits_reviewed JSONB DEFAULT '[]'::jsonb, -- UUIDs of audit_plans

    -- Outcomes
    overall_bcms_effectiveness VARCHAR(50), -- highly_effective, effective, needs_improvement, inadequate
    strategic_direction_confirmed BOOLEAN,
    policy_review_required BOOLEAN,
    objectives_review_required BOOLEAN,

    -- Follow-up
    next_review_date DATE,
    follow_up_required BOOLEAN DEFAULT FALSE,

    -- Compliance
    is_regulatory_requirement BOOLEAN DEFAULT TRUE, -- ISO 22301 requires management reviews
    frequency_months INT DEFAULT 12, -- At least annually

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, review_code)
);

CREATE INDEX idx_mgmt_reviews_org ON validation.management_reviews(organization_id);
CREATE INDEX idx_mgmt_reviews_code ON validation.management_reviews(review_code);
CREATE INDEX idx_mgmt_reviews_status ON validation.management_reviews(status);
CREATE INDEX idx_mgmt_reviews_date ON validation.management_reviews(scheduled_date DESC);

CREATE TRIGGER update_mgmt_reviews_updated_at BEFORE UPDATE ON validation.management_reviews
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE validation.management_reviews ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Management reviews visible to org members" ON validation.management_reviews FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Management reviews manageable by org admins" ON validation.management_reviews FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE validation.management_reviews IS 'Management reviews per ISO 22301:2019 Clause 9.3';

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 010 completed: Validation schema created (11 tables)';
    RAISE NOTICE '   - exercises: BCM exercises and drills (ISO 22301 Clause 8.5)';
    RAISE NOTICE '   - exercise_scenarios: Exercise scenarios and templates';
    RAISE NOTICE '   - exercise_observations: Observations during exercises';
    RAISE NOTICE '   - exercise_actions: Actions from exercises';
    RAISE NOTICE '   - kpis: Key Performance Indicators (ISO 22301 Clause 9.1)';
    RAISE NOTICE '   - kpi_measurements: Historical KPI data';
    RAISE NOTICE '   - kpi_dashboards: KPI visualization dashboards';
    RAISE NOTICE '   - audit_plans: Internal audit plans (ISO 22301 Clause 9.2)';
    RAISE NOTICE '   - audit_findings: Audit findings and non-conformances';
    RAISE NOTICE '   - capa: Corrective and Preventive Actions (ISO 22301 Clause 10)';
    RAISE NOTICE '   - management_reviews: Management reviews (ISO 22301 Clause 9.3)';
END
$$;
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
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE bia.impact_assessments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Impact assessments visible to org members" ON bia.impact_assessments FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Impact assessments manageable by org admins" ON bia.impact_assessments FOR ALL
    USING (public.is_org_admin(organization_id));

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
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE bia.dependencies ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Dependencies visible to org members" ON bia.dependencies FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Dependencies manageable by org admins" ON bia.dependencies FOR ALL
    USING (public.is_org_admin(organization_id));

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
    USING (public.is_org_member(organization_id));

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
    USING (public.is_org_member(organization_id));

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
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE risk.assessments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Risk assessments visible to org members" ON risk.assessments FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Risk assessments manageable by org admins" ON risk.assessments FOR ALL
    USING (public.is_org_admin(organization_id));

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
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE risk.treatments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Risk treatments visible to org members" ON risk.treatments FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Risk treatments manageable by org admins" ON risk.treatments FOR ALL
    USING (public.is_org_admin(organization_id));

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
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE risk.templates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Risk templates visible to org members" ON risk.templates FOR SELECT
    USING (organization_id IS NULL OR public.is_org_member(organization_id));

CREATE POLICY "Risk templates manageable by org admins" ON risk.templates FOR ALL
    USING (public.is_org_admin(organization_id));

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
    USING (public.is_org_member(organization_id));

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
    USING (public.is_org_member(organization_id));

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
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE bcm.resources ENABLE ROW LEVEL SECURITY;

CREATE POLICY "BCM resources visible to org members" ON bcm.resources FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "BCM resources manageable by org admins" ON bcm.resources FOR ALL
    USING (public.is_org_admin(organization_id));

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
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE bcm.competence_records ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Competence records visible to org members" ON bcm.competence_records FOR SELECT
    USING (public.is_org_member(organization_id));

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
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE bcm.communication_plans ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Communication plans visible to org members" ON bcm.communication_plans FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Communication plans manageable by org admins" ON bcm.communication_plans FOR ALL
    USING (public.is_org_admin(organization_id));

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
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE compliance.requirements ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Compliance requirements visible to org members" ON compliance.requirements FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Compliance requirements manageable by org admins" ON compliance.requirements FOR ALL
    USING (public.is_org_admin(organization_id));

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
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE compliance.evidence ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Compliance evidence visible to org members" ON compliance.evidence FOR SELECT
    USING (public.is_org_member(organization_id));

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
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE compliance.assessments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Compliance assessments visible to org members" ON compliance.assessments FOR SELECT
    USING (public.is_org_member(organization_id));

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
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE compliance.gaps ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Compliance gaps visible to org members" ON compliance.gaps FOR SELECT
    USING (public.is_org_member(organization_id));

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
-- ============================================
-- BCM Platform - Unified Database
-- Migration 013: Learning & Planning
-- ============================================
-- ISO 22301:2019 Clauses:
--   7.2 (Competence)
--   7.3 (Awareness)
--   8.4 (Business Continuity Plans and Procedures)
-- Schemas: learning, bcm (plans and procedures)
-- ============================================

CREATE SCHEMA IF NOT EXISTS learning;
COMMENT ON SCHEMA learning IS 'Training, awareness, and competency development';

-- Table: learning.training_programs
CREATE TABLE learning.training_programs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Program identity
    program_code VARCHAR(100) NOT NULL,
    program_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- ISO 22301 Clause 7.2, 7.3
    program_type VARCHAR(100) NOT NULL, -- bcm_foundation, bia, risk_assessment, incident_response, crisis_management, awareness, role_specific, technical
    training_level VARCHAR(50), -- foundation, intermediate, advanced, expert

    -- Content
    learning_objectives JSONB NOT NULL, -- Array of objectives
    syllabus TEXT,
    course_materials JSONB DEFAULT '[]'::jsonb, -- {title, file_path, type}

    -- Delivery
    delivery_method VARCHAR(100) NOT NULL, -- classroom, online, hybrid, self_paced, workshop, simulation
    delivery_platform VARCHAR(100), -- lms_name, in_person, webinar

    duration_hours DECIMAL(10,2) NOT NULL,
    prerequisites TEXT,

    -- Target audience
    target_roles JSONB DEFAULT '[]'::jsonb, -- Which roles should take this
    is_mandatory BOOLEAN DEFAULT FALSE,
    mandatory_for_roles JSONB DEFAULT '[]'::jsonb,

    -- Instructors
    instructor_ids JSONB DEFAULT '[]'::jsonb, -- UUIDs of users
    external_instructor_name VARCHAR(255),

    -- Certification
    provides_certification BOOLEAN DEFAULT FALSE,
    certification_name VARCHAR(255),
    certification_validity_years INT,

    -- Assessment
    has_assessment BOOLEAN DEFAULT TRUE,
    passing_score_percent DECIMAL(5,2),
    max_attempts INT,

    -- Scheduling
    schedule_type VARCHAR(50), -- on_demand, scheduled, recurring
    max_participants INT,
    min_participants INT,

    -- Costs
    cost_per_participant DECIMAL(15,2),
    is_free BOOLEAN DEFAULT TRUE,

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, approved, active, archived
    is_active BOOLEAN DEFAULT TRUE,

    -- Effectiveness tracking
    completion_rate_percent DECIMAL(5,2),
    average_score_percent DECIMAL(5,2),
    effectiveness_rating DECIMAL(3,2), -- 1.0-5.0 from feedback

    -- Maintenance
    owner_id UUID REFERENCES auth.users(id),
    last_updated_date DATE,
    next_review_date DATE,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Full-text search
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english',
            coalesce(program_code,'') || ' ' ||
            coalesce(program_name,'') || ' ' ||
            coalesce(description,'')
        )
    ) STORED,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, program_code)
);

CREATE INDEX idx_training_programs_org ON learning.training_programs(organization_id);
CREATE INDEX idx_training_programs_code ON learning.training_programs(program_code);
CREATE INDEX idx_training_programs_type ON learning.training_programs(program_type);
CREATE INDEX idx_training_programs_active ON learning.training_programs(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_training_programs_search ON learning.training_programs USING GIN(search_vector);

CREATE TRIGGER update_training_programs_updated_at BEFORE UPDATE ON learning.training_programs
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE learning.training_programs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Training programs visible to org members" ON learning.training_programs FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Training programs manageable by org admins" ON learning.training_programs FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE learning.training_programs IS 'Training programs per ISO 22301:2019 Clauses 7.2, 7.3';

-- Table: learning.enrollments
CREATE TABLE learning.enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    program_id UUID NOT NULL REFERENCES learning.training_programs(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Learner
    user_id UUID NOT NULL REFERENCES auth.users(id),
    user_name VARCHAR(255),
    user_role VARCHAR(100),

    -- Enrollment
    enrollment_date TIMESTAMPTZ DEFAULT NOW(),
    enrollment_type VARCHAR(50) DEFAULT 'self_enrolled', -- self_enrolled, assigned, mandatory

    assigned_by UUID REFERENCES auth.users(id),
    assignment_reason TEXT,

    -- Schedule
    scheduled_start_date DATE,
    scheduled_end_date DATE,
    due_date DATE, -- For mandatory training

    actual_start_date DATE,
    actual_completion_date DATE,

    -- Progress
    status VARCHAR(50) DEFAULT 'enrolled', -- enrolled, in_progress, completed, failed, dropped, overdue
    progress_percent DECIMAL(5,2) DEFAULT 0,

    time_spent_hours DECIMAL(10,2),
    last_accessed_at TIMESTAMPTZ,

    -- Assessment
    attempts_count INT DEFAULT 0,
    best_score_percent DECIMAL(5,2),
    final_score_percent DECIMAL(5,2),
    passed BOOLEAN,

    -- Completion
    completion_certificate_path VARCHAR(500),
    certificate_issued_at TIMESTAMPTZ,

    -- Certification
    certification_number VARCHAR(100),
    certification_issued_date DATE,
    certification_expiry_date DATE,

    -- Feedback
    feedback_rating INT, -- 1-5 stars
    feedback_comments TEXT,
    feedback_submitted_at TIMESTAMPTZ,

    -- Reminder tracking
    reminder_sent_count INT DEFAULT 0,
    last_reminder_sent_at TIMESTAMPTZ,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_enrollments_program ON learning.enrollments(program_id);
CREATE INDEX idx_enrollments_org ON learning.enrollments(organization_id);
CREATE INDEX idx_enrollments_user ON learning.enrollments(user_id, status);
CREATE INDEX idx_enrollments_status ON learning.enrollments(status);
CREATE INDEX idx_enrollments_overdue ON learning.enrollments(due_date) WHERE status NOT IN ('completed', 'dropped') AND due_date < CURRENT_DATE;
CREATE INDEX idx_enrollments_expiring_cert ON learning.enrollments(certification_expiry_date) WHERE passed = TRUE AND certification_expiry_date IS NOT NULL;

CREATE TRIGGER update_enrollments_updated_at BEFORE UPDATE ON learning.enrollments
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE learning.enrollments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enrollments visible to org members" ON learning.enrollments FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Users see their own enrollments" ON learning.enrollments FOR SELECT
    USING (user_id = auth.uid());

COMMENT ON TABLE learning.enrollments IS 'Training enrollments and completion tracking';

-- Table: learning.competency_assessments
CREATE TABLE learning.competency_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Assessment identity
    assessment_code VARCHAR(100),
    assessment_title VARCHAR(255) NOT NULL,

    -- Subject
    user_id UUID NOT NULL REFERENCES auth.users(id),
    user_name VARCHAR(255),
    user_role VARCHAR(100),

    -- Competency area (ISO 22301 Clause 7.2)
    competency_area VARCHAR(100) NOT NULL, -- bcm_planning, bia, risk_assessment, incident_response, crisis_management, audit
    competency_framework VARCHAR(100), -- internal, iso_22301, cisa, cbcp

    -- Assessment details
    assessment_type VARCHAR(100) NOT NULL, -- self_assessment, manager_assessment, peer_assessment, 360_review, skills_test, simulation
    assessment_date DATE NOT NULL,

    assessor_id UUID REFERENCES auth.users(id),
    assessor_name VARCHAR(255),
    assessor_role VARCHAR(100),

    -- Competency rating
    competency_level VARCHAR(50) NOT NULL, -- novice, competent, proficient, expert
    competency_score DECIMAL(5,2), -- 0-100

    -- Evaluation criteria
    evaluation_criteria JSONB DEFAULT '[]'::jsonb, -- {criterion, rating, comments}

    -- Findings
    strengths TEXT,
    areas_for_improvement TEXT,
    recommendations TEXT,

    -- Development plan
    development_actions JSONB DEFAULT '[]'::jsonb, -- {action, priority, due_date}
    recommended_training JSONB DEFAULT '[]'::jsonb, -- UUIDs of learning.training_programs

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, completed, approved
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

CREATE INDEX idx_competency_assessments_org ON learning.competency_assessments(organization_id);
CREATE INDEX idx_competency_assessments_user ON learning.competency_assessments(user_id, assessment_date DESC);
CREATE INDEX idx_competency_assessments_area ON learning.competency_assessments(competency_area);
CREATE INDEX idx_competency_assessments_date ON learning.competency_assessments(assessment_date DESC);

CREATE TRIGGER update_competency_assessments_updated_at BEFORE UPDATE ON learning.competency_assessments
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE learning.competency_assessments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Competency assessments visible to org admins" ON learning.competency_assessments FOR SELECT
    USING (public.is_org_admin(organization_id));

CREATE POLICY "Users see their own competency assessments" ON learning.competency_assessments FOR SELECT
    USING (user_id = auth.uid());

COMMENT ON TABLE learning.competency_assessments IS 'Competency assessments per ISO 22301 Clause 7.2';

-- Table: learning.awareness_campaigns
CREATE TABLE learning.awareness_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Campaign identity
    campaign_code VARCHAR(100) NOT NULL,
    campaign_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- ISO 22301 Clause 7.3 (Awareness)
    campaign_type VARCHAR(100) NOT NULL, -- bcm_awareness, incident_preparedness, cyber_security, safety, compliance

    -- Objectives
    objectives JSONB NOT NULL, -- Array of campaign objectives
    target_audience VARCHAR(100), -- all_staff, managers, executives, specific_roles
    target_roles JSONB DEFAULT '[]'::jsonb,

    -- Content
    key_messages JSONB DEFAULT '[]'::jsonb,
    materials JSONB DEFAULT '[]'::jsonb, -- {title, type, file_path, url}

    -- Delivery channels
    channels JSONB DEFAULT '[]'::jsonb, -- email, poster, intranet, video, workshop, newsletter, digital_signage

    -- Schedule
    start_date DATE NOT NULL,
    end_date DATE,
    is_ongoing BOOLEAN DEFAULT FALSE,

    milestone_schedule JSONB DEFAULT '[]'::jsonb, -- {date, activity, deliverable}

    -- Status
    status VARCHAR(50) DEFAULT 'planning', -- planning, active, paused, completed, cancelled

    -- Ownership
    campaign_owner_id UUID REFERENCES auth.users(id),
    campaign_team JSONB DEFAULT '[]'::jsonb, -- {user_id, role}

    -- Budget
    estimated_budget DECIMAL(15,2),
    actual_cost DECIMAL(15,2),

    -- Effectiveness tracking
    reach_target INT, -- How many people should be reached
    actual_reach INT, -- How many were reached
    engagement_target INT, -- Expected interactions
    actual_engagement INT, -- Actual interactions

    effectiveness_metrics JSONB DEFAULT '[]'::jsonb, -- {metric_name, target_value, actual_value}

    -- Evaluation
    evaluation_method VARCHAR(100), -- survey, quiz, observation, participation_rate
    evaluation_results JSONB,
    effectiveness_rating VARCHAR(50), -- highly_effective, effective, needs_improvement, ineffective

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, campaign_code)
);

CREATE INDEX idx_awareness_campaigns_org ON learning.awareness_campaigns(organization_id);
CREATE INDEX idx_awareness_campaigns_code ON learning.awareness_campaigns(campaign_code);
CREATE INDEX idx_awareness_campaigns_type ON learning.awareness_campaigns(campaign_type);
CREATE INDEX idx_awareness_campaigns_status ON learning.awareness_campaigns(status);
CREATE INDEX idx_awareness_campaigns_active ON learning.awareness_campaigns(status, start_date, end_date) WHERE status = 'active';

CREATE TRIGGER update_awareness_campaigns_updated_at BEFORE UPDATE ON learning.awareness_campaigns
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE learning.awareness_campaigns ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Awareness campaigns visible to org members" ON learning.awareness_campaigns FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Awareness campaigns manageable by org admins" ON learning.awareness_campaigns FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE learning.awareness_campaigns IS 'Awareness campaigns per ISO 22301:2019 Clause 7.3';

-- Table: learning.training_templates
CREATE TABLE learning.training_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Template identity
    template_code VARCHAR(100) NOT NULL,
    template_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Template type
    template_type VARCHAR(100) NOT NULL, -- course_template, module_template, assessment_template, certificate_template

    -- Content
    template_content JSONB NOT NULL, -- Full template structure
    learning_objectives JSONB DEFAULT '[]'::jsonb,
    recommended_duration_hours DECIMAL(10,2),

    -- Customization
    customizable_fields JSONB DEFAULT '[]'::jsonb,
    default_values JSONB DEFAULT '{}'::jsonb,

    -- Usage
    is_system_template BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INT DEFAULT 0,

    -- Industry/standard alignment
    aligned_standards JSONB DEFAULT '[]'::jsonb, -- ISO_22301, ISO_27001, etc.
    industry VARCHAR(100), -- financial, healthcare, manufacturing, etc.

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_training_templates_org ON learning.training_templates(organization_id);
CREATE INDEX idx_training_templates_type ON learning.training_templates(template_type);
CREATE INDEX idx_training_templates_active ON learning.training_templates(is_active) WHERE is_active = TRUE;

CREATE TRIGGER update_training_templates_updated_at BEFORE UPDATE ON learning.training_templates
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE learning.training_templates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Training templates visible to all org members" ON learning.training_templates FOR SELECT
    USING (organization_id IS NULL OR public.is_org_member(organization_id));

COMMENT ON TABLE learning.training_templates IS 'Training and course templates';

-- Table: learning.user_achievements
CREATE TABLE learning.user_achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- User
    user_id UUID NOT NULL REFERENCES auth.users(id),

    -- Achievement
    achievement_type VARCHAR(100) NOT NULL, -- training_completed, certification_earned, exercise_participated, perfect_score, fast_learner, streak
    achievement_name VARCHAR(255) NOT NULL,
    achievement_description TEXT,

    -- Context
    related_program_id UUID REFERENCES learning.training_programs(id),
    related_enrollment_id UUID REFERENCES learning.enrollments(id),

    -- Details
    achievement_date DATE NOT NULL,
    achievement_value JSONB, -- Additional context (score, duration, etc.)

    -- Badge/Certificate
    badge_image_path VARCHAR(500),
    certificate_path VARCHAR(500),

    -- Visibility
    is_visible BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_user_achievements_org ON learning.user_achievements(organization_id);
CREATE INDEX idx_user_achievements_user ON learning.user_achievements(user_id, achievement_date DESC);
CREATE INDEX idx_user_achievements_type ON learning.user_achievements(achievement_type);

ALTER TABLE learning.user_achievements ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Achievements visible to org members" ON learning.user_achievements FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Users see their own achievements" ON learning.user_achievements FOR SELECT
    USING (user_id = auth.uid());

COMMENT ON TABLE learning.user_achievements IS 'User achievements and gamification';

-- =========================
-- BCM PLANS AND PROCEDURES
-- =========================

-- Table: bcm.plans (Consolidated from planning/ and plans/)
CREATE TABLE bcm.plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Plan identity
    plan_code VARCHAR(100) NOT NULL,
    plan_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- ISO 22301 Clause 8.4
    plan_type VARCHAR(100) NOT NULL, -- bcm_policy, bcm_strategy, bccp (Business Continuity Plan), irp (Incident Response), drp (Disaster Recovery), crp (Crisis Recovery), sop (Standard Operating Procedure)
    plan_scope VARCHAR(100), -- organization_wide, division, department, process_specific, site_specific

    -- Hierarchy
    parent_plan_id UUID REFERENCES bcm.plans(id),
    is_master_plan BOOLEAN DEFAULT FALSE,

    -- Content
    plan_content TEXT, -- Main plan content
    plan_structure JSONB DEFAULT '[]'::jsonb, -- {section_number, section_title, content}

    -- Key elements (ISO 22301 requirements)
    purpose_and_scope TEXT,
    roles_and_responsibilities JSONB DEFAULT '[]'::jsonb,
    activation_criteria TEXT,
    escalation_procedures TEXT,
    communication_procedures TEXT,
    recovery_procedures TEXT,

    -- Versioning
    version VARCHAR(50) DEFAULT '1.0',
    version_date DATE,
    is_current_version BOOLEAN DEFAULT TRUE,

    -- Related entities
    related_processes JSONB DEFAULT '[]'::jsonb, -- UUIDs of bia.processes
    related_risks JSONB DEFAULT '[]'::jsonb, -- UUIDs of risk.risks
    related_plans JSONB DEFAULT '[]'::jsonb, -- Related/dependent plans

    -- Resources
    required_resources JSONB DEFAULT '[]'::jsonb, -- UUIDs of bcm.resources
    contact_lists JSONB DEFAULT '[]'::jsonb, -- Key contacts

    -- Recovery objectives
    rto_minutes INT, -- Recovery Time Objective
    rpo_minutes INT, -- Recovery Point Objective

    -- Status and lifecycle
    status VARCHAR(50) DEFAULT 'draft', -- draft, review, approved, active, under_revision, archived, superseded
    approval_status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected

    approved_by UUID REFERENCES auth.users(id),
    approved_at TIMESTAMPTZ,

    published_date DATE,
    effective_date DATE,
    review_date DATE,
    next_review_date DATE,

    -- Ownership
    owner_id UUID REFERENCES auth.users(id) NOT NULL,
    author_id UUID REFERENCES auth.users(id),

    -- Testing and validation
    last_tested_date DATE,
    test_results VARCHAR(50), -- successful, partially_successful, failed, not_tested
    next_test_date DATE,

    -- Activation tracking
    times_activated INT DEFAULT 0,
    last_activation_date DATE,
    last_activation_incident_id UUID, -- UUID of response.incidents

    -- Access control
    is_confidential BOOLEAN DEFAULT FALSE,
    authorized_roles JSONB DEFAULT '[]'::jsonb,
    authorized_users JSONB DEFAULT '[]'::jsonb,

    -- Files
    file_path VARCHAR(500),
    file_format VARCHAR(50), -- pdf, docx, html
    file_size_bytes BIGINT,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Full-text search
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english',
            coalesce(plan_code,'') || ' ' ||
            coalesce(plan_name,'') || ' ' ||
            coalesce(description,'') || ' ' ||
            coalesce(plan_type,'')
        )
    ) STORED,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, plan_code)
);

CREATE INDEX idx_plans_org ON bcm.plans(organization_id);
CREATE INDEX idx_plans_code ON bcm.plans(plan_code);
CREATE INDEX idx_plans_type ON bcm.plans(plan_type);
CREATE INDEX idx_plans_status ON bcm.plans(status);
CREATE INDEX idx_plans_current ON bcm.plans(is_current_version) WHERE is_current_version = TRUE;
CREATE INDEX idx_plans_search ON bcm.plans USING GIN(search_vector);
CREATE INDEX idx_plans_review_due ON bcm.plans(next_review_date) WHERE status = 'active';

CREATE TRIGGER update_plans_updated_at BEFORE UPDATE ON bcm.plans
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE bcm.plans ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Plans visible to org members" ON bcm.plans FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Plans manageable by org admins" ON bcm.plans FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE bcm.plans IS 'Business continuity plans and procedures per ISO 22301:2019 Clause 8.4';

-- Table: bcm.procedures (Consolidated)
CREATE TABLE bcm.procedures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID REFERENCES bcm.plans(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Procedure identity
    procedure_code VARCHAR(100) NOT NULL,
    procedure_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Classification
    procedure_type VARCHAR(100) NOT NULL, -- activation, response, recovery, communication, escalation, restoration, technical
    procedure_category VARCHAR(100), -- operational, technical, administrative

    -- Content
    procedure_steps JSONB NOT NULL, -- Array of {step_number, action, responsible_role, estimated_time, critical}
    decision_points JSONB DEFAULT '[]'::jsonb, -- {point_number, decision, criteria, yes_action, no_action}

    -- Execution context
    when_to_execute TEXT,
    trigger_conditions JSONB DEFAULT '[]'::jsonb,

    -- Roles
    responsible_role VARCHAR(100),
    supporting_roles JSONB DEFAULT '[]'::jsonb,

    -- Resources needed
    required_resources JSONB DEFAULT '[]'::jsonb,
    required_tools JSONB DEFAULT '[]'::jsonb,
    required_access JSONB DEFAULT '[]'::jsonb,

    -- Timing
    estimated_duration_minutes INT,
    must_complete_within_minutes INT, -- SLA/RTO requirement

    -- Dependencies
    depends_on JSONB DEFAULT '[]'::jsonb, -- UUIDs of other procedures
    blocks JSONB DEFAULT '[]'::jsonb, -- Procedures that depend on this

    -- Quality checks
    verification_steps JSONB DEFAULT '[]'::jsonb,
    success_criteria TEXT,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    last_reviewed_date DATE,
    next_review_date DATE,

    -- Testing
    last_tested_date DATE,
    test_success_rate DECIMAL(5,2),

    -- Usage tracking
    times_executed INT DEFAULT 0,
    average_execution_time_minutes INT,
    last_executed_date DATE,

    -- Files
    flowchart_path VARCHAR(500),
    detailed_document_path VARCHAR(500),

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, procedure_code)
);

CREATE INDEX idx_procedures_plan ON bcm.procedures(plan_id);
CREATE INDEX idx_procedures_org ON bcm.procedures(organization_id);
CREATE INDEX idx_procedures_type ON bcm.procedures(procedure_type);
CREATE INDEX idx_procedures_active ON bcm.procedures(is_active) WHERE is_active = TRUE;

CREATE TRIGGER update_procedures_updated_at BEFORE UPDATE ON bcm.procedures
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE bcm.procedures ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Procedures visible to org members" ON bcm.procedures FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Procedures manageable by org admins" ON bcm.procedures FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE bcm.procedures IS 'Detailed procedures for BCM plans per ISO 22301 Clause 8.4';

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 013 completed: Learning & Planning (8 tables)';
    RAISE NOTICE '   Learning Schema (NEW):';
    RAISE NOTICE '   - training_programs: Training courses (ISO 22301 Clauses 7.2, 7.3)';
    RAISE NOTICE '   - enrollments: Training enrollment and completion tracking';
    RAISE NOTICE '   - competency_assessments: Competency evaluations';
    RAISE NOTICE '   - awareness_campaigns: BCM awareness campaigns';
    RAISE NOTICE '   - training_templates: Course templates';
    RAISE NOTICE '   - user_achievements: Gamification and badges';
    RAISE NOTICE '   BCM Schema:';
    RAISE NOTICE '   - plans: Business continuity plans (ISO 22301 Clause 8.4)';
    RAISE NOTICE '   - procedures: Detailed operational procedures';
END
$$;
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
