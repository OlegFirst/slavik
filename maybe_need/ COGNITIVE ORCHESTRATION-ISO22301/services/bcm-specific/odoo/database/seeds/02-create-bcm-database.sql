-- =====================================================
-- BCM Platform - Auto Database Creation
-- Creates bcm_platform database automatically
-- =====================================================

-- Create BCM platform database if not exists
SELECT 'CREATE DATABASE bcm_platform'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'bcm_platform')\gexec

-- Create odoo user if not exists
DO
$do$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'odoo') THEN
      CREATE ROLE odoo WITH LOGIN PASSWORD 'postgres123' CREATEDB;
   END IF;
END
$do$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE bcm_platform TO odoo;

-- Set up for Odoo web interface auto-creation
\c bcm_platform;

-- Ensure database is ready for Odoo initialization
SELECT 'BCM Platform database ready for Odoo' as status;