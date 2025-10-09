-- ============================================================================
-- BIA MODULE - DATABASE SCHEMA (PostgreSQL + Supabase)
-- ============================================================================
-- Version: 1.0
-- Date: 2025-10-09
-- Based on: SRS_BIA_MODULE.md
-- Target: Supabase PostgreSQL 15+
-- ============================================================================

-- ============================================================================
-- SECTION 1: CORE BIA TABLES
-- ============================================================================

-- BIA Analysis (главная таблица анализа)
CREATE TABLE bia_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,

    -- Metadata
    name VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'in_progress', 'completed', 'archived')),
    collection_method VARCHAR(50) CHECK (collection_method IN ('questionnaire', 'document_upload', 'erp_integration', 'hybrid')),

    -- AI Processing
    ai_processing_status VARCHAR(50) DEFAULT 'pending' CHECK (ai_processing_status IN ('pending', 'processing', 'completed', 'failed')),
    ai_model_version VARCHAR(50),

    -- Compliance & Scoring
    compliance_score INTEGER CHECK (compliance_score >= 0 AND compliance_score <= 100),
    iso_22301_coverage JSONB, -- {clause_8_2: true, clause_8_2_3: true, ...}

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Audit
    created_by UUID REFERENCES auth.users(id),
    last_modified_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_bia_analyses_org ON bia_analyses(organization_id);
CREATE INDEX idx_bia_analyses_status ON bia_analyses(status);
CREATE INDEX idx_bia_analyses_created_at ON bia_analyses(created_at DESC);

-- ============================================================================
-- SECTION 2: PROCESS IDENTIFICATION
-- ============================================================================

-- Business Processes
CREATE TABLE bia_processes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bia_analysis_id UUID NOT NULL REFERENCES bia_analyses(id) ON DELETE CASCADE,

    -- Process Info
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100), -- 'core_business', 'support', 'management'
    owner_department VARCHAR(100),
    owner_person VARCHAR(255),

    -- Criticality Assessment
    criticality VARCHAR(50) NOT NULL CHECK (criticality IN ('critical', 'high', 'medium', 'low')),
    criticality_score INTEGER CHECK (criticality_score >= 0 AND criticality_score <= 100),

    -- Time Objectives (in hours)
    rto_hours INTEGER, -- Recovery Time Objective
    rpo_hours INTEGER, -- Recovery Point Objective
    mtpd_hours INTEGER, -- Maximum Tolerable Period of Disruption

    -- Financial Impact
    financial_impact_per_hour DECIMAL(15,2),
    financial_impact_daily DECIMAL(15,2),
    financial_impact_weekly DECIMAL(15,2),
    revenue_percentage DECIMAL(5,2), -- % of total org revenue

    -- Operational Impact
    employees_affected INTEGER,
    customers_affected INTEGER,
    regulatory_impact BOOLEAN DEFAULT FALSE,
    reputational_risk VARCHAR(50) CHECK (reputational_risk IN ('critical', 'high', 'medium', 'low', 'none')),

    -- AI-generated insights
    ai_recommendations TEXT,
    industry_benchmark JSONB, -- {rto_range: "2-6 hours", similar_orgs: 347}

    -- Source tracking
    data_source VARCHAR(50) CHECK (data_source IN ('questionnaire', 'document', 'erp', 'manual')),
    source_confidence DECIMAL(3,2) CHECK (source_confidence >= 0 AND source_confidence <= 1), -- 0.0 to 1.0

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_bia_processes_analysis ON bia_processes(bia_analysis_id);
CREATE INDEX idx_bia_processes_criticality ON bia_processes(criticality);
CREATE INDEX idx_bia_processes_category ON bia_processes(category);

-- ============================================================================
-- SECTION 3: DEPENDENCIES & RELATIONSHIPS
-- ============================================================================

-- Process Dependencies (граф зависимостей)
CREATE TABLE bia_dependencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bia_analysis_id UUID NOT NULL REFERENCES bia_analyses(id) ON DELETE CASCADE,

    source_process_id UUID NOT NULL REFERENCES bia_processes(id) ON DELETE CASCADE,
    target_process_id UUID NOT NULL REFERENCES bia_processes(id) ON DELETE CASCADE,

    -- Dependency characteristics
    dependency_type VARCHAR(50) NOT NULL CHECK (dependency_type IN ('hard', 'soft', 'optional', 'cascading')),
    dependency_strength INTEGER CHECK (dependency_strength >= 1 AND dependency_strength <= 10), -- 1=weak, 10=critical

    -- Impact analysis
    cascade_impact_hours INTEGER, -- if source fails, target fails after X hours

    -- AI detection
    ai_detected BOOLEAN DEFAULT FALSE,
    detection_confidence DECIMAL(3,2) CHECK (detection_confidence >= 0 AND detection_confidence <= 1),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_bia_deps_analysis ON bia_dependencies(bia_analysis_id);
CREATE INDEX idx_bia_deps_source ON bia_dependencies(source_process_id);
CREATE INDEX idx_bia_deps_target ON bia_dependencies(target_process_id);

-- Prevent circular dependencies
ALTER TABLE bia_dependencies ADD CONSTRAINT no_self_dependency
    CHECK (source_process_id != target_process_id);

-- ============================================================================
-- SECTION 4: DATA COLLECTION - QUESTIONNAIRE
-- ============================================================================

-- AI-Generated Questions
CREATE TABLE bia_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bia_analysis_id UUID NOT NULL REFERENCES bia_analyses(id) ON DELETE CASCADE,

    -- Question content
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL CHECK (question_type IN ('text', 'number', 'choice', 'multiple_choice', 'scale')),
    question_category VARCHAR(100), -- 'process_identification', 'impact_assessment', 'recovery_objectives'

    -- Options (for choice questions)
    options JSONB, -- ["Option A", "Option B", "Option C"]

    -- AI metadata
    ai_generated BOOLEAN DEFAULT TRUE,
    ai_prefilled_answer TEXT, -- AI suggestion from knowledge base
    ai_confidence DECIMAL(3,2),

    -- Question order
    sequence_number INTEGER NOT NULL,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_bia_questions_analysis ON bia_questions(bia_analysis_id);
CREATE INDEX idx_bia_questions_sequence ON bia_questions(bia_analysis_id, sequence_number);

-- User Answers
CREATE TABLE bia_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL REFERENCES bia_questions(id) ON DELETE CASCADE,

    -- Answer content
    answer_text TEXT,
    answer_number DECIMAL(15,2),
    answer_choice JSONB, -- can be array for multiple choice

    -- Validation
    validated BOOLEAN DEFAULT FALSE,
    validation_notes TEXT,

    -- Audit
    answered_by UUID REFERENCES auth.users(id),
    answered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_bia_answers_question ON bia_answers(question_id);

-- ============================================================================
-- SECTION 5: DATA COLLECTION - DOCUMENT UPLOAD
-- ============================================================================

-- Uploaded Documents
CREATE TABLE bia_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bia_analysis_id UUID NOT NULL REFERENCES bia_analyses(id) ON DELETE CASCADE,

    -- File info
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50), -- 'pdf', 'docx', 'xlsx', 'image'
    file_size_bytes BIGINT,
    storage_path TEXT NOT NULL, -- Supabase Storage path

    -- OCR Processing
    ocr_status VARCHAR(50) DEFAULT 'pending' CHECK (ocr_status IN ('pending', 'processing', 'completed', 'failed')),
    ocr_text TEXT,
    ocr_confidence DECIMAL(3,2),

    -- AI Extraction
    ai_extraction_status VARCHAR(50) DEFAULT 'pending' CHECK (ai_extraction_status IN ('pending', 'processing', 'completed', 'failed')),
    ai_extracted_data JSONB, -- structured data extracted by AI

    -- Metadata
    uploaded_by UUID REFERENCES auth.users(id),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_bia_documents_analysis ON bia_documents(bia_analysis_id);
CREATE INDEX idx_bia_documents_status ON bia_documents(ocr_status, ai_extraction_status);

-- ============================================================================
-- SECTION 6: DATA COLLECTION - ERP INTEGRATION
-- ============================================================================

-- ERP Connections
CREATE TABLE bia_erp_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bia_analysis_id UUID NOT NULL REFERENCES bia_analyses(id) ON DELETE CASCADE,

    -- ERP Info
    erp_type VARCHAR(50) NOT NULL CHECK (erp_type IN ('odoo', 'sap', 'oracle', 'custom')),
    erp_url TEXT NOT NULL,

    -- Credentials (encrypted)
    credentials_encrypted TEXT, -- encrypted JSON

    -- Connection status
    connection_status VARCHAR(50) DEFAULT 'disconnected' CHECK (connection_status IN ('connected', 'disconnected', 'error')),
    last_sync_at TIMESTAMP WITH TIME ZONE,
    sync_frequency VARCHAR(50), -- 'manual', 'daily', 'weekly'

    -- Mapping
    field_mapping JSONB, -- {odoo_field: 'sale.order.line', bia_field: 'revenue'}

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_bia_erp_analysis ON bia_erp_connections(bia_analysis_id);

-- ERP Sync Logs
CREATE TABLE bia_erp_sync_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    erp_connection_id UUID NOT NULL REFERENCES bia_erp_connections(id) ON DELETE CASCADE,

    sync_status VARCHAR(50) NOT NULL CHECK (sync_status IN ('success', 'partial', 'failed')),
    records_synced INTEGER,
    errors JSONB,

    synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- SECTION 7: AI PROCESSING & ANALYSIS
-- ============================================================================

-- AI Analysis Jobs (для фоновых задач)
CREATE TABLE bia_ai_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bia_analysis_id UUID NOT NULL REFERENCES bia_analyses(id) ON DELETE CASCADE,

    job_type VARCHAR(50) NOT NULL CHECK (job_type IN ('process_mapping', 'rto_calculation', 'financial_impact', 'monte_carlo')),
    status VARCHAR(50) DEFAULT 'queued' CHECK (status IN ('queued', 'running', 'completed', 'failed')),

    -- Input/Output
    input_data JSONB,
    output_data JSONB,

    -- Execution details
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_bia_ai_jobs_analysis ON bia_ai_jobs(bia_analysis_id);
CREATE INDEX idx_bia_ai_jobs_status ON bia_ai_jobs(status);

-- Monte Carlo Simulation Results
CREATE TABLE bia_monte_carlo_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bia_analysis_id UUID NOT NULL REFERENCES bia_analyses(id) ON DELETE CASCADE,
    process_id UUID REFERENCES bia_processes(id) ON DELETE CASCADE,

    -- Simulation parameters
    iterations INTEGER DEFAULT 10000,

    -- Results
    financial_impact_best_case DECIMAL(15,2),
    financial_impact_likely_case DECIMAL(15,2),
    financial_impact_worst_case DECIMAL(15,2),

    -- Distribution data (for charts)
    distribution_data JSONB, -- [{value: 10000, probability: 0.15}, ...]

    -- Cascading impact included
    includes_cascade BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_monte_carlo_analysis ON bia_monte_carlo_results(bia_analysis_id);
CREATE INDEX idx_monte_carlo_process ON bia_monte_carlo_results(process_id);

-- ============================================================================
-- SECTION 8: FINDINGS & RECOMMENDATIONS
-- ============================================================================

-- BIA Findings (AI-generated insights)
CREATE TABLE bia_findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bia_analysis_id UUID NOT NULL REFERENCES bia_analyses(id) ON DELETE CASCADE,

    finding_type VARCHAR(50) NOT NULL CHECK (finding_type IN ('gap', 'risk', 'opportunity', 'recommendation')),
    severity VARCHAR(50) CHECK (severity IN ('critical', 'high', 'medium', 'low', 'info')),

    -- Content
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    affected_processes JSONB, -- array of process IDs

    -- ISO mapping
    iso_clause VARCHAR(50), -- e.g., "8.2.3"

    -- Recommendation
    recommended_action TEXT,
    estimated_effort VARCHAR(50), -- 'low', 'medium', 'high'
    priority INTEGER CHECK (priority >= 1 AND priority <= 10),

    -- AI metadata
    ai_generated BOOLEAN DEFAULT TRUE,
    ai_confidence DECIMAL(3,2),

    -- User interaction
    status VARCHAR(50) DEFAULT 'new' CHECK (status IN ('new', 'acknowledged', 'in_progress', 'resolved', 'dismissed')),
    user_notes TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_bia_findings_analysis ON bia_findings(bia_analysis_id);
CREATE INDEX idx_bia_findings_severity ON bia_findings(severity);
CREATE INDEX idx_bia_findings_status ON bia_findings(status);

-- ============================================================================
-- SECTION 9: REPORTS
-- ============================================================================

-- Generated Reports
CREATE TABLE bia_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bia_analysis_id UUID NOT NULL REFERENCES bia_analyses(id) ON DELETE CASCADE,

    -- Report metadata
    report_type VARCHAR(50) NOT NULL CHECK (report_type IN ('executive_summary', 'technical_detail', 'compliance_audit', 'custom')),
    format VARCHAR(50) NOT NULL CHECK (format IN ('pdf', 'docx', 'html', 'json')),

    -- Content
    title VARCHAR(255) NOT NULL,
    content JSONB, -- structured report data
    storage_path TEXT, -- if PDF/DOCX

    -- Generation details
    template_used VARCHAR(100),
    generated_by UUID REFERENCES auth.users(id),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_bia_reports_analysis ON bia_reports(bia_analysis_id);
CREATE INDEX idx_bia_reports_type ON bia_reports(report_type);

-- ============================================================================
-- SECTION 10: CONTINUOUS MONITORING
-- ============================================================================

-- Monitoring Alerts
CREATE TABLE bia_monitoring_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bia_analysis_id UUID NOT NULL REFERENCES bia_analyses(id) ON DELETE CASCADE,
    process_id UUID REFERENCES bia_processes(id) ON DELETE CASCADE,

    alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN ('rto_breach', 'process_change', 'dependency_broken', 'compliance_drift')),
    severity VARCHAR(50) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),

    -- Alert content
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,

    -- Detection
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    detection_method VARCHAR(50), -- 'ai_monitoring', 'threshold_breach', 'manual'

    -- Status
    status VARCHAR(50) DEFAULT 'open' CHECK (status IN ('open', 'acknowledged', 'investigating', 'resolved', 'false_positive')),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID REFERENCES auth.users(id),
    resolution_notes TEXT
);

CREATE INDEX idx_monitoring_alerts_analysis ON bia_monitoring_alerts(bia_analysis_id);
CREATE INDEX idx_monitoring_alerts_status ON bia_monitoring_alerts(status);
CREATE INDEX idx_monitoring_alerts_severity ON bia_monitoring_alerts(severity);

-- ============================================================================
-- SECTION 11: AUDIT & CHANGELOG
-- ============================================================================

-- Audit Log (для всех изменений в BIA)
CREATE TABLE bia_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bia_analysis_id UUID NOT NULL REFERENCES bia_analyses(id) ON DELETE CASCADE,

    -- Event details
    event_type VARCHAR(50) NOT NULL, -- 'created', 'updated', 'deleted', 'status_changed'
    entity_type VARCHAR(50) NOT NULL, -- 'process', 'dependency', 'finding', etc.
    entity_id UUID NOT NULL,

    -- Changes
    old_values JSONB,
    new_values JSONB,

    -- User context
    user_id UUID REFERENCES auth.users(id),
    user_role VARCHAR(50),
    ip_address INET,
    user_agent TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_log_analysis ON bia_audit_log(bia_analysis_id);
CREATE INDEX idx_audit_log_entity ON bia_audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_user ON bia_audit_log(user_id);
CREATE INDEX idx_audit_log_created ON bia_audit_log(created_at DESC);

-- ============================================================================
-- SECTION 12: ROW-LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE bia_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE bia_processes ENABLE ROW LEVEL SECURITY;
ALTER TABLE bia_dependencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE bia_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE bia_answers ENABLE ROW LEVEL SECURITY;
ALTER TABLE bia_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE bia_erp_connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE bia_erp_sync_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE bia_ai_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE bia_monte_carlo_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE bia_findings ENABLE ROW LEVEL SECURITY;
ALTER TABLE bia_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE bia_monitoring_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE bia_audit_log ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access BIA from their organization
CREATE POLICY bia_analyses_org_policy ON bia_analyses
    FOR ALL USING (
        organization_id IN (
            SELECT organization_id FROM organization_members
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY bia_processes_org_policy ON bia_processes
    FOR ALL USING (
        bia_analysis_id IN (
            SELECT id FROM bia_analyses WHERE organization_id IN (
                SELECT organization_id FROM organization_members WHERE user_id = auth.uid()
            )
        )
    );

-- Replicate for all other tables
CREATE POLICY bia_dependencies_org_policy ON bia_dependencies
    FOR ALL USING (bia_analysis_id IN (SELECT id FROM bia_analyses WHERE organization_id IN (SELECT organization_id FROM organization_members WHERE user_id = auth.uid())));

CREATE POLICY bia_questions_org_policy ON bia_questions
    FOR ALL USING (bia_analysis_id IN (SELECT id FROM bia_analyses WHERE organization_id IN (SELECT organization_id FROM organization_members WHERE user_id = auth.uid())));

CREATE POLICY bia_answers_org_policy ON bia_answers
    FOR ALL USING (question_id IN (SELECT id FROM bia_questions WHERE bia_analysis_id IN (SELECT id FROM bia_analyses WHERE organization_id IN (SELECT organization_id FROM organization_members WHERE user_id = auth.uid()))));

CREATE POLICY bia_documents_org_policy ON bia_documents
    FOR ALL USING (bia_analysis_id IN (SELECT id FROM bia_analyses WHERE organization_id IN (SELECT organization_id FROM organization_members WHERE user_id = auth.uid())));

CREATE POLICY bia_erp_connections_org_policy ON bia_erp_connections
    FOR ALL USING (bia_analysis_id IN (SELECT id FROM bia_analyses WHERE organization_id IN (SELECT organization_id FROM organization_members WHERE user_id = auth.uid())));

CREATE POLICY bia_erp_sync_logs_org_policy ON bia_erp_sync_logs
    FOR ALL USING (erp_connection_id IN (SELECT id FROM bia_erp_connections WHERE bia_analysis_id IN (SELECT id FROM bia_analyses WHERE organization_id IN (SELECT organization_id FROM organization_members WHERE user_id = auth.uid()))));

CREATE POLICY bia_ai_jobs_org_policy ON bia_ai_jobs
    FOR ALL USING (bia_analysis_id IN (SELECT id FROM bia_analyses WHERE organization_id IN (SELECT organization_id FROM organization_members WHERE user_id = auth.uid())));

CREATE POLICY bia_monte_carlo_results_org_policy ON bia_monte_carlo_results
    FOR ALL USING (bia_analysis_id IN (SELECT id FROM bia_analyses WHERE organization_id IN (SELECT organization_id FROM organization_members WHERE user_id = auth.uid())));

CREATE POLICY bia_findings_org_policy ON bia_findings
    FOR ALL USING (bia_analysis_id IN (SELECT id FROM bia_analyses WHERE organization_id IN (SELECT organization_id FROM organization_members WHERE user_id = auth.uid())));

CREATE POLICY bia_reports_org_policy ON bia_reports
    FOR ALL USING (bia_analysis_id IN (SELECT id FROM bia_analyses WHERE organization_id IN (SELECT organization_id FROM organization_members WHERE user_id = auth.uid())));

CREATE POLICY bia_monitoring_alerts_org_policy ON bia_monitoring_alerts
    FOR ALL USING (bia_analysis_id IN (SELECT id FROM bia_analyses WHERE organization_id IN (SELECT organization_id FROM organization_members WHERE user_id = auth.uid())));

CREATE POLICY bia_audit_log_org_policy ON bia_audit_log
    FOR SELECT USING (bia_analysis_id IN (SELECT id FROM bia_analyses WHERE organization_id IN (SELECT organization_id FROM organization_members WHERE user_id = auth.uid())));

-- ============================================================================
-- SECTION 13: TRIGGERS & FUNCTIONS
-- ============================================================================

-- Function: Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to relevant tables
CREATE TRIGGER update_bia_analyses_updated_at BEFORE UPDATE ON bia_analyses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bia_processes_updated_at BEFORE UPDATE ON bia_processes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bia_findings_updated_at BEFORE UPDATE ON bia_findings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function: Auto-create audit log entries
CREATE OR REPLACE FUNCTION log_bia_changes()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO bia_audit_log (
        bia_analysis_id,
        event_type,
        entity_type,
        entity_id,
        old_values,
        new_values,
        user_id
    ) VALUES (
        COALESCE(NEW.bia_analysis_id, OLD.bia_analysis_id),
        TG_OP::VARCHAR,
        TG_TABLE_NAME::VARCHAR,
        COALESCE(NEW.id, OLD.id),
        CASE WHEN TG_OP = 'DELETE' THEN row_to_json(OLD) ELSE NULL END,
        CASE WHEN TG_OP != 'DELETE' THEN row_to_json(NEW) ELSE NULL END,
        auth.uid()
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Apply audit logging to key tables
CREATE TRIGGER audit_bia_processes AFTER INSERT OR UPDATE OR DELETE ON bia_processes
    FOR EACH ROW EXECUTE FUNCTION log_bia_changes();

CREATE TRIGGER audit_bia_findings AFTER INSERT OR UPDATE OR DELETE ON bia_findings
    FOR EACH ROW EXECUTE FUNCTION log_bia_changes();

-- Function: Calculate compliance score
CREATE OR REPLACE FUNCTION calculate_bia_compliance_score(analysis_id UUID)
RETURNS INTEGER AS $$
DECLARE
    score INTEGER := 0;
    total_processes INTEGER;
    processes_with_rto INTEGER;
    processes_with_financial_impact INTEGER;
BEGIN
    -- Count total processes
    SELECT COUNT(*) INTO total_processes
    FROM bia_processes WHERE bia_analysis_id = analysis_id;

    IF total_processes = 0 THEN
        RETURN 0;
    END IF;

    -- Count processes with RTO defined
    SELECT COUNT(*) INTO processes_with_rto
    FROM bia_processes
    WHERE bia_analysis_id = analysis_id AND rto_hours IS NOT NULL;

    -- Count processes with financial impact
    SELECT COUNT(*) INTO processes_with_financial_impact
    FROM bia_processes
    WHERE bia_analysis_id = analysis_id AND financial_impact_per_hour IS NOT NULL;

    -- Calculate score (0-100)
    score := (
        (processes_with_rto::DECIMAL / total_processes * 50) +
        (processes_with_financial_impact::DECIMAL / total_processes * 50)
    )::INTEGER;

    RETURN score;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SECTION 14: PERFORMANCE INDEXES
-- ============================================================================

-- Composite indexes for common queries
CREATE INDEX idx_bia_processes_analysis_criticality ON bia_processes(bia_analysis_id, criticality);
CREATE INDEX idx_bia_processes_analysis_rto ON bia_processes(bia_analysis_id, rto_hours);
CREATE INDEX idx_bia_findings_analysis_severity_status ON bia_findings(bia_analysis_id, severity, status);
CREATE INDEX idx_bia_dependencies_source_type ON bia_dependencies(source_process_id, dependency_type);

-- GIN indexes for JSONB columns (для быстрого поиска)
CREATE INDEX idx_bia_analyses_iso_coverage_gin ON bia_analyses USING GIN(iso_22301_coverage);
CREATE INDEX idx_bia_ai_jobs_output_gin ON bia_ai_jobs USING GIN(output_data);
CREATE INDEX idx_bia_findings_affected_processes_gin ON bia_findings USING GIN(affected_processes);

-- ============================================================================
-- SECTION 15: MATERIALIZED VIEWS (для быстрой аналитики)
-- ============================================================================

-- View: BIA Summary Statistics
CREATE MATERIALIZED VIEW bia_summary_stats AS
SELECT
    ba.id AS bia_analysis_id,
    ba.organization_id,
    ba.status,
    ba.compliance_score,

    COUNT(bp.id) AS total_processes,
    COUNT(bp.id) FILTER (WHERE bp.criticality = 'critical') AS critical_processes,
    COUNT(bp.id) FILTER (WHERE bp.criticality = 'high') AS high_processes,

    AVG(bp.rto_hours) AS avg_rto_hours,
    AVG(bp.financial_impact_per_hour) AS avg_financial_impact,
    SUM(bp.financial_impact_daily) AS total_daily_impact,

    COUNT(bd.id) AS total_dependencies,
    COUNT(bd.id) FILTER (WHERE bd.dependency_type = 'hard') AS hard_dependencies,

    COUNT(bf.id) AS total_findings,
    COUNT(bf.id) FILTER (WHERE bf.severity = 'critical') AS critical_findings,
    COUNT(bf.id) FILTER (WHERE bf.status = 'new') AS unresolved_findings,

    ba.created_at,
    ba.completed_at
FROM bia_analyses ba
LEFT JOIN bia_processes bp ON ba.id = bp.bia_analysis_id
LEFT JOIN bia_dependencies bd ON ba.id = bd.bia_analysis_id
LEFT JOIN bia_findings bf ON ba.id = bf.bia_analysis_id
GROUP BY ba.id, ba.organization_id, ba.status, ba.compliance_score, ba.created_at, ba.completed_at;

CREATE UNIQUE INDEX idx_bia_summary_stats_id ON bia_summary_stats(bia_analysis_id);

-- Refresh function (можно вызывать по расписанию)
CREATE OR REPLACE FUNCTION refresh_bia_summary_stats()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY bia_summary_stats;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SECTION 16: SAMPLE DATA (для тестирования)
-- ============================================================================

-- Commented out - uncomment to insert sample data
/*
INSERT INTO bia_analyses (organization_id, name, status, collection_method) VALUES
('00000000-0000-0000-0000-000000000001', 'Healthcare BIA 2025', 'completed', 'questionnaire');

INSERT INTO bia_processes (bia_analysis_id, name, criticality, rto_hours, rpo_hours, financial_impact_per_hour) VALUES
((SELECT id FROM bia_analyses WHERE name = 'Healthcare BIA 2025'), 'Emergency Surgery', 'critical', 4, 0, 15000),
((SELECT id FROM bia_analyses WHERE name = 'Healthcare BIA 2025'), 'Patient Billing', 'high', 48, 24, 2500);
*/

-- ============================================================================
-- MIGRATION NOTES
-- ============================================================================

-- To apply this schema:
-- 1. Ensure organizations table exists (referenced by bia_analyses)
-- 2. Ensure organization_members table exists (used in RLS policies)
-- 3. Run this entire script in order
-- 4. Refresh materialized view: SELECT refresh_bia_summary_stats();

-- To rollback (DESTRUCTIVE):
-- DROP SCHEMA IF EXISTS bia CASCADE;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
