-- Migration 026: Process Framework Tables
-- Date: 2025-10-11
-- Description: Tables for Process Framework - business process formalization, execution, and document generation

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- 1. PROCESS DEFINITIONS
-- =====================================================

-- Process definition versions (immutable)
CREATE TABLE IF NOT EXISTS process_definitions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    process_id VARCHAR(255) NOT NULL,  -- e.g., "bcm_bia_v1"
    name VARCHAR(500) NOT NULL,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    category VARCHAR(100),  -- e.g., "bcm_analysis", "bcm_planning"

    -- ISO compliance
    iso_clause VARCHAR(50),  -- e.g., "8.2.2" for BIA
    compliance_requirements JSONB DEFAULT '[]',

    -- Process structure
    start_step_id VARCHAR(255) NOT NULL,
    end_step_ids JSONB NOT NULL DEFAULT '[]',  -- Array of end step IDs

    -- Process metadata
    owner VARCHAR(255),
    tags JSONB DEFAULT '[]',

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(process_id, version)
);

CREATE INDEX idx_process_definitions_process_id ON process_definitions(process_id);
CREATE INDEX idx_process_definitions_category ON process_definitions(category);
CREATE INDEX idx_process_definitions_iso_clause ON process_definitions(iso_clause);

COMMENT ON TABLE process_definitions IS 'Process Framework - immutable process definitions';

-- =====================================================
-- 2. PROCESS STEPS
-- =====================================================

CREATE TABLE IF NOT EXISTS process_steps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    process_definition_id UUID NOT NULL REFERENCES process_definitions(id) ON DELETE CASCADE,

    -- Step identification
    step_id VARCHAR(255) NOT NULL,  -- e.g., "bia_initiation"
    name VARCHAR(500) NOT NULL,
    description TEXT,

    -- Step type
    step_type VARCHAR(100) NOT NULL,  -- FORM_INPUT, ANALYSIS, DECISION, APPROVAL, etc.

    -- Navigation
    next_steps JSONB DEFAULT '[]',  -- Array of next step IDs
    transition_conditions JSONB DEFAULT '{}',  -- Conditional transitions

    -- Access control
    allowed_roles JSONB DEFAULT '[]',  -- Array of role names

    -- Automation
    ai_agent VARCHAR(100),  -- e.g., "analytics_specialist"
    document_template VARCHAR(255),  -- e.g., "bia_report_template.docx"
    auto_approve BOOLEAN DEFAULT false,

    -- SLA
    estimated_duration_minutes INTEGER,
    sla_hours INTEGER,

    -- Form definition
    form_fields JSONB DEFAULT '[]',  -- Array of FormField objects

    -- Order in process
    step_order INTEGER,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(process_definition_id, step_id)
);

CREATE INDEX idx_process_steps_process_def ON process_steps(process_definition_id);
CREATE INDEX idx_process_steps_step_type ON process_steps(step_type);

COMMENT ON TABLE process_steps IS 'Process Framework - step definitions within processes';

-- =====================================================
-- 3. PROCESS INSTANCES (Runtime)
-- =====================================================

CREATE TABLE IF NOT EXISTS process_instances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    instance_id VARCHAR(500) NOT NULL UNIQUE,  -- e.g., "bcm_bia_v1-20251011120000"

    process_definition_id UUID NOT NULL REFERENCES process_definitions(id),

    -- Current state
    status VARCHAR(50) NOT NULL,  -- draft, active, in_progress, completed, suspended, cancelled
    current_step_id VARCHAR(255) NOT NULL,

    -- Execution history
    step_history JSONB DEFAULT '[]',  -- Array of step executions

    -- Process data (collected from forms)
    data JSONB DEFAULT '{}',

    -- Metadata
    started_by VARCHAR(255) NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,

    -- Participants
    participants JSONB DEFAULT '[]',  -- Array of email/usernames

    -- Generated documents
    documents JSONB DEFAULT '[]',  -- Array of {path, template_id, generated_at}

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_process_instances_process_def ON process_instances(process_definition_id);
CREATE INDEX idx_process_instances_status ON process_instances(status);
CREATE INDEX idx_process_instances_started_by ON process_instances(started_by);
CREATE INDEX idx_process_instances_started_at ON process_instances(started_at DESC);

COMMENT ON TABLE process_instances IS 'Process Framework - runtime process instances';

-- =====================================================
-- 4. STEP EXECUTIONS (Audit trail)
-- =====================================================

CREATE TABLE IF NOT EXISTS step_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    process_instance_id UUID NOT NULL REFERENCES process_instances(id) ON DELETE CASCADE,
    step_id VARCHAR(255) NOT NULL,

    -- Execution details
    executed_by VARCHAR(255) NOT NULL,  -- User email or "AI_System"
    executed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Input/Output
    input_data JSONB DEFAULT '{}',
    output_data JSONB DEFAULT '{}',

    -- Result
    result VARCHAR(50) NOT NULL,  -- success, failure, pending
    error_message TEXT,

    -- Duration
    duration_ms INTEGER,

    -- AI involvement
    ai_agent_used VARCHAR(100),
    ai_confidence FLOAT,  -- 0.0 to 1.0

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_step_executions_process_instance ON step_executions(process_instance_id);
CREATE INDEX idx_step_executions_executed_at ON step_executions(executed_at DESC);
CREATE INDEX idx_step_executions_step_id ON step_executions(step_id);

COMMENT ON TABLE step_executions IS 'Process Framework - audit trail of step executions';

-- =====================================================
-- 5. DOCUMENT TEMPLATES
-- =====================================================

CREATE TABLE IF NOT EXISTS document_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id VARCHAR(255) NOT NULL UNIQUE,  -- e.g., "bia_report_v1"

    name VARCHAR(500) NOT NULL,
    description TEXT,
    version VARCHAR(50) NOT NULL,

    -- Template metadata
    document_type VARCHAR(100) NOT NULL,  -- bia_report, risk_register, bc_plan
    iso_clause VARCHAR(50),

    -- Template structure (stored as JSONB for flexibility)
    header_template TEXT,
    footer_template TEXT,
    sections JSONB NOT NULL DEFAULT '[]',  -- Array of DocumentSection objects

    -- Styling
    style_config JSONB DEFAULT '{}',

    -- Required variables
    required_variables JSONB DEFAULT '[]',  -- Array of variable names

    -- Metadata
    created_by VARCHAR(255),
    tags JSONB DEFAULT '[]',

    -- Status
    status VARCHAR(50) DEFAULT 'active',  -- active, archived

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_document_templates_document_type ON document_templates(document_type);
CREATE INDEX idx_document_templates_status ON document_templates(status);

COMMENT ON TABLE document_templates IS 'Process Framework - document templates for generation';

-- =====================================================
-- 6. GENERATED DOCUMENTS
-- =====================================================

CREATE TABLE IF NOT EXISTS generated_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    process_instance_id UUID REFERENCES process_instances(id) ON DELETE SET NULL,
    template_id UUID NOT NULL REFERENCES document_templates(id),

    -- Document details
    document_name VARCHAR(500) NOT NULL,
    document_path TEXT NOT NULL,
    format VARCHAR(20) NOT NULL,  -- pdf, docx, html, md

    -- Generation details
    generated_by VARCHAR(255) NOT NULL,  -- User or "AI_DocGen"
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Variables used
    variables JSONB DEFAULT '{}',

    -- AI enrichment
    ai_enriched BOOLEAN DEFAULT false,
    ai_enrichments JSONB DEFAULT '{}',  -- What AI added (summary, recommendations, etc.)

    -- File metadata
    file_size_bytes BIGINT,
    checksum VARCHAR(64),  -- SHA256

    -- Version control
    version INTEGER DEFAULT 1,
    parent_document_id UUID REFERENCES generated_documents(id),

    -- Status
    status VARCHAR(50) DEFAULT 'generated',  -- generated, approved, archived

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_generated_documents_process_instance ON generated_documents(process_instance_id);
CREATE INDEX idx_generated_documents_template ON generated_documents(template_id);
CREATE INDEX idx_generated_documents_generated_at ON generated_documents(generated_at DESC);
CREATE INDEX idx_generated_documents_status ON generated_documents(status);

COMMENT ON TABLE generated_documents IS 'Process Framework - generated documents from templates';

-- =====================================================
-- 7. FORM VALIDATIONS (Optional - for complex validations)
-- =====================================================

CREATE TABLE IF NOT EXISTS form_validations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    process_instance_id UUID NOT NULL REFERENCES process_instances(id) ON DELETE CASCADE,
    step_id VARCHAR(255) NOT NULL,

    -- Validation details
    field_name VARCHAR(255) NOT NULL,
    validation_rule VARCHAR(100) NOT NULL,  -- required, min_length, pattern, etc.
    validation_value TEXT,

    -- Result
    is_valid BOOLEAN NOT NULL,
    error_message TEXT,

    -- Timing
    validated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_form_validations_process_instance ON form_validations(process_instance_id);
CREATE INDEX idx_form_validations_is_valid ON form_validations(is_valid);

COMMENT ON TABLE form_validations IS 'Process Framework - form validation audit trail';

-- =====================================================
-- 8. VIEWS FOR ANALYTICS
-- =====================================================

-- Process completion metrics
CREATE OR REPLACE VIEW process_completion_stats AS
SELECT
    pd.process_id,
    pd.name AS process_name,
    pd.category,
    COUNT(pi.id) AS total_instances,
    COUNT(CASE WHEN pi.status = 'completed' THEN 1 END) AS completed_instances,
    COUNT(CASE WHEN pi.status = 'in_progress' THEN 1 END) AS in_progress_instances,
    COUNT(CASE WHEN pi.status = 'suspended' THEN 1 END) AS suspended_instances,
    COUNT(CASE WHEN pi.status = 'cancelled' THEN 1 END) AS cancelled_instances,
    ROUND(AVG(EXTRACT(EPOCH FROM (pi.completed_at - pi.started_at)) / 60), 2) AS avg_duration_minutes,
    ROUND(CAST(COUNT(CASE WHEN pi.status = 'completed' THEN 1 END) AS FLOAT) / NULLIF(COUNT(pi.id), 0) * 100, 2) AS completion_rate_percent
FROM process_definitions pd
LEFT JOIN process_instances pi ON pd.id = pi.process_definition_id
GROUP BY pd.process_id, pd.name, pd.category;

COMMENT ON VIEW process_completion_stats IS 'Process Framework - completion statistics by process';

-- Step execution performance
CREATE OR REPLACE VIEW step_execution_stats AS
SELECT
    ps.step_id,
    ps.name AS step_name,
    ps.step_type,
    COUNT(se.id) AS total_executions,
    COUNT(CASE WHEN se.result = 'success' THEN 1 END) AS successful_executions,
    COUNT(CASE WHEN se.ai_agent_used IS NOT NULL THEN 1 END) AS ai_executions,
    ROUND(AVG(se.duration_ms), 2) AS avg_duration_ms,
    ROUND(AVG(CASE WHEN se.ai_agent_used IS NOT NULL THEN se.ai_confidence END), 3) AS avg_ai_confidence,
    ROUND(CAST(COUNT(CASE WHEN se.result = 'success' THEN 1 END) AS FLOAT) / NULLIF(COUNT(se.id), 0) * 100, 2) AS success_rate_percent
FROM process_steps ps
LEFT JOIN step_executions se ON ps.step_id = se.step_id
GROUP BY ps.step_id, ps.name, ps.step_type;

COMMENT ON VIEW step_execution_stats IS 'Process Framework - step execution statistics';

-- Document generation stats
CREATE OR REPLACE VIEW document_generation_stats AS
SELECT
    dt.template_id,
    dt.name AS template_name,
    dt.document_type,
    COUNT(gd.id) AS total_generated,
    COUNT(CASE WHEN gd.ai_enriched THEN 1 END) AS ai_enriched_count,
    COUNT(CASE WHEN gd.status = 'approved' THEN 1 END) AS approved_count,
    ROUND(AVG(gd.file_size_bytes / 1024.0), 2) AS avg_size_kb,
    MAX(gd.generated_at) AS last_generated_at
FROM document_templates dt
LEFT JOIN generated_documents gd ON dt.id = gd.template_id
GROUP BY dt.template_id, dt.name, dt.document_type;

COMMENT ON VIEW document_generation_stats IS 'Process Framework - document generation statistics';

-- =====================================================
-- 9. FUNCTIONS
-- =====================================================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to tables
CREATE TRIGGER update_process_definitions_updated_at BEFORE UPDATE ON process_definitions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_process_instances_updated_at BEFORE UPDATE ON process_instances
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_document_templates_updated_at BEFORE UPDATE ON document_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_generated_documents_updated_at BEFORE UPDATE ON generated_documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 10. SEED DATA - Standard BCM Processes
-- =====================================================

-- Insert BIA Process Definition
INSERT INTO process_definitions (
    process_id, name, version, description, category, iso_clause,
    compliance_requirements, start_step_id, end_step_ids, owner, tags
) VALUES (
    'bcm_bia_v1',
    'Business Impact Analysis',
    '1.0',
    'Formalized Business Impact Analysis process in accordance with ISO 22301',
    'bcm_analysis',
    '8.2.2',
    '["ISO 22301:2019 - Clause 8.2.2", "ISO 22313:2020 - BIA Guidelines"]',
    'bia_initiation',
    '["END"]',
    'BCM Team',
    '["BCM", "BIA", "ISO22301"]'
) ON CONFLICT (process_id, version) DO NOTHING;

-- Insert Risk Assessment Process Definition
INSERT INTO process_definitions (
    process_id, name, version, description, category, iso_clause,
    compliance_requirements, start_step_id, end_step_ids, owner, tags
) VALUES (
    'bcm_risk_assessment_v1',
    'Risk Assessment',
    '1.0',
    'Risk assessment process for business continuity',
    'bcm_analysis',
    '8.2.3',
    '["ISO 22301:2019 - Clause 8.2.3"]',
    'risk_identification',
    '["END"]',
    'Risk Management Team',
    '["BCM", "Risk", "ISO22301"]'
) ON CONFLICT (process_id, version) DO NOTHING;

-- Insert BC Plan Development Process Definition
INSERT INTO process_definitions (
    process_id, name, version, description, category, iso_clause,
    compliance_requirements, start_step_id, end_step_ids, owner, tags
) VALUES (
    'bcm_bc_plan_v1',
    'Business Continuity Plan Development',
    '1.0',
    'Development of Business Continuity Plan',
    'bcm_planning',
    '8.4',
    '["ISO 22301:2019 - Clause 8.4"]',
    'plan_initiation',
    '["END"]',
    'BCM Team',
    '["BCM", "BC Plan", "ISO22301"]'
) ON CONFLICT (process_id, version) DO NOTHING;

-- Insert Document Templates
INSERT INTO document_templates (
    template_id, name, version, description, document_type, iso_clause,
    required_variables, status
) VALUES (
    'bia_report_v1',
    'Business Impact Analysis Report',
    '1.0',
    'Standard BIA Report template compliant with ISO 22301',
    'bia_report',
    '8.2.2',
    '["organization_name", "analysis_date", "prepared_by", "scope", "critical_functions", "rto_summary", "rpo_summary", "impact_analysis"]',
    'active'
) ON CONFLICT (template_id) DO NOTHING;

INSERT INTO document_templates (
    template_id, name, version, description, document_type, iso_clause,
    required_variables, status
) VALUES (
    'risk_register_v1',
    'Risk Register',
    '1.0',
    'Risk Register template for BCM',
    'risk_register',
    '8.2.3',
    '["organization_name", "register_date", "risks"]',
    'active'
) ON CONFLICT (template_id) DO NOTHING;

INSERT INTO document_templates (
    template_id, name, version, description, document_type, iso_clause,
    required_variables, status
) VALUES (
    'bc_plan_v1',
    'Business Continuity Plan',
    '1.0',
    'BC Plan template',
    'bc_plan',
    '8.4',
    '["organization_name", "plan_date", "scope", "critical_functions", "recovery_strategies", "roles_responsibilities", "contact_list", "recovery_procedures"]',
    'active'
) ON CONFLICT (template_id) DO NOTHING;

-- =====================================================
-- 11. GRANTS (Adjust based on your role structure)
-- =====================================================

-- Grant permissions to application role (adjust role name as needed)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO workflow_intelligence_role;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO workflow_intelligence_role;

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

COMMENT ON SCHEMA public IS 'Process Framework migration 026 applied - 2025-10-11';
