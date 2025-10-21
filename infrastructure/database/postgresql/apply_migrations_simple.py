#!/usr/bin/env python3
"""
Auto-apply remaining migrations to Supabase via REST API
Workaround for DNS issues with direct PostgreSQL connection
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Load environment
load_dotenv("/Users/MD/AI-Platform-ISO/.env")

MIGRATIONS_DIR = Path("/Users/MD/AI-Platform-ISO/infrastructure/database/migrations_source")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Already applied migrations
APPLIED = [
    "001_schemas_and_extensions.sql",
    "002_rls_functions.sql",
    "003_core_tables.sql",
    "004_community_schema.sql",
    "005_intelligence_schema.sql"
]

def main():
    print(" Auto-applying migrations via Supabase REST API...")
    print(f" Directory: {MIGRATIONS_DIR}\n")

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Get all migration files sorted
    migrations = sorted(MIGRATIONS_DIR.glob("*.sql"))

    for migration_file in migrations:
        filename = migration_file.name

        # Skip already applied
        if filename in APPLIED:
            print(f"⏭️  Skipping (already applied): {filename}")
            continue

        print(f" Applying: {filename}")

        # Read SQL
        sql = migration_file.read_text()

        # Execute via Supabase (this uses REST API, not direct SQL)
        # We need to use raw SQL execution
        try:
            # Supabase Python client doesn't support raw SQL execution directly
            # We'll need to print the SQL and user applies manually, OR
            # Use requests to call a custom stored procedure

            print(f"️  Cannot auto-apply via REST API")
            print(f"   Please apply manually: {filename}")
            print(f"   Or use: psql with connection pooler")

            # Alternative: Write to a combined file

        except Exception as e:
            print(f" Error: {e}")
            sys.exit(1)

    print("\n Suggestion: Copy migrations 006-018 into one file and apply manually")
    print("   Or fix DNS to use direct PostgreSQL connection")

if __name__ == "__main__":
    main()
