-- Migration 053: Governance Layer DB Persistence
-- Purpose: Add database tables for Decision Center persistence
-- Author: Security hardening initiative
-- Date: 2025-10-19

-- ============================================
-- DECISION CENTER PERSISTENCE TABLES
-- ============================================

-- Store all infrastructure decisions
CREATE TABLE IF NOT EXISTS governance.decisions (
    id SERIAL PRIMARY KEY,
    decision_id VARCHAR(100) UNIQUE NOT NULL,
    decision_type VARCHAR(50) NOT NULL, -- auto_recovery, optimization, manual, ai_assisted
    service_id VARCHAR(255),
    action_type VARCHAR(100) NOT NULL,
    context JSONB NOT NULL,
    outcome VARCHAR(50) NOT NULL, -- approved, rejected, escalated, pending
    reason TEXT,
    policy_match VARCHAR(255),
    approver VARCHAR(255),
    ai_consultation_id VARCHAR(100),
    ai_confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    decided_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB
);

CREATE INDEX idx_decisions_service ON governance.decisions(service_id);
CREATE INDEX idx_decisions_outcome ON governance.decisions(outcome);
CREATE INDEX idx_decisions_created_at ON governance.decisions(created_at DESC);
CREATE INDEX idx_decisions_type ON governance.decisions(decision_type);
CREATE INDEX idx_decisions_pending ON governance.decisions(outcome) WHERE outcome = 'pending';

COMMENT ON TABLE governance.decisions IS 'Audit trail of all infrastructure decisions';

-- Store approval requests
CREATE TABLE IF NOT EXISTS governance.approval_requests (
    id SERIAL PRIMARY KEY,
    approval_id VARCHAR(100) UNIQUE NOT NULL,
    decision_id VARCHAR(100) REFERENCES governance.decisions(decision_id),
    service_id VARCHAR(255) NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    action_details JSONB NOT NULL,
    requester VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, approved, rejected, expired
    priority VARCHAR(50) DEFAULT 'medium', -- low, medium, high, critical
    expires_at TIMESTAMP WITH TIME ZONE,
    approved_by VARCHAR(255),
    approved_at TIMESTAMP WITH TIME ZONE,
    rejection_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_approvals_status ON governance.approval_requests(status);
CREATE INDEX idx_approvals_service ON governance.approval_requests(service_id);
CREATE INDEX idx_approvals_expires ON governance.approval_requests(expires_at);
CREATE INDEX idx_approvals_pending ON governance.approval_requests(status, created_at) WHERE status = 'pending';

COMMENT ON TABLE governance.approval_requests IS 'Manual approval requests for infrastructure actions';

-- Store escalation requests
CREATE TABLE IF NOT EXISTS governance.escalation_requests (
    id SERIAL PRIMARY KEY,
    escalation_id VARCHAR(100) UNIQUE NOT NULL,
    decision_id VARCHAR(100) REFERENCES governance.decisions(decision_id),
    service_id VARCHAR(255) NOT NULL,
    issue_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL, -- low, medium, high, critical
    description TEXT NOT NULL,
    context JSONB,
    status VARCHAR(50) NOT NULL DEFAULT 'open', -- open, acknowledged, resolved, closed
    assigned_to VARCHAR(255),
    escalated_by VARCHAR(255),
    escalated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution TEXT,
    metadata JSONB
);

CREATE INDEX idx_escalations_status ON governance.escalation_requests(status);
CREATE INDEX idx_escalations_service ON governance.escalation_requests(service_id);
CREATE INDEX idx_escalations_severity ON governance.escalation_requests(severity);
CREATE INDEX idx_escalations_open ON governance.escalation_requests(status, escalated_at) WHERE status IN ('open', 'acknowledged');

COMMENT ON TABLE governance.escalation_requests IS 'Escalation requests for human intervention';

-- ============================================
-- NOTIFICATION TRACKING
-- ============================================

CREATE TABLE IF NOT EXISTS governance.notifications (
    id SERIAL PRIMARY KEY,
    notification_id VARCHAR(100) UNIQUE NOT NULL,
    notification_type VARCHAR(50) NOT NULL, -- email, slack, pagerduty, webhook
    recipient VARCHAR(255) NOT NULL,
    subject VARCHAR(500),
    message TEXT NOT NULL,
    related_entity_type VARCHAR(50), -- decision, approval, escalation
    related_entity_id VARCHAR(100),
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, sent, failed, bounced
    sent_at TIMESTAMP WITH TIME ZONE,
    failed_reason TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_notifications_status ON governance.notifications(status);
CREATE INDEX idx_notifications_type ON governance.notifications(notification_type);
CREATE INDEX idx_notifications_created_at ON governance.notifications(created_at DESC);
CREATE INDEX idx_notifications_pending ON governance.notifications(status) WHERE status = 'pending';

COMMENT ON TABLE governance.notifications IS 'Tracking of all governance notifications';

-- ============================================
-- GOVERNANCE METRICS
-- ============================================

CREATE TABLE IF NOT EXISTS governance.decision_metrics (
    id SERIAL PRIMARY KEY,
    metric_date DATE NOT NULL,
    decision_type VARCHAR(50) NOT NULL,
    total_count INTEGER DEFAULT 0,
    approved_count INTEGER DEFAULT 0,
    rejected_count INTEGER DEFAULT 0,
    escalated_count INTEGER DEFAULT 0,
    avg_decision_time_seconds FLOAT,
    ai_consultations INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(metric_date, decision_type)
);

CREATE INDEX idx_metrics_date ON governance.decision_metrics(metric_date DESC);

COMMENT ON TABLE governance.decision_metrics IS 'Daily aggregated governance metrics';

-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Function to get pending approvals
CREATE OR REPLACE FUNCTION governance.get_pending_approvals()
RETURNS TABLE (
    approval_id VARCHAR,
    service_id VARCHAR,
    action_type VARCHAR,
    priority VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        a.approval_id,
        a.service_id,
        a.action_type,
        a.priority,
        a.created_at,
        a.expires_at
    FROM governance.approval_requests a
    WHERE a.status = 'pending'
      AND (a.expires_at IS NULL OR a.expires_at > CURRENT_TIMESTAMP)
    ORDER BY
        CASE a.priority
            WHEN 'critical' THEN 1
            WHEN 'high' THEN 2
            WHEN 'medium' THEN 3
            WHEN 'low' THEN 4
        END,
        a.created_at ASC;
END;
$$ LANGUAGE plpgsql;

-- Function to expire old pending approvals
CREATE OR REPLACE FUNCTION governance.expire_old_approvals()
RETURNS INTEGER AS $$
DECLARE
    rows_updated INTEGER;
BEGIN
    UPDATE governance.approval_requests
    SET status = 'expired'
    WHERE status = 'pending'
      AND expires_at IS NOT NULL
      AND expires_at < CURRENT_TIMESTAMP;

    GET DIAGNOSTICS rows_updated = ROW_COUNT;
    RETURN rows_updated;
END;
$$ LANGUAGE plpgsql;

-- Function to get open escalations
CREATE OR REPLACE FUNCTION governance.get_open_escalations()
RETURNS TABLE (
    escalation_id VARCHAR,
    service_id VARCHAR,
    severity VARCHAR,
    description TEXT,
    escalated_at TIMESTAMP WITH TIME ZONE,
    assigned_to VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.escalation_id,
        e.service_id,
        e.severity,
        e.description,
        e.escalated_at,
        e.assigned_to
    FROM governance.escalation_requests e
    WHERE e.status IN ('open', 'acknowledged')
    ORDER BY
        CASE e.severity
            WHEN 'critical' THEN 1
            WHEN 'high' THEN 2
            WHEN 'medium' THEN 3
            WHEN 'low' THEN 4
        END,
        e.escalated_at ASC;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- GRANTS
-- ============================================

GRANT USAGE ON SCHEMA governance TO authenticated;

-- Allow services to insert and query governance tables
GRANT SELECT, INSERT, UPDATE ON governance.decisions TO authenticated;
GRANT SELECT, INSERT, UPDATE ON governance.approval_requests TO authenticated;
GRANT SELECT, INSERT, UPDATE ON governance.escalation_requests TO authenticated;
GRANT SELECT, INSERT, UPDATE ON governance.notifications TO authenticated;
GRANT SELECT ON governance.decision_metrics TO authenticated;

-- Grant sequence usage
GRANT USAGE ON ALL SEQUENCES IN SCHEMA governance TO authenticated;

-- Grant function execution
GRANT EXECUTE ON FUNCTION governance.get_pending_approvals() TO authenticated;
GRANT EXECUTE ON FUNCTION governance.expire_old_approvals() TO authenticated;
GRANT EXECUTE ON FUNCTION governance.get_open_escalations() TO authenticated;

-- ============================================
-- VERIFICATION
-- ============================================

DO $$
BEGIN
    RAISE NOTICE 'Migration 053 completed successfully';
    RAISE NOTICE 'Created tables: decisions, approval_requests, escalation_requests, notifications, decision_metrics';
    RAISE NOTICE 'Created helper functions: get_pending_approvals, expire_old_approvals, get_open_escalations';
END $$;
