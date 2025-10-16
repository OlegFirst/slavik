-- Decision Center - Database Initialization
-- Creates tables for decision history, audit logs, and escalations

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Decision History Table
CREATE TABLE IF NOT EXISTS decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    decision_id VARCHAR(255) UNIQUE NOT NULL,
    request_id VARCHAR(255) NOT NULL,
    service VARCHAR(255) NOT NULL,
    action VARCHAR(255) NOT NULL,
    decision_type VARCHAR(50) NOT NULL,
    outcome VARCHAR(50) NOT NULL,
    justification TEXT,
    decided_by VARCHAR(255) NOT NULL,
    decided_at TIMESTAMP WITH TIME ZONE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit Log Table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    decision_id VARCHAR(255) REFERENCES decisions(decision_id),
    event_type VARCHAR(100) NOT NULL,
    service VARCHAR(255) NOT NULL,
    action VARCHAR(255) NOT NULL,
    outcome VARCHAR(50) NOT NULL,
    operator VARCHAR(255),
    reason TEXT,
    context JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Escalation Table
CREATE TABLE IF NOT EXISTS escalations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    escalation_id VARCHAR(255) UNIQUE NOT NULL,
    request_id VARCHAR(255) NOT NULL,
    service VARCHAR(255) NOT NULL,
    action VARCHAR(255) NOT NULL,
    escalation_level VARCHAR(50) NOT NULL,
    urgency INTEGER NOT NULL,
    reason TEXT NOT NULL,
    assigned_to VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution TEXT,
    operator VARCHAR(255)
);

-- Consultation Log Table (for learning)
CREATE TABLE IF NOT EXISTS consultation_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id VARCHAR(255) NOT NULL,
    service VARCHAR(255) NOT NULL,
    action VARCHAR(255) NOT NULL,
    reason TEXT,
    specialists_consulted JSONB,
    recommendation VARCHAR(100),
    confidence DECIMAL(5,4),
    consensus BOOLEAN,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Policy Change Log Table
CREATE TABLE IF NOT EXISTS policy_changes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service VARCHAR(255) NOT NULL,
    change_type VARCHAR(100) NOT NULL,
    old_value JSONB,
    new_value JSONB,
    changed_by VARCHAR(255) NOT NULL,
    reason TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_decisions_service ON decisions(service);
CREATE INDEX IF NOT EXISTS idx_decisions_decided_at ON decisions(decided_at);
CREATE INDEX IF NOT EXISTS idx_decisions_outcome ON decisions(outcome);

CREATE INDEX IF NOT EXISTS idx_audit_service ON audit_logs(service);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_decision_id ON audit_logs(decision_id);

CREATE INDEX IF NOT EXISTS idx_escalations_status ON escalations(status);
CREATE INDEX IF NOT EXISTS idx_escalations_service ON escalations(service);
CREATE INDEX IF NOT EXISTS idx_escalations_created_at ON escalations(created_at);

CREATE INDEX IF NOT EXISTS idx_consultation_service ON consultation_logs(service);
CREATE INDEX IF NOT EXISTS idx_consultation_timestamp ON consultation_logs(timestamp);

-- Partitioning for audit_logs (by month) - for high-volume production
-- Uncomment if needed for large scale deployments
-- CREATE TABLE audit_logs_template (LIKE audit_logs INCLUDING ALL);
-- SELECT create_parent('public.audit_logs_template', 'timestamp', 'native', 'monthly');

-- Retention policy - auto-cleanup old data (requires pg_cron extension)
-- Example: Delete audit logs older than 90 days
-- SELECT cron.schedule('cleanup-old-audit-logs', '0 2 * * *', $$
--     DELETE FROM audit_logs WHERE timestamp < NOW() - INTERVAL '90 days';
-- $$);

-- Grant permissions
GRANT SELECT, INSERT, UPDATE ON decisions TO decision_center;
GRANT SELECT, INSERT ON audit_logs TO decision_center;
GRANT SELECT, INSERT, UPDATE ON escalations TO decision_center;
GRANT SELECT, INSERT ON consultation_logs TO decision_center;
GRANT SELECT, INSERT ON policy_changes TO decision_center;

-- Initial data / seed (optional)
-- INSERT INTO policy_changes (service, change_type, new_value, changed_by, reason)
-- VALUES ('system', 'initialization', '{"version": "1.0.0"}'::jsonb, 'system', 'Database initialized');

COMMENT ON TABLE decisions IS 'Decision history for audit and learning';
COMMENT ON TABLE audit_logs IS 'Detailed audit trail for all decision events';
COMMENT ON TABLE escalations IS 'Escalation tracking for human review';
COMMENT ON TABLE consultation_logs IS 'AI consultation logs for pattern learning';
COMMENT ON TABLE policy_changes IS 'Policy modification audit trail';
