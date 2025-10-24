-- ============================================
-- BCM Platform - Unified Database
-- Migration 000: Migration Tracking System
-- ============================================
-- Creates migration tracking infrastructure
-- Run this migration FIRST before any other migrations
-- ============================================

-- Migration tracking table
CREATE TABLE IF NOT EXISTS public.migration_tracking (
    id SERIAL PRIMARY KEY,
    migration_number INTEGER NOT NULL UNIQUE,
    migration_name VARCHAR(255) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    applied_at TIMESTAMP DEFAULT NOW(),
    checksum VARCHAR(64),
    status VARCHAR(20) DEFAULT 'applied',
    applied_by VARCHAR(100) DEFAULT CURRENT_USER,
    execution_time_ms INTEGER,
    notes TEXT
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_migration_number ON public.migration_tracking(migration_number);
CREATE INDEX IF NOT EXISTS idx_migration_status ON public.migration_tracking(status);
CREATE INDEX IF NOT EXISTS idx_applied_at ON public.migration_tracking(applied_at DESC);

-- Function to register migration
CREATE OR REPLACE FUNCTION public.register_migration(
    p_number INTEGER,
    p_name VARCHAR(255),
    p_filename VARCHAR(255),
    p_checksum VARCHAR(64) DEFAULT NULL,
    p_execution_time_ms INTEGER DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    INSERT INTO public.migration_tracking (
        migration_number,
        migration_name,
        filename,
        checksum,
        execution_time_ms,
        status
    ) VALUES (
        p_number,
        p_name,
        p_filename,
        p_checksum,
        p_execution_time_ms,
        'applied'
    )
    ON CONFLICT (migration_number) DO UPDATE SET
        applied_at = NOW(),
        status = 'applied',
        execution_time_ms = COALESCE(EXCLUDED.execution_time_ms, migration_tracking.execution_time_ms);
END;
$$ LANGUAGE plpgsql;

-- Function to check if migration is applied
CREATE OR REPLACE FUNCTION public.is_migration_applied(p_number INTEGER)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.migration_tracking
        WHERE migration_number = p_number
        AND status = 'applied'
    );
END;
$$ LANGUAGE plpgsql;

-- Function to get latest migration
CREATE OR REPLACE FUNCTION public.get_latest_migration()
RETURNS INTEGER AS $$
BEGIN
    RETURN COALESCE(
        (SELECT MAX(migration_number) FROM public.migration_tracking WHERE status = 'applied'),
        0
    );
END;
$$ LANGUAGE plpgsql;

-- View for migration status
CREATE OR REPLACE VIEW public.migration_status AS
SELECT
    migration_number,
    migration_name,
    filename,
    applied_at,
    applied_by,
    execution_time_ms,
    status
FROM public.migration_tracking
ORDER BY migration_number;

-- Grant permissions
GRANT SELECT ON public.migration_tracking TO authenticated;
GRANT SELECT ON public.migration_status TO authenticated;

-- Register this migration
SELECT public.register_migration(
    0,
    'Migration Tracking System',
    '000_migration_tracking.sql',
    NULL,
    NULL
);

COMMENT ON TABLE public.migration_tracking IS 'Tracks all applied database migrations';
COMMENT ON FUNCTION public.register_migration IS 'Registers a migration as applied';
COMMENT ON FUNCTION public.is_migration_applied IS 'Checks if a migration has been applied';
COMMENT ON FUNCTION public.get_latest_migration IS 'Returns the latest applied migration number';
