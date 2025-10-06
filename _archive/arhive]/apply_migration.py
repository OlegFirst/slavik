#!/usr/bin/env python3
"""
Apply the RLS policy consolidation migration to the database.
"""

from urllib.parse import quote_plus
import psycopg2

# Database connection
DB_PASSWORD = "K@x3ta9V8GK5rnW"
ENCODED_PASSWORD = quote_plus(DB_PASSWORD)
DB_URL = f"postgresql://postgres.tpdkhddtbhpoqzzgxfni:{ENCODED_PASSWORD}@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"

MIGRATION_FILE = "/Users/MD/AI-Platform-ISO/migrations/023_consolidate_rls_policies.sql"

def main():
    print("=" * 80)
    print("APPLYING RLS POLICY CONSOLIDATION MIGRATION")
    print("=" * 80)
    print()

    # Read migration file
    print(f"1. Reading migration file: {MIGRATION_FILE}")
    with open(MIGRATION_FILE, 'r') as f:
        migration_sql = f.read()

    print(f"   Migration file read ({len(migration_sql)} characters)")

    # Connect to database
    print("\n2. Connecting to database...")
    try:
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = False
        print("   Connected successfully")
    except Exception as e:
        print(f"   ERROR: Failed to connect: {e}")
        return

    # Apply migration
    print("\n3. Applying migration...")
    cursor = conn.cursor()

    try:
        cursor.execute(migration_sql)
        conn.commit()
        print("   Migration applied successfully!")

    except Exception as e:
        print(f"   ERROR: Migration failed: {e}")
        print("\n   Rolling back...")
        conn.rollback()
        cursor.close()
        conn.close()
        return

    cursor.close()

    # Verify the changes
    print("\n4. Verifying consolidation...")
    cursor = conn.cursor()

    # Check for remaining multiple permissive policies
    query = """
        WITH policy_counts AS (
            SELECT
                schemaname,
                tablename,
                cmd,
                unnest(roles) as role,
                COUNT(*) as policy_count
            FROM pg_policies
            WHERE permissive = 'PERMISSIVE'
            GROUP BY schemaname, tablename, cmd, unnest(roles)
            HAVING COUNT(*) > 1
        )
        SELECT COUNT(*) FROM policy_counts
    """

    cursor.execute(query)
    remaining_count = cursor.fetchone()[0]

    print(f"   Remaining multiple permissive policy issues: {remaining_count}")

    if remaining_count == 0:
        print("   SUCCESS: All multiple permissive policies have been consolidated!")
    else:
        print(f"   WARNING: Still have {remaining_count} multiple permissive policy issues")

    cursor.close()
    conn.close()

    print("\n" + "=" * 80)
    print("MIGRATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
