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
