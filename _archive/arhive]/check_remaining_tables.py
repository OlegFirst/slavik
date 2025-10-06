#!/usr/bin/env python3
"""
Check if the remaining 42 tables from CSV actually have issues in the database.
"""

from urllib.parse import quote_plus
import psycopg2

# Database connection
DB_PASSWORD = "K@x3ta9V8GK5rnW"
ENCODED_PASSWORD = quote_plus(DB_PASSWORD)
DB_URL = f"postgresql://postgres.tpdkhddtbhpoqzzgxfni:{ENCODED_PASSWORD}@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"

# Tables from CSV
CSV_TABLES = [
    ('bcm', 'communication_plans'),
    ('bcm', 'competence_records'),
    ('bcm', 'documents'),
    ('bcm', 'plans'),
    ('bcm', 'procedures'),
    ('bcm', 'resources'),
    ('bia', 'dependencies'),
    ('bia', 'impact_assessments'),
    ('bia', 'processes'),
    ('bia', 'supplier_disruptions'),
    ('bia', 'suppliers'),
    ('community', 'ai_digital_colleagues'),
    ('community', 'specialist_certifications'),
    ('community', 'specialist_portfolio'),
    ('community', 'specialist_services'),
    ('compliance', 'improvement_initiatives'),
    ('compliance', 'requirements'),
    ('governance', 'context_analysis'),
    ('governance', 'objectives'),
    ('governance', 'policies'),
    ('governance', 'roles'),
    ('governance', 'stakeholders'),
    ('intelligence', 'digital_twins'),
    ('learning', 'awareness_campaigns'),
    ('learning', 'competency_assessments'),
    ('learning', 'enrollments'),
    ('learning', 'training_programs'),
    ('learning', 'user_achievements'),
    ('public', 'organization_users'),
    ('public', 'team_members'),
    ('public', 'teams'),
    ('response', 'communication_templates'),
    ('response', 'communications'),
    ('response', 'escalations'),
    ('response', 'incidents'),
    ('response', 'notifications'),
    ('response', 'response_teams'),
    ('response', 'timeline_events'),
    ('risk', 'assessments'),
    ('risk', 'controls'),
    ('risk', 'risks'),
    ('risk', 'templates'),
    ('risk', 'treatments'),
    ('validation', 'audit_findings'),
    ('validation', 'audit_plans'),
    ('validation', 'capa'),
    ('validation', 'exercise_actions'),
    ('validation', 'exercise_scenarios'),
    ('validation', 'exercises'),
    ('validation', 'kpi_alerts'),
    ('validation', 'kpi_dashboards'),
    ('validation', 'kpis'),
    ('validation', 'management_reviews'),
]

def main():
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()

    print("Checking tables from CSV for policies...")
    print()

    tables_with_multiple = []
    tables_not_found = []
    tables_ok = []

    for schema, table in CSV_TABLES:
        # Check if table exists and get policies
        cursor.execute("""
            SELECT COUNT(*)
            FROM pg_policies
            WHERE schemaname = %s AND tablename = %s AND permissive = 'PERMISSIVE'
        """, (schema, table))

        policy_count = cursor.fetchone()[0]

        if policy_count == 0:
            tables_not_found.append(f"{schema}.{table}")
            continue

        # Check for multiple policies for same role+action
        cursor.execute("""
            SELECT
                cmd,
                unnest(roles) as role,
                COUNT(*) as count
            FROM pg_policies
            WHERE schemaname = %s AND tablename = %s AND permissive = 'PERMISSIVE'
            GROUP BY cmd, unnest(roles)
            HAVING COUNT(*) > 1
        """, (schema, table))

        multiples = cursor.fetchall()

        if multiples:
            tables_with_multiple.append((f"{schema}.{table}", multiples))
        else:
            tables_ok.append(f"{schema}.{table}")

    cursor.close()
    conn.close()

    print(f"Summary:")
    print(f"  Tables with multiple permissive policies: {len(tables_with_multiple)}")
    print(f"  Tables OK (no multiple policies): {len(tables_ok)}")
    print(f"  Tables not found in database: {len(tables_not_found)}")
    print()

    if tables_with_multiple:
        print(f"\nTables STILL with multiple permissive policies:")
        for table, multiples in tables_with_multiple:
            print(f"  {table}:")
            for cmd, role, count in multiples:
                print(f"    - {role} / {cmd}: {count} policies")

    if tables_not_found:
        print(f"\nTables not found in database:")
        for table in tables_not_found:
            print(f"  - {table}")

    if tables_ok:
        print(f"\nTables OK (already consolidated or only have single policies):")
        for table in tables_ok:
            print(f"  - {table}")

if __name__ == "__main__":
    main()
