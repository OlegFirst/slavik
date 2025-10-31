#!/bin/bash
set -e

# Create multiple databases
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE bcm_events;
    CREATE DATABASE odoo_bcm;
    GRANT ALL PRIVILEGES ON DATABASE bcm_events TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON DATABASE odoo_bcm TO $POSTGRES_USER;
EOSQL

# Create events table in bcm_events database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname=bcm_events <<-EOSQL
    CREATE TABLE IF NOT EXISTS events (
        id SERIAL PRIMARY KEY,
        event_type VARCHAR(255) NOT NULL,
        tenant_id VARCHAR(255) NOT NULL,
        data JSONB DEFAULT '{}',
        user_id VARCHAR(255),
        correlation_id VARCHAR(255),
        event_id VARCHAR(255) UNIQUE,
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(50) DEFAULT 'published'
    );

    -- Migration: Add event_id column if it doesn't exist (for backward compatibility)
    DO \$\$ 
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'events' AND column_name = 'event_id'
        ) THEN
            ALTER TABLE events ADD COLUMN event_id VARCHAR(255) UNIQUE;
        END IF;
    END \$\$;

    CREATE INDEX IF NOT EXISTS idx_event_type ON events(event_type);
    CREATE INDEX IF NOT EXISTS idx_tenant_id ON events(tenant_id);
    CREATE INDEX IF NOT EXISTS idx_created_at ON events(created_at);
    CREATE INDEX IF NOT EXISTS idx_correlation_id ON events(correlation_id);
    CREATE UNIQUE INDEX IF NOT EXISTS idx_event_id ON events(event_id) WHERE event_id IS NOT NULL;
EOSQL

echo "PostgreSQL initialization completed"
