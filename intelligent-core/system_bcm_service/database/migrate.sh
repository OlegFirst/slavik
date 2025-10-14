#!/bin/bash

# System BCM - Database Migration Script
# Runs database migrations using Alembic

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   System BCM - Database Migration                    ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# Load environment variables
if [ -f .env ]; then
    echo -e "${BLUE}Loading environment variables...${NC}"
    export $(cat .env | grep -v '^#' | xargs)
    echo -e "${GREEN}✅ Environment loaded${NC}"
else
    echo -e "${YELLOW}⚠️  No .env file found, using defaults${NC}"
fi

# Set defaults
export POSTGRES_HOST=${POSTGRES_HOST:-localhost}
export POSTGRES_PORT=${POSTGRES_PORT:-5432}
export POSTGRES_USER=${POSTGRES_USER:-postgres}
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-}
export POSTGRES_DB=${POSTGRES_DB:-platform}

echo ""
echo -e "${BLUE}Database Configuration:${NC}"
echo "  Host: $POSTGRES_HOST"
echo "  Port: $POSTGRES_PORT"
echo "  Database: $POSTGRES_DB"
echo "  User: $POSTGRES_USER"
echo ""

# Check PostgreSQL connection
echo -e "${BLUE}Checking PostgreSQL connection...${NC}"
if PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL connection successful${NC}"
else
    echo -e "${RED}❌ Cannot connect to PostgreSQL${NC}"
    echo ""
    echo "Please check:"
    echo "  1. PostgreSQL is running"
    echo "  2. Database '$POSTGRES_DB' exists"
    echo "  3. User '$POSTGRES_USER' has access"
    echo "  4. Credentials in .env are correct"
    exit 1
fi

echo ""

# Check if alembic is installed
if ! command -v alembic &> /dev/null; then
    echo -e "${YELLOW}⚠️  Alembic not found, installing...${NC}"
    pip install alembic
    echo -e "${GREEN}✅ Alembic installed${NC}"
fi

echo ""

# Migration command
COMMAND=${1:-upgrade}

case $COMMAND in
    upgrade)
        echo -e "${BLUE}Running database migrations (upgrade to head)...${NC}"
        alembic upgrade head
        echo -e "${GREEN}✅ Migrations applied successfully${NC}"
        ;;

    downgrade)
        echo -e "${BLUE}Rolling back last migration...${NC}"
        alembic downgrade -1
        echo -e "${GREEN}✅ Rollback complete${NC}"
        ;;

    current)
        echo -e "${BLUE}Current migration version:${NC}"
        alembic current
        ;;

    history)
        echo -e "${BLUE}Migration history:${NC}"
        alembic history
        ;;

    init)
        echo -e "${BLUE}Initializing database with schema.sql directly...${NC}"
        PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -f database/schema.sql
        echo -e "${GREEN}✅ Database initialized${NC}"
        ;;

    reset)
        echo -e "${YELLOW}⚠️  Resetting database (this will drop all tables!)${NC}"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            # Drop all System BCM tables
            PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB <<EOF
DROP TABLE IF EXISTS system_bcm_events CASCADE;
DROP TABLE IF EXISTS system_bcm_improvements CASCADE;
DROP TABLE IF EXISTS system_bcm_patterns CASCADE;
DROP TABLE IF EXISTS system_bcm_platform_health CASCADE;
DROP TABLE IF EXISTS system_bcm_insights CASCADE;
DROP TABLE IF EXISTS system_bcm_recovery_executions CASCADE;
DROP TABLE IF EXISTS system_bcm_cycles CASCADE;
DROP VIEW IF EXISTS v_platform_health_summary;
DROP VIEW IF EXISTS v_active_insights;
DROP VIEW IF EXISTS v_recovery_performance;
DROP VIEW IF EXISTS v_recent_cycles;
DROP FUNCTION IF EXISTS update_updated_at_column();
EOF
            echo -e "${GREEN}✅ Database reset complete${NC}"

            # Re-run migrations
            echo -e "${BLUE}Re-applying migrations...${NC}"
            alembic upgrade head
            echo -e "${GREEN}✅ Migrations applied${NC}"
        else
            echo -e "${YELLOW}Reset cancelled${NC}"
        fi
        ;;

    verify)
        echo -e "${BLUE}Verifying database schema...${NC}"

        # Check if tables exist
        TABLES=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -t -c "
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name LIKE 'system_bcm%'
            ORDER BY table_name;
        " | tr -d ' ')

        if [ -z "$TABLES" ]; then
            echo -e "${RED}❌ No System BCM tables found${NC}"
            echo ""
            echo "Run: ./database/migrate.sh init"
            exit 1
        fi

        echo -e "${GREEN}✅ Found System BCM tables:${NC}"
        echo "$TABLES" | sed 's/^/  - /'

        # Count rows in each table
        echo ""
        echo -e "${BLUE}Table statistics:${NC}"

        for table in $TABLES; do
            count=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -t -c "SELECT COUNT(*) FROM $table" | tr -d ' ')
            echo "  $table: $count rows"
        done

        echo ""
        echo -e "${GREEN}✅ Database verification complete${NC}"
        ;;

    *)
        echo "Usage: $0 {upgrade|downgrade|current|history|init|reset|verify}"
        echo ""
        echo "Commands:"
        echo "  upgrade    - Apply all pending migrations"
        echo "  downgrade  - Roll back the last migration"
        echo "  current    - Show current migration version"
        echo "  history    - Show migration history"
        echo "  init       - Initialize database with schema.sql directly"
        echo "  reset      - Drop all tables and re-apply migrations"
        echo "  verify     - Verify database schema exists"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ Database Migration Complete                      ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
