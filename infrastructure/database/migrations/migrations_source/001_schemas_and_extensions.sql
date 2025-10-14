-- ============================================
-- BCM Platform - Unified Database
-- Migration 001: Schemas and Extensions
-- ============================================
-- Creates all database schemas and enables required extensions
-- Run this migration first on fresh Supabase PostgreSQL instance
-- ============================================

-- Enable required PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";      -- UUID generation
CREATE EXTENSION IF NOT EXISTS "pg_trgm";        -- Trigram matching for fuzzy search
CREATE EXTENSION IF NOT EXISTS "btree_gin";      -- GIN indexes for multiple column types

-- Create schemas
CREATE SCHEMA IF NOT EXISTS public;              -- Core shared tables
CREATE SCHEMA IF NOT EXISTS community;           -- Community & Marketplace
CREATE SCHEMA IF NOT EXISTS intelligence;        -- Digital Twins & AI
CREATE SCHEMA IF NOT EXISTS seh;                 -- Social Enterprise Hub (WHO programs)
CREATE SCHEMA IF NOT EXISTS bcm;                 -- BCM shared resources
CREATE SCHEMA IF NOT EXISTS bia;                 -- Business Impact Analysis (ISO 22301:2019 Clause 8.2.2)
CREATE SCHEMA IF NOT EXISTS risk;                -- Risk Management (ISO 22301:2019 Clause 8.2.3)
CREATE SCHEMA IF NOT EXISTS governance;          -- BCM Governance (ISO 22301 Clauses 5, 6, 7)
CREATE SCHEMA IF NOT EXISTS audit;               -- Audit logs and event sourcing

-- Grant usage on schemas to authenticated users (Supabase)
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT USAGE ON SCHEMA community TO authenticated;
GRANT USAGE ON SCHEMA intelligence TO authenticated;
GRANT USAGE ON SCHEMA seh TO authenticated;
GRANT USAGE ON SCHEMA bcm TO authenticated;
GRANT USAGE ON SCHEMA bia TO authenticated;
GRANT USAGE ON SCHEMA risk TO authenticated;
GRANT USAGE ON SCHEMA governance TO authenticated;
GRANT USAGE ON SCHEMA audit TO authenticated;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA community GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA intelligence GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA seh GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA bcm GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA bia GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA risk GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA governance GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA audit GRANT SELECT ON TABLES TO authenticated; -- Read-only for audit

COMMENT ON SCHEMA public IS 'Core shared tables: organizations, users, teams';
COMMENT ON SCHEMA community IS 'Community marketplace: specialists, services, engagements';
COMMENT ON SCHEMA intelligence IS 'Digital twins, simulations, AI systems';
COMMENT ON SCHEMA seh IS 'Social Enterprise Hub for NPO/NGO management';
COMMENT ON SCHEMA bcm IS 'BCM shared resources and templates';
COMMENT ON SCHEMA bia IS 'Business Impact Analysis - ISO 22301:2019 Clause 8.2.2';
COMMENT ON SCHEMA risk IS 'Risk Management - ISO 22301:2019 Clause 8.2.3';
COMMENT ON SCHEMA governance IS 'BCM Governance - ISO 22301 Clauses 5, 6, 7';
COMMENT ON SCHEMA audit IS 'Unified audit logging and event sourcing';

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 001 completed: Schemas and extensions created';
END
$$;
