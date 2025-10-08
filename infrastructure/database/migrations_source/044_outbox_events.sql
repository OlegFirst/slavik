-- Migration: Outbox Events Table
-- Purpose: Implement outbox pattern for guaranteed event delivery
-- Date: 2025-10-08

-- ============================================================
-- OUTBOX EVENTS TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS public.outbox_events (
    id BIGSERIAL PRIMARY KEY,
    event_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    event_type VARCHAR(255) NOT NULL,
    aggregate_type VARCHAR(255),
    aggregate_id VARCHAR(255),
    payload JSONB NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    tenant_id VARCHAR(100),
    source VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    published_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending' NOT NULL CHECK (status IN ('pending', 'published', 'failed')),
    retry_count INTEGER DEFAULT 0 NOT NULL,
    error TEXT
);

-- ============================================================
-- INDEXES
-- ============================================================

-- For finding pending events to publish
CREATE INDEX idx_outbox_status_created ON public.outbox_events(status, created_at)
WHERE status = 'pending';

-- For tenant isolation
CREATE INDEX idx_outbox_tenant ON public.outbox_events(tenant_id);

-- For event type queries
CREATE INDEX idx_outbox_event_type ON public.outbox_events(event_type);

-- For aggregate lookup
CREATE INDEX idx_outbox_aggregate ON public.outbox_events(aggregate_type, aggregate_id);

-- For retry logic
CREATE INDEX idx_outbox_retry ON public.outbox_events(status, retry_count)
WHERE status = 'pending' AND retry_count > 0;

-- ============================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================

ALTER TABLE public.outbox_events ENABLE ROW LEVEL SECURITY;

-- Allow service accounts to read/write their own events
CREATE POLICY outbox_tenant_isolation ON public.outbox_events
    FOR ALL
    USING (
        tenant_id = current_setting('app.current_tenant_id', TRUE)
        OR current_setting('app.current_tenant_id', TRUE) IS NULL
        OR auth.role() = 'service_role'
    );

-- ============================================================
-- HELPER FUNCTIONS
-- ============================================================

-- Function to cleanup old published events (keep last 30 days)
CREATE OR REPLACE FUNCTION cleanup_outbox_events()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM public.outbox_events
    WHERE status = 'published'
    AND published_at < NOW() - INTERVAL '30 days';

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get outbox statistics
CREATE OR REPLACE FUNCTION get_outbox_stats()
RETURNS TABLE (
    total_events BIGINT,
    pending_events BIGINT,
    published_events BIGINT,
    failed_events BIGINT,
    events_with_retries BIGINT,
    oldest_pending_age INTERVAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT as total_events,
        COUNT(*) FILTER (WHERE status = 'pending')::BIGINT as pending_events,
        COUNT(*) FILTER (WHERE status = 'published')::BIGINT as published_events,
        COUNT(*) FILTER (WHERE status = 'failed')::BIGINT as failed_events,
        COUNT(*) FILTER (WHERE retry_count > 0)::BIGINT as events_with_retries,
        MAX(NOW() - created_at) FILTER (WHERE status = 'pending') as oldest_pending_age
    FROM public.outbox_events;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================
-- SCHEDULED CLEANUP JOB (Optional - requires pg_cron extension)
-- ============================================================

-- Uncomment if pg_cron is available:
-- SELECT cron.schedule(
--     'cleanup-outbox-events',
--     '0 2 * * *',  -- Run daily at 2 AM
--     $$SELECT cleanup_outbox_events();$$
-- );

-- ============================================================
-- GRANTS
-- ============================================================

GRANT SELECT, INSERT, UPDATE ON public.outbox_events TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.outbox_events TO service_role;
GRANT USAGE ON SEQUENCE outbox_events_id_seq TO authenticated, service_role;

-- ============================================================
-- COMMENTS
-- ============================================================

COMMENT ON TABLE public.outbox_events IS
'Outbox pattern for guaranteed event delivery. Events are saved here first, then published to EventBus.';

COMMENT ON COLUMN public.outbox_events.event_id IS
'Unique event identifier (UUID)';

COMMENT ON COLUMN public.outbox_events.event_type IS
'Event type (e.g., workflow.completed, bia.risk.identified)';

COMMENT ON COLUMN public.outbox_events.aggregate_type IS
'Type of aggregate that created the event (e.g., workflow, bia, incident)';

COMMENT ON COLUMN public.outbox_events.aggregate_id IS
'ID of the aggregate instance';

COMMENT ON COLUMN public.outbox_events.payload IS
'Event data (JSON)';

COMMENT ON COLUMN public.outbox_events.status IS
'Event status: pending (not yet published), published (successfully published), failed (max retries exceeded)';

COMMENT ON COLUMN public.outbox_events.retry_count IS
'Number of publish attempts';

-- ============================================================
-- MIGRATION VERIFICATION
-- ============================================================

DO $$
BEGIN
    -- Verify table exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables
                   WHERE table_schema = 'public'
                   AND table_name = 'outbox_events') THEN
        RAISE EXCEPTION 'Table outbox_events was not created';
    END IF;

    -- Verify indexes exist
    IF NOT EXISTS (SELECT 1 FROM pg_indexes
                   WHERE tablename = 'outbox_events'
                   AND indexname = 'idx_outbox_status_created') THEN
        RAISE EXCEPTION 'Index idx_outbox_status_created was not created';
    END IF;

    RAISE NOTICE '✅ Migration 044_outbox_events completed successfully';
END $$;
