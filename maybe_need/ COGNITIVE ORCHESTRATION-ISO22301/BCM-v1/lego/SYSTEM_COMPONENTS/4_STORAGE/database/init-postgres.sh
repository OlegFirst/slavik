#!/bin/sh
set -e

# Create BCM user if it doesn't exist
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create user if not exists
    DO
    \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'bcm_user') THEN
            CREATE USER bcm_user WITH PASSWORD 'bcm_secure_pwd';
        END IF;
    END
    \$\$;
    
    -- Grant privileges
    GRANT ALL PRIVILEGES ON DATABASE bcm_platform TO bcm_user;
    GRANT ALL ON SCHEMA public TO bcm_user;
    
    -- Create tables for event store
    CREATE TABLE IF NOT EXISTS events (
        id SERIAL PRIMARY KEY,
        event_id VARCHAR(255) UNIQUE NOT NULL,
        event_type VARCHAR(255) NOT NULL,
        tenant_id VARCHAR(255) NOT NULL,
        data JSONB NOT NULL,
        metadata JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_event_type (event_type),
        INDEX idx_tenant_id (tenant_id),
        INDEX idx_created_at (created_at)
    );
    
    -- Create tables for orchestrator decisions
    CREATE TABLE IF NOT EXISTS ai_decisions (
        id SERIAL PRIMARY KEY,
        decision_id VARCHAR(255) UNIQUE NOT NULL,
        tenant_id VARCHAR(255) NOT NULL,
        decision_type VARCHAR(255) NOT NULL,
        confidence FLOAT NOT NULL,
        reasoning TEXT,
        data JSONB NOT NULL,
        status VARCHAR(50) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_status (status),
        INDEX idx_tenant_decision (tenant_id, status)
    );
    
    -- Grant permissions on new tables
    GRANT ALL ON ALL TABLES IN SCHEMA public TO bcm_user;
    GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO bcm_user;
EOSQL

echo "PostgreSQL initialization completed successfully"
