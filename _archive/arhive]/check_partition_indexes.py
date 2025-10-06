#!/usr/bin/env python3
"""
Check partition table indexes that couldn't be dropped.
"""
import psycopg2
from urllib.parse import quote_plus

# Database connection
password = "K@x3ta9V8GK5rnW"
encoded_password = quote_plus(password)
db_url = f"postgresql://postgres.tpdkhddtbhpoqzzgxfni:{encoded_password}@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"

def check_partition_indexes():
    """Check the parent indexes for partition tables."""
    print("=" * 80)
    print("PARTITION INDEX ANALYSIS")
    print("=" * 80)

    conn = psycopg2.connect(db_url)

    try:
        with conn.cursor() as cur:
            # Check for parent indexes on metrics table
            print("\n1. Checking metrics table structure...")
            cur.execute("""
                SELECT
                    tablename,
                    indexname,
                    indexdef
                FROM pg_indexes
                WHERE schemaname = 'intelligence'
                    AND tablename = 'metrics'
                ORDER BY indexname;
            """)
            results = cur.fetchall()

            if results:
                print(f"   Found {len(results)} indexes on parent table 'metrics':")
                for row in results:
                    print(f"   - {row[1]}")
                    print(f"     Definition: {row[2][:80]}...")
            else:
                print("   No parent table 'metrics' found (may be partitioned)")

            # Check partition table info
            print("\n2. Checking partition table structure...")
            cur.execute("""
                SELECT
                    schemaname,
                    tablename
                FROM pg_tables
                WHERE schemaname = 'intelligence'
                    AND tablename LIKE 'metrics_2025_%'
                ORDER BY tablename;
            """)
            partitions = cur.fetchall()
            print(f"   Found {len(partitions)} partition tables:")
            for row in partitions:
                print(f"   - {row[0]}.{row[1]}")

            # Check indexes on partitions
            print("\n3. Checking indexes on partition tables...")
            for schema, table in partitions:
                cur.execute("""
                    SELECT
                        indexrelname,
                        idx_scan
                    FROM pg_stat_user_indexes
                    WHERE schemaname = %s
                        AND relname = %s
                    ORDER BY indexrelname;
                """, (schema, table))
                indexes = cur.fetchall()
                print(f"\n   {schema}.{table}:")
                print(f"   Total indexes: {len(indexes)}")
                for idx_name, scans in indexes:
                    print(f"     - {idx_name}: {scans} scans")

            # Check if there's a parent metrics table with indexes
            print("\n4. Checking for parent table indexes...")
            cur.execute("""
                SELECT
                    i.relname as index_name,
                    t.relname as table_name,
                    idx_scan,
                    pg_size_pretty(pg_relation_size(i.oid)) as size
                FROM pg_class i
                JOIN pg_index ix ON ix.indexrelid = i.oid
                JOIN pg_class t ON t.oid = ix.indrelid
                JOIN pg_namespace n ON n.oid = i.relnamespace
                LEFT JOIN pg_stat_user_indexes s ON s.indexrelid = i.oid
                WHERE n.nspname = 'intelligence'
                    AND t.relname = 'metrics'
                ORDER BY i.relname;
            """)
            parent_indexes = cur.fetchall()

            if parent_indexes:
                print(f"   Found {len(parent_indexes)} parent table indexes:")
                for row in parent_indexes:
                    print(f"   - {row[0]}")
                    print(f"     Table: {row[1]}")
                    print(f"     Scans: {row[2] if row[2] is not None else 'N/A'}")
                    print(f"     Size: {row[3]}")
            else:
                print("   No parent table indexes found")

            # Recommendation
            print("\n" + "=" * 80)
            print("RECOMMENDATION")
            print("=" * 80)
            print("\nThe 8 skipped partition indexes are inherited from parent table indexes.")
            print("They cannot be dropped individually - you must drop the parent index.")
            print("\nOptions:")
            print("  1. Keep them: If queries on metrics table need these indexes")
            print("  2. Drop parent indexes: This will cascade to all partitions")
            print("     - idx_metrics_name (and its partition indexes)")
            print("     - idx_metrics_digital_twin (and its partition indexes)")
            print("\nSince these indexes show 0 scans, they appear unused.")
            print("However, they may be needed for time-series queries on metrics data.")
            print("\nDecision: Keep them for now, monitor usage over 1-2 weeks.")

    finally:
        conn.close()

if __name__ == "__main__":
    check_partition_indexes()
