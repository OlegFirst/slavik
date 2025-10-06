#!/bin/bash
# Apply Portal Service Database Migrations

set -e

echo "🚀 Applying Portal Service Database Migrations..."

# Database connection settings
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-bcm_platform}
DB_USER=${DB_USER:-bcm_user}
DB_PASSWORD=${DB_PASSWORD:-bcm_password}

# Export password for psql
export PGPASSWORD=$DB_PASSWORD

MIGRATIONS_DIR="$(dirname "$0")/../database/migrations"

echo "📊 Database: $DB_NAME @ $DB_HOST:$DB_PORT"
echo "👤 User: $DB_USER"
echo ""

# Function to run migration
apply_migration() {
    local migration_file=$1
    local migration_name=$(basename "$migration_file")

    echo "▶️  Applying: $migration_name"

    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$migration_file" > /dev/null 2>&1; then
        echo "✅ Success: $migration_name"
    else
        echo "❌ Failed: $migration_name"
        exit 1
    fi
}

# Apply migrations in order
echo "1️⃣  Knowledge Hub & Scenarios..."
apply_migration "$MIGRATIONS_DIR/001_initial_portal_schema.sql"

echo ""
echo "2️⃣  Scenario Marketplace..."
apply_migration "$MIGRATIONS_DIR/002_add_scenarios.sql"

echo ""
echo "3️⃣  Community Forum..."
apply_migration "$MIGRATIONS_DIR/003_add_forum.sql"

echo ""
echo "🎉 All migrations applied successfully!"
echo ""
echo "Verifying schema..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\dt portal.*"

echo ""
echo "✅ Portal Service database is ready!"
