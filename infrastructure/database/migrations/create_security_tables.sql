-- ============================================================================
-- Security Tables for Grafana Dashboard
-- ============================================================================
-- Creates tables needed for Security & Data Management Dashboard
-- Tables: security_events, audit_logs, sessions
-- ============================================================================

-- =============================================================================
-- 1. SECURITY EVENTS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.security_events (
    id SERIAL PRIMARY KEY,
    event_type TEXT NOT NULL,
    severity TEXT DEFAULT 'info',  -- info, warning, critical
    user_id UUID,
    ip_address TEXT,
    user_agent TEXT,
    resource_type TEXT,
    resource_id TEXT,
    action TEXT,
    success BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_security_events_created
    ON public.security_events(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_security_events_type
    ON public.security_events(event_type);

CREATE INDEX IF NOT EXISTS idx_security_events_severity
    ON public.security_events(severity)
    WHERE severity IN ('warning', 'critical');

CREATE INDEX IF NOT EXISTS idx_security_events_user
    ON public.security_events(user_id)
    WHERE user_id IS NOT NULL;

-- Comment
COMMENT ON TABLE public.security_events IS
    'Security events log for monitoring and alerting. Used by Grafana Security Dashboard.';


-- =============================================================================
-- 2. AUDIT LOGS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.audit_logs (
    id SERIAL PRIMARY KEY,
    action TEXT NOT NULL,
    user_id UUID,
    user_email TEXT,
    resource_type TEXT,
    resource_id TEXT,
    old_value JSONB,
    new_value JSONB,
    ip_address TEXT,
    user_agent TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_audit_logs_created
    ON public.audit_logs(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_audit_logs_action
    ON public.audit_logs(action);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user
    ON public.audit_logs(user_id)
    WHERE user_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_audit_logs_resource
    ON public.audit_logs(resource_type, resource_id);

-- GIN index for JSONB metadata queries
CREATE INDEX IF NOT EXISTS idx_audit_logs_metadata
    ON public.audit_logs USING GIN (metadata);

-- Comment
COMMENT ON TABLE public.audit_logs IS
    'Audit trail for all system actions. Used for compliance and security monitoring.';


-- =============================================================================
-- 3. SESSIONS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    user_email TEXT,
    ip_address TEXT,
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    last_activity TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_sessions_user
    ON public.sessions(user_id);

CREATE INDEX IF NOT EXISTS idx_sessions_expires
    ON public.sessions(expires_at);

CREATE INDEX IF NOT EXISTS idx_sessions_active
    ON public.sessions(expires_at)
    WHERE expires_at > NOW();

-- Comment
COMMENT ON TABLE public.sessions IS
    'Active user sessions. Used for monitoring active users and security.';


-- =============================================================================
-- 4. INSERT SAMPLE DATA (for testing)
-- =============================================================================

-- Sample security events
INSERT INTO public.security_events (event_type, severity, user_id, ip_address, action, success, metadata)
VALUES
    ('authentication', 'info', gen_random_uuid(), '192.168.1.100', 'login', true, '{"method": "password"}'),
    ('authentication', 'warning', gen_random_uuid(), '192.168.1.101', 'login', false, '{"method": "password", "attempts": 3}'),
    ('authorization', 'critical', gen_random_uuid(), '192.168.1.102', 'access_denied', false, '{"resource": "admin_panel"}'),
    ('data_access', 'info', gen_random_uuid(), '192.168.1.103', 'secret_accessed', true, '{"secret_name": "api_key"}'),
    ('configuration', 'warning', gen_random_uuid(), '192.168.1.104', 'config_changed', true, '{"setting": "security_policy"}')
ON CONFLICT DO NOTHING;

-- Sample audit logs
INSERT INTO public.audit_logs (action, user_id, user_email, resource_type, ip_address, metadata)
VALUES
    ('auth_success', gen_random_uuid(), 'user1@example.com', 'session', '192.168.1.100', '{"method": "password"}'),
    ('auth_failed', gen_random_uuid(), 'user2@example.com', 'session', '192.168.1.101', '{"reason": "invalid_password"}'),
    ('secret_accessed', gen_random_uuid(), 'admin@example.com', 'vault_secret', '192.168.1.102', '{"secret_name": "jwt-secret"}'),
    ('config_updated', gen_random_uuid(), 'admin@example.com', 'system_config', '192.168.1.103', '{"setting": "retention_policy"}'),
    ('unauthorized_access', gen_random_uuid(), 'user3@example.com', 'admin_panel', '192.168.1.104', '{"attempted_action": "delete_user"}')
ON CONFLICT DO NOTHING;

-- Sample sessions
INSERT INTO public.sessions (user_id, user_email, ip_address, expires_at)
VALUES
    (gen_random_uuid(), 'user1@example.com', '192.168.1.100', NOW() + INTERVAL '1 hour'),
    (gen_random_uuid(), 'user2@example.com', '192.168.1.101', NOW() + INTERVAL '2 hours'),
    (gen_random_uuid(), 'admin@example.com', '192.168.1.102', NOW() + INTERVAL '30 minutes')
ON CONFLICT DO NOTHING;


-- =============================================================================
-- 5. VERIFY TABLES
-- =============================================================================

-- Check table counts
DO $$
BEGIN
    RAISE NOTICE '✅ Security Events: % rows', (SELECT COUNT(*) FROM public.security_events);
    RAISE NOTICE '✅ Audit Logs: % rows', (SELECT COUNT(*) FROM public.audit_logs);
    RAISE NOTICE '✅ Sessions: % rows', (SELECT COUNT(*) FROM public.sessions);
END $$;


-- =============================================================================
-- 6. GRANT PERMISSIONS
-- =============================================================================

-- Grant SELECT to authenticated users (for Grafana)
GRANT SELECT ON public.security_events TO authenticated;
GRANT SELECT ON public.audit_logs TO authenticated;
GRANT SELECT ON public.sessions TO authenticated;

-- Grant all to service_role (for backend services)
GRANT ALL ON public.security_events TO service_role;
GRANT ALL ON public.audit_logs TO service_role;
GRANT ALL ON public.sessions TO service_role;


-- =============================================================================
-- SUCCESS
-- =============================================================================

RAISE NOTICE '✅ All security tables created successfully!';
