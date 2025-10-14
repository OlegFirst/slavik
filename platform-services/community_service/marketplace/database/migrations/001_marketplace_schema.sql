-- Marketplace Service - Database Schema
-- Based on BCM_1 Odoo models (bcm_marketplace.py, bcm_specialist.py)
-- Adapted for PostgreSQL + FastAPI

-- Create schema
CREATE SCHEMA IF NOT EXISTS marketplace;

-- ============================================================================
-- ENUMS
-- ============================================================================

-- Service types (from BCM_1)
CREATE TYPE marketplace.service_type AS ENUM (
    'consulting',
    'assessment',
    'bia',
    'planning',
    'training',
    'audit',
    'implementation',
    'crisis_support',
    'other'
);

-- Project urgency levels
CREATE TYPE marketplace.urgency_level AS ENUM (
    'low',       -- Flexible timeline
    'medium',    -- Within 2-4 weeks
    'high',      -- Within 1 week
    'urgent'     -- ASAP
);

-- Budget types
CREATE TYPE marketplace.budget_type AS ENUM (
    'hourly',
    'fixed',
    'negotiable'
);

-- Work location
CREATE TYPE marketplace.work_location AS ENUM (
    'remote',
    'onsite',
    'hybrid'
);

-- Project status
CREATE TYPE marketplace.project_status AS ENUM (
    'draft',
    'published',
    'in_progress',
    'completed',
    'cancelled'
);

-- Proposal status
CREATE TYPE marketplace.proposal_status AS ENUM (
    'pending',
    'accepted',
    'rejected',
    'withdrawn'
);

-- Specialist availability
CREATE TYPE marketplace.availability_status AS ENUM (
    'available',
    'busy',
    'unavailable'
);

-- ============================================================================
-- SPECIALISTS
-- ============================================================================

CREATE TABLE marketplace.specialists (
    id SERIAL PRIMARY KEY,

    -- User Reference (from Clients service)
    user_id UUID NOT NULL UNIQUE,
    tenant_id UUID NOT NULL,

    -- Basic Information
    name VARCHAR(255) NOT NULL,
    title VARCHAR(255),  -- Professional title (e.g., "Senior BCM Consultant")
    bio TEXT,
    years_experience INTEGER DEFAULT 0,

    -- Pricing
    hourly_rate DECIMAL(10,2),  -- USD/hour
    currency VARCHAR(3) DEFAULT 'USD',

    -- Skills & Specializations (JSONB for flexibility)
    specializations JSONB DEFAULT '[]',  -- ["ISO 22301", "BIA", "Risk Assessment"]
    industries JSONB DEFAULT '[]',       -- ["Financial", "Healthcare", "IT"]
    skills JSONB DEFAULT '[]',           -- ["Business Continuity", "Crisis Management"]

    -- Availability
    availability_status marketplace.availability_status DEFAULT 'available',
    availability_hours JSONB,  -- Weekly availability schedule
    timezone VARCHAR(50) DEFAULT 'UTC',

    -- Location
    country VARCHAR(100),
    state VARCHAR(100),
    city VARCHAR(100),
    remote_available BOOLEAN DEFAULT true,
    onsite_available BOOLEAN DEFAULT true,

    -- Languages
    languages JSONB DEFAULT '[]',  -- ["English", "Spanish", "French"]

    -- Metrics
    rating DECIMAL(3,2) DEFAULT 0.00,  -- Average rating (0-5)
    total_reviews INTEGER DEFAULT 0,
    completed_projects INTEGER DEFAULT 0,
    response_time_hours DECIMAL(10,2),  -- Average response time
    acceptance_rate DECIMAL(5,2),       -- Project acceptance rate (%)

    -- Verification
    is_verified BOOLEAN DEFAULT false,
    verified_at TIMESTAMP,
    verified_by UUID,  -- Admin who verified
    verification_notes TEXT,

    -- Profile completeness
    profile_completion INTEGER DEFAULT 0,  -- 0-100%

    -- Status
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()

    -- Note: Foreign key to clients.users will be added when integrated with Clients service
    -- CONSTRAINT specialists_user_id_fkey FOREIGN KEY (user_id) REFERENCES clients.users(id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX idx_specialists_user_id ON marketplace.specialists(user_id);
CREATE INDEX idx_specialists_tenant_id ON marketplace.specialists(tenant_id);
CREATE INDEX idx_specialists_rating ON marketplace.specialists(rating DESC);
CREATE INDEX idx_specialists_verified ON marketplace.specialists(is_verified);
CREATE INDEX idx_specialists_availability ON marketplace.specialists(availability_status);
CREATE INDEX idx_specialists_specializations ON marketplace.specialists USING GIN (specializations);
CREATE INDEX idx_specialists_industries ON marketplace.specialists USING GIN (industries);

-- ============================================================================
-- CERTIFICATIONS
-- ============================================================================

CREATE TABLE marketplace.certifications (
    id SERIAL PRIMARY KEY,
    specialist_id INTEGER NOT NULL REFERENCES marketplace.specialists(id) ON DELETE CASCADE,

    -- Certification Details
    name VARCHAR(255) NOT NULL,  -- e.g., "ISO 22301 Lead Implementer"
    issuing_organization VARCHAR(255),  -- e.g., "PECB"
    issue_date DATE,
    expiry_date DATE,
    credential_id VARCHAR(255),  -- Credential ID/number
    credential_url VARCHAR(500),  -- Verification URL

    -- Verification
    is_verified BOOLEAN DEFAULT false,
    verified_at TIMESTAMP,
    verified_by UUID,

    -- Documents
    documents JSONB DEFAULT '[]',  -- Array of file URLs

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_certifications_specialist ON marketplace.certifications(specialist_id);
CREATE INDEX idx_certifications_name ON marketplace.certifications(name);

-- ============================================================================
-- PORTFOLIO
-- ============================================================================

CREATE TABLE marketplace.portfolio_items (
    id SERIAL PRIMARY KEY,
    specialist_id INTEGER NOT NULL REFERENCES marketplace.specialists(id) ON DELETE CASCADE,

    -- Project Details
    title VARCHAR(255) NOT NULL,
    description TEXT,
    client_name VARCHAR(255),  -- Can be anonymous
    industry VARCHAR(100),
    project_type marketplace.service_type,

    -- Timeline
    start_date DATE,
    end_date DATE,
    duration_months INTEGER,

    -- Deliverables
    deliverables TEXT,
    outcomes TEXT,

    -- Media
    images JSONB DEFAULT '[]',  -- Array of image URLs
    documents JSONB DEFAULT '[]',  -- Array of document URLs

    -- Visibility
    is_public BOOLEAN DEFAULT true,
    display_order INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_portfolio_specialist ON marketplace.portfolio_items(specialist_id);
CREATE INDEX idx_portfolio_public ON marketplace.portfolio_items(is_public);

-- ============================================================================
-- PROJECTS (Service Requests)
-- ============================================================================

CREATE TABLE marketplace.projects (
    id SERIAL PRIMARY KEY,

    -- Client Information
    client_id UUID NOT NULL,  -- From Clients service
    tenant_id UUID NOT NULL,
    client_name VARCHAR(255),
    company_name VARCHAR(255),
    industry VARCHAR(100),
    company_size VARCHAR(50),

    -- Project Details
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    service_type marketplace.service_type NOT NULL,
    urgency marketplace.urgency_level DEFAULT 'medium',

    -- Scope
    scope_of_work TEXT,
    deliverables TEXT,

    -- Timeline
    start_date DATE,
    end_date DATE,
    duration_estimate_hours DECIMAL(10,2),

    -- Budget
    budget_type marketplace.budget_type DEFAULT 'negotiable',
    budget_min DECIMAL(10,2),
    budget_max DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',

    -- Requirements
    required_certifications TEXT,
    required_experience_years INTEGER,
    required_skills JSONB DEFAULT '[]',  -- ["ISO 22301", "BIA"]

    -- Location
    work_location marketplace.work_location DEFAULT 'remote',
    location_country VARCHAR(100),
    location_state VARCHAR(100),
    location_city VARCHAR(100),

    -- Status
    status marketplace.project_status DEFAULT 'draft',
    published_at TIMESTAMP,

    -- Selected Proposal
    selected_proposal_id INTEGER,  -- References proposals(id)
    selected_specialist_id INTEGER,  -- References specialists(id)

    -- Metrics
    view_count INTEGER DEFAULT 0,
    proposal_count INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()

    -- Note: Foreign key to clients.users will be added when integrated with Clients service
    -- CONSTRAINT projects_client_id_fkey FOREIGN KEY (client_id) REFERENCES clients.users(id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX idx_projects_client_id ON marketplace.projects(client_id);
CREATE INDEX idx_projects_tenant_id ON marketplace.projects(tenant_id);
CREATE INDEX idx_projects_status ON marketplace.projects(status);
CREATE INDEX idx_projects_service_type ON marketplace.projects(service_type);
CREATE INDEX idx_projects_urgency ON marketplace.projects(urgency);
CREATE INDEX idx_projects_published_at ON marketplace.projects(published_at DESC);
CREATE INDEX idx_projects_required_skills ON marketplace.projects USING GIN (required_skills);

-- ============================================================================
-- PROPOSALS
-- ============================================================================

CREATE TABLE marketplace.proposals (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES marketplace.projects(id) ON DELETE CASCADE,
    specialist_id INTEGER NOT NULL REFERENCES marketplace.specialists(id) ON DELETE CASCADE,

    -- Proposal Details
    cover_letter TEXT NOT NULL,
    proposed_rate DECIMAL(10,2),  -- Hourly rate
    estimated_duration_hours DECIMAL(10,2),
    estimated_total_cost DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',

    -- Timeline
    proposed_start_date DATE,
    proposed_end_date DATE,

    -- Deliverables
    deliverables TEXT,
    methodology TEXT,

    -- Attachments
    attachments JSONB DEFAULT '[]',  -- Array of file URLs

    -- Status
    status marketplace.proposal_status DEFAULT 'pending',

    -- Response tracking
    viewed_by_client BOOLEAN DEFAULT false,
    viewed_at TIMESTAMP,
    responded_at TIMESTAMP,
    response_notes TEXT,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Unique constraint: one proposal per specialist per project
    CONSTRAINT unique_specialist_project UNIQUE (project_id, specialist_id)
);

CREATE INDEX idx_proposals_project ON marketplace.proposals(project_id);
CREATE INDEX idx_proposals_specialist ON marketplace.proposals(specialist_id);
CREATE INDEX idx_proposals_status ON marketplace.proposals(status);
CREATE INDEX idx_proposals_created ON marketplace.proposals(created_at DESC);

-- ============================================================================
-- REVIEWS
-- ============================================================================

CREATE TABLE marketplace.reviews (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES marketplace.projects(id) ON DELETE CASCADE,
    specialist_id INTEGER NOT NULL REFERENCES marketplace.specialists(id) ON DELETE CASCADE,
    reviewer_id UUID NOT NULL,  -- Client user

    -- Rating
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),

    -- Review Details
    title VARCHAR(255),
    review_text TEXT,

    -- Category Ratings
    communication_rating INTEGER CHECK (communication_rating >= 1 AND communication_rating <= 5),
    quality_rating INTEGER CHECK (quality_rating >= 1 AND quality_rating <= 5),
    professionalism_rating INTEGER CHECK (professionalism_rating >= 1 AND professionalism_rating <= 5),
    timeliness_rating INTEGER CHECK (timeliness_rating >= 1 AND timeliness_rating <= 5),

    -- Specialist Response
    specialist_response TEXT,
    responded_at TIMESTAMP,

    -- Visibility
    is_public BOOLEAN DEFAULT true,

    -- Verification
    is_verified BOOLEAN DEFAULT true,  -- Verified that project happened

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- One review per client per specialist per project
    CONSTRAINT unique_project_reviewer UNIQUE (project_id, reviewer_id)
);

CREATE INDEX idx_reviews_specialist ON marketplace.reviews(specialist_id);
CREATE INDEX idx_reviews_project ON marketplace.reviews(project_id);
CREATE INDEX idx_reviews_rating ON marketplace.reviews(rating DESC);
CREATE INDEX idx_reviews_public ON marketplace.reviews(is_public);
CREATE INDEX idx_reviews_created ON marketplace.reviews(created_at DESC);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update specialist rating on review insert/update/delete
CREATE OR REPLACE FUNCTION update_specialist_rating()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE marketplace.specialists
    SET
        rating = (
            SELECT COALESCE(AVG(rating), 0)
            FROM marketplace.reviews
            WHERE specialist_id = COALESCE(NEW.specialist_id, OLD.specialist_id)
            AND is_public = true
        ),
        total_reviews = (
            SELECT COUNT(*)
            FROM marketplace.reviews
            WHERE specialist_id = COALESCE(NEW.specialist_id, OLD.specialist_id)
            AND is_public = true
        ),
        updated_at = NOW()
    WHERE id = COALESCE(NEW.specialist_id, OLD.specialist_id);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_specialist_rating
AFTER INSERT OR UPDATE OR DELETE ON marketplace.reviews
FOR EACH ROW
EXECUTE FUNCTION update_specialist_rating();

-- Update project proposal count
CREATE OR REPLACE FUNCTION update_project_proposal_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE marketplace.projects
    SET
        proposal_count = (
            SELECT COUNT(*)
            FROM marketplace.proposals
            WHERE project_id = COALESCE(NEW.project_id, OLD.project_id)
        ),
        updated_at = NOW()
    WHERE id = COALESCE(NEW.project_id, OLD.project_id);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_project_proposal_count
AFTER INSERT OR DELETE ON marketplace.proposals
FOR EACH ROW
EXECUTE FUNCTION update_project_proposal_count();

-- Update specialist completed_projects count
CREATE OR REPLACE FUNCTION update_specialist_completed_projects()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'completed' AND (OLD.status IS NULL OR OLD.status != 'completed') THEN
        UPDATE marketplace.specialists
        SET
            completed_projects = completed_projects + 1,
            updated_at = NOW()
        WHERE id = NEW.selected_specialist_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_specialist_completed_projects
AFTER UPDATE ON marketplace.projects
FOR EACH ROW
WHEN (NEW.selected_specialist_id IS NOT NULL)
EXECUTE FUNCTION update_specialist_completed_projects();

-- ============================================================================
-- SAMPLE DATA (for testing)
-- ============================================================================

-- Sample specializations for JSONB
COMMENT ON COLUMN marketplace.specialists.specializations IS 'Array of specializations, e.g., ["ISO 22301", "Business Impact Analysis", "Risk Assessment", "Crisis Management"]';
COMMENT ON COLUMN marketplace.specialists.industries IS 'Array of industries, e.g., ["Financial Services", "Healthcare", "IT/Technology", "Manufacturing"]';
COMMENT ON COLUMN marketplace.specialists.skills IS 'Array of skills, e.g., ["Business Continuity Planning", "Disaster Recovery", "Risk Management", "Compliance"]';

-- Sample required_skills for projects
COMMENT ON COLUMN marketplace.projects.required_skills IS 'Array of required skills, e.g., ["ISO 22301 Lead Implementer", "BIA Experience", "Financial Sector Knowledge"]';

-- ============================================================================
-- ROLLBACK (if needed)
-- ============================================================================

-- DROP TABLE IF EXISTS marketplace.reviews CASCADE;
-- DROP TABLE IF EXISTS marketplace.proposals CASCADE;
-- DROP TABLE IF EXISTS marketplace.projects CASCADE;
-- DROP TABLE IF EXISTS marketplace.portfolio_items CASCADE;
-- DROP TABLE IF EXISTS marketplace.certifications CASCADE;
-- DROP TABLE IF EXISTS marketplace.specialists CASCADE;
--
-- DROP TYPE IF EXISTS marketplace.availability_status CASCADE;
-- DROP TYPE IF EXISTS marketplace.proposal_status CASCADE;
-- DROP TYPE IF EXISTS marketplace.project_status CASCADE;
-- DROP TYPE IF EXISTS marketplace.work_location CASCADE;
-- DROP TYPE IF EXISTS marketplace.budget_type CASCADE;
-- DROP TYPE IF EXISTS marketplace.urgency_level CASCADE;
-- DROP TYPE IF EXISTS marketplace.service_type CASCADE;
--
-- DROP SCHEMA IF EXISTS marketplace CASCADE;
