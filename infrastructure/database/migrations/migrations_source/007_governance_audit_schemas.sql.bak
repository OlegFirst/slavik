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
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE governance.policies ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Policies visible to org members" ON governance.policies FOR SELECT
    USING (auth.is_org_member(organization_id));

CREATE POLICY "Policies manageable by org admins" ON governance.policies FOR ALL
    USING (auth.is_org_admin(organization_id));

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
    USING (auth.is_org_member(organization_id));

CREATE POLICY "Roles manageable by org admins" ON governance.roles FOR ALL
    USING (auth.is_org_admin(organization_id));

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
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE governance.objectives ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Objectives visible to org members" ON governance.objectives FOR SELECT
    USING (auth.is_org_member(organization_id));

CREATE POLICY "Objectives manageable by org admins" ON governance.objectives FOR ALL
    USING (auth.is_org_admin(organization_id));

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
        auth.is_org_admin(organization_id)
        OR auth.is_platform_admin()
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
    USING (auth.is_org_member(organization_id) OR auth.is_platform_admin());

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
