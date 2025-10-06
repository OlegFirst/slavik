#!/usr/bin/env python3
"""
Analyze unused indexes from Supabase linter CSV and query database to verify.
"""
import csv
import json
import psycopg2
from urllib.parse import quote_plus
from collections import defaultdict

# Database connection
password = "K@x3ta9V8GK5rnW"
encoded_password = quote_plus(password)
db_url = f"postgresql://postgres.tpdkhddtbhpoqzzgxfni:{encoded_password}@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"

# CSV file path
csv_file = "/Users/MD/Downloads/Supabase Performance Security Lints (tpdkhddtbhpoqzzgxfni) (3).csv"

def extract_unused_indexes_from_csv():
    """Extract all unused_index issues from CSV."""
    unused_indexes = []

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['name'] == 'unused_index':
                metadata = json.loads(row['metadata'])
                # Extract index name from cache_key: unused_index_schema_table_indexname
                cache_key = row['cache_key']
                parts = cache_key.split('_')
                # Find the index name - it's after schema and table
                # Format: unused_index_{schema}_{table}_{index_name}
                schema = metadata['schema']
                table = metadata['name']
                # Reconstruct: unused_index_schema_table_indexname
                prefix = f"unused_index_{schema}_{table}_"
                index_name = cache_key[len(prefix):]

                unused_indexes.append({
                    'schema': schema,
                    'table': table,
                    'index_name': index_name,
                    'detail': row['detail']
                })

    return unused_indexes

def query_index_stats(conn):
    """Query pg_stat_user_indexes to get actual usage stats."""
    query = """
    SELECT
        schemaname,
        relname,
        indexrelname,
        idx_scan,
        idx_tup_read,
        idx_tup_fetch,
        pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
        pg_relation_size(indexrelid) as size_bytes
    FROM pg_stat_user_indexes
    WHERE schemaname IN ('public', 'bcm', 'auth')
    ORDER BY schemaname, relname, indexrelname;
    """

    with conn.cursor() as cur:
        cur.execute(query)
        results = cur.fetchall()

        index_stats = {}
        for row in results:
            key = f"{row[0]}.{row[2]}"  # schema.indexname
            index_stats[key] = {
                'schema': row[0],
                'table': row[1],
                'index_name': row[2],
                'scans': row[3],
                'tuples_read': row[4],
                'tuples_fetched': row[5],
                'size': row[6],
                'size_bytes': row[7]
            }

        return index_stats

def query_index_definitions(conn):
    """Query index definitions to identify PK, FK, and unique indexes."""
    query = """
    SELECT
        n.nspname as schema,
        t.relname as table,
        i.relname as index_name,
        ix.indisprimary as is_primary,
        ix.indisunique as is_unique,
        pg_get_indexdef(ix.indexrelid) as index_def
    FROM pg_index ix
    JOIN pg_class i ON i.oid = ix.indexrelid
    JOIN pg_class t ON t.oid = ix.indrelid
    JOIN pg_namespace n ON n.oid = t.relnamespace
    WHERE n.nspname IN ('public', 'bcm', 'auth')
    ORDER BY n.nspname, t.relname, i.relname;
    """

    with conn.cursor() as cur:
        cur.execute(query)
        results = cur.fetchall()

        index_defs = {}
        for row in results:
            key = f"{row[0]}.{row[2]}"  # schema.indexname
            index_defs[key] = {
                'schema': row[0],
                'table': row[1],
                'index_name': row[2],
                'is_primary': row[3],
                'is_unique': row[4],
                'definition': row[5]
            }

        return index_defs

def query_foreign_key_indexes(conn):
    """Query to find indexes supporting foreign keys."""
    query = """
    SELECT
        n.nspname as schema,
        t.relname as table,
        c.conname as fk_name,
        a.attname as column_name
    FROM pg_constraint c
    JOIN pg_class t ON t.oid = c.conrelid
    JOIN pg_namespace n ON n.oid = t.relnamespace
    JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY(c.conkey)
    WHERE c.contype = 'f'
        AND n.nspname IN ('public', 'bcm', 'auth')
    ORDER BY n.nspname, t.relname, c.conname;
    """

    with conn.cursor() as cur:
        cur.execute(query)
        results = cur.fetchall()

        fk_columns = defaultdict(list)
        for row in results:
            key = f"{row[0]}.{row[1]}"  # schema.table
            fk_columns[key].append(row[3])  # column_name

        return fk_columns

def is_critical_index(index_def, fk_columns):
    """Determine if an index is critical and should NOT be dropped."""
    # Handle case where index_def is empty (index not found in DB)
    if not index_def:
        return False, None

    schema = index_def.get('schema', '')
    table = index_def.get('table', '')
    index_name = index_def.get('index_name', '')
    definition = index_def.get('definition', '')

    # Don't drop primary keys
    if index_def.get('is_primary', False):
        return True, "Primary key index"

    # Don't drop unique constraints
    if index_def.get('is_unique', False):
        return True, "Unique constraint index"

    # Check for critical column patterns
    critical_patterns = [
        '_id_',
        '_pkey',
        'organization_id',
        'user_id',
        'created_by',
        'updated_by',
        'owner_id'
    ]

    # Check if it's an FK index we just created in migration 021
    table_key = f"{schema}.{table}"
    if table_key in fk_columns:
        for col in fk_columns[table_key]:
            if col in definition.lower():
                return True, f"Foreign key index on {col}"

    # Check for critical patterns in index name or definition
    for pattern in critical_patterns:
        if pattern in index_name.lower() or pattern in definition.lower():
            # But if it's a duplicate or redundant index, it might still be droppable
            # We'll be conservative here
            pass

    return False, None

def analyze_indexes():
    """Main analysis function."""
    print("=" * 80)
    print("UNUSED INDEX ANALYSIS")
    print("=" * 80)

    # Step 1: Extract from CSV
    print("\n1. Extracting unused indexes from CSV...")
    csv_indexes = extract_unused_indexes_from_csv()
    print(f"   Found {len(csv_indexes)} unused indexes in CSV")

    # Step 2: Connect to database
    print("\n2. Connecting to database...")
    conn = psycopg2.connect(db_url)
    print("   Connected successfully")

    try:
        # Step 3: Query index stats
        print("\n3. Querying index statistics...")
        index_stats = query_index_stats(conn)
        print(f"   Found {len(index_stats)} indexes with stats")

        # Step 4: Query index definitions
        print("\n4. Querying index definitions...")
        index_defs = query_index_definitions(conn)
        print(f"   Found {len(index_defs)} index definitions")

        # Step 5: Query FK columns
        print("\n5. Querying foreign key columns...")
        fk_columns = query_foreign_key_indexes(conn)
        print(f"   Found {len(fk_columns)} tables with foreign keys")

        # Step 6: Analyze each index
        print("\n6. Analyzing indexes...")
        safe_to_drop = []
        keep_indexes = []
        total_size_to_free = 0

        for csv_index in csv_indexes:
            schema = csv_index['schema']
            table = csv_index['table']
            index_name = csv_index['index_name']
            key = f"{schema}.{index_name}"

            # Get stats
            stats = index_stats.get(key, {})
            index_def = index_defs.get(key, {})

            # Check if critical
            is_critical, reason = is_critical_index(index_def, fk_columns)

            if is_critical:
                keep_indexes.append({
                    'schema': schema,
                    'table': table,
                    'index_name': index_name,
                    'reason': reason,
                    'scans': stats.get('scans', 0),
                    'size': stats.get('size', 'unknown')
                })
            else:
                safe_to_drop.append({
                    'schema': schema,
                    'table': table,
                    'index_name': index_name,
                    'scans': stats.get('scans', 0),
                    'size': stats.get('size', 'unknown'),
                    'size_bytes': stats.get('size_bytes', 0)
                })
                total_size_to_free += stats.get('size_bytes', 0)

        # Step 7: Print results
        print("\n" + "=" * 80)
        print("ANALYSIS RESULTS")
        print("=" * 80)

        print(f"\nTotal indexes analyzed: {len(csv_indexes)}")
        print(f"Safe to drop: {len(safe_to_drop)}")
        print(f"Recommend keeping: {len(keep_indexes)}")
        print(f"Estimated space to free: {total_size_to_free / (1024*1024):.2f} MB")

        # Print keep list
        if keep_indexes:
            print("\n" + "-" * 80)
            print("INDEXES TO KEEP (Critical)")
            print("-" * 80)
            for idx in keep_indexes[:20]:  # Show first 20
                print(f"  {idx['schema']}.{idx['index_name']}")
                print(f"    Table: {idx['table']}")
                print(f"    Reason: {idx['reason']}")
                print(f"    Scans: {idx['scans']}, Size: {idx['size']}")
                print()

            if len(keep_indexes) > 20:
                print(f"  ... and {len(keep_indexes) - 20} more")

        # Print drop list
        if safe_to_drop:
            print("\n" + "-" * 80)
            print("INDEXES SAFE TO DROP")
            print("-" * 80)
            for idx in safe_to_drop[:20]:  # Show first 20
                print(f"  {idx['schema']}.{idx['index_name']}")
                print(f"    Table: {idx['table']}")
                print(f"    Scans: {idx['scans']}, Size: {idx['size']}")
                print()

            if len(safe_to_drop) > 20:
                print(f"  ... and {len(safe_to_drop) - 20} more")

        # Step 8: Generate migration
        print("\n7. Generating migration SQL...")
        generate_migration(safe_to_drop)

        return {
            'total_analyzed': len(csv_indexes),
            'safe_to_drop': len(safe_to_drop),
            'keep': len(keep_indexes),
            'space_to_free_mb': total_size_to_free / (1024*1024),
            'safe_to_drop_list': safe_to_drop,
            'keep_list': keep_indexes
        }

    finally:
        conn.close()

def generate_migration(indexes_to_drop):
    """Generate SQL migration to drop indexes."""
    if not indexes_to_drop:
        print("   No indexes to drop!")
        return

    migration_file = "/Users/MD/AI-Platform-ISO/migrations/024_drop_unused_indexes.sql"

    sql_lines = [
        "-- Migration 024: Drop Unused Indexes",
        "-- Generated from Supabase performance linter analysis",
        "-- Total indexes to drop: {}".format(len(indexes_to_drop)),
        "",
        "-- Drop unused indexes to improve write performance and save disk space",
        ""
    ]

    # Group by schema
    by_schema = defaultdict(list)
    for idx in indexes_to_drop:
        by_schema[idx['schema']].append(idx)

    for schema in sorted(by_schema.keys()):
        sql_lines.append(f"-- Schema: {schema}")
        sql_lines.append("")

        for idx in sorted(by_schema[schema], key=lambda x: x['table']):
            sql_lines.append(f"-- Table: {idx['table']}, Size: {idx['size']}, Scans: {idx['scans']}")
            sql_lines.append(f"DROP INDEX IF EXISTS {schema}.{idx['index_name']};")
            sql_lines.append("")

    migration_content = "\n".join(sql_lines)

    with open(migration_file, 'w') as f:
        f.write(migration_content)

    print(f"   Migration generated: {migration_file}")
    print(f"   Total DROP INDEX statements: {len(indexes_to_drop)}")

if __name__ == "__main__":
    try:
        results = analyze_indexes()
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
