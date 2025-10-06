#!/usr/bin/env python3
"""
Script to fix all 266 multiple_permissive_policies warnings in Supabase database.
Consolidates multiple PERMISSIVE RLS policies into single policies with OR conditions.
"""

import csv
import json
from urllib.parse import quote_plus
from collections import defaultdict
import psycopg2
from psycopg2 import sql

# Database connection configuration
DB_PASSWORD = "K@x3ta9V8GK5rnW"
ENCODED_PASSWORD = quote_plus(DB_PASSWORD)
DB_URL = f"postgresql://postgres.tpdkhddtbhpoqzzgxfni:{ENCODED_PASSWORD}@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"

CSV_FILE = "/Users/MD/Downloads/Supabase Performance Security Lints (tpdkhddtbhpoqzzgxfni) (2).csv"

def parse_csv():
    """Parse CSV file and extract multiple_permissive_policies issues."""
    issues = []

    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['name'] == 'multiple_permissive_policies':
                # Parse metadata to get table info
                metadata = json.loads(row['metadata'])

                # Extract role and action from detail
                detail = row['detail']
                # Example: "Table `bcm.communication_plans` has multiple permissive policies for role `anon` for action `SELECT`..."

                # Extract role
                role_start = detail.find("for role `") + len("for role `")
                role_end = detail.find("`", role_start)
                role = detail[role_start:role_end]

                # Extract action
                action_start = detail.find("for action `") + len("for action `")
                action_end = detail.find("`", action_start)
                action = detail[action_start:action_end]

                # Extract policy names
                policies_start = detail.find("Policies include `{") + len("Policies include `{")
                policies_end = detail.find("}`", policies_start)
                policies_str = detail[policies_start:policies_end]

                # Parse policy names - they can be either quoted or unquoted
                policies = []
                if '""' in policies_str:
                    # Quoted format: "Policy 1","Policy 2"
                    import re
                    policies = re.findall(r'""([^""]+)""', policies_str)
                else:
                    # Unquoted format: policy1,policy2
                    policies = [p.strip() for p in policies_str.split(',')]

                issues.append({
                    'schema': metadata['schema'],
                    'table': metadata['name'],
                    'role': role,
                    'action': action,
                    'policies': policies
                })

    return issues

def group_issues_by_table(issues):
    """Group issues by table."""
    by_table = defaultdict(list)

    for issue in issues:
        table_key = f"{issue['schema']}.{issue['table']}"
        by_table[table_key].append(issue)

    return dict(by_table)

def get_policy_definition(conn, schema, table, policy_name):
    """Get the definition of a policy from pg_policies."""
    cursor = conn.cursor()

    query = """
        SELECT
            schemaname,
            tablename,
            policyname,
            permissive,
            roles,
            cmd,
            qual,
            with_check
        FROM pg_policies
        WHERE schemaname = %s
          AND tablename = %s
          AND policyname = %s
    """

    cursor.execute(query, (schema, table, policy_name))
    result = cursor.fetchone()
    cursor.close()

    if result:
        return {
            'schema': result[0],
            'table': result[1],
            'policy_name': result[2],
            'permissive': result[3],
            'roles': result[4],
            'cmd': result[5],
            'qual': result[6],
            'with_check': result[7]
        }
    return None

def generate_consolidated_policy(schema, table, role, action, policies_info):
    """Generate SQL for consolidated policy."""

    # Extract USING clauses from all policies
    using_clauses = []
    with_check_clauses = []

    for policy in policies_info:
        if policy['qual']:
            # Clean up the clause - remove outer parentheses if present
            clause = policy['qual'].strip()
            if clause.startswith('(') and clause.endswith(')'):
                clause = clause[1:-1].strip()
            using_clauses.append(f"({clause})")

        if policy['with_check']:
            clause = policy['with_check'].strip()
            if clause.startswith('(') and clause.endswith(')'):
                clause = clause[1:-1].strip()
            with_check_clauses.append(f"({clause})")

    # Create consolidated policy name
    consolidated_name = f"{table}_{action.lower()}_consolidated"

    # Combine USING clauses with OR
    combined_using = " OR ".join(using_clauses) if using_clauses else "true"

    # Combine WITH CHECK clauses with OR (if any)
    combined_with_check = " OR ".join(with_check_clauses) if with_check_clauses else None

    # Generate SQL
    sql_statements = []

    # Drop old policies
    for policy in policies_info:
        sql_statements.append(
            f"DROP POLICY IF EXISTS \"{policy['policy_name']}\" ON {schema}.{table};"
        )

    # Create new consolidated policy
    create_sql = f"CREATE POLICY \"{consolidated_name}\" ON {schema}.{table}\n"
    create_sql += f"    AS PERMISSIVE\n"
    create_sql += f"    FOR {action}\n"
    create_sql += f"    TO {role}\n"
    create_sql += f"    USING ({combined_using})"

    if combined_with_check and action in ['INSERT', 'UPDATE']:
        create_sql += f"\n    WITH CHECK ({combined_with_check})"

    create_sql += ";"

    sql_statements.append(create_sql)

    return sql_statements

def main():
    """Main execution function."""
    print("=" * 80)
    print("FIXING MULTIPLE PERMISSIVE POLICIES IN SUPABASE DATABASE")
    print("=" * 80)
    print()

    # Parse CSV file
    print("1. Parsing CSV file...")
    issues = parse_csv()
    print(f"   Found {len(issues)} multiple_permissive_policies issues")

    # Group by table
    print("\n2. Grouping issues by table...")
    by_table = group_issues_by_table(issues)
    print(f"   Found {len(by_table)} tables affected")

    # Connect to database
    print("\n3. Connecting to database...")
    try:
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = False
        print("   Connected successfully")
    except Exception as e:
        print(f"   ERROR: Failed to connect to database: {e}")
        return

    # Generate migration SQL
    print("\n4. Generating consolidated policies...")
    migration_sql = []
    migration_sql.append("-- Migration to consolidate multiple permissive RLS policies")
    migration_sql.append("-- Generated automatically to fix 266 performance warnings")
    migration_sql.append("")

    total_policies_before = 0
    total_policies_after = 0
    tables_fixed = 0
    errors = []

    for table_key, table_issues in sorted(by_table.items()):
        schema, table = table_key.split('.')
        migration_sql.append(f"\n-- Table: {schema}.{table}")
        migration_sql.append(f"-- Issues: {len(table_issues)}")

        for issue in table_issues:
            role = issue['role']
            action = issue['action']
            policy_names = issue['policies']

            migration_sql.append(f"\n-- Consolidating {len(policy_names)} policies for {role}/{action}")

            # Get policy definitions
            policies_info = []
            for policy_name in policy_names:
                policy_def = get_policy_definition(conn, schema, table, policy_name)
                if policy_def:
                    policies_info.append(policy_def)
                else:
                    error_msg = f"WARNING: Policy not found: {schema}.{table}.{policy_name}"
                    print(f"   {error_msg}")
                    errors.append(error_msg)

            if len(policies_info) == len(policy_names):
                # Generate consolidated policy
                sql_statements = generate_consolidated_policy(
                    schema, table, role, action, policies_info
                )

                for stmt in sql_statements:
                    migration_sql.append(stmt)

                total_policies_before += len(policy_names)
                total_policies_after += 1
                tables_fixed += 1
            else:
                error_msg = f"ERROR: Could not retrieve all policies for {schema}.{table} {role}/{action}"
                print(f"   {error_msg}")
                errors.append(error_msg)

        migration_sql.append("")

    conn.close()

    # Write migration file
    migration_file = "/Users/MD/AI-Platform-ISO/migrations/023_consolidate_rls_policies.sql"
    print(f"\n5. Writing migration file: {migration_file}")

    with open(migration_file, 'w') as f:
        f.write('\n'.join(migration_sql))

    print(f"   Migration file written successfully")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Tables affected: {len(by_table)}")
    print(f"Tables fixed: {tables_fixed}")
    print(f"Total issues: {len(issues)}")
    print(f"Policies before consolidation: {total_policies_before}")
    print(f"Policies after consolidation: {total_policies_after}")
    print(f"Reduction: {total_policies_before - total_policies_after} policies removed")
    print(f"\nErrors encountered: {len(errors)}")

    if errors:
        print("\nERRORS:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")

    print(f"\nMigration file: {migration_file}")
    print("\nNext steps:")
    print("1. Review the migration file")
    print("2. Apply it to database: psql <connection> -f migrations/023_consolidate_rls_policies.sql")
    print("3. Verify no more multiple_permissive_policies warnings")

if __name__ == "__main__":
    main()
