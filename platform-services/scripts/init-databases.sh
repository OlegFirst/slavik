#!/bin/bash
set -e

# This script creates multiple databases in PostgreSQL for BCM Platform services
# It's executed automatically when the PostgreSQL container starts

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create additional databases for different BCM services
    SELECT 'CREATE DATABASE planning'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'planning')\gexec

    SELECT 'CREATE DATABASE plans'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'plans')\gexec

    SELECT 'CREATE DATABASE governance'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'governance')\gexec

    SELECT 'CREATE DATABASE risk'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'risk')\gexec

    SELECT 'CREATE DATABASE response'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'response')\gexec

    SELECT 'CREATE DATABASE learning'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'learning')\gexec

    -- Grant all privileges to bcm_user on all databases
    GRANT ALL PRIVILEGES ON DATABASE planning TO bcm_user;
    GRANT ALL PRIVILEGES ON DATABASE plans TO bcm_user;
    GRANT ALL PRIVILEGES ON DATABASE governance TO bcm_user;
    GRANT ALL PRIVILEGES ON DATABASE risk TO bcm_user;
    GRANT ALL PRIVILEGES ON DATABASE response TO bcm_user;
    GRANT ALL PRIVILEGES ON DATABASE learning TO bcm_user;

    -- Enable UUID extension on main database
    \c bcm_platform
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    -- Enable extensions on planning database
    \c planning
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    GRANT ALL ON SCHEMA public TO bcm_user;

    -- Enable extensions on plans database
    \c plans
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    GRANT ALL ON SCHEMA public TO bcm_user;

EOSQL

echo "✅ All BCM databases created successfully!"
