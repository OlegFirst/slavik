-- ============================================
-- ISO 22301 Compliance Data Storage Schema
-- Database: Supabase PostgreSQL
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. NOTIFICATIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    channel VARCHAR(50) NOT NULL, -- email, sms, push, webhook, teams, slack
    recipients JSONB NOT NULL, -- Array of recipients
    subject VARCHAR(500),
    message TEXT NOT NULL,
    title VARCHAR(500),
    severity VARCHAR(20) DEFAULT 'info', -- info, warning, critical, emergency
    status VARCHAR(20) DEFAULT 'pending', -- pending, sent, failed, retry
    metadata JSONB DEFAULT '{}',
    error_message TEXT,
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3
);

CREATE INDEX idx_notifications_channel ON notifications(channel);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_severity ON notifications(severity);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);

-- ============================================
-- 2. COMPLIANCE ALERTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS compliance_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_id VARCHAR(100) UNIQUE NOT NULL,
    alert_type VARCHAR(50) NOT NULL, -- security, availability, performance, compliance
    severity VARCHAR(20) NOT NULL, -- low, medium, high, critical
    service_name VARCHAR(100),
    title VARCHAR(500) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'active', -- active, acknowledged, resolved, closed
    iso_clause VARCHAR(20), -- ISO 22301 clause reference
    metadata JSONB DEFAULT '{}',
    triggered_at TIMESTAMPTZ DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_alerts_alert_id ON compliance_alerts(alert_id);
CREATE INDEX idx_alerts_type ON compliance_alerts(alert_type);
CREATE INDEX idx_alerts_severity ON compliance_alerts(severity);
CREATE INDEX idx_alerts_status ON compliance_alerts(status);
CREATE INDEX idx_alerts_triggered_at ON compliance_alerts(triggered_at DESC);

-- ============================================
-- 3. NONCONFORMITIES TABLE (ISO 10.1)
-- ============================================
CREATE TABLE IF NOT EXISTS nonconformities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nc_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL, -- minor, major, critical
    iso_clause VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'open', -- open, in_progress, resolved, closed, verified
    service_name VARCHAR(100),
    responsible_person VARCHAR(200),
    root_cause TEXT,
    corrective_action TEXT,
    preventive_action TEXT,
    verification_evidence TEXT,
    metadata JSONB DEFAULT '{}',
    identified_at TIMESTAMPTZ DEFAULT NOW(),
    target_resolution_date TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_nc_nc_id ON nonconformities(nc_id);
CREATE INDEX idx_nc_severity ON nonconformities(severity);
CREATE INDEX idx_nc_status ON nonconformities(status);
CREATE INDEX idx_nc_iso_clause ON nonconformities(iso_clause);

-- ============================================
-- 4. AUDITS TABLE (ISO 9.2)
-- ============================================
CREATE TABLE IF NOT EXISTS audits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_id VARCHAR(100) UNIQUE NOT NULL,
    audit_type VARCHAR(50) NOT NULL, -- internal, external, surveillance, certification
    title VARCHAR(500) NOT NULL,
    description TEXT,
    iso_clauses TEXT[], -- Array of ISO clauses audited
    auditor_name VARCHAR(200),
    audit_date TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'planned', -- planned, in_progress, completed, reported
    findings JSONB DEFAULT '[]', -- Array of findings
    recommendations JSONB DEFAULT '[]',
    score INTEGER, -- 0-100
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audits_audit_id ON audits(audit_id);
CREATE INDEX idx_audits_type ON audits(audit_type);
CREATE INDEX idx_audits_status ON audits(status);
CREATE INDEX idx_audits_audit_date ON audits(audit_date DESC);

-- ============================================
-- 5. BUSINESS METRICS TABLE (RTO/RPO/MTPD)
-- ============================================
CREATE TABLE IF NOT EXISTS business_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(100) NOT NULL,
    metric_type VARCHAR(50) NOT NULL, -- rto, rpo, mtpd, availability, mttr
    target_value NUMERIC NOT NULL,
    actual_value NUMERIC,
    unit VARCHAR(20), -- seconds, minutes, hours, percentage
    status VARCHAR(20) DEFAULT 'compliant', -- compliant, warning, breach
    measured_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_metrics_service ON business_metrics(service_name);
CREATE INDEX idx_metrics_type ON business_metrics(metric_type);
CREATE INDEX idx_metrics_status ON business_metrics(status);
CREATE INDEX idx_metrics_measured_at ON business_metrics(measured_at DESC);

-- ============================================
-- 6. SERVICE REGISTRY TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS service_registry (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(100) UNIQUE NOT NULL,
    service_type VARCHAR(50), -- bcm, infrastructure, business
    base_url VARCHAR(500),
    health_endpoint VARCHAR(200),
    metrics_endpoint VARCHAR(200),
    port INTEGER,
    iso_clauses TEXT[],
    criticality VARCHAR(20), -- low, medium, high, critical
    status VARCHAR(20) DEFAULT 'unknown', -- up, down, degraded, unknown
    last_health_check TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    registered_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_services_name ON service_registry(service_name);
CREATE INDEX idx_services_type ON service_registry(service_type);
CREATE INDEX idx_services_status ON service_registry(status);
CREATE INDEX idx_services_criticality ON service_registry(criticality);

-- ============================================
-- 7. AUTOMATION JOBS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS automation_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id VARCHAR(100) UNIQUE NOT NULL,
    job_type VARCHAR(50) NOT NULL, -- service_discovery, security_scan, complexity_analysis, backup
    status VARCHAR(20) DEFAULT 'pending', -- pending, running, completed, failed
    results JSONB DEFAULT '{}',
    error_message TEXT,
    duration_ms INTEGER,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_jobs_job_id ON automation_jobs(job_id);
CREATE INDEX idx_jobs_type ON automation_jobs(job_type);
CREATE INDEX idx_jobs_status ON automation_jobs(status);
CREATE INDEX idx_jobs_created_at ON automation_jobs(created_at DESC);

-- ============================================
-- 8. COMPLIANCE SNAPSHOTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS compliance_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    snapshot_date DATE NOT NULL,
    alerts_count INTEGER DEFAULT 0,
    nonconformities_count INTEGER DEFAULT 0,
    audits_count INTEGER DEFAULT 0,
    services_count INTEGER DEFAULT 0,
    compliance_score NUMERIC,
    snapshot_data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_snapshots_date ON compliance_snapshots(snapshot_date DESC);

-- ============================================
-- FUNCTIONS AND TRIGGERS
-- ============================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all tables with updated_at
CREATE TRIGGER update_notifications_updated_at BEFORE UPDATE ON notifications FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_alerts_updated_at BEFORE UPDATE ON compliance_alerts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_nc_updated_at BEFORE UPDATE ON nonconformities FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_audits_updated_at BEFORE UPDATE ON audits FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_services_updated_at BEFORE UPDATE ON service_registry FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================

-- Enable RLS on all tables
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE compliance_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE nonconformities ENABLE ROW LEVEL SECURITY;
ALTER TABLE audits ENABLE ROW LEVEL SECURITY;
ALTER TABLE business_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE service_registry ENABLE ROW LEVEL SECURITY;
ALTER TABLE automation_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE compliance_snapshots ENABLE ROW LEVEL SECURITY;

-- Service role can do everything (for backend services)
CREATE POLICY "Service role can do everything on notifications" ON notifications FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role can do everything on alerts" ON compliance_alerts FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role can do everything on nc" ON nonconformities FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role can do everything on audits" ON audits FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role can do everything on metrics" ON business_metrics FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role can do everything on services" ON service_registry FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role can do everything on jobs" ON automation_jobs FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role can do everything on snapshots" ON compliance_snapshots FOR ALL USING (auth.role() = 'service_role');

-- Authenticated users can read (for frontend)
CREATE POLICY "Authenticated users can read notifications" ON notifications FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users can read alerts" ON compliance_alerts FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users can read nc" ON nonconformities FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users can read audits" ON audits FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users can read metrics" ON business_metrics FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users can read services" ON service_registry FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users can read jobs" ON automation_jobs FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users can read snapshots" ON compliance_snapshots FOR SELECT USING (auth.role() = 'authenticated');

-- ============================================
-- INITIAL DATA
-- ============================================

-- Create initial compliance snapshot
INSERT INTO compliance_snapshots (snapshot_date, snapshot_data, compliance_score)
VALUES (CURRENT_DATE, '{"initialized": true}'::jsonb, 100.0)
ON CONFLICT DO NOTHING;

-- ============================================
-- VIEWS FOR REPORTING
-- ============================================

-- Active alerts view
CREATE OR REPLACE VIEW active_alerts AS
SELECT
    alert_id,
    alert_type,
    severity,
    service_name,
    title,
    triggered_at,
    EXTRACT(EPOCH FROM (NOW() - triggered_at))/3600 as hours_active
FROM compliance_alerts
WHERE status = 'active'
ORDER BY
    CASE severity
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END,
    triggered_at DESC;

-- Open nonconformities view
CREATE OR REPLACE VIEW open_nonconformities AS
SELECT
    nc_id,
    title,
    severity,
    iso_clause,
    status,
    responsible_person,
    identified_at,
    target_resolution_date,
    CASE
        WHEN target_resolution_date < NOW() THEN true
        ELSE false
    END as overdue
FROM nonconformities
WHERE status IN ('open', 'in_progress')
ORDER BY
    CASE severity
        WHEN 'critical' THEN 1
        WHEN 'major' THEN 2
        WHEN 'minor' THEN 3
    END,
    identified_at DESC;

-- Service health view
CREATE OR REPLACE VIEW service_health_overview AS
SELECT
    service_name,
    service_type,
    status,
    criticality,
    last_health_check,
    EXTRACT(EPOCH FROM (NOW() - last_health_check))/60 as minutes_since_check
FROM service_registry
ORDER BY
    CASE criticality
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END,
    service_name;

-- Notification statistics view
CREATE OR REPLACE VIEW notification_stats AS
SELECT
    channel,
    status,
    COUNT(*) as total_count,
    DATE_TRUNC('day', created_at) as day
FROM notifications
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY channel, status, DATE_TRUNC('day', created_at)
ORDER BY day DESC, channel, status;

-- ============================================
-- DONE!
-- ============================================

-- Grant permissions to authenticated role
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- Grant permissions to service_role
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO service_role;
