#!/usr/bin/env python3
"""
Check how many tables have policies with multiple roles that need consolidation.
"""

from urllib.parse import quote_plus
import psycopg2

# Database connection
DB_PASSWORD = "K@x3ta9V8GK5rnW"
ENCODED_PASSWORD = quote_plus(DB_PASSWORD)
DB_URL = f"postgresql://postgres.tpdkhddtbhpoqzzgxfni:{ENCODED_PASSWORD}@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"

def main():
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()

    # Query to find tables with multiple permissive policies
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
        SELECT
            schemaname,
            tablename,
            role,
            cmd,
            policy_count
        FROM policy_counts
        ORDER BY schemaname, tablename, role, cmd
    """

    cursor.execute(query)
    results = cursor.fetchall()

    print(f"Found {len(results)} combinations of (schema, table, role, cmd) with multiple policies:")
    print()

    current_table = None
    for row in results:
        schema, table, role, cmd, count = row
        table_key = f"{schema}.{table}"

        if table_key != current_table:
            print(f"\n{table_key}:")
            current_table = table_key

        print(f"  - Role: {role:20s} Action: {cmd:10s} Policies: {count}")

    # Get list of all policy names for these tables
    print("\n" + "=" * 80)
    print("POLICY DETAILS")
    print("=" * 80)

    unique_tables = list(set((r[0], r[1]) for r in results))

    for schema, table in sorted(unique_tables):
        cursor.execute("""
            SELECT policyname, roles, cmd, permissive
            FROM pg_policies
            WHERE schemaname = %s AND tablename = %s AND permissive = 'PERMISSIVE'
            ORDER BY cmd, policyname
        """, (schema, table))

        policies = cursor.fetchall()

        print(f"\n{schema}.{table}:")
        for policy in policies:
            name, roles, cmd, permissive = policy
            print(f"  {name}")
            print(f"    Roles: {roles}")
            print(f"    Action: {cmd}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
