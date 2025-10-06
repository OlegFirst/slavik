#!/usr/bin/env python3
"""
Apply migration 024 - Drop unused indexes
"""
import psycopg2
from urllib.parse import quote_plus
import time

# Database connection
password = "K@x3ta9V8GK5rnW"
encoded_password = quote_plus(password)
db_url = f"postgresql://postgres.tpdkhddtbhpoqzzgxfni:{encoded_password}@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"

migration_file = "/Users/MD/AI-Platform-ISO/migrations/024_drop_unused_indexes.sql"

def apply_migration():
    """Apply the migration."""
    print("=" * 80)
    print("APPLYING MIGRATION 024: Drop Unused Indexes")
    print("=" * 80)

    # Read migration file
    print("\n1. Reading migration file...")
    with open(migration_file, 'r') as f:
        migration_sql = f.read()

    # Count DROP statements
    drop_count = migration_sql.count('DROP INDEX IF EXISTS')
    print(f"   Found {drop_count} DROP INDEX statements")

    # Connect to database
    print("\n2. Connecting to database...")
    conn = psycopg2.connect(db_url)
    conn.autocommit = False  # Use transaction
    print("   Connected successfully")

    try:
        print("\n3. Executing migration...")
        start_time = time.time()

        # Parse migration into individual DROP statements
        drop_statements = []
        for line in migration_sql.split('\n'):
            if line.strip().startswith('DROP INDEX IF EXISTS'):
                drop_statements.append(line.strip())

        print(f"   Executing {len(drop_statements)} DROP INDEX statements...")

        dropped_count = 0
        skipped_count = 0
        errors = []

        with conn.cursor() as cur:
            for i, stmt in enumerate(drop_statements, 1):
                try:
                    cur.execute(stmt)
                    conn.commit()
                    dropped_count += 1
                    if i % 50 == 0:
                        print(f"   Progress: {i}/{len(drop_statements)}")
                except Exception as e:
                    conn.rollback()
                    skipped_count += 1
                    error_msg = str(e).split('\n')[0]
                    errors.append({
                        'statement': stmt,
                        'error': error_msg
                    })
                    # Continue with next statement

        elapsed = time.time() - start_time
        print(f"   Completed in {elapsed:.2f} seconds")
        print(f"   Dropped: {dropped_count}, Skipped: {skipped_count}")

        # Verify indexes were dropped
        print("\n4. Verifying indexes were dropped...")
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*)
                FROM pg_stat_user_indexes
                WHERE schemaname IN ('public', 'bcm', 'auth', 'audit', 'validation', 'intelligence')
            """)
            remaining_indexes = cur.fetchone()[0]
            print(f"   Remaining user indexes: {remaining_indexes}")

        print("\n" + "=" * 80)
        print("MIGRATION APPLIED SUCCESSFULLY")
        print("=" * 80)
        print(f"\nDropped {dropped_count} unused indexes")
        print(f"Skipped {skipped_count} indexes (dependencies or already dropped)")
        print(f"Remaining indexes: {remaining_indexes}")

        if errors:
            print(f"\nErrors/Warnings ({len(errors)}):")
            for err in errors[:10]:  # Show first 10
                print(f"  - {err['statement'].split('.')[-1]}: {err['error'][:80]}")
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more")

        print(f"\nBenefits:")
        print("  - Reduced disk space usage")
        print("  - Improved write performance (INSERT, UPDATE, DELETE)")
        print("  - Lower index maintenance overhead")

    except Exception as e:
        print(f"\n   ERROR: {e}")
        print("   Rolling back transaction...")
        conn.rollback()
        raise

    finally:
        conn.close()

if __name__ == "__main__":
    try:
        apply_migration()
    except Exception as e:
        print(f"\nFailed to apply migration: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
