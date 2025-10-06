#!/bin/bash

# =====================================================
# Learning System Enhancements - Database Migration
# =====================================================

echo "🎓 Applying Learning System Enhancements Migration..."
echo ""

# Supabase connection details
DB_HOST="aws-1-eu-north-1.pooler.supabase.com"
DB_USER="postgres.tpdkhddtbhpoqzzgxfni"
DB_NAME="postgres"
DB_PORT="5432"
DB_PASSWORD="K@x3ta9V8GK5rnW"

MIGRATION_FILE="../../infrastructure/database/migrations_source/043_learning_system_enhancements.sql"

# Check if migration file exists
if [ ! -f "$MIGRATION_FILE" ]; then
    echo "❌ Migration file not found: $MIGRATION_FILE"
    exit 1
fi

echo "📋 Migration Details:"
echo "   File: $MIGRATION_FILE"
echo "   Database: $DB_NAME @ $DB_HOST"
echo ""

# Apply migration
echo "🚀 Applying migration..."
PGPASSWORD="$DB_PASSWORD" psql \
    -h "$DB_HOST" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    -p "$DB_PORT" \
    -f "$MIGRATION_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migration applied successfully!"
    echo ""
    echo "📊 New Tables Created:"
    echo "   - learning.user_competencies"
    echo "   - learning.team_competencies"
    echo "   - learning.role_competency_gaps"
    echo "   - learning.bcm_processes"
    echo "   - learning.process_coverage"
    echo "   - learning.gamification_profiles"
    echo "   - learning.badge_definitions (with seed data)"
    echo "   - learning.achievement_definitions"
    echo "   - learning.leaderboards"
    echo "   - learning.gap_knowledge_mappings"
    echo "   - learning.learning_paths"
    echo "   - learning.user_learning_progress"
    echo "   - learning.smart_goals"
    echo "   - learning.alerts"
    echo ""
    echo "🎯 Next Steps:"
    echo "   1. Start the Learning System service: python main.py"
    echo "   2. Access API docs: http://localhost:8033/docs"
    echo "   3. Test endpoints from ENHANCEMENT_IMPLEMENTATION_COMPLETE.md"
else
    echo ""
    echo "❌ Migration failed!"
    echo "   Check the error messages above for details"
    exit 1
fi
