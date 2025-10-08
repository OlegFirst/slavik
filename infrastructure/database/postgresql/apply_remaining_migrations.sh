#!/bin/bash
# Apply remaining migrations 037-043 to Supabase

set -e

DB_HOST="aws-1-eu-north-1.pooler.supabase.com"
DB_USER="postgres.tpdkhddtbhpoqzzgxfni"
DB_NAME="postgres"
DB_PORT="5432"
export PGPASSWORD='K@x3ta9V8GK5rnW'

MIGRATIONS_DIR="/Users/MD/AI-Platform-ISO/infrastructure/database/migrations_source"

echo "🚀 Applying remaining migrations to Supabase..."
echo ""

# Migrations to apply (avoiding duplicates)
MIGRATIONS=(
    "037_community_intelligence.sql"
    "038_add_gateway_state.sql"
    "040_community_intelligence.sql"
    "041_collective_agents.sql"
    "042_predictive_service.sql"
    "043_learning_system_enhancements.sql"
)

for migration in "${MIGRATIONS[@]}"; do
    migration_file="$MIGRATIONS_DIR/$migration"
    migration_num=$(echo $migration | grep -oE '^[0-9]+')

    if [ ! -f "$migration_file" ]; then
        echo "⚠️  Migration file not found: $migration"
        continue
    fi

    echo "📝 Applying migration: $migration"

    # Apply migration
    psql -h $DB_HOST -U $DB_USER -d $DB_NAME -p $DB_PORT -f "$migration_file"

    if [ $? -eq 0 ]; then
        echo "✅ Migration $migration applied successfully"

        # Record migration
        psql -h $DB_HOST -U $DB_USER -d $DB_NAME -p $DB_PORT -c \
            "INSERT INTO public.schema_migrations (version) VALUES ('$migration_num') ON CONFLICT DO NOTHING"

        echo ""
    else
        echo "❌ Migration $migration FAILED"
        exit 1
    fi
done

echo ""
echo "✅ All migrations applied successfully!"
echo ""

# Show current migration status
echo "📊 Current migrations:"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -p $DB_PORT -c \
    "SELECT version FROM public.schema_migrations ORDER BY version DESC LIMIT 10"
