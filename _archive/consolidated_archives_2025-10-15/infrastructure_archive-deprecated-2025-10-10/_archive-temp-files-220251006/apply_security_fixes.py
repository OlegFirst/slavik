#!/usr/bin/env python3
"""
Apply Supabase Security and Performance Fixes
Applies migrations 029-033 to fix linter issues
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# Migration files in order
MIGRATIONS = [
    "029_fix_security_definer_view.sql",
    "030_fix_function_search_path.sql",
    "031_fix_auth_rls_initplan.sql",
    "032_add_foreign_key_indexes.sql",
    "033_consolidate_permissive_policies.sql",
]

async def apply_migration(engine, migration_file: str, migrations_dir: Path):
    """Apply a single migration file"""
    migration_path = migrations_dir / migration_file

    if not migration_path.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return False

    print(f"\n📝 Applying migration: {migration_file}")

    try:
        # Read migration SQL
        with open(migration_path, 'r', encoding='utf-8') as f:
            sql = f.read()

        # Execute migration
        async with engine.begin() as conn:
            # Split by semicolon and execute each statement
            statements = [s.strip() for s in sql.split(';') if s.strip()]

            for i, statement in enumerate(statements, 1):
                # Skip comments and empty statements
                if not statement or statement.startswith('--'):
                    continue

                try:
                    await conn.execute(text(statement))
                    print(f"  ✅ Statement {i}/{len(statements)} executed")
                except Exception as e:
                    # Continue on policy not found errors (they may have been already dropped)
                    if "does not exist" in str(e).lower():
                        print(f"  ⚠️  Statement {i}: {str(e)[:100]}")
                        continue
                    else:
                        raise

        print(f"✅ Migration {migration_file} applied successfully!")
        return True

    except Exception as e:
        print(f"❌ Error applying migration {migration_file}:")
        print(f"   {str(e)}")
        return False

async def main():
    print("=" * 70)
    print("🔧 Applying Supabase Security & Performance Fixes")
    print("=" * 70)

    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        sys.exit(1)

    # Convert to async URL
    async_db_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

    print(f"\n📊 Database: {database_url.split('@')[1].split('/')[0]}")
    print(f"📂 Migrations directory: infrastructure/database/migrations_source/")
    print(f"📝 Migrations to apply: {len(MIGRATIONS)}")

    # Create engine
    engine = create_async_engine(
        async_db_url,
        echo=False,
        pool_pre_ping=True
    )

    # Test connection
    print("\n🔌 Testing database connection...")
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connected to PostgreSQL")
            print(f"   Version: {version.split(',')[0]}")
    except Exception as e:
        print(f"❌ Failed to connect to database:")
        print(f"   {str(e)}")
        await engine.dispose()
        sys.exit(1)

    # Get migrations directory
    migrations_dir = Path(__file__).parent / "migrations_source"

    # Apply migrations
    print("\n" + "=" * 70)
    print("🚀 Applying Migrations")
    print("=" * 70)

    success_count = 0
    failed_count = 0

    for migration_file in MIGRATIONS:
        success = await apply_migration(engine, migration_file, migrations_dir)
        if success:
            success_count += 1
        else:
            failed_count += 1

    # Summary
    print("\n" + "=" * 70)
    print("📊 Migration Summary")
    print("=" * 70)
    print(f"✅ Successful: {success_count}/{len(MIGRATIONS)}")
    print(f"❌ Failed: {failed_count}/{len(MIGRATIONS)}")

    if failed_count == 0:
        print("\n🎉 All migrations applied successfully!")
        print("\n📋 Next Steps:")
        print("   1. Check Supabase Dashboard > Database > Linter")
        print("   2. Configure Auth settings (leaked password protection, MFA)")
        print("   3. Run performance tests to verify improvements")
    else:
        print("\n⚠️  Some migrations failed. Please check the errors above.")

    # Cleanup
    await engine.dispose()

    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
