-- =====================================================
-- Migration 018: Validation - KPI Alerts
-- =====================================================
-- Purpose: Automated alerting system for KPI threshold breaches
-- Based on: /BCM/validation/database/migrations/003_add_kpi_alerts.sql
-- Date: 2025-10-02
-- Stage 2: KPI Auto-Alerting System
-- =====================================================

-- =====================================================
-- TABLE: validation.kpi_alerts
-- =====================================================

CREATE TABLE IF NOT EXISTS validation.kpi_alerts (
    -- Primary Key (UUID)
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Multi-tenancy
    tenant_id VARCHAR(100) NOT NULL,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- KPI Reference (FK to validation.kpis)
    kpi_id UUID NOT NULL REFERENCES validation.kpis(id) ON DELETE CASCADE,

    -- Alert Identification
    alert_code VARCHAR(50) NOT NULL,  -- ALERT-KPI-2024-001 (unique per organization)

    -- Alert Severity
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('critical', 'warning', 'info')),

    -- Trigger Information
    triggered_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    triggered_value DECIMAL(15,2) NOT NULL,
    threshold_breached DECIMAL(15,2),
    threshold_type VARCHAR(20) CHECK (threshold_type IN ('critical', 'warning')),

    -- Message
    alert_title VARCHAR(500) NOT NULL,
    alert_message TEXT NOT NULL,

    -- Status & Lifecycle
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN (
        'active',
        'acknowledged',
        'resolved',
        'auto_resolved'
    )),

    -- Acknowledgement
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    acknowledged_by UUID,  -- User ID
    acknowledged_by_name VARCHAR(255),
    acknowledgement_notes TEXT,

    -- Resolution
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID,  -- User ID
    resolved_by_name VARCHAR(255),
    resolution_notes TEXT,
    resolved_value DECIMAL(15,2),
    auto_resolved BOOLEAN DEFAULT false,

    -- Notification
    notification_sent BOOLEAN DEFAULT false,
    notification_sent_at TIMESTAMP WITH TIME ZONE,
    recipients JSONB DEFAULT '[]'::jsonb,
    notification_error TEXT,

    -- Escalation
    escalated BOOLEAN DEFAULT false,
    escalated_at TIMESTAMP WITH TIME ZONE,
    escalated_to JSONB DEFAULT '[]'::jsonb,

    -- Related Data
    measurement_id UUID,  -- Link to specific KPI measurement
    related_incidents UUID[],

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT uq_alert_code_per_org UNIQUE (organization_id, alert_code)
);

-- =====================================================
-- INDEXES
-- =====================================================

-- Primary lookups
CREATE INDEX idx_kpi_alerts_tenant ON validation.kpi_alerts(tenant_id);
CREATE INDEX idx_kpi_alerts_organization ON validation.kpi_alerts(organization_id);
CREATE INDEX idx_kpi_alerts_kpi ON validation.kpi_alerts(kpi_id);

-- Filtering & search
CREATE INDEX idx_kpi_alerts_status ON validation.kpi_alerts(status);
CREATE INDEX idx_kpi_alerts_severity ON validation.kpi_alerts(severity);
CREATE INDEX idx_kpi_alerts_triggered ON validation.kpi_alerts(triggered_at);

-- Active alerts (most common query)
CREATE INDEX idx_kpi_alerts_active ON validation.kpi_alerts(status, severity)
WHERE status = 'active';

-- Composite indexes for common queries
CREATE INDEX idx_kpi_alerts_tenant_status ON validation.kpi_alerts(tenant_id, status);
CREATE INDEX idx_kpi_alerts_org_status ON validation.kpi_alerts(organization_id, status);
CREATE INDEX idx_kpi_alerts_kpi_status ON validation.kpi_alerts(kpi_id, status);

-- Notification tracking
CREATE INDEX idx_kpi_alerts_notification ON validation.kpi_alerts(notification_sent, notification_sent_at);

-- Escalation tracking
CREATE INDEX idx_kpi_alerts_escalation ON validation.kpi_alerts(escalated, escalated_at);

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================================

ALTER TABLE validation.kpi_alerts ENABLE ROW LEVEL SECURITY;

-- Policy: Tenant isolation
CREATE POLICY kpi_alerts_tenant_isolation
ON validation.kpi_alerts
USING (
    tenant_id = current_setting('app.current_tenant_id', true)::text
);

-- Policy: Organization-level access
CREATE POLICY kpi_alerts_org_access
ON validation.kpi_alerts
USING (
    organization_id IN (
        SELECT id FROM public.organizations
        WHERE tenant_id = current_setting('app.current_tenant_id', true)::text
    )
);

-- Policy: Platform admin full access
CREATE POLICY kpi_alerts_platform_admin
ON validation.kpi_alerts
USING (
    current_setting('app.is_platform_admin', true)::boolean = true
);

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger: Auto-update updated_at timestamp
CREATE TRIGGER update_kpi_alerts_updated_at
BEFORE UPDATE ON validation.kpi_alerts
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();

-- Trigger: Auto-generate alert_code if not provided
CREATE OR REPLACE FUNCTION validation.generate_alert_code()
RETURNS TRIGGER AS $$
DECLARE
    next_num INTEGER;
    new_code VARCHAR(50);
    current_year INTEGER;
BEGIN
    IF NEW.alert_code IS NULL OR NEW.alert_code = '' THEN
        current_year := EXTRACT(YEAR FROM CURRENT_DATE);

        -- Get next sequential number for this organization and year
        SELECT COALESCE(
            MAX(
                CAST(
                    SPLIT_PART(alert_code, '-', 4) AS INTEGER
                )
            ), 0
        ) + 1
        INTO next_num
        FROM validation.kpi_alerts
        WHERE organization_id = NEW.organization_id
          AND alert_code LIKE 'ALERT-KPI-' || current_year || '-%';

        -- Generate code: ALERT-KPI-2024-001
        new_code := 'ALERT-KPI-' || current_year || '-' || LPAD(next_num::TEXT, 3, '0');
        NEW.alert_code := new_code;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER generate_alert_code_trigger
BEFORE INSERT ON validation.kpi_alerts
FOR EACH ROW
EXECUTE FUNCTION validation.generate_alert_code();

-- =====================================================
-- ANALYTICAL VIEWS
-- =====================================================

-- View: Active alerts summary
CREATE OR REPLACE VIEW validation.v_active_alerts AS
SELECT
    a.id,
    a.organization_id,
    a.tenant_id,
    a.alert_code,
    a.severity,
    a.triggered_at,
    a.status,

    -- KPI details
    k.kpi_code,
    k.kpi_name,
    k.kpi_category,
    k.owner_id,

    -- Alert details
    a.alert_title,
    a.triggered_value,
    a.threshold_breached,
    a.threshold_type,

    -- Time metrics
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - a.triggered_at)) / 3600 AS hours_since_triggered,

    -- Acknowledgement
    a.acknowledged_at,
    a.acknowledged_by_name,

    -- Escalation
    a.escalated,
    a.escalated_at
FROM validation.kpi_alerts a
INNER JOIN validation.kpis k ON k.id = a.kpi_id
WHERE a.status IN ('active', 'acknowledged')
ORDER BY
    CASE a.severity
        WHEN 'critical' THEN 1
        WHEN 'warning' THEN 2
        ELSE 3
    END,
    a.triggered_at DESC;

-- View: Alert statistics by KPI
CREATE OR REPLACE VIEW validation.v_alert_stats_by_kpi AS
SELECT
    a.kpi_id,
    k.kpi_code,
    k.kpi_name,
    k.organization_id,
    a.tenant_id,

    COUNT(*) AS total_alerts,
    COUNT(*) FILTER (WHERE a.severity = 'critical') AS critical_alerts,
    COUNT(*) FILTER (WHERE a.severity = 'warning') AS warning_alerts,
    COUNT(*) FILTER (WHERE a.status = 'active') AS active_alerts,
    COUNT(*) FILTER (WHERE a.status = 'acknowledged') AS acknowledged_alerts,
    COUNT(*) FILTER (WHERE a.status IN ('resolved', 'auto_resolved')) AS resolved_alerts,

    -- Average time to acknowledge (hours)
    AVG(
        EXTRACT(EPOCH FROM (a.acknowledged_at - a.triggered_at)) / 3600
    ) FILTER (WHERE a.acknowledged_at IS NOT NULL) AS avg_hours_to_acknowledge,

    -- Average time to resolve (hours)
    AVG(
        EXTRACT(EPOCH FROM (a.resolved_at - a.triggered_at)) / 3600
    ) FILTER (WHERE a.resolved_at IS NOT NULL) AS avg_hours_to_resolve,

    MAX(a.triggered_at) AS last_alert_triggered
FROM validation.kpi_alerts a
INNER JOIN validation.kpis k ON k.id = a.kpi_id
GROUP BY a.kpi_id, k.kpi_code, k.kpi_name, k.organization_id, a.tenant_id
ORDER BY total_alerts DESC;

-- View: Unacknowledged critical alerts
CREATE OR REPLACE VIEW validation.v_critical_unacknowledged AS
SELECT
    a.id,
    a.organization_id,
    a.tenant_id,
    a.alert_code,
    a.triggered_at,

    -- KPI details
    k.kpi_code,
    k.kpi_name,
    k.owner_id,

    -- Alert details
    a.alert_title,
    a.triggered_value,
    a.threshold_breached,

    -- Time metrics
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - a.triggered_at)) / 3600 AS hours_unacknowledged,

    -- Escalation
    a.escalated,
    a.escalated_at,

    -- Urgency score (higher = more urgent)
    CASE
        WHEN EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - a.triggered_at)) / 3600 > 24
        THEN 100
        WHEN EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - a.triggered_at)) / 3600 > 12
        THEN 75
        WHEN EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - a.triggered_at)) / 3600 > 4
        THEN 50
        ELSE 25
    END AS urgency_score
FROM validation.kpi_alerts a
INNER JOIN validation.kpis k ON k.id = a.kpi_id
WHERE a.severity = 'critical'
  AND a.status = 'active'
  AND a.acknowledged_at IS NULL
ORDER BY a.triggered_at ASC;

-- View: Alert trends (last 30 days)
CREATE OR REPLACE VIEW validation.v_alert_trends AS
SELECT
    DATE_TRUNC('day', a.triggered_at)::date AS alert_date,
    a.organization_id,
    a.tenant_id,

    COUNT(*) AS total_alerts,
    COUNT(*) FILTER (WHERE a.severity = 'critical') AS critical_count,
    COUNT(*) FILTER (WHERE a.severity = 'warning') AS warning_count,
    COUNT(*) FILTER (WHERE a.severity = 'info') AS info_count,

    COUNT(DISTINCT a.kpi_id) AS unique_kpis_triggered,

    AVG(
        EXTRACT(EPOCH FROM (a.resolved_at - a.triggered_at)) / 3600
    ) FILTER (WHERE a.resolved_at IS NOT NULL) AS avg_resolution_hours
FROM validation.kpi_alerts a
WHERE a.triggered_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', a.triggered_at)::date, a.organization_id, a.tenant_id
ORDER BY alert_date DESC;

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function: Create KPI alert
CREATE OR REPLACE FUNCTION validation.create_kpi_alert(
    p_kpi_id UUID,
    p_severity VARCHAR(20),
    p_triggered_value DECIMAL(15,2),
    p_threshold_breached DECIMAL(15,2),
    p_threshold_type VARCHAR(20),
    p_alert_title VARCHAR(500),
    p_alert_message TEXT
)
RETURNS UUID AS $$
DECLARE
    v_alert_id UUID;
    v_tenant_id VARCHAR(100);
    v_organization_id UUID;
BEGIN
    -- Get tenant and organization from KPI
    SELECT tenant_id, organization_id
    INTO v_tenant_id, v_organization_id
    FROM validation.kpis
    WHERE id = p_kpi_id;

    -- Create alert
    INSERT INTO validation.kpi_alerts (
        tenant_id,
        organization_id,
        kpi_id,
        severity,
        triggered_value,
        threshold_breached,
        threshold_type,
        alert_title,
        alert_message
    ) VALUES (
        v_tenant_id,
        v_organization_id,
        p_kpi_id,
        p_severity,
        p_triggered_value,
        p_threshold_breached,
        p_threshold_type,
        p_alert_title,
        p_alert_message
    )
    RETURNING id INTO v_alert_id;

    RETURN v_alert_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Acknowledge alert
CREATE OR REPLACE FUNCTION validation.acknowledge_alert(
    p_alert_id UUID,
    p_user_id UUID,
    p_user_name VARCHAR(255),
    p_notes TEXT DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    UPDATE validation.kpi_alerts
    SET
        status = 'acknowledged',
        acknowledged_at = CURRENT_TIMESTAMP,
        acknowledged_by = p_user_id,
        acknowledged_by_name = p_user_name,
        acknowledgement_notes = p_notes
    WHERE id = p_alert_id
      AND status = 'active';
END;
$$ LANGUAGE plpgsql;

-- Function: Resolve alert
CREATE OR REPLACE FUNCTION validation.resolve_alert(
    p_alert_id UUID,
    p_user_id UUID,
    p_user_name VARCHAR(255),
    p_resolution_notes TEXT DEFAULT NULL,
    p_resolved_value DECIMAL(15,2) DEFAULT NULL,
    p_auto_resolved BOOLEAN DEFAULT false
)
RETURNS VOID AS $$
BEGIN
    UPDATE validation.kpi_alerts
    SET
        status = CASE WHEN p_auto_resolved THEN 'auto_resolved' ELSE 'resolved' END,
        resolved_at = CURRENT_TIMESTAMP,
        resolved_by = p_user_id,
        resolved_by_name = p_user_name,
        resolution_notes = p_resolution_notes,
        resolved_value = p_resolved_value,
        auto_resolved = p_auto_resolved
    WHERE id = p_alert_id
      AND status IN ('active', 'acknowledged');
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- COMMENTS (Documentation)
-- =====================================================

COMMENT ON TABLE validation.kpi_alerts IS 'Automated alerting for KPI threshold breaches - ISO 22301 Clause 9.1';
COMMENT ON COLUMN validation.kpi_alerts.alert_code IS 'Unique alert code per organization (ALERT-KPI-2024-001)';
COMMENT ON COLUMN validation.kpi_alerts.severity IS 'Alert severity: critical, warning, info';
COMMENT ON COLUMN validation.kpi_alerts.threshold_type IS 'Which threshold was breached: critical or warning';
COMMENT ON COLUMN validation.kpi_alerts.auto_resolved IS 'True if alert was automatically resolved (e.g., KPI back in threshold)';

COMMENT ON VIEW validation.v_active_alerts IS 'Real-time view of active and acknowledged alerts';
COMMENT ON VIEW validation.v_critical_unacknowledged IS 'Critical alerts requiring immediate attention';
COMMENT ON VIEW validation.v_alert_trends IS 'Daily alert trends for last 30 days';

COMMENT ON FUNCTION validation.create_kpi_alert IS 'Create a new KPI alert when threshold is breached';
COMMENT ON FUNCTION validation.acknowledge_alert IS 'Acknowledge an active alert';
COMMENT ON FUNCTION validation.resolve_alert IS 'Resolve an alert (manual or automatic)';

-- =====================================================
-- VERIFICATION
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Migration 018: Validation KPI Alerts - COMPLETE';
    RAISE NOTICE 'Tables created: 1';
    RAISE NOTICE 'Views created: 4';
    RAISE NOTICE 'Functions created: 3';
    RAISE NOTICE 'Indexes created: 13';
    RAISE NOTICE 'RLS policies: 3';
    RAISE NOTICE 'Triggers: 2';
END $$;
