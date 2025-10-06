#!/usr/bin/env python3
"""
Script to fix all 266 multiple_permissive_policies warnings in Supabase database.
This version queries the database directly to find and consolidate policies.
"""

from urllib.parse import quote_plus
from collections import defaultdict
import psycopg2
from psycopg2 import sql

# Database connection configuration
DB_PASSWORD = "K@x3ta9V8GK5rnW"
ENCODED_PASSWORD = quote_plus(DB_PASSWORD)
DB_URL = f"postgresql://postgres.tpdkhddtbhpoqzzgxfni:{ENCODED_PASSWORD}@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"

def get_all_policies(conn):
    """Get all RLS policies from the database."""
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
        WHERE permissive = 'PERMISSIVE'
        ORDER BY schemaname, tablename, roles, cmd
    """

    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()

    policies = []
    for row in results:
        policies.append({
            'schema': row[0],
            'table': row[1],
            'policy_name': row[2],
            'permissive': row[3],
            'roles': row[4],  # This is an array
            'cmd': row[5],
            'qual': row[6],
            'with_check': row[7]
        })

    return policies

def find_multiple_permissive_policies(policies):
    """Find tables with multiple permissive policies for same role+action."""
    # Group by (schema, table, role, cmd)
    grouped = defaultdict(list)

    for policy in policies:
        # roles is an array, we need to handle each role separately
        roles = policy['roles']
        if isinstance(roles, str):
            # Parse array format {role1,role2}
            roles = roles.strip('{}').split(',') if roles != '{}' else []

        for role in roles:
            role = role.strip()
            key = (policy['schema'], policy['table'], role, policy['cmd'])
            grouped[key].append(policy)

    # Find groups with more than one policy
    multiple = {}
    for key, policy_list in grouped.items():
        if len(policy_list) > 1:
            multiple[key] = policy_list

    return multiple

def generate_consolidated_policy_sql(schema, table, role, action, policies):
    """Generate SQL to consolidate multiple policies into one."""

    # Extract USING clauses
    using_clauses = []
    with_check_clauses = []

    for policy in policies:
        if policy['qual']:
            clause = policy['qual'].strip()
            # Wrap in parentheses if not already
            if not (clause.startswith('(') and clause.endswith(')')):
                clause = f"({clause})"
            using_clauses.append(clause)

        if policy['with_check']:
            clause = policy['with_check'].strip()
            if not (clause.startswith('(') and clause.endswith(')')):
                clause = f"({clause})"
            with_check_clauses.append(clause)

    # Create consolidated policy name
    consolidated_name = f"{table}_{action.lower()}_consolidated_{role}"

    # Combine clauses with OR
    combined_using = " OR ".join(using_clauses) if using_clauses else "true"

    # For WITH CHECK, only use if action is INSERT or UPDATE
    combined_with_check = None
    if action in ['INSERT', 'UPDATE'] and with_check_clauses:
        combined_with_check = " OR ".join(with_check_clauses)

    # Generate SQL
    sql_statements = []

    # Drop old policies
    for policy in policies:
        drop_sql = f"DROP POLICY IF EXISTS \"{policy['policy_name']}\" ON \"{schema}\".\"{table}\";"
        sql_statements.append(drop_sql)

    # Create new consolidated policy
    create_sql = f"CREATE POLICY \"{consolidated_name}\"\n"
    create_sql += f"    ON \"{schema}\".\"{table}\"\n"
    create_sql += f"    AS PERMISSIVE\n"
    create_sql += f"    FOR {action}\n"
    create_sql += f"    TO {role}\n"
    create_sql += f"    USING ({combined_using})"

    if combined_with_check:
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

    # Connect to database
    print("1. Connecting to database...")
    try:
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = False
        print("   Connected successfully")
    except Exception as e:
        print(f"   ERROR: Failed to connect: {e}")
        return

    # Get all policies
    print("\n2. Fetching all RLS policies from database...")
    try:
        all_policies = get_all_policies(conn)
        print(f"   Found {len(all_policies)} PERMISSIVE policies total")
    except Exception as e:
        print(f"   ERROR: Failed to fetch policies: {e}")
        conn.close()
        return

    # Find multiple permissive policies
    print("\n3. Analyzing for multiple permissive policies...")
    multiple = find_multiple_permissive_policies(all_policies)
    print(f"   Found {len(multiple)} cases of multiple permissive policies")

    # Count total issues (each case might affect multiple roles)
    total_issues = len(multiple)
    total_policies_before = sum(len(policies) for policies in multiple.values())
    total_policies_after = len(multiple)

    # Group by table for reporting
    tables_affected = set((schema, table) for schema, table, _, _ in multiple.keys())
    print(f"   Affects {len(tables_affected)} tables")

    # Generate migration SQL
    print("\n4. Generating consolidated policies...")
    migration_sql = []
    migration_sql.append("-- Migration to consolidate multiple permissive RLS policies")
    migration_sql.append("-- Generated automatically to fix performance warnings")
    migration_sql.append("-- This consolidates policies with OR conditions for better performance")
    migration_sql.append("")
    migration_sql.append("BEGIN;")
    migration_sql.append("")

    tables_fixed = 0
    current_table = None

    for (schema, table, role, action), policies in sorted(multiple.items()):
        table_key = f"{schema}.{table}"

        # Add table header if new table
        if table_key != current_table:
            migration_sql.append(f"\n-- ============================================")
            migration_sql.append(f"-- Table: {schema}.{table}")
            migration_sql.append(f"-- ============================================")
            current_table = table_key
            tables_fixed += 1

        policy_names = [p['policy_name'] for p in policies]
        migration_sql.append(f"\n-- Consolidating {len(policies)} policies for {role}/{action}:")
        for name in policy_names:
            migration_sql.append(f"--   - {name}")

        # Generate SQL
        try:
            sql_statements = generate_consolidated_policy_sql(
                schema, table, role, action, policies
            )
            for stmt in sql_statements:
                migration_sql.append(stmt)
            migration_sql.append("")
        except Exception as e:
            error_msg = f"-- ERROR generating SQL for {schema}.{table} {role}/{action}: {e}"
            migration_sql.append(error_msg)
            print(f"   {error_msg}")

    migration_sql.append("\nCOMMIT;")
    migration_sql.append("")
    migration_sql.append(f"-- Summary:")
    migration_sql.append(f"-- Tables affected: {len(tables_affected)}")
    migration_sql.append(f"-- Total consolidations: {total_issues}")
    migration_sql.append(f"-- Policies before: {total_policies_before}")
    migration_sql.append(f"-- Policies after: {total_policies_after}")
    migration_sql.append(f"-- Policies removed: {total_policies_before - total_policies_after}")

    conn.close()

    # Write migration file
    migration_file = "/Users/MD/AI-Platform-ISO/migrations/023_consolidate_rls_policies.sql"
    print(f"\n5. Writing migration file: {migration_file}")

    with open(migration_file, 'w') as f:
        f.write('\n'.join(migration_sql))

    print(f"   Migration file written successfully ({len(migration_sql)} lines)")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Tables affected: {len(tables_affected)}")
    print(f"Tables in migration: {tables_fixed}")
    print(f"Total consolidations: {total_issues}")
    print(f"Policies before: {total_policies_before}")
    print(f"Policies after: {total_policies_after}")
    print(f"Reduction: {total_policies_before - total_policies_after} policies removed")
    print(f"\nMigration file: {migration_file}")
    print(f"\nNext step: Review and apply the migration")

if __name__ == "__main__":
    main()
