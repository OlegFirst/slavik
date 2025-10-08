#!/bin/bash
# ============================================
# Apply migrations using Supabase CLI
# More reliable than REST API
# ============================================

set -e

MIGRATIONS_DIR="/Users/MD/AI-Platform-ISO/infrastructure/database/migrations_source"

# Load .env
source /Users/MD/AI-Platform-ISO/.env

echo "🚀 Applying migrations via Supabase CLI..."

# Check if supabase CLI installed
if ! command -v supabase &> /dev/null; then
    echo "📦 Installing Supabase CLI..."
    brew install supabase/tap/supabase
fi

# Apply each migration via psql directly
for migration in $(ls $MIGRATIONS_DIR/*.sql | sort); do
    filename=$(basename "$migration")

    # Skip already applied (check your notes)
    if [[ "$filename" < "006_" ]]; then
        echo "⏭️  Skipping (already applied): $filename"
        continue
    fi

    echo "📄 Applying: $filename"

    # Use psql with connection string
    PGPASSWORD="${SUPABASE_SERVICE_ROLE_KEY}" psql \
        "postgresql://postgres:K@x3ta9V8GK5rnW@db.tpdkhddtbhpoqzzgxfni.supabase.co:5432/postgres" \
        -f "$migration" \
        -v ON_ERROR_STOP=1

    if [ $? -eq 0 ]; then
        echo "✅ Success: $filename"
    else
        echo "❌ Failed: $filename"
        exit 1
    fi
done

echo ""
echo "🎉 All migrations applied!"
