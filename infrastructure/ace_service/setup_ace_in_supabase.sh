#!/bin/bash

# ACE Schema Setup for Supabase
# =============================

set -e

echo "🚀 ACE Schema Setup for Supabase"
echo "=================================="
echo ""

# Load environment variables
if [ -f "../../.env" ]; then
    export $(cat ../../.env | grep -v '^#' | xargs)
    echo "✅ Loaded .env file"
else
    echo "❌ .env file not found!"
    echo "Please create /Users/MD/AI-Platform-ISO/.env with DATABASE_URL"
    exit 1
fi

# Check DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not set!"
    echo "Please set DATABASE_URL in .env file"
    exit 1
fi

echo "📊 Database: $DATABASE_URL"
echo ""

# Apply ACE schema
echo "📝 Applying ACE schema to Supabase..."
echo ""

psql "$DATABASE_URL" -f ../database/schemas/ace_playbooks.sql

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ ACE schema applied successfully!"
    echo ""
    echo "📊 Checking tables..."
    psql "$DATABASE_URL" -c "
        SELECT table_name
        FROM information_schema.tables
        WHERE table_name LIKE 'ace_%'
        ORDER BY table_name;
    "

    echo ""
    echo "✅ ACE Setup Complete!"
    echo ""
    echo "Next steps:"
    echo "1. Start ACE Service: docker-compose up -d"
    echo "2. Check health: curl http://localhost:8050/health"
    echo "3. Integrate with modules (see INTEGRATION_GUIDE.md)"
else
    echo ""
    echo "❌ Failed to apply ACE schema"
    echo "Please check the error above"
    exit 1
fi
