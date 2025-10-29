-- =====================================================
-- BCM Platform: Unified Database Schema
-- Централизованная архитектура с proper foreign keys
-- =====================================================

-- Включаем расширения для UUID и других функций
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- =====================================================
-- CORE SYSTEM TABLES
-- =====================================================

-- Centralized Service Registry
CREATE TABLE IF NOT EXISTS bcm_service_registry (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) UNIQUE NOT NULL,
    service_url VARCHAR(255) NOT NULL,
    service_port INTEGER,
    health_endpoint VARCHAR(100) DEFAULT '/health',
    description TEXT,
    service_type VARCHAR(50), -- core, bcm_module, infrastructure, development
    status VARCHAR(20) DEFAULT 'unknown', -- healthy, degraded, unhealthy, unknown
    last_health_check TIMESTAMP WITH TIME ZONE,
    response_time_ms DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Centralized Event Bus Registry
CREATE TABLE IF NOT EXISTS bcm_event_registry (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    source_module VARCHAR(100) NOT NULL,
    target_module VARCHAR(100),
    description TEXT,
    schema_definition JSONB, -- JSON schema for event data validation
    handler_class VARCHAR(255),
    priority VARCHAR(20) DEFAULT 'normal', -- low, normal, high, critical
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(event_type, source_module)
);

-- Centralized Configuration Registry
CREATE TABLE IF NOT EXISTS bcm_config_registry (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(255) UNIQUE NOT NULL,
    config_value TEXT,
    config_type VARCHAR(50), -- string, integer, boolean, json, url
    service_name VARCHAR(100),
    description TEXT,
    is_encrypted BOOLEAN DEFAULT FALSE,
    is_required BOOLEAN DEFAULT FALSE,
    default_value TEXT,
    validation_rule TEXT, -- regex or JSON schema for validation
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (service_name) REFERENCES bcm_service_registry(service_name) ON DELETE SET NULL
);

-- =====================================================
-- CENTRALIZED CRM INTEGRATION TABLES
-- =====================================================

-- Unified CRM Projects (extends Odoo crm.lead)
CREATE TABLE IF NOT EXISTS bcm_crm_projects (
    id SERIAL PRIMARY KEY,
    odoo_lead_id INTEGER UNIQUE, -- Reference to Odoo crm.lead
    project_uuid UUID DEFAULT uuid_generate_v4(),
    partner_id INTEGER, -- Reference to Odoo res.partner
    partner_name VARCHAR(255),
    project_name VARCHAR(255) NOT NULL,
    stage_name VARCHAR(100),
    industry VARCHAR(100),
    employee_count INTEGER,
    compliance_target VARCHAR(100), -- iso_22301, iso_27001, etc.
    bcm_maturity_score DECIMAL(5,2) DEFAULT 0.0,
    iso_compliance_score DECIMAL(5,2) DEFAULT 0.0,
    implementation_progress DECIMAL(5,2) DEFAULT 0.0,
    project_manager_id INTEGER,
    status VARCHAR(50) DEFAULT 'active', -- active, won, lost, on_hold
    workspace_created BOOLEAN DEFAULT FALSE,
    workspace_created_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- BCM Workspace Structure (created when project is won)
CREATE TABLE IF NOT EXISTS bcm_workspaces (
    id SERIAL PRIMARY KEY,
    workspace_uuid UUID DEFAULT uuid_generate_v4(),
    crm_project_id INTEGER NOT NULL,
    organization_name VARCHAR(255) NOT NULL,
    workspace_status VARCHAR(50) DEFAULT 'initializing', -- initializing, active, maintenance, archived
    setup_progress DECIMAL(5,2) DEFAULT 0.0,
    modules_enabled JSONB, -- {"audit": true, "incident": true, "plans": true}
    configuration JSONB, -- Workspace-specific configuration
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (crm_project_id) REFERENCES bcm_crm_projects(id) ON DELETE CASCADE
);

-- =====================================================
-- UNIFIED BCM MODULE TABLES
-- =====================================================

-- Centralized Context (Organization Setup)
CREATE TABLE IF NOT EXISTS bcm_contexts (
    id SERIAL PRIMARY KEY,
    context_uuid UUID DEFAULT uuid_generate_v4(),
    workspace_id INTEGER NOT NULL,
    crm_project_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    maturity_level VARCHAR(50) DEFAULT 'initial', -- initial, developing, managed, optimized
    industry VARCHAR(100),
    employee_count INTEGER,
    compliance_targets TEXT[], -- Array of compliance standards
    risk_appetite VARCHAR(50), -- low, medium, high
    context_data JSONB, -- Additional context information
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workspace_id) REFERENCES bcm_workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (crm_project_id) REFERENCES bcm_crm_projects(id) ON DELETE CASCADE
);

-- Unified Audits
CREATE TABLE IF NOT EXISTS bcm_audits (
    id SERIAL PRIMARY KEY,
    audit_uuid UUID DEFAULT uuid_generate_v4(),
    workspace_id INTEGER NOT NULL,
    crm_project_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    audit_type VARCHAR(100), -- initial_assessment, internal_audit, external_audit, surveillance
    auditor_id INTEGER,
    scheduled_date DATE,
    completion_date DATE,
    status VARCHAR(50) DEFAULT 'scheduled', -- scheduled, in_progress, completed, cancelled
    compliance_score DECIMAL(5,2),
    findings_count INTEGER DEFAULT 0,
    critical_findings INTEGER DEFAULT 0,
    major_findings INTEGER DEFAULT 0,
    minor_findings INTEGER DEFAULT 0,
    audit_report_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workspace_id) REFERENCES bcm_workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (crm_project_id) REFERENCES bcm_crm_projects(id) ON DELETE CASCADE
);

-- Audit Findings
CREATE TABLE IF NOT EXISTS bcm_audit_findings (
    id SERIAL PRIMARY KEY,
    finding_uuid UUID DEFAULT uuid_generate_v4(),
    audit_id INTEGER NOT NULL,
    workspace_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    severity VARCHAR(50), -- critical, major, minor, observation
    requirement_reference VARCHAR(100), -- ISO clause reference
    evidence TEXT,
    recommendation TEXT,
    status VARCHAR(50) DEFAULT 'open', -- open, in_progress, closed, verified
    assigned_to_id INTEGER,
    due_date DATE,
    resolution_date DATE,
    resolution_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (audit_id) REFERENCES bcm_audits(id) ON DELETE CASCADE,
    FOREIGN KEY (workspace_id) REFERENCES bcm_workspaces(id) ON DELETE CASCADE
);

-- Unified Incidents
CREATE TABLE IF NOT EXISTS bcm_incidents (
    id SERIAL PRIMARY KEY,
    incident_uuid UUID DEFAULT uuid_generate_v4(),
    workspace_id INTEGER NOT NULL,
    crm_project_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    incident_type VARCHAR(100), -- cyber, natural_disaster, operational, supply_chain
    severity VARCHAR(50), -- low, medium, high, critical
    status VARCHAR(50) DEFAULT 'open', -- open, investigating, contained, resolved, closed
    reported_by_id INTEGER,
    assigned_to_id INTEGER,
    reported_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    detected_at TIMESTAMP WITH TIME ZONE,
    contained_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    impact_assessment JSONB, -- {"financial": 10000, "operational": "high", "reputational": "medium"}
    response_plan_activated BOOLEAN DEFAULT FALSE,
    lessons_learned TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workspace_id) REFERENCES bcm_workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (crm_project_id) REFERENCES bcm_crm_projects(id) ON DELETE CASCADE
);

-- Unified Plans
CREATE TABLE IF NOT EXISTS bcm_plans (
    id SERIAL PRIMARY KEY,
    plan_uuid UUID DEFAULT uuid_generate_v4(),
    workspace_id INTEGER NOT NULL,
    crm_project_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    plan_type VARCHAR(100), -- bcp, drp, crisis_management, communication, implementation
    version VARCHAR(20) DEFAULT '1.0',
    status VARCHAR(50) DEFAULT 'draft', -- draft, review, approved, active, archived
    owner_id INTEGER,
    approved_by_id INTEGER,
    approval_date DATE,
    review_date DATE,
    next_review_date DATE,
    activation_criteria TEXT,
    plan_content JSONB, -- Structured plan content
    document_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workspace_id) REFERENCES bcm_workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (crm_project_id) REFERENCES bcm_crm_projects(id) ON DELETE CASCADE
);

-- Unified Training
CREATE TABLE IF NOT EXISTS bcm_training (
    id SERIAL PRIMARY KEY,
    training_uuid UUID DEFAULT uuid_generate_v4(),
    workspace_id INTEGER NOT NULL,
    crm_project_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    training_type VARCHAR(100), -- awareness, technical, exercise, simulation
    description TEXT,
    target_audience VARCHAR(255),
    duration_hours DECIMAL(4,2),
    scheduled_date DATE,
    completion_date DATE,
    status VARCHAR(50) DEFAULT 'scheduled', -- scheduled, in_progress, completed, cancelled
    trainer_id INTEGER,
    attendees_count INTEGER DEFAULT 0,
    pass_rate DECIMAL(5,2),
    training_materials JSONB, -- Array of material references
    feedback_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workspace_id) REFERENCES bcm_workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (crm_project_id) REFERENCES bcm_crm_projects(id) ON DELETE CASCADE
);

-- =====================================================
-- EVENT BUS TABLES
-- =====================================================

-- Event Log (centralized event tracking)
CREATE TABLE IF NOT EXISTS bcm_event_log (
    id SERIAL PRIMARY KEY,
    event_uuid UUID DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,
    source_module VARCHAR(100) NOT NULL,
    target_module VARCHAR(100),
    workspace_id INTEGER,
    crm_project_id INTEGER,
    user_id INTEGER,
    event_data JSONB,
    priority VARCHAR(20) DEFAULT 'normal',
    status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed
    processing_started_at TIMESTAMP WITH TIME ZONE,
    processing_completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workspace_id) REFERENCES bcm_workspaces(id) ON DELETE SET NULL,
    FOREIGN KEY (crm_project_id) REFERENCES bcm_crm_projects(id) ON DELETE SET NULL
);

-- Event Processing Stats
CREATE TABLE IF NOT EXISTS bcm_event_stats (
    id SERIAL PRIMARY KEY,
    stat_date DATE DEFAULT CURRENT_DATE,
    event_type VARCHAR(100),
    source_module VARCHAR(100),
    events_count INTEGER DEFAULT 0,
    successful_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    avg_processing_time_ms DECIMAL(10,2),
    max_processing_time_ms DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stat_date, event_type, source_module)
);

-- =====================================================
-- GAMIFICATION TABLES
-- =====================================================

-- User Achievements (based on bcm_content_training_bridge pattern)
CREATE TABLE IF NOT EXISTS bcm_user_achievements (
    id SERIAL PRIMARY KEY,
    achievement_uuid UUID DEFAULT uuid_generate_v4(),
    user_id INTEGER NOT NULL,
    workspace_id INTEGER,
    points INTEGER DEFAULT 0,
    action_type VARCHAR(100), -- create, complete, review, assess, exercise
    content_type VARCHAR(100), -- template, plan, training, audit, incident
    content_ref VARCHAR(255), -- Reference to content (e.g., "bcm_plans,123")
    achievement_date DATE DEFAULT CURRENT_DATE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workspace_id) REFERENCES bcm_workspaces(id) ON DELETE SET NULL
);

-- Badge System
CREATE TABLE IF NOT EXISTS bcm_badges (
    id SERIAL PRIMARY KEY,
    badge_code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    badge_type VARCHAR(100), -- completion, expertise, milestone, special
    requirements JSONB, -- {"points": 1000, "activities": ["create", "complete"]}
    icon_path VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User Badges (many-to-many)
CREATE TABLE IF NOT EXISTS bcm_user_badges (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    badge_id INTEGER NOT NULL,
    workspace_id INTEGER,
    earned_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (badge_id) REFERENCES bcm_badges(id) ON DELETE CASCADE,
    FOREIGN KEY (workspace_id) REFERENCES bcm_workspaces(id) ON DELETE SET NULL,
    UNIQUE(user_id, badge_id, workspace_id)
);

-- =====================================================
-- MONITORING & METRICS TABLES
-- =====================================================

-- Service Health History
CREATE TABLE IF NOT EXISTS bcm_service_health_log (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    check_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20), -- healthy, degraded, unhealthy
    response_time_ms DECIMAL(10,2),
    error_message TEXT,
    additional_metrics JSONB,
    FOREIGN KEY (service_name) REFERENCES bcm_service_registry(service_name) ON DELETE CASCADE
);

-- System Metrics
CREATE TABLE IF NOT EXISTS bcm_system_metrics (
    id SERIAL PRIMARY KEY,
    metric_date DATE DEFAULT CURRENT_DATE,
    metric_hour INTEGER DEFAULT EXTRACT(HOUR FROM CURRENT_TIMESTAMP), -- 0-23
    total_requests INTEGER DEFAULT 0,
    successful_requests INTEGER DEFAULT 0,
    failed_requests INTEGER DEFAULT 0,
    avg_response_time_ms DECIMAL(10,2),
    active_users INTEGER DEFAULT 0,
    active_workspaces INTEGER DEFAULT 0,
    events_processed INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(metric_date, metric_hour)
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Service Registry Indexes
CREATE INDEX IF NOT EXISTS idx_service_registry_name ON bcm_service_registry(service_name);
CREATE INDEX IF NOT EXISTS idx_service_registry_type ON bcm_service_registry(service_type);
CREATE INDEX IF NOT EXISTS idx_service_registry_status ON bcm_service_registry(status);

-- CRM Projects Indexes
CREATE INDEX IF NOT EXISTS idx_crm_projects_odoo_lead ON bcm_crm_projects(odoo_lead_id);
CREATE INDEX IF NOT EXISTS idx_crm_projects_partner ON bcm_crm_projects(partner_id);
CREATE INDEX IF NOT EXISTS idx_crm_projects_status ON bcm_crm_projects(status);
CREATE INDEX IF NOT EXISTS idx_crm_projects_uuid ON bcm_crm_projects(project_uuid);

-- Workspace Indexes
CREATE INDEX IF NOT EXISTS idx_workspaces_crm_project ON bcm_workspaces(crm_project_id);
CREATE INDEX IF NOT EXISTS idx_workspaces_status ON bcm_workspaces(workspace_status);
CREATE INDEX IF NOT EXISTS idx_workspaces_uuid ON bcm_workspaces(workspace_uuid);

-- BCM Module Indexes
CREATE INDEX IF NOT EXISTS idx_contexts_workspace ON bcm_contexts(workspace_id);
CREATE INDEX IF NOT EXISTS idx_contexts_crm_project ON bcm_contexts(crm_project_id);
CREATE INDEX IF NOT EXISTS idx_audits_workspace ON bcm_audits(workspace_id);
CREATE INDEX IF NOT EXISTS idx_audits_crm_project ON bcm_audits(crm_project_id);
CREATE INDEX IF NOT EXISTS idx_audits_status ON bcm_audits(status);
CREATE INDEX IF NOT EXISTS idx_incidents_workspace ON bcm_incidents(workspace_id);
CREATE INDEX IF NOT EXISTS idx_incidents_severity ON bcm_incidents(severity);
CREATE INDEX IF NOT EXISTS idx_incidents_status ON bcm_incidents(status);

-- Event Log Indexes
CREATE INDEX IF NOT EXISTS idx_event_log_type ON bcm_event_log(event_type);
CREATE INDEX IF NOT EXISTS idx_event_log_source ON bcm_event_log(source_module);
CREATE INDEX IF NOT EXISTS idx_event_log_status ON bcm_event_log(status);
CREATE INDEX IF NOT EXISTS idx_event_log_created ON bcm_event_log(created_at);
CREATE INDEX IF NOT EXISTS idx_event_log_workspace ON bcm_event_log(workspace_id);

-- Monitoring Indexes
CREATE INDEX IF NOT EXISTS idx_service_health_log_service ON bcm_service_health_log(service_name);
CREATE INDEX IF NOT EXISTS idx_service_health_log_time ON bcm_service_health_log(check_time);
CREATE INDEX IF NOT EXISTS idx_system_metrics_date ON bcm_system_metrics(metric_date, metric_hour);

-- =====================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- =====================================================

-- Update timestamps automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update triggers to all tables with updated_at
CREATE TRIGGER update_bcm_service_registry_updated_at BEFORE UPDATE ON bcm_service_registry FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bcm_event_registry_updated_at BEFORE UPDATE ON bcm_event_registry FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bcm_config_registry_updated_at BEFORE UPDATE ON bcm_config_registry FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bcm_crm_projects_updated_at BEFORE UPDATE ON bcm_crm_projects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bcm_workspaces_updated_at BEFORE UPDATE ON bcm_workspaces FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bcm_contexts_updated_at BEFORE UPDATE ON bcm_contexts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bcm_audits_updated_at BEFORE UPDATE ON bcm_audits FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bcm_incidents_updated_at BEFORE UPDATE ON bcm_incidents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bcm_plans_updated_at BEFORE UPDATE ON bcm_plans FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bcm_training_updated_at BEFORE UPDATE ON bcm_training FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- SAMPLE DATA INSERTION
-- =====================================================

-- Insert Service Registry entries
INSERT INTO bcm_service_registry (service_name, service_url, service_port, service_type, description) VALUES
    ('unified_database_gateway', 'http://unified_database_gateway:8888', 8888, 'core', 'Centralized database access gateway'),
    ('unified_api_gateway', 'http://unified_api_gateway:8777', 8777, 'core', 'Centralized API routing gateway'),
    ('crm_bridge', 'http://crm_bridge:8778', 8778, 'core', 'CRM integration bridge service'),
    ('monitoring_service', 'http://monitoring_service:8779', 8779, 'core', 'Centralized monitoring and logging'),
    ('odoo', 'http://odoo:8069', 8069, 'core', 'Odoo BCM Core application'),
    ('ai_orchestrator', 'http://ai_orchestrator:8000', 8000, 'core', 'AI services orchestrator'),
    ('bia_engine', 'http://bia_engine:8082', 8082, 'bcm_module', 'Business Impact Analysis engine'),
    ('document_processor', 'http://document_processor:8083', 8083, 'bcm_module', 'Document processing service'),
    ('compliance_checker', 'http://compliance_checker:8084', 8084, 'bcm_module', 'Compliance checking service'),
    ('scenario_orchestrator', 'http://scenario_orchestrator:8085', 8085, 'bcm_module', 'Scenario orchestration service')
ON CONFLICT (service_name) DO UPDATE SET
    service_url = EXCLUDED.service_url,
    service_port = EXCLUDED.service_port,
    description = EXCLUDED.description,
    updated_at = CURRENT_TIMESTAMP;

-- Insert Event Registry entries
INSERT INTO bcm_event_registry (event_type, source_module, target_module, description, handler_class) VALUES
    ('project.won', 'crm_project', 'crm_bridge', 'Project won in CRM, create BCM workspace', 'CrmProjectEventHandler'),
    ('project.stage_changed', 'crm_project', 'crm_bridge', 'Project stage changed', 'CrmProjectEventHandler'),
    ('project.lost', 'crm_project', 'crm_bridge', 'Project lost, archive workspace', 'CrmProjectEventHandler'),
    ('audit.completed', 'bcm_audit', 'crm_bridge', 'Audit completed, update compliance score', 'AuditEventHandler'),
    ('audit.finding_created', 'bcm_audit', 'crm_bridge', 'New audit finding created', 'AuditEventHandler'),
    ('incident.critical', 'bcm_incident', 'crm_bridge', 'Critical incident reported', 'IncidentEventHandler'),
    ('incident.resolved', 'bcm_incident', 'crm_bridge', 'Incident resolved', 'IncidentEventHandler'),
    ('content.created', 'bcm_content', 'crm_bridge', 'Content created for gamification', 'GamificationEventHandler'),
    ('training.completed', 'bcm_training', 'crm_bridge', 'Training completed for gamification', 'GamificationEventHandler'),
    ('assessment.passed', 'bcm_assessment', 'crm_bridge', 'Assessment passed for certification', 'GamificationEventHandler')
ON CONFLICT (event_type, source_module) DO UPDATE SET
    description = EXCLUDED.description,
    handler_class = EXCLUDED.handler_class,
    updated_at = CURRENT_TIMESTAMP;

-- Insert Badge System
INSERT INTO bcm_badges (badge_code, name, description, badge_type, requirements) VALUES
    ('content_creator', 'Content Creator', 'Created first BCM content', 'completion', '{"points": 50, "activities": ["create"]}'),
    ('audit_expert', 'Audit Expert', 'Completed 5 audits successfully', 'expertise', '{"audits_completed": 5}'),
    ('incident_responder', 'Incident Responder', 'Responded to critical incident', 'milestone', '{"critical_incidents": 1}'),
    ('bcm_champion', 'BCM Champion', 'Achieved 1000 points in BCM activities', 'special', '{"points": 1000}'),
    ('trainer', 'Trainer', 'Conducted BCM training session', 'completion', '{"trainings_conducted": 1}')
ON CONFLICT (badge_code) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    requirements = EXCLUDED.requirements;

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- Comprehensive Project Overview
CREATE OR REPLACE VIEW v_project_overview AS
SELECT
    p.id as project_id,
    p.project_uuid,
    p.odoo_lead_id,
    p.partner_name,
    p.project_name,
    p.stage_name,
    p.status as project_status,
    p.bcm_maturity_score,
    p.iso_compliance_score,
    p.implementation_progress,
    w.workspace_uuid,
    w.workspace_status,
    w.setup_progress,
    c.name as context_name,
    c.maturity_level,
    COUNT(DISTINCT a.id) as audit_count,
    COUNT(DISTINCT i.id) as incident_count,
    COUNT(DISTINCT pl.id) as plan_count,
    COUNT(DISTINCT t.id) as training_count,
    p.created_at as project_created,
    w.created_at as workspace_created
FROM bcm_crm_projects p
LEFT JOIN bcm_workspaces w ON p.id = w.crm_project_id
LEFT JOIN bcm_contexts c ON w.id = c.workspace_id
LEFT JOIN bcm_audits a ON w.id = a.workspace_id
LEFT JOIN bcm_incidents i ON w.id = i.workspace_id
LEFT JOIN bcm_plans pl ON w.id = pl.workspace_id
LEFT JOIN bcm_training t ON w.id = t.workspace_id
GROUP BY p.id, w.id, c.id;

-- Service Health Summary
CREATE OR REPLACE VIEW v_service_health_summary AS
SELECT
    sr.service_name,
    sr.service_type,
    sr.service_url,
    sr.status as current_status,
    sr.response_time_ms as current_response_time,
    sr.last_health_check,
    AVG(shl.response_time_ms) as avg_response_time_24h,
    COUNT(CASE WHEN shl.status = 'healthy' THEN 1 END) * 100.0 / COUNT(*) as uptime_percentage_24h,
    COUNT(*) as health_checks_24h
FROM bcm_service_registry sr
LEFT JOIN bcm_service_health_log shl ON sr.service_name = shl.service_name
    AND shl.check_time > CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY sr.service_name, sr.service_type, sr.service_url, sr.status, sr.response_time_ms, sr.last_health_check;

-- Event Processing Summary
CREATE OR REPLACE VIEW v_event_processing_summary AS
SELECT
    el.event_type,
    el.source_module,
    COUNT(*) as total_events,
    COUNT(CASE WHEN el.status = 'completed' THEN 1 END) as successful_events,
    COUNT(CASE WHEN el.status = 'failed' THEN 1 END) as failed_events,
    AVG(EXTRACT(EPOCH FROM (el.processing_completed_at - el.processing_started_at)) * 1000) as avg_processing_time_ms,
    MAX(EXTRACT(EPOCH FROM (el.processing_completed_at - el.processing_started_at)) * 1000) as max_processing_time_ms
FROM bcm_event_log el
WHERE el.created_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY el.event_type, el.source_module;

-- =====================================================
-- FUNCTIONS FOR DATA OPERATIONS
-- =====================================================

-- Function to create BCM workspace when project is won
CREATE OR REPLACE FUNCTION create_bcm_workspace(
    p_crm_project_id INTEGER,
    p_organization_name VARCHAR(255)
) RETURNS UUID AS $$
DECLARE
    v_workspace_uuid UUID;
    v_workspace_id INTEGER;
    v_context_id INTEGER;
BEGIN
    -- Create workspace
    INSERT INTO bcm_workspaces (crm_project_id, organization_name, workspace_status)
    VALUES (p_crm_project_id, p_organization_name, 'initializing')
    RETURNING workspace_uuid, id INTO v_workspace_uuid, v_workspace_id;

    -- Create initial context
    INSERT INTO bcm_contexts (workspace_id, crm_project_id, name, maturity_level)
    VALUES (v_workspace_id, p_crm_project_id, p_organization_name, 'initial')
    RETURNING id INTO v_context_id;

    -- Mark project as workspace created
    UPDATE bcm_crm_projects
    SET workspace_created = TRUE, workspace_created_at = CURRENT_TIMESTAMP
    WHERE id = p_crm_project_id;

    -- Log the event
    INSERT INTO bcm_event_log (event_type, source_module, workspace_id, crm_project_id, event_data, status)
    VALUES ('workspace.created', 'database_function', v_workspace_id, p_crm_project_id,
            jsonb_build_object('workspace_uuid', v_workspace_uuid, 'organization_name', p_organization_name),
            'completed');

    RETURN v_workspace_uuid;
END;
$$ LANGUAGE plpgsql;

-- Function to update service health
CREATE OR REPLACE FUNCTION update_service_health(
    p_service_name VARCHAR(100),
    p_status VARCHAR(20),
    p_response_time_ms DECIMAL(10,2),
    p_error_message TEXT DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    -- Update service registry
    UPDATE bcm_service_registry
    SET status = p_status,
        response_time_ms = p_response_time_ms,
        last_health_check = CURRENT_TIMESTAMP
    WHERE service_name = p_service_name;

    -- Log health check
    INSERT INTO bcm_service_health_log (service_name, status, response_time_ms, error_message)
    VALUES (p_service_name, p_status, p_response_time_ms, p_error_message);
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- CLEANUP AND MAINTENANCE PROCEDURES
-- =====================================================

-- Function to cleanup old logs (keep last 30 days)
CREATE OR REPLACE FUNCTION cleanup_old_logs() RETURNS INTEGER AS $$
DECLARE
    v_deleted_count INTEGER;
BEGIN
    -- Delete old service health logs
    DELETE FROM bcm_service_health_log
    WHERE check_time < CURRENT_TIMESTAMP - INTERVAL '30 days';
    GET DIAGNOSTICS v_deleted_count = ROW_COUNT;

    -- Delete old event logs (keep last 7 days for completed events)
    DELETE FROM bcm_event_log
    WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '7 days'
    AND status = 'completed';

    -- Delete old system metrics (keep last 90 days)
    DELETE FROM bcm_system_metrics
    WHERE metric_date < CURRENT_DATE - INTERVAL '90 days';

    RETURN v_deleted_count;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- GRANTS AND PERMISSIONS
-- =====================================================

-- Create monitoring user for read-only access
-- CREATE USER bcm_monitor WITH PASSWORD 'monitor_pass_2024';
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO bcm_monitor;
-- GRANT USAGE ON SCHEMA public TO bcm_monitor;

-- Create api user for application access
-- CREATE USER bcm_api WITH PASSWORD 'api_pass_2024';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO bcm_api;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO bcm_api;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO bcm_api;

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON TABLE bcm_service_registry IS 'Central registry of all BCM platform services';
COMMENT ON TABLE bcm_event_registry IS 'Registry of all event types and their handlers';
COMMENT ON TABLE bcm_crm_projects IS 'Unified CRM projects with BCM integration';
COMMENT ON TABLE bcm_workspaces IS 'BCM workspaces created for each won project';
COMMENT ON TABLE bcm_event_log IS 'Centralized log of all system events';
COMMENT ON TABLE bcm_user_achievements IS 'Gamification achievements for users';

COMMENT ON FUNCTION create_bcm_workspace IS 'Creates a complete BCM workspace when project is won';
COMMENT ON FUNCTION update_service_health IS 'Updates service health status and logs the check';
COMMENT ON FUNCTION cleanup_old_logs IS 'Cleanup procedure for old logs and metrics';

-- =====================================================
-- END OF SCHEMA
-- =====================================================