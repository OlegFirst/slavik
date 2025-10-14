#!/bin/bash

# Script to apply SEH migrations to Supabase
# Usage: ./apply-migrations.sh

echo "[START] Applying SEH migrations to Supabase..."

# You can apply migrations in 3 ways:

# Option 1: Through Supabase SQL Editor (Recommended)
echo ""
echo "Option 1: SUPABASE SQL EDITOR (Recommended)"
echo "1. Go to your Supabase dashboard"
echo "2. Navigate to SQL Editor"
echo "3. Copy and paste each migration file in order:"
echo "   - 005_seh_phase1_core_models.sql"
echo "   - 006_seh_phase2_grant_management.sql"
echo "   - 007_seh_phase3_bcm_poi.sql"
echo "4. Run each script"

# Option 2: Using psql command line
echo ""
echo "Option 2: PSQL COMMAND LINE"
echo "If you have psql installed and database URL:"
echo ""
echo "export DATABASE_URL='postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT].supabase.co:5432/postgres'"
echo ""
echo "psql \$DATABASE_URL < 005_seh_phase1_core_models.sql"
echo "psql \$DATABASE_URL < 006_seh_phase2_grant_management.sql"
echo "psql \$DATABASE_URL < 007_seh_phase3_bcm_poi.sql"

# Option 3: Using Supabase CLI (if installed)
echo ""
echo "Option 3: SUPABASE CLI"
echo "If you have Supabase CLI installed:"
echo ""
echo "supabase db push --db-url \$DATABASE_URL"
echo ""
echo "Or for local development:"
echo "supabase db reset"

echo ""
echo "[INFO] Migration files are located in: docs/setup/migrations/"
echo "[INFO] Apply them in numerical order (005, 006, 007)"
echo ""
echo "After applying migrations, test with:"
echo "- Check tables in Supabase Table Editor"
echo "- Run: node test-seh-integration.js"