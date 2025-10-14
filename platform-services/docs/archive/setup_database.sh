#!/bin/bash
# ============================================
# BCM Platform - Database Setup Script
# ============================================
# Complete database initialization and migration application
# Handles both fresh setup and incremental migrations
# ============================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   BCM Platform - Database Setup & Migration Script            ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo ""

# ============================================
# Configuration
# ============================================

PROJECT_ROOT="/Users/MD/AI-Platform-ISO"
DB_DIR="${PROJECT_ROOT}/infrastructure/database"
MIGRATIONS_DIR="${DB_DIR}/migrations_source"
POSTGRESQL_DIR="${DB_DIR}/postgresql/migrations_source"

# Load environment variables
ENV_FILE="${PROJECT_ROOT}/.env"
if [ -f "$ENV_FILE" ]; then
    echo -e "${GREEN}✓${NC} Loading environment from ${ENV_FILE}"
    export $(cat "$ENV_FILE" | grep -v '^#' | grep -v '^$' | xargs)
else
    echo -e "${YELLOW}⚠${NC} No .env file found at ${ENV_FILE}"
    echo -e "${YELLOW}⚠${NC} Using environment variables if set"
fi

# Check for required environment variables
check_env_var() {
    local var_name=$1
    if [ -z "${!var_name}" ]; then
        echo -e "${RED}✗${NC} Required environment variable ${var_name} is not set"
        return 1
    else
        echo -e "${GREEN}✓${NC} ${var_name} is configured"
        return 0
    fi
}

# ============================================
# Database Connection Check
# ============================================

echo ""
echo -e "${BLUE}[1/5] Checking Database Connection${NC}"
echo "───────────────────────────────────────────────────────────────"

# Check if using Supabase or local PostgreSQL
if [ -n "$SUPABASE_URL" ] && [ -n "$SUPABASE_SERVICE_ROLE_KEY" ]; then
    echo -e "${GREEN}✓${NC} Using Supabase database"
    DB_TYPE="supabase"

    # Extract database connection details from Supabase URL
    SUPABASE_PROJECT_ID=$(echo "$SUPABASE_URL" | sed -E 's|https://([^.]+)\.supabase\.co|\1|')
    echo -e "  Project: ${SUPABASE_PROJECT_ID}"

elif check_env_var "DATABASE_URL"; then
    echo -e "${GREEN}✓${NC} Using PostgreSQL database"
    DB_TYPE="postgresql"
    echo -e "  Connection: ${DATABASE_URL%%\?*}"  # Hide query params

    # Test connection
    if command -v psql &> /dev/null; then
        if psql "$DATABASE_URL" -c "SELECT 1;" &> /dev/null; then
            echo -e "${GREEN}✓${NC} Database connection successful"
        else
            echo -e "${RED}✗${NC} Cannot connect to database"
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠${NC} psql not installed, skipping connection test"
    fi
else
    echo -e "${RED}✗${NC} No database configuration found"
    echo ""
    echo "Please set one of:"
    echo "  - SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY (for Supabase)"
    echo "  - DATABASE_URL (for PostgreSQL)"
    exit 1
fi

# ============================================
# Check Migration Status
# ============================================

echo ""
echo -e "${BLUE}[2/5] Analyzing Migration Status${NC}"
echo "───────────────────────────────────────────────────────────────"

# Count available migrations
TOTAL_MIGRATIONS=$(find "$MIGRATIONS_DIR" -name "*.sql" 2>/dev/null | wc -l | tr -d ' ')
POSTGRES_MIGRATIONS=$(find "$POSTGRESQL_DIR" -name "*.sql" 2>/dev/null | wc -l | tr -d ' ')

echo -e "${GREEN}✓${NC} Found ${TOTAL_MIGRATIONS} migration files in migrations_source/"
if [ "$POSTGRES_MIGRATIONS" -gt 0 ]; then
    echo -e "${GREEN}✓${NC} Found ${POSTGRES_MIGRATIONS} additional migrations in postgresql/migrations_source/"
fi

# List migration files
echo ""
echo "Available migrations:"
ls -1 "$MIGRATIONS_DIR"/*.sql 2>/dev/null | while read -r migration; do
    filename=$(basename "$migration")
    migration_num="${filename:0:3}"
    echo -e "  ${migration_num}: ${filename}"
done | head -10
if [ "$TOTAL_MIGRATIONS" -gt 10 ]; then
    echo -e "  ... and $((TOTAL_MIGRATIONS - 10)) more"
fi

# ============================================
# Create Migration Tracking Table
# ============================================

echo ""
echo -e "${BLUE}[3/5] Setting Up Migration Tracking${NC}"
echo "───────────────────────────────────────────────────────────────"

TRACKING_SQL="
-- Create migration tracking table
CREATE TABLE IF NOT EXISTS public.schema_migrations (
    id SERIAL PRIMARY KEY,
    migration_number VARCHAR(10) UNIQUE NOT NULL,
    migration_name VARCHAR(255) NOT NULL,
    applied_at TIMESTAMP DEFAULT NOW() NOT NULL,
    checksum VARCHAR(64),
    execution_time_ms INTEGER,
    applied_by VARCHAR(100) DEFAULT current_user
);

CREATE INDEX IF NOT EXISTS idx_migrations_number ON public.schema_migrations(migration_number);
CREATE INDEX IF NOT EXISTS idx_migrations_applied_at ON public.schema_migrations(applied_at);

COMMENT ON TABLE public.schema_migrations IS 'Tracks applied database migrations';
"

if [ "$DB_TYPE" = "postgresql" ]; then
    echo "$TRACKING_SQL" | psql "$DATABASE_URL" -v ON_ERROR_STOP=1
    echo -e "${GREEN}✓${NC} Migration tracking table created"
elif [ "$DB_TYPE" = "supabase" ]; then
    # Use Supabase REST API
    TRACKING_SQL_ESCAPED=$(echo "$TRACKING_SQL" | jq -Rs .)
    RESPONSE=$(curl -s -X POST "${SUPABASE_URL}/rest/v1/rpc/exec_sql" \
        -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
        -H "Content-Type: application/json" \
        -d "{\"query\": ${TRACKING_SQL_ESCAPED}}")

    if echo "$RESPONSE" | grep -q "error"; then
        echo -e "${YELLOW}⚠${NC} Migration tracking table may already exist"
    else
        echo -e "${GREEN}✓${NC} Migration tracking table created"
    fi
fi

# ============================================
# Apply Migrations
# ============================================

echo ""
echo -e "${BLUE}[4/5] Applying Migrations${NC}"
echo "───────────────────────────────────────────────────────────────"

apply_migration() {
    local migration_file=$1
    local filename=$(basename "$migration_file")
    local migration_num="${filename:0:3}"
    local migration_name="${filename%.sql}"

    # Check if already applied
    local check_sql="SELECT COUNT(*) FROM public.schema_migrations WHERE migration_number = '$migration_num';"

    if [ "$DB_TYPE" = "postgresql" ]; then
        local applied=$(psql "$DATABASE_URL" -t -c "$check_sql" 2>/dev/null | tr -d ' ')
        if [ "$applied" = "1" ]; then
            echo -e "${BLUE}⊙${NC} ${filename} (already applied)"
            return 0
        fi
    fi

    echo -e "${YELLOW}→${NC} Applying ${filename}..."

    # Read migration SQL
    local migration_sql=$(cat "$migration_file")
    local start_time=$(date +%s%3N)

    # Apply migration
    if [ "$DB_TYPE" = "postgresql" ]; then
        if echo "$migration_sql" | psql "$DATABASE_URL" -v ON_ERROR_STOP=1 > /dev/null 2>&1; then
            local end_time=$(date +%s%3N)
            local execution_time=$((end_time - start_time))

            # Record successful migration
            psql "$DATABASE_URL" -c "INSERT INTO public.schema_migrations (migration_number, migration_name, execution_time_ms) VALUES ('$migration_num', '$migration_name', $execution_time);" > /dev/null

            echo -e "${GREEN}✓${NC} ${filename} applied successfully (${execution_time}ms)"
            return 0
        else
            echo -e "${RED}✗${NC} ${filename} failed"
            return 1
        fi
    elif [ "$DB_TYPE" = "supabase" ]; then
        # Supabase migration (via REST API)
        local migration_sql_escaped=$(echo "$migration_sql" | jq -Rs .)
        local response=$(curl -s -X POST "${SUPABASE_URL}/rest/v1/rpc/exec_sql" \
            -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
            -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
            -H "Content-Type: application/json" \
            -d "{\"query\": ${migration_sql_escaped}}")

        if echo "$response" | grep -q "error"; then
            echo -e "${RED}✗${NC} ${filename} failed"
            echo "$response" | jq -r '.error.message // .message // .' 2>/dev/null
            return 1
        else
            echo -e "${GREEN}✓${NC} ${filename} applied successfully"
            return 0
        fi
    fi
}

# Apply migrations in order
SUCCESS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0

for migration in $(ls -1 "$MIGRATIONS_DIR"/*.sql 2>/dev/null | sort); do
    if apply_migration "$migration"; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
        echo -e "${YELLOW}⚠${NC} Continuing with next migration..."
    fi
done

# Apply PostgreSQL specific migrations if they exist
if [ "$POSTGRES_MIGRATIONS" -gt 0 ]; then
    echo ""
    echo "Applying PostgreSQL-specific migrations..."
    for migration in $(ls -1 "$POSTGRESQL_DIR"/*.sql 2>/dev/null | sort); do
        if apply_migration "$migration"; then
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        else
            FAIL_COUNT=$((FAIL_COUNT + 1))
        fi
    done
fi

# ============================================
# Migration Summary
# ============================================

echo ""
echo -e "${BLUE}[5/5] Migration Summary${NC}"
echo "───────────────────────────────────────────────────────────────"
echo -e "  Total available:  ${TOTAL_MIGRATIONS}"
echo -e "  ${GREEN}Successfully applied: ${SUCCESS_COUNT}${NC}"
if [ "$FAIL_COUNT" -gt 0 ]; then
    echo -e "  ${RED}Failed: ${FAIL_COUNT}${NC}"
fi
echo ""

# Get final schema count
if [ "$DB_TYPE" = "postgresql" ]; then
    SCHEMA_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name NOT IN ('pg_catalog', 'information_schema');" 2>/dev/null | tr -d ' ')
    TABLE_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog', 'information_schema');" 2>/dev/null | tr -d ' ')

    echo -e "Database status:"
    echo -e "  Schemas: ${SCHEMA_COUNT}"
    echo -e "  Tables:  ${TABLE_COUNT}"
    echo ""
fi

# ============================================
# Completion
# ============================================

if [ "$FAIL_COUNT" -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   ✓ Database setup completed successfully!                     ║${NC}"
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    exit 0
else
    echo -e "${YELLOW}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║   ⚠ Database setup completed with ${FAIL_COUNT} failures                ║${NC}"
    echo -e "${YELLOW}╔════════════════════════════════════════════════════════════════╗${NC}"
    exit 1
fi
