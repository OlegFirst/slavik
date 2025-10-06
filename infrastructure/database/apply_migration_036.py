#!/usr/bin/env python3
"""
Apply Migration 036: Unified Workflow Engine

Applies BPMN workflow tables to Supabase
"""

import os
import sys
import asyncio
from pathlib import Path
from supabase import create_client, Client
import asyncpg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))


async def apply_migration():
    """Apply migration 036 to Supabase"""

    print("="*60)
    print("Applying Migration 036: Unified Workflow Engine")
    print("="*60)

    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    database_url = os.getenv("DATABASE_URL")

    if not all([supabase_url, supabase_key, database_url]):
        print("\n❌ Error: Missing Supabase credentials!")
        print("\nPlease set in .env:")
        print("  SUPABASE_URL=https://your-project.supabase.co")
        print("  SUPABASE_SERVICE_ROLE_KEY=your-service-role-key")
        print("  DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres")
        return False

    print(f"\n🔗 Connecting to Supabase...")
    print(f"   URL: {supabase_url}")

    # Read migration file
    migration_file = Path(__file__).parent / "migrations_source" / "036_unified_workflow.sql"

    if not migration_file.exists():
        print(f"\n❌ Migration file not found: {migration_file}")
        return False

    print(f"\n📄 Reading migration: {migration_file.name}")

    with open(migration_file, 'r') as f:
        migration_sql = f.read()

    print(f"   Size: {len(migration_sql)} characters")

    # Connect to PostgreSQL directly (more reliable than Supabase client for DDL)
    try:
        print(f"\n🔌 Connecting to PostgreSQL...")

        conn = await asyncpg.connect(database_url)

        print(f"✅ Connected successfully")

        # Execute migration
        print(f"\n⚙️  Executing migration...")

        await conn.execute(migration_sql)

        print(f"✅ Migration executed successfully!")

        # Verify tables created
        print(f"\n🔍 Verifying tables...")

        tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'workflow'
            ORDER BY table_name
        """)

        print(f"\n📊 Created tables in 'workflow' schema:")
        for table in tables:
            print(f"   ✓ {table['table_name']}")

        # Check migration record
        migration_record = await conn.fetchrow("""
            SELECT * FROM public.schema_migrations
            WHERE version = '036'
        """)

        if migration_record:
            print(f"\n✅ Migration record inserted:")
            print(f"   Version: {migration_record['version']}")
            print(f"   Applied at: {migration_record.get('applied_at') or migration_record.get('inserted_at')}")

        await conn.close()

        print("\n" + "="*60)
        print("✅ Migration 036 applied successfully!")
        print("="*60)

        return True

    except Exception as e:
        print(f"\n❌ Error applying migration: {e}")
        import traceback
        traceback.print_exc()
        return False


async def rollback_migration():
    """Rollback migration 036 (if needed)"""

    print("="*60)
    print("Rolling back Migration 036")
    print("="*60)

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("❌ DATABASE_URL not set")
        return False

    rollback_sql = """
    -- Drop tables
    DROP TABLE IF EXISTS workflow.process_analytics CASCADE;
    DROP TABLE IF EXISTS workflow.bpmn_tasks CASCADE;
    DROP TABLE IF EXISTS workflow.bpmn_instances CASCADE;
    DROP TABLE IF EXISTS workflow.bpmn_processes CASCADE;

    -- Drop functions
    DROP FUNCTION IF EXISTS workflow.get_active_tasks CASCADE;
    DROP FUNCTION IF EXISTS workflow.get_process_duration_stats CASCADE;

    -- Drop schema (if empty)
    -- DROP SCHEMA IF EXISTS workflow CASCADE;

    -- Remove migration record
    DELETE FROM public.schema_migrations WHERE version = '036';
    """

    try:
        conn = await asyncpg.connect(database_url)

        print("\n⚙️  Executing rollback...")
        await conn.execute(rollback_sql)

        print("✅ Rollback completed")

        await conn.close()

        return True

    except Exception as e:
        print(f"❌ Error during rollback: {e}")
        return False


async def check_migration_status():
    """Check if migration 036 is already applied"""

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        return None

    try:
        conn = await asyncpg.connect(database_url)

        # Check migration record
        record = await conn.fetchrow("""
            SELECT * FROM public.schema_migrations
            WHERE version = '036'
        """)

        # Check if workflow schema exists
        schema_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.schemata
                WHERE schema_name = 'workflow'
            )
        """)

        await conn.close()

        return {
            "migration_record": record is not None,
            "schema_exists": schema_exists,
            "applied": record is not None and schema_exists
        }

    except Exception as e:
        print(f"Error checking status: {e}")
        return None


async def main():
    """Main entry point"""

    import argparse

    parser = argparse.ArgumentParser(
        description="Apply Migration 036: Unified Workflow Engine"
    )
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Rollback migration instead of applying"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Check migration status"
    )

    args = parser.parse_args()

    if args.status:
        status = await check_migration_status()
        if status:
            print("\n📊 Migration 036 Status:")
            print(f"   Migration record: {'✓' if status['migration_record'] else '✗'}")
            print(f"   Schema exists: {'✓' if status['schema_exists'] else '✗'}")
            print(f"   Applied: {'✅ Yes' if status['applied'] else '❌ No'}\n")
        return

    if args.rollback:
        success = await rollback_migration()
    else:
        # Check if already applied
        status = await check_migration_status()
        if status and status['applied']:
            print("\n⚠️  Migration 036 is already applied!")
            print("   Use --rollback to rollback first, or --status to check\n")
            return

        success = await apply_migration()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
