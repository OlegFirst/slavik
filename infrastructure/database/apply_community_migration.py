#!/usr/bin/env python3
"""
Apply Community Intelligence Migration (037)

Usage:
    python apply_community_migration.py
"""

import os
import sys
from pathlib import Path

# Add infrastructure to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def apply_migration():
    """Apply migration 037"""

    print("=" * 60)
    print("Community Intelligence Migration (037)")
    print("=" * 60)
    print()

    # Check DATABASE_URL
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ ERROR: DATABASE_URL not set")
        print()
        print("Please set DATABASE_URL:")
        print("  export DATABASE_URL='postgresql://user:pass@host:5432/db'")
        print()
        print("Or load from .env:")
        print("  from dotenv import load_dotenv; load_dotenv()")
        return False

    # Try to load from .env if DATABASE_URL not in environment
    if not db_url:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            db_url = os.getenv('DATABASE_URL')
            print("✅ Loaded DATABASE_URL from .env")
        except ImportError:
            print("💡 Tip: Install python-dotenv to load from .env")

    print(f"Database: {db_url[:30]}...")
    print()

    # Get migration file
    migration_file = Path(__file__).parent / "migrations_source" / "037_community_intelligence.sql"

    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return False

    print(f"Migration file: {migration_file.name}")
    print(f"Size: {migration_file.stat().st_size / 1024:.1f} KB")
    print()

    # Confirm
    response = input("Apply migration? (y/N): ").strip().lower()
    if response != 'y':
        print("Aborted.")
        return False

    print()
    print("Applying migration...")
    print()

    # Apply using psycopg2 or subprocess
    try:
        import asyncpg
        import asyncio

        async def run_migration():
            conn = await asyncpg.connect(db_url)
            try:
                sql = migration_file.read_text()
                await conn.execute(sql)
                print("✅ Migration applied successfully!")
                return True
            finally:
                await conn.close()

        success = asyncio.run(run_migration())

    except ImportError:
        # Fallback to subprocess
        import subprocess

        result = subprocess.run(
            ['psql', db_url, '-f', str(migration_file)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("✅ Migration applied successfully!")
            success = True
        else:
            print(f"❌ Migration failed:")
            print(result.stderr)
            success = False

    if success:
        print()
        print("Created tables:")
        print("  - case_contributions")
        print("  - peer_reviews")
        print("  - user_reputation")
        print("  - reputation_transactions")
        print("  - community_annotations")
        print("  - synthesized_guidance")
        print()
        print("Verify with:")
        print("  psql $DATABASE_URL -c \"\\dt *contributions*\"")
        print()

    return success

if __name__ == "__main__":
    success = apply_migration()
    sys.exit(0 if success else 1)
