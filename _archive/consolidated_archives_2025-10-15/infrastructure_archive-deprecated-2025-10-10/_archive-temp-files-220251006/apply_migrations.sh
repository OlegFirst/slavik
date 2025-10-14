#!/bin/bash
# ============================================
# Auto-apply all migrations to Supabase
# ============================================

set -e  # Exit on error

MIGRATIONS_DIR="/Users/MD/AI-Platform-ISO/infrastructure/database/migrations_source"
DB_URL="${DATABASE_URL}"

echo "🚀 Starting migration application..."
echo "📁 Migrations directory: $MIGRATIONS_DIR"
echo ""

# Load .env
if [ -f "/Users/MD/AI-Platform-ISO/.env" ]; then
    export $(cat /Users/MD/AI-Platform-ISO/.env | grep -v '^#' | xargs)
fi

# Check psql
if ! command -v psql &> /dev/null; then
    echo "❌ psql not found. Installing..."
    brew install postgresql
fi

# Apply migrations in order
for migration in $(ls $MIGRATIONS_DIR/*.sql | sort); do
    filename=$(basename "$migration")
    echo "📄 Applying: $filename"

    # Use Supabase REST API instead of direct psql
    RESPONSE=$(curl -s -X POST "${SUPABASE_URL}/rest/v1/rpc/exec_sql" \
        -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
        -H "Content-Type: application/json" \
        -d "{\"query\": $(jq -Rs . < "$migration")}")

    if echo "$RESPONSE" | grep -q "error"; then
        echo "❌ Failed: $filename"
        echo "$RESPONSE"
        exit 1
    else
        echo "✅ Success: $filename"
    fi
done

echo ""
echo "🎉 All migrations applied successfully!"
