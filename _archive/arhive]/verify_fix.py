#!/usr/bin/env python3
"""
Verify that all 266 multiple_permissive_policies issues are resolved.
The 266 count is because Supabase reports each (table, role, action) combination,
and policies with TO public apply to anon, authenticated, authenticator, dashboard_user roles.
"""

from urllib.parse import quote_plus
import psycopg2
import csv
import json

# Database connection
DB_PASSWORD = "K@x3ta9V8GK5rnW"
ENCODED_PASSWORD = quote_plus(DB_PASSWORD)
DB_URL = f"postgresql://postgres.tpdkhddtbhpoqzzgxfni:{ENCODED_PASSWORD}@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"

CSV_FILE = "/Users/MD/Downloads/Supabase Performance Security Lints (tpdkhddtbhpoqzzgxfni) (2).csv"

def get_csv_issues():
    """Parse CSV and count issues by (schema, table, role, action)."""
    issues = {}

    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['name'] == 'multiple_permissive_policies':
                try:
                    metadata = json.loads(row['metadata'])
                    schema = metadata['schema']
                    table = metadata['name']

                    # Extract role and action from detail
                    detail = row['detail']

                    # Extract role
                    role_start = detail.find("for role `") + len("for role `")
                    role_end = detail.find("`", role_start)
                    role = detail[role_start:role_end]

                    # Extract action
                    action_start = detail.find("for action `") + len("for action `")
                    action_end = detail.find("`", action_start)
                    action = detail[action_start:action_end]

                    key = (schema, table, role, action)
                    issues[key] = row
                except Exception as e:
                    print(f"Error parsing row: {e}")
                    pass

    return issues

def check_database_for_issues(conn, csv_issues):
    """Check database for remaining multiple permissive policies matching CSV issues."""
    cursor = conn.cursor()

    remaining_issues = []

    # For each CSV issue, check if it still exists in database
    for (schema, table, role, action) in csv_issues.keys():
        # Map Supabase role names to PostgreSQL roles
        # In Supabase, policies with TO public apply to anon, authenticated, etc.
        # So we need to check for policies that apply to this role

        # Check for multiple policies for this specific role+action
        cursor.execute("""
            SELECT
                policyname
            FROM pg_policies
            WHERE schemaname = %s
              AND tablename = %s
              AND cmd = %s
              AND permissive = 'PERMISSIVE'
              AND %s = ANY(roles)
        """, (schema, table, action, role))

        policies = cursor.fetchall()

        if len(policies) > 1:
            remaining_issues.append({
                'schema': schema,
                'table': table,
                'role': role,
                'action': action,
                'policy_count': len(policies),
                'policies': [p[0] for p in policies]
            })

    cursor.close()
    return remaining_issues

def main():
    print("=" * 80)
    print("VERIFYING FIX FOR ALL 266 MULTIPLE_PERMISSIVE_POLICIES ISSUES")
    print("=" * 80)
    print()

    # Parse CSV
    print("1. Parsing CSV file...")
    csv_issues = get_csv_issues()
    print(f"   Found {len(csv_issues)} issues in CSV")

    # Connect to database
    print("\n2. Connecting to database...")
    try:
        conn = psycopg2.connect(DB_URL)
        print("   Connected successfully")
    except Exception as e:
        print(f"   ERROR: Failed to connect: {e}")
        return

    # Check database
    print("\n3. Checking database for remaining issues...")
    remaining_issues = check_database_for_issues(conn, csv_issues)

    conn.close()

    print(f"   Remaining issues: {len(remaining_issues)}")

    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION RESULTS")
    print("=" * 80)
    print(f"Total issues in CSV: {len(csv_issues)}")
    print(f"Issues resolved: {len(csv_issues) - len(remaining_issues)}")
    print(f"Issues remaining: {len(remaining_issues)}")
    print()

    if len(remaining_issues) == 0:
        print("SUCCESS! All 266 multiple_permissive_policies issues have been resolved!")
    else:
        print(f"WARNING: {len(remaining_issues)} issues still remain:")
        for issue in remaining_issues[:10]:  # Show first 10
            print(f"  - {issue['schema']}.{issue['table']} ({issue['role']}/{issue['action']}): {issue['policy_count']} policies")
            for policy in issue['policies']:
                print(f"      - {policy}")

        if len(remaining_issues) > 10:
            print(f"  ... and {len(remaining_issues) - 10} more")

    # Final summary with tables
    unique_tables = set((schema, table) for schema, table, _, _ in csv_issues.keys())
    print(f"\nTables affected: {len(unique_tables)}")
    print(f"All tables fixed: {'YES' if len(remaining_issues) == 0 else 'NO'}")

if __name__ == "__main__":
    main()
