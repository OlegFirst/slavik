-- Migration 005: Add Organizations Table
-- Centralized organization/tenant information

-- =============================================================================
-- Organizations Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS core.organizations (
    id VARCHAR(255) PRIMARY KEY,

    -- Basic Info
    name VARCHAR(500) NOT NULL,
    legal_name VARCHAR(500),

    -- Classification
    industry VARCHAR(100),
    organization_size VARCHAR(50), -- small, medium, large, enterprise
    organization_type VARCHAR(50), -- public, private, government, ngo

    -- Location
    country VARCHAR(100),
    city VARCHAR(200),
    address TEXT,
    timezone VARCHAR(100),

    -- Contact
    primary_contact_name VARCHAR(255),
    primary_contact_email VARCHAR(255),
    primary_contact_phone VARCHAR(50),
    website VARCHAR(500),

    -- BCM Program Info
    bcm_maturity_level VARCHAR(50), -- initial, developing, defined, managed, optimizing
    iso22301_certified BOOLEAN DEFAULT FALSE,
    certification_date DATE,
    certification_body VARCHAR(255),

    -- Compliance & Standards
    applicable_standards JSONB DEFAULT '[]', -- ISO 22301, ISO 27001, SOC 2, etc.
    regulatory_requirements JSONB DEFAULT '[]', -- GDPR, HIPAA, etc.

    -- Business Context
    critical_services JSONB DEFAULT '[]',
    key_dependencies JSONB DEFAULT '[]',
    risk_appetite VARCHAR(50), -- low, medium, high

    -- Subscription & Licensing
    subscription_tier VARCHAR(50), -- free, basic, professional, enterprise
    subscription_status VARCHAR(50) DEFAULT 'active', -- active, suspended, cancelled
    subscription_start_date DATE,
    subscription_end_date DATE,
    max_users INT DEFAULT 10,

    -- Features & Modules
    enabled_modules JSONB DEFAULT '[]', -- ['bia', 'risk', 'compliance', 'learning', 'simulation']
    feature_flags JSONB DEFAULT '{}',

    -- Configuration
    settings JSONB DEFAULT '{}', -- custom organization settings
    branding JSONB DEFAULT '{}', -- logo, colors, etc.

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    onboarding_completed BOOLEAN DEFAULT FALSE,
    onboarding_completed_at TIMESTAMPTZ,

    -- Metadata
    notes TEXT,
    tags JSONB DEFAULT '[]',

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(255),
    updated_by VARCHAR(255),

    -- Constraints
    CONSTRAINT chk_org_size CHECK (organization_size IN ('small', 'medium', 'large', 'enterprise', NULL)),
    CONSTRAINT chk_org_type CHECK (organization_type IN ('public', 'private', 'government', 'ngo', NULL)),
    CONSTRAINT chk_maturity CHECK (bcm_maturity_level IN ('initial', 'developing', 'defined', 'managed', 'optimizing', NULL)),
    CONSTRAINT chk_subscription_tier CHECK (subscription_tier IN ('free', 'basic', 'professional', 'enterprise', NULL)),
    CONSTRAINT chk_subscription_status CHECK (subscription_status IN ('active', 'suspended', 'cancelled', 'trial')),
    CONSTRAINT chk_risk_appetite CHECK (risk_appetite IN ('low', 'medium', 'high', NULL))
);

-- =============================================================================
-- Indexes
-- =============================================================================
CREATE INDEX idx_organizations_name ON core.organizations(name);
CREATE INDEX idx_organizations_industry ON core.organizations(industry);
CREATE INDEX idx_organizations_size ON core.organizations(organization_size);
CREATE INDEX idx_organizations_subscription ON core.organizations(subscription_tier, subscription_status);
CREATE INDEX idx_organizations_active ON core.organizations(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_organizations_created ON core.organizations(created_at DESC);

-- =============================================================================
-- Organization Users Junction Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS core.organization_users (
    id SERIAL PRIMARY KEY,
    organization_id VARCHAR(255) NOT NULL REFERENCES core.organizations(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,

    -- Role in Organization
    role VARCHAR(50) NOT NULL, -- owner, admin, manager, member, viewer
    title VARCHAR(255), -- Job title
    department VARCHAR(255),

    -- Permissions
    permissions JSONB DEFAULT '[]',

    -- Status
    is_primary_contact BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    invited_at TIMESTAMPTZ,
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    last_active_at TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(organization_id, user_id),
    CONSTRAINT chk_user_role CHECK (role IN ('owner', 'admin', 'manager', 'member', 'viewer'))
);

CREATE INDEX idx_org_users_org ON core.organization_users(organization_id);
CREATE INDEX idx_org_users_user ON core.organization_users(user_id);
CREATE INDEX idx_org_users_role ON core.organization_users(organization_id, role);
CREATE INDEX idx_org_users_active ON core.organization_users(organization_id, is_active) WHERE is_active = TRUE;

-- =============================================================================
-- Organization Audit Log
-- =============================================================================
CREATE TABLE IF NOT EXISTS core.organization_audit_log (
    id SERIAL PRIMARY KEY,
    organization_id VARCHAR(255) NOT NULL REFERENCES core.organizations(id) ON DELETE CASCADE,

    -- Event Info
    event_type VARCHAR(100) NOT NULL, -- created, updated, settings_changed, user_added, etc.
    event_category VARCHAR(50), -- admin, security, billing, users

    -- Actor
    performed_by VARCHAR(255),
    performed_by_role VARCHAR(50),

    -- Details
    description TEXT,
    changes JSONB, -- old and new values
    metadata JSONB DEFAULT '{}',

    -- Context
    ip_address INET,
    user_agent TEXT,

    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_org_audit_org ON core.organization_audit_log(organization_id, created_at DESC);
CREATE INDEX idx_org_audit_type ON core.organization_audit_log(event_type);
CREATE INDEX idx_org_audit_category ON core.organization_audit_log(event_category);
CREATE INDEX idx_org_audit_user ON core.organization_audit_log(performed_by);

-- =============================================================================
-- Comments
-- =============================================================================
COMMENT ON TABLE core.organizations IS 'Master organization/tenant information';
COMMENT ON TABLE core.organization_users IS 'Users belonging to organizations with roles';
COMMENT ON TABLE core.organization_audit_log IS 'Audit trail for organization changes';

COMMENT ON COLUMN core.organizations.bcm_maturity_level IS 'BCMS maturity: initial, developing, defined, managed, optimizing';
COMMENT ON COLUMN core.organizations.enabled_modules IS 'Array of enabled modules: [bia, risk, compliance, learning, simulation, etc.]';
COMMENT ON COLUMN core.organizations.subscription_tier IS 'Subscription level: free, basic, professional, enterprise';

-- =============================================================================
-- Sample Data (for testing)
-- =============================================================================
-- Insert a test organization
INSERT INTO core.organizations (
    id,
    name,
    legal_name,
    industry,
    organization_size,
    organization_type,
    country,
    city,
    bcm_maturity_level,
    iso22301_certified,
    subscription_tier,
    subscription_status,
    subscription_start_date,
    max_users,
    enabled_modules,
    is_active,
    onboarding_completed
) VALUES (
    'test-tenant-001',
    'Test Organization Ltd',
    'Test Organization Limited',
    'Technology',
    'medium',
    'private',
    'United Kingdom',
    'London',
    'developing',
    FALSE,
    'professional',
    'active',
    CURRENT_DATE,
    50,
    '["bia", "risk", "compliance", "learning", "simulation"]',
    TRUE,
    TRUE
) ON CONFLICT (id) DO NOTHING;

-- Insert another test organization
INSERT INTO core.organizations (
    id,
    name,
    industry,
    organization_size,
    organization_type,
    subscription_tier,
    subscription_status,
    enabled_modules,
    is_active
) VALUES (
    'demo-org-001',
    'Demo Financial Services',
    'Finance',
    'large',
    'public',
    'enterprise',
    'active',
    '["bia", "risk", "compliance", "learning", "simulation", "intelligence"]',
    TRUE
) ON CONFLICT (id) DO NOTHING;

-- =============================================================================
-- Grant permissions (adjust based on your user setup)
-- =============================================================================
-- GRANT ALL PRIVILEGES ON TABLE core.organizations TO bcm_user;
-- GRANT ALL PRIVILEGES ON TABLE core.organization_users TO bcm_user;
-- GRANT ALL PRIVILEGES ON TABLE core.organization_audit_log TO bcm_user;
-- GRANT ALL PRIVILEGES ON SEQUENCE core.organization_users_id_seq TO bcm_user;
-- GRANT ALL PRIVILEGES ON SEQUENCE core.organization_audit_log_id_seq TO bcm_user;
