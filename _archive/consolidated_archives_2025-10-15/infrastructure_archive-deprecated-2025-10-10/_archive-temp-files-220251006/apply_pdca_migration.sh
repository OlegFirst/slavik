#!/bin/bash
# ============================================================================
# Apply PDCA Cycles Migration to Supabase
# ============================================================================
# Purpose: Create pdca_cycles table and functions in Supabase
# Usage: ./apply_pdca_migration.sh
# ============================================================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}================================${NC}"
echo -e "${YELLOW}PDCA Migration to Supabase${NC}"
echo -e "${YELLOW}================================${NC}"
echo ""

# ============================================================================
# Configuration
# ============================================================================

SUPABASE_HOST="aws-1-eu-north-1.pooler.supabase.com"
SUPABASE_PORT="5432"
SUPABASE_DB="postgres"
SUPABASE_USER="postgres.tpdkhddtbhpoqzzgxfni"
SUPABASE_PASSWORD="K@x3ta9V8GK5rnW"

MIGRATION_FILE="$(dirname "$0")/migrations/025_pdca_cycles.sql"

# ============================================================================
# Validation
# ============================================================================

echo -e "${YELLOW}Step 1: Validating migration file...${NC}"

if [ ! -f "$MIGRATION_FILE" ]; then
    echo -e "${RED}❌ Migration file not found: $MIGRATION_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Migration file found${NC}"
echo ""

# ============================================================================
# Connection Test
# ============================================================================

echo -e "${YELLOW}Step 2: Testing Supabase connection...${NC}"

PGPASSWORD=$SUPABASE_PASSWORD psql \
    -h $SUPABASE_HOST \
    -U $SUPABASE_USER \
    -d $SUPABASE_DB \
    -p $SUPABASE_PORT \
    -c "SELECT version();" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Connection successful${NC}"
else
    echo -e "${RED}❌ Connection failed${NC}"
    echo -e "${YELLOW}Check your credentials and network${NC}"
    exit 1
fi

echo ""

# ============================================================================
# Check Existing Table
# ============================================================================

echo -e "${YELLOW}Step 3: Checking for existing pdca_cycles table...${NC}"

EXISTING_TABLE=$(PGPASSWORD=$SUPABASE_PASSWORD psql \
    -h $SUPABASE_HOST \
    -U $SUPABASE_USER \
    -d $SUPABASE_DB \
    -p $SUPABASE_PORT \
    -t \
    -c "SELECT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'workflow_intelligence'
        AND table_name = 'pdca_cycles'
    );")

if [[ $EXISTING_TABLE == *"t"* ]]; then
    echo -e "${YELLOW}⚠️  Table pdca_cycles already exists${NC}"
    echo -e "${YELLOW}Do you want to DROP and recreate it? (yes/no)${NC}"
    read -r CONFIRM

    if [ "$CONFIRM" != "yes" ]; then
        echo -e "${RED}❌ Migration cancelled${NC}"
        exit 1
    fi

    echo -e "${YELLOW}Dropping existing table...${NC}"
    PGPASSWORD=$SUPABASE_PASSWORD psql \
        -h $SUPABASE_HOST \
        -U $SUPABASE_USER \
        -d $SUPABASE_DB \
        -p $SUPABASE_PORT \
        -c "DROP TABLE IF EXISTS workflow_intelligence.pdca_cycles CASCADE;"

    echo -e "${GREEN}✅ Table dropped${NC}"
else
    echo -e "${GREEN}✅ No existing table found${NC}"
fi

echo ""

# ============================================================================
# Apply Migration
# ============================================================================

echo -e "${YELLOW}Step 4: Applying migration...${NC}"

PGPASSWORD=$SUPABASE_PASSWORD psql \
    -h $SUPABASE_HOST \
    -U $SUPABASE_USER \
    -d $SUPABASE_DB \
    -p $SUPABASE_PORT \
    -f "$MIGRATION_FILE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Migration applied successfully${NC}"
else
    echo -e "${RED}❌ Migration failed${NC}"
    exit 1
fi

echo ""

# ============================================================================
# Verification
# ============================================================================

echo -e "${YELLOW}Step 5: Verifying migration...${NC}"

# Check table exists
TABLE_CHECK=$(PGPASSWORD=$SUPABASE_PASSWORD psql \
    -h $SUPABASE_HOST \
    -U $SUPABASE_USER \
    -d $SUPABASE_DB \
    -p $SUPABASE_PORT \
    -t \
    -c "SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = 'workflow_intelligence'
        AND table_name = 'pdca_cycles';")

if [[ $TABLE_CHECK -eq 1 ]]; then
    echo -e "${GREEN}✅ Table created${NC}"
else
    echo -e "${RED}❌ Table not found${NC}"
    exit 1
fi

# Check RLS enabled
RLS_CHECK=$(PGPASSWORD=$SUPABASE_PASSWORD psql \
    -h $SUPABASE_HOST \
    -U $SUPABASE_USER \
    -d $SUPABASE_DB \
    -p $SUPABASE_PORT \
    -t \
    -c "SELECT rowsecurity
        FROM pg_tables
        WHERE schemaname = 'workflow_intelligence'
        AND tablename = 'pdca_cycles';")

if [[ $RLS_CHECK == *"t"* ]]; then
    echo -e "${GREEN}✅ RLS enabled${NC}"
else
    echo -e "${RED}❌ RLS not enabled${NC}"
    exit 1
fi

# Check indexes
INDEX_COUNT=$(PGPASSWORD=$SUPABASE_PASSWORD psql \
    -h $SUPABASE_HOST \
    -U $SUPABASE_USER \
    -d $SUPABASE_DB \
    -p $SUPABASE_PORT \
    -t \
    -c "SELECT COUNT(*)
        FROM pg_indexes
        WHERE schemaname = 'workflow_intelligence'
        AND tablename = 'pdca_cycles';")

echo -e "${GREEN}✅ Indexes created: $INDEX_COUNT${NC}"

# Check functions
FUNCTION_COUNT=$(PGPASSWORD=$SUPABASE_PASSWORD psql \
    -h $SUPABASE_HOST \
    -U $SUPABASE_USER \
    -d $SUPABASE_DB \
    -p $SUPABASE_PORT \
    -t \
    -c "SELECT COUNT(*)
        FROM pg_proc
        WHERE proname LIKE '%pdca%'
        AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'workflow_intelligence');")

echo -e "${GREEN}✅ Functions created: $FUNCTION_COUNT${NC}"

# Check policies
POLICY_COUNT=$(PGPASSWORD=$SUPABASE_PASSWORD psql \
    -h $SUPABASE_HOST \
    -U $SUPABASE_USER \
    -d $SUPABASE_DB \
    -p $SUPABASE_PORT \
    -t \
    -c "SELECT COUNT(*)
        FROM pg_policies
        WHERE schemaname = 'workflow_intelligence'
        AND tablename = 'pdca_cycles';")

echo -e "${GREEN}✅ RLS policies created: $POLICY_COUNT${NC}"

echo ""

# ============================================================================
# Summary
# ============================================================================

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✅ MIGRATION SUCCESSFUL${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "📊 Summary:"
echo -e "  • Schema: workflow_intelligence"
echo -e "  • Table: pdca_cycles"
echo -e "  • Indexes: $INDEX_COUNT"
echo -e "  • Functions: $FUNCTION_COUNT"
echo -e "  • RLS Policies: $POLICY_COUNT"
echo -e "  • RLS: Enabled"
echo ""
echo -e "🎯 Next steps:"
echo -e "  1. Update pdca_rules.py to use PostgreSQL"
echo -e "  2. Test cycle creation and retrieval"
echo -e "  3. Verify RLS with tenant isolation"
echo ""
echo -e "${GREEN}Ready to use!${NC}"
