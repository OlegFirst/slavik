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
