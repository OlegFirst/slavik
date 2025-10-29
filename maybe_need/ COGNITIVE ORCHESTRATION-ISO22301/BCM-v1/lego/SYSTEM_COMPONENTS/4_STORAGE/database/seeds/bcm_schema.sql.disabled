-- =====================================================
-- BCM Platform - Complete Database Schema
-- ISO 22301:2019 Compliant Database Design
-- PostgreSQL 15+ Compatible
-- =====================================================

-- Create BCM database extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =====================================================
-- BCM Core Tables (Floor 1)
-- =====================================================

-- Organization Context (bcm_context module)
CREATE TABLE IF NOT EXISTS bcm_context (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sequence INTEGER DEFAULT 10,
    active BOOLEAN DEFAULT TRUE,
    context_type VARCHAR(50) NOT NULL CHECK (context_type IN ('internal', 'external', 'stakeholder', 'regulatory', 'strategic')),
    description TEXT,
    impact_on_bcms TEXT,
    risk_level VARCHAR(20) CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    opportunity_level VARCHAR(20) CHECK (opportunity_level IN ('low', 'medium', 'high')),
    review_frequency VARCHAR(20) DEFAULT 'quarterly' CHECK (review_frequency IN ('monthly', 'quarterly', 'semiannually', 'annually')),
    last_review_date DATE,
    next_review_date DATE,
    responsible_user_id INTEGER,
    department_id INTEGER,
    company_id INTEGER NOT NULL,
    create_uid INTEGER,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    write_uid INTEGER,
    write_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stakeholders (bcm_context module)
CREATE TABLE IF NOT EXISTS bcm_stakeholder (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    stakeholder_type VARCHAR(50) NOT NULL CHECK (stakeholder_type IN ('internal', 'external', 'regulatory', 'customer', 'supplier', 'partner', 'community')),
    contact_person VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    requirements TEXT,
    influence_level VARCHAR(20) NOT NULL CHECK (influence_level IN ('low', 'medium', 'high', 'critical')),
    interest_level VARCHAR(20) NOT NULL CHECK (interest_level IN ('low', 'medium', 'high')),
    communication_method VARCHAR(50) CHECK (communication_method IN ('email', 'phone', 'meeting', 'portal', 'report')),
    communication_frequency VARCHAR(50) CHECK (communication_frequency IN ('daily', 'weekly', 'monthly', 'quarterly', 'as_needed', 'emergency_only')),
    context_id INTEGER REFERENCES bcm_context(id),
    company_id INTEGER NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    create_uid INTEGER,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    write_uid INTEGER,
    write_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- BCMS Scope (bcm_context module)
CREATE TABLE IF NOT EXISTS bcm_scope (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    scope_type VARCHAR(20) NOT NULL CHECK (scope_type IN ('inclusion', 'exclusion', 'boundary')),
    description TEXT,
    justification TEXT,
    geographical_scope TEXT,
    services_products TEXT,
    approved_by INTEGER,
    approval_date DATE,
    company_id INTEGER NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    create_uid INTEGER,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    write_uid INTEGER,
    write_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- BCM Policies (bcm_context module)
CREATE TABLE IF NOT EXISTS bcm_policy (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sequence INTEGER DEFAULT 10,
    policy_type VARCHAR(20) NOT NULL CHECK (policy_type IN ('policy', 'objective', 'principle', 'standard')),
    content TEXT,
    measurable BOOLEAN DEFAULT FALSE,
    target_value NUMERIC,
    measurement_unit VARCHAR(50),
    version VARCHAR(20) DEFAULT '1.0',
    effective_date DATE DEFAULT CURRENT_DATE,
    review_date DATE,
    approved_by INTEGER,
    approval_date DATE,
    company_id INTEGER NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    create_uid INTEGER,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    write_uid INTEGER,
    write_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Business Impact Analysis (Floor 2)
-- =====================================================

-- Industry Types for BIA
CREATE TABLE IF NOT EXISTS bcm_industry_type (
    id SERIAL PRIMARY KEY,
    sequence INTEGER DEFAULT 10,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    revenue_loss_multiplier NUMERIC(10,2) DEFAULT 1.0,
    reputation_impact NUMERIC(10,2) DEFAULT 1.0,
    regulatory_penalty NUMERIC(10,2) DEFAULT 0.5,
    base_rto_hours INTEGER DEFAULT 24,
    base_rpo_minutes INTEGER DEFAULT 240,
    description TEXT,
    company_id INTEGER NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    create_uid INTEGER,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    write_uid INTEGER,
    write_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Business Processes for BIA
CREATE TABLE IF NOT EXISTS bcm_business_process (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    industry_id INTEGER REFERENCES bcm_industry_type(id),
    criticality VARCHAR(20) NOT NULL DEFAULT 'medium' CHECK (criticality IN ('low', 'medium', 'high', 'critical')),
    annual_revenue_impact NUMERIC(15,2) DEFAULT 0.0,
    peak_concurrent_users INTEGER DEFAULT 0,
    staff_count INTEGER DEFAULT 1,
    geographical_scope VARCHAR(20) DEFAULT 'local' CHECK (geographical_scope IN ('local', 'regional', 'national', 'global')),
    
    -- AI-optimized parameters
    optimized_rto_hours NUMERIC(10,2),
    optimized_rpo_minutes NUMERIC(10,2),
    mtpd_hours NUMERIC(10,2),
    confidence_score NUMERIC(3,2),
    
    -- Financial calculations
    total_financial_impact_24h NUMERIC(15,2),
    hourly_impact_rate NUMERIC(15,2),
    annual_risk_exposure NUMERIC(15,2),
    
    -- Cascade risks
    cascade_risk_score NUMERIC(5,2),
    dependency_depth INTEGER,
    impact_breadth INTEGER,
    
    -- AI analysis metadata
    last_ai_analysis TIMESTAMP,
    ai_recommendations TEXT,
    analysis_confidence VARCHAR(20) CHECK (analysis_confidence IN ('low', 'medium', 'high')),
    
    company_id INTEGER NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    create_uid INTEGER,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    write_uid INTEGER,
    write_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Process Dependencies (Many2Many)
CREATE TABLE IF NOT EXISTS bcm_process_dependency_rel (
    process_id INTEGER REFERENCES bcm_business_process(id) ON DELETE CASCADE,
    dependency_id INTEGER REFERENCES bcm_business_process(id) ON DELETE CASCADE,
    PRIMARY KEY (process_id, dependency_id)
);

-- Compliance Requirements
CREATE TABLE IF NOT EXISTS bcm_compliance_requirement (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    company_id INTEGER NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    create_uid INTEGER,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    write_uid INTEGER,
    write_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Technology Stack
CREATE TABLE IF NOT EXISTS bcm_technology_stack (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    description TEXT,
    company_id INTEGER NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    create_uid INTEGER,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    write_uid INTEGER,
    write_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- BIA Analysis Results
CREATE TABLE IF NOT EXISTS bcm_bia_analysis (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    analysis_period_days INTEGER DEFAULT 365,
    risk_tolerance NUMERIC(3,2) DEFAULT 0.05,
    budget_constraint NUMERIC(15,2) DEFAULT 0.0,
    
    -- Results
    total_processes_analyzed INTEGER,
    critical_processes_count INTEGER,
    total_annual_risk_exposure NUMERIC(15,2),
    average_rto_hours NUMERIC(10,2),
    
    state VARCHAR(20) DEFAULT 'draft' CHECK (state IN ('draft', 'analyzing', 'completed', 'failed')),
    analysis_results TEXT,
    dependency_recommendations TEXT,
    critical_path_processes TEXT,
    analysis_date TIMESTAMP,
    methodology VARCHAR(100),
    
    company_id INTEGER NOT NULL,
    create_uid INTEGER,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    write_uid INTEGER,
    write_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Many2Many between BIA Analysis and Business Processes
CREATE TABLE IF NOT EXISTS bcm_bia_analysis_process_rel (
    bia_analysis_id INTEGER REFERENCES bcm_bia_analysis(id) ON DELETE CASCADE,
    process_id INTEGER REFERENCES bcm_business_process(id) ON DELETE CASCADE,
    PRIMARY KEY (bia_analysis_id, process_id)
);

-- =====================================================
-- Incident Management (Floor 3)
-- =====================================================

-- BCM Incidents
CREATE TABLE IF NOT EXISTS bcm_incident (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    incident_type VARCHAR(50),
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    status VARCHAR(50) DEFAULT 'new',
    impact_assessment TEXT,
    root_cause TEXT,
    lessons_learned TEXT,
    
    -- TheHive integration fields
    thehive_case_id VARCHAR(100),
    thehive_sync_status VARCHAR(20) DEFAULT 'pending',
    last_thehive_sync TIMESTAMP,
    
    -- Timing
    incident_date TIMESTAMP,
    detection_date TIMESTAMP,
    response_start_date TIMESTAMP,
    resolution_date TIMESTAMP,
    
    -- Assignment
    assigned_to INTEGER,
    response_team_ids TEXT, -- JSON array of user IDs
    
    company_id INTEGER NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    create_uid INTEGER,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    write_uid INTEGER,
    write_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Plans and Procedures (Floor 1-2)
-- =====================================================

-- BCM Plans
CREATE TABLE IF NOT EXISTS bcm_plan (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    plan_type VARCHAR(50),
    description TEXT,
    objective TEXT,
    scope TEXT,
    activation_criteria TEXT,
    deactivation_criteria TEXT,
    
    -- Plan details
    rto_target NUMERIC(10,2),
    rpo_target NUMERIC(10,2),
    mtpd_target NUMERIC(10,2),
    
    -- Review and approval
    version VARCHAR(20) DEFAULT '1.0',
    approval_date DATE,
    approved_by INTEGER,
    next_review_date DATE,
    
    -- Status
    state VARCHAR(20) DEFAULT 'draft' CHECK (state IN ('draft', 'review', 'approved', 'active', 'deprecated')),
    
    company_id INTEGER NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    create_uid INTEGER,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    write_uid INTEGER,
    write_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Exercises and Testing (Floor 3)
-- =====================================================

-- BCM Exercises
CREATE TABLE IF NOT EXISTS bcm_exercise (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    exercise_type VARCHAR(50),
    description TEXT,
    objectives TEXT,
    scenario TEXT,
    
    -- Timing
    planned_date DATE,
    actual_start_date TIMESTAMP,
    actual_end_date TIMESTAMP,
    duration_hours NUMERIC(10,2),
    
    -- Participants
    facilitator_id INTEGER,
    participants_count INTEGER DEFAULT 0,
    
    -- Results
    success_criteria TEXT,
    results TEXT,
    lessons_learned TEXT,
    improvement_actions TEXT,
    
    -- Integration with simulators
    jaamsim_model_path VARCHAR(500),
    nics_incident_id VARCHAR(100),
    simulator_results TEXT,
    
    state VARCHAR(20) DEFAULT 'planned' CHECK (state IN ('planned', 'preparing', 'active', 'completed', 'cancelled')),
    
    company_id INTEGER NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    create_uid INTEGER,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    write_uid INTEGER,
    write_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Training and Competence (Floor 2)
-- =====================================================

-- BCM Training
CREATE TABLE IF NOT EXISTS bcm_training (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    training_type VARCHAR(50),
    description TEXT,
    target_audience VARCHAR(100),
    competency_area VARCHAR(100),
    
    -- Content
    learning_objectives TEXT,
    content_outline TEXT,
    assessment_method VARCHAR(100),
    
    -- Moodle integration
    moodle_course_id INTEGER,
    moodle_sync_status VARCHAR(20) DEFAULT 'pending',
    last_moodle_sync TIMESTAMP,
    
    -- Timing
    duration_hours NUMERIC(5,2),
    validity_months INTEGER DEFAULT 12,
    
    -- Status
    state VARCHAR(20) DEFAULT 'draft' CHECK (state IN ('draft', 'active', 'archived')),
    
    company_id INTEGER NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    create_uid INTEGER,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    write_uid INTEGER,
    write_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- KPIs and Metrics (Floor 1)
-- =====================================================

-- BCM KPIs
CREATE TABLE IF NOT EXISTS bcm_kpi (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    kpi_type VARCHAR(50),
    category VARCHAR(100),
    
    -- Measurement
    measurement_method VARCHAR(200),
    unit_of_measure VARCHAR(50),
    target_value NUMERIC(15,4),
    threshold_warning NUMERIC(15,4),
    threshold_critical NUMERIC(15,4),
    
    -- Data source
    data_source VARCHAR(200),
    calculation_formula TEXT,
    frequency VARCHAR(50),
    
    -- Current values
    current_value NUMERIC(15,4),
    last_measured TIMESTAMP,
    trend VARCHAR(20) CHECK (trend IN ('improving', 'stable', 'declining')),
    
    -- Responsibility
    owner_id INTEGER,
    reviewer_id INTEGER,
    
    company_id INTEGER NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    create_uid INTEGER,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    write_uid INTEGER,
    write_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Audit and Compliance (Floor 4)
-- =====================================================

-- BCM Audits
CREATE TABLE IF NOT EXISTS bcm_audit (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    audit_type VARCHAR(50),
    description TEXT,
    scope TEXT,
    
    -- Planning
    planned_start_date DATE,
    planned_end_date DATE,
    audit_program TEXT,
    audit_criteria TEXT,
    
    -- Execution
    actual_start_date DATE,
    actual_end_date DATE,
    audit_team TEXT, -- JSON array of auditor details
    
    -- Results
    findings_summary TEXT,
    conclusions TEXT,
    recommendations TEXT,
    
    -- Status
    state VARCHAR(20) DEFAULT 'planned' CHECK (state IN ('planned', 'in_progress', 'completed', 'cancelled')),
    
    company_id INTEGER NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    create_uid INTEGER,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    write_uid INTEGER,
    write_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Templates and Documents (Floor 4)
-- =====================================================

-- BCM Templates
CREATE TABLE IF NOT EXISTS bcm_template (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    template_type VARCHAR(50),
    description TEXT,
    category VARCHAR(100),
    
    -- Content
    template_content TEXT,
    placeholders TEXT, -- JSON object with placeholder definitions
    
    -- Usage
    usage_instructions TEXT,
    applicable_standards VARCHAR(200),
    
    -- Version control
    version VARCHAR(20) DEFAULT '1.0',
    approved_by INTEGER,
    approval_date DATE,
    
    company_id INTEGER NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    create_uid INTEGER,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    write_uid INTEGER,
    write_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Governance (Floor 5)
-- =====================================================

-- BCM Governance
CREATE TABLE IF NOT EXISTS bcm_governance (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    governance_type VARCHAR(50),
    description TEXT,
    
    -- Structure
    roles_responsibilities TEXT,
    authority_matrix TEXT,
    reporting_structure TEXT,
    
    -- Meetings and Reviews
    meeting_frequency VARCHAR(50),
    last_meeting_date DATE,
    next_meeting_date DATE,
    meeting_minutes TEXT,
    
    -- Decision making
    decision_criteria TEXT,
    escalation_procedures TEXT,
    
    company_id INTEGER NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    create_uid INTEGER,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    write_uid INTEGER,
    write_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Multi-tenancy and Client Management
-- =====================================================

-- BCM Clients (Multi-tenancy)
CREATE TABLE IF NOT EXISTS bcm_client (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    
    -- Configuration
    bcm_maturity_level VARCHAR(20) DEFAULT 'basic',
    iso_certification_status VARCHAR(50),
    industry_sector VARCHAR(100),
    employee_count INTEGER,
    annual_revenue NUMERIC(15,2),
    
    -- Tenant isolation
    database_schema VARCHAR(100),
    custom_domain VARCHAR(200),
    
    -- Subscription
    subscription_plan VARCHAR(50),
    subscription_start DATE,
    subscription_end DATE,
    max_users INTEGER DEFAULT 10,
    
    -- Status
    client_status VARCHAR(20) DEFAULT 'active' CHECK (client_status IN ('active', 'suspended', 'terminated')),
    onboarding_status VARCHAR(20) DEFAULT 'pending',
    
    company_id INTEGER NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    create_uid INTEGER,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    write_uid INTEGER,
    write_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Client API Keys
CREATE TABLE IF NOT EXISTS bcm_client_appkey (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES bcm_client(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    key_value VARCHAR(255) UNIQUE NOT NULL,
    key_type VARCHAR(50) DEFAULT 'api',
    
    -- Permissions
    permissions TEXT, -- JSON object with permissions
    ip_whitelist TEXT, -- JSON array of allowed IPs
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_date TIMESTAMP,
    last_used TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    
    company_id INTEGER NOT NULL,
    create_uid INTEGER,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    write_uid INTEGER,
    write_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- AI Integration Hub (Floor 5)
-- =====================================================

-- AI Services Configuration
CREATE TABLE IF NOT EXISTS bcm_ai_integration (
    id SERIAL PRIMARY KEY,
    sequence INTEGER DEFAULT 10,
    service_name VARCHAR(255) NOT NULL,
    service_type VARCHAR(50) NOT NULL CHECK (service_type IN ('orchestrator', 'bia_engine', 'document_processor', 'compliance_checker')),
    service_url VARCHAR(500) NOT NULL,
    api_key VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Health monitoring
    last_health_check TIMESTAMP,
    health_status VARCHAR(20) DEFAULT 'unknown' CHECK (health_status IN ('healthy', 'degraded', 'unhealthy', 'unknown')),
    
    company_id INTEGER NOT NULL,
    create_uid INTEGER,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    write_uid INTEGER,
    write_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Common Tables and Utilities
-- =====================================================

-- BCM Tags for categorization
CREATE TABLE IF NOT EXISTS bcm_tag (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    color INTEGER,
    description TEXT,
    active BOOLEAN DEFAULT TRUE,
    create_uid INTEGER,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    write_uid INTEGER,
    write_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Indexes for Performance
-- =====================================================

-- Core indexes
CREATE INDEX IF NOT EXISTS idx_bcm_context_company ON bcm_context(company_id);
CREATE INDEX IF NOT EXISTS idx_bcm_stakeholder_company ON bcm_stakeholder(company_id);
CREATE INDEX IF NOT EXISTS idx_bcm_business_process_company ON bcm_business_process(company_id);
CREATE INDEX IF NOT EXISTS idx_bcm_incident_company ON bcm_incident(company_id);
CREATE INDEX IF NOT EXISTS idx_bcm_plan_company ON bcm_plan(company_id);
CREATE INDEX IF NOT EXISTS idx_bcm_exercise_company ON bcm_exercise(company_id);
CREATE INDEX IF NOT EXISTS idx_bcm_training_company ON bcm_training(company_id);
CREATE INDEX IF NOT EXISTS idx_bcm_kpi_company ON bcm_kpi(company_id);
CREATE INDEX IF NOT EXISTS idx_bcm_audit_company ON bcm_audit(company_id);
CREATE INDEX IF NOT EXISTS idx_bcm_template_company ON bcm_template(company_id);
CREATE INDEX IF NOT EXISTS idx_bcm_governance_company ON bcm_governance(company_id);
CREATE INDEX IF NOT EXISTS idx_bcm_client_company ON bcm_client(company_id);

-- Performance indexes for common queries
CREATE INDEX IF NOT EXISTS idx_bcm_business_process_criticality ON bcm_business_process(criticality);
CREATE INDEX IF NOT EXISTS idx_bcm_incident_severity ON bcm_incident(severity);
CREATE INDEX IF NOT EXISTS idx_bcm_incident_status ON bcm_incident(status);
CREATE INDEX IF NOT EXISTS idx_bcm_plan_state ON bcm_plan(state);
CREATE INDEX IF NOT EXISTS idx_bcm_exercise_state ON bcm_exercise(state);
CREATE INDEX IF NOT EXISTS idx_bcm_kpi_category ON bcm_kpi(category);

-- Full text search indexes
CREATE INDEX IF NOT EXISTS idx_bcm_context_description_trgm ON bcm_context USING gin(description gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_bcm_business_process_name_trgm ON bcm_business_process USING gin(name gin_trgm_ops);

-- =====================================================
-- Demo Data Insertion (Optional)
-- =====================================================

-- Insert basic industry types
INSERT INTO bcm_industry_type (name, code, revenue_loss_multiplier, reputation_impact, company_id, create_uid) 
VALUES 
    ('Financial Services', 'FINANCE', 2.5, 3.0, 1, 1),
    ('Healthcare', 'HEALTH', 3.0, 4.0, 1, 1),
    ('Manufacturing', 'MANUFACTURING', 1.8, 2.0, 1, 1),
    ('Technology', 'TECH', 2.0, 2.5, 1, 1),
    ('Government', 'GOV', 1.5, 5.0, 1, 1)
ON CONFLICT (code) DO NOTHING;

-- Insert basic compliance requirements
INSERT INTO bcm_compliance_requirement (name, code, description, company_id, create_uid)
VALUES
    ('ISO 22301 Clause 4.1', 'ISO22301-4.1', 'Understanding the organization and its context', 1, 1),
    ('ISO 22301 Clause 8.2.2', 'ISO22301-8.2.2', 'Business impact analysis', 1, 1),
    ('PCI DSS', 'PCI-DSS', 'Payment Card Industry Data Security Standard', 1, 1),
    ('SOX', 'SOX', 'Sarbanes-Oxley Act compliance', 1, 1),
    ('GDPR', 'GDPR', 'General Data Protection Regulation', 1, 1)
ON CONFLICT (code) DO NOTHING;

-- Insert basic BCM tags
INSERT INTO bcm_tag (name, color, description)
VALUES
    ('High Priority', 1, 'High priority items requiring immediate attention'),
    ('ISO 22301', 2, 'Related to ISO 22301 standard'),
    ('Critical Process', 3, 'Critical business processes'),
    ('Financial', 4, 'Financial impact related'),
    ('Regulatory', 5, 'Regulatory compliance related'),
    ('Security', 6, 'Information security related')
ON CONFLICT (name) DO NOTHING;

-- =====================================================
-- Database Maintenance Functions
-- =====================================================

-- Function to update write_date automatically
CREATE OR REPLACE FUNCTION update_write_date()
RETURNS TRIGGER AS $$
BEGIN
    NEW.write_date = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply the trigger to all BCM tables
DO $$
DECLARE
    table_name text;
BEGIN
    FOR table_name IN 
        SELECT tablename FROM pg_tables 
        WHERE tablename LIKE 'bcm_%' AND schemaname = 'public'
    LOOP
        EXECUTE format('
            CREATE TRIGGER trigger_update_write_date_%s
            BEFORE UPDATE ON %s
            FOR EACH ROW
            EXECUTE FUNCTION update_write_date();
        ', table_name, table_name);
    END LOOP;
END
$$;

-- =====================================================
-- Views for Reporting and Analytics
-- =====================================================

-- BCM Dashboard Summary View
CREATE OR REPLACE VIEW bcm_dashboard_summary AS
SELECT 
    c.name as company_name,
    COUNT(DISTINCT bp.id) as total_processes,
    COUNT(DISTINCT CASE WHEN bp.criticality = 'critical' THEN bp.id END) as critical_processes,
    COUNT(DISTINCT i.id) as total_incidents,
    COUNT(DISTINCT CASE WHEN i.status = 'open' THEN i.id END) as open_incidents,
    COUNT(DISTINCT e.id) as total_exercises,
    COUNT(DISTINCT CASE WHEN e.state = 'completed' THEN e.id END) as completed_exercises,
    COUNT(DISTINCT t.id) as total_trainings,
    COUNT(DISTINCT a.id) as total_audits,
    AVG(bp.optimized_rto_hours) as avg_rto_hours
FROM res_company c
LEFT JOIN bcm_business_process bp ON bp.company_id = c.id
LEFT JOIN bcm_incident i ON i.company_id = c.id
LEFT JOIN bcm_exercise e ON e.company_id = c.id
LEFT JOIN bcm_training t ON t.company_id = c.id
LEFT JOIN bcm_audit a ON a.company_id = c.id
GROUP BY c.id, c.name;

-- BCM Risk Summary View
CREATE OR REPLACE VIEW bcm_risk_summary AS
SELECT 
    company_id,
    SUM(annual_risk_exposure) as total_annual_risk_exposure,
    AVG(optimized_rto_hours) as avg_rto_hours,
    AVG(optimized_rpo_minutes) as avg_rpo_minutes,
    COUNT(*) as total_processes,
    COUNT(CASE WHEN criticality = 'critical' THEN 1 END) as critical_processes,
    MAX(last_ai_analysis) as last_analysis_date
FROM bcm_business_process
WHERE active = true
GROUP BY company_id;

COMMENT ON DATABASE bcm_platform IS 'BCM Platform - ISO 22301:2019 Compliant Business Continuity Management System';
COMMENT ON SCHEMA public IS 'Main schema containing all BCM platform tables and business logic';

-- Grant permissions for Odoo user
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO odoo;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO odoo;
-- GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO odoo;
