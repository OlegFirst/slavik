#!/usr/bin/env python3
"""
Auto-apply all remaining migrations via Supabase Management API
Uses SQL execution through Supabase edge functions
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path("/Users/MD/AI-Platform-ISO/.env")
load_dotenv(env_path)

MIGRATIONS_DIR = Path("/Users/MD/AI-Platform-ISO/infrastructure/database/migrations_source")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Already applied
APPLIED = {
    "001_schemas_and_extensions.sql",
    "002_rls_functions.sql",
    "003_core_tables.sql",
    "004_community_schema.sql",
    "005_intelligence_schema.sql",
    "006_bia_risk_schemas.sql",
    "007_governance_audit_schemas.sql",
    "008_documents_schema.sql"
}

def execute_sql(sql: str) -> dict:
    """Execute SQL via Supabase REST API"""
    # Use postgrest RPC endpoint
    url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    # This won't work - we need direct database access
    # Let's use Python psycopg2 with correct connection string

    return {"error": "Direct SQL execution not available via REST API"}

def apply_via_psycopg():
    """Apply migrations using psycopg2 with IPv4 connection"""
    try:
        import psycopg2
    except ImportError:
        print(" psycopg2 not installed. Installing...")
        os.system("pip3 install psycopg2-binary")
        import psycopg2

    # Use pooler with IP address (bypass DNS)
    # Get IP from: aws-0-eu-central-1.pooler.supabase.com = 18.198.145.223

    conn_params = {
        "host": "aws-1-eu-north-1.pooler.supabase.com",
        "port": 5432,
        "dbname": "postgres",
        "user": "postgres.tpdkhddtbhpoqzzgxfni",
        "password": "K@x3ta9V8GK5rnW",
        "sslmode": "require"
    }

    print(f" Connecting via IP {conn_params['host']}:{conn_params['port']}...")

    try:
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cur = conn.cursor()

        print(" Connected!")

        # Get all migrations
        migrations = sorted(MIGRATIONS_DIR.glob("*.sql"))

        for migration_file in migrations:
            filename = migration_file.name

            # Skip applied
            if filename in APPLIED:
                print(f"⏭️  Skip: {filename}")
                continue

            print(f"\n Applying: {filename}")
            sql = migration_file.read_text()

            try:
                cur.execute(sql)
                print(f" Success: {filename}")
            except Exception as e:
                print(f" Error in {filename}: {e}")
                # Continue or stop?
                response = input("Continue? (y/n): ")
                if response.lower() != 'y':
                    break

        cur.close()
        conn.close()
        print("\n Migration process complete!")

    except Exception as e:
        print(f" Connection failed: {e}")
        print("\n Trying batch files instead...")
        return False

    return True

def main():
    print(" Auto-applying migrations to Supabase...")
    print(f" Migrations: {MIGRATIONS_DIR}\n")

    # Try direct connection
    if not apply_via_psycopg():
        print("\n Use batch files manually:")
        print("   1. BATCH_1_migrations_006-009.sql")
        print("   2. BATCH_2_migrations_010-013.sql")
        print("   3. BATCH_3_migrations_014-018.sql")
        sys.exit(1)

if __name__ == "__main__":
    main()
