#!/bin/bash

# Apply Community Intelligence Migration (037)
# Usage: ./apply_community_intelligence.sh

set -e

echo "=========================================="
echo "Applying Community Intelligence Migration"
echo "=========================================="

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL not set"
    echo "Please set DATABASE_URL environment variable"
    echo ""
    echo "Example:"
    echo "  export DATABASE_URL='postgresql://user:pass@host:5432/dbname'"
    exit 1
fi

echo ""
echo "Database: $DATABASE_URL"
echo ""

# Confirm
read -p "Apply migration 037_community_intelligence.sql? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# Apply migration
echo ""
echo "Applying migration..."
psql "$DATABASE_URL" -f migrations_source/037_community_intelligence.sql

echo ""
echo "✅ Migration applied successfully!"
echo ""
echo "Created tables:"
echo "  - case_contributions"
echo "  - peer_reviews"
echo "  - user_reputation"
echo "  - reputation_transactions"
echo "  - community_annotations"
echo "  - synthesized_guidance"
echo ""
echo "Verify with:"
echo "  psql \$DATABASE_URL -c \"\\dt *contributions*\""
echo ""
