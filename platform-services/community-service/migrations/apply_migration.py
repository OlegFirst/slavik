#!/usr/bin/env python3
"""
Apply Community Service migrations to Supabase

Usage:
    python3 apply_migration.py [migration_file]

    # Apply specific migration
    python3 apply_migration.py 001_community_schemas.sql

    # Apply all migrations
    python3 apply_migration.py --all
"""

import os
import sys
from pathlib import Path
import asyncpg
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent.parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment!")
    print("Please set DATABASE_URL in .env file")
    sys.exit(1)


async def apply_migration(migration_file: str):
    """Apply a single migration file"""
    migration_path = Path(__file__).parent / migration_file

    if not migration_path.exists():
        print(f"❌ Migration file not found: {migration_path}")
        return False

    print(f"📝 Reading migration: {migration_file}")
    sql = migration_path.read_text()

    print(f"🔗 Connecting to database...")
    # Extract connection params from URL for asyncpg
    # postgresql://user:pass@host:port/db
    import re
    match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', DATABASE_URL)
    if not match:
        print(f"❌ Invalid DATABASE_URL format")
        return False

    user, password, host, port, database = match.groups()

    try:
        conn = await asyncpg.connect(
            user=user,
            password=password,
            database=database,
            host=host,
            port=int(port)
        )

        print(f"✅ Connected to {database}@{host}")

        # Execute migration
        print(f"🚀 Applying migration...")
        await conn.execute(sql)

        print(f"✅ Migration applied successfully!")

        # Verify schemas created
        schemas = await conn.fetch("""
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name IN ('portal', 'marketplace')
        """)

        print(f"\n📊 Schemas:")
        for schema in schemas:
            print(f"  ✅ {schema['schema_name']}")

            # Count tables in schema
            tables = await conn.fetch(f"""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = '{schema['schema_name']}'
                AND table_type = 'BASE TABLE'
            """)
            print(f"     Tables: {len(tables)}")
            for table in tables:
                print(f"       - {table['table_name']}")

        await conn.close()
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def apply_all_migrations():
    """Apply all migration files in order"""
    migrations_dir = Path(__file__).parent
    migration_files = sorted(migrations_dir.glob("*.sql"))

    if not migration_files:
        print("❌ No migration files found")
        return False

    print(f"Found {len(migration_files)} migrations:")
    for f in migration_files:
        print(f"  - {f.name}")

    print()

    for migration_file in migration_files:
        success = await apply_migration(migration_file.name)
        if not success:
            print(f"\n❌ Migration sequence failed at {migration_file.name}")
            return False
        print()

    print("✅ All migrations applied successfully!")
    return True


async def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            await apply_all_migrations()
        else:
            migration_file = sys.argv[1]
            await apply_migration(migration_file)
    else:
        # Default: apply 001_community_schemas.sql
        await apply_migration("001_community_schemas.sql")


if __name__ == "__main__":
    asyncio.run(main())
