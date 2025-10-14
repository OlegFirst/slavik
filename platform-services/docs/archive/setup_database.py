#!/usr/bin/env python3
"""
BCM Platform - Database Setup Script
Comprehensive database initialization and migration application
"""
import os
import sys
import psycopg2
import hashlib
import time
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime

# Colors for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_header():
    print(f"{Colors.BLUE}╔════════════════════════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.BLUE}║   BCM Platform - Database Setup & Migration Script            ║{Colors.NC}")
    print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════════════╝{Colors.NC}")
    print()

def load_env_file(env_path: Path) -> dict:
    """Load environment variables from .env file"""
    env_vars = {}
    if env_path.exists():
        print(f"{Colors.GREEN}✓{Colors.NC} Loading environment from {env_path}")
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value.strip('"').strip("'")
    else:
        print(f"{Colors.YELLOW}⚠{Colors.NC} No .env file found at {env_path}")
    return env_vars

def get_db_connection(database_url: str) -> psycopg2.extensions.connection:
    """Create database connection"""
    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        return conn
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.NC} Database connection failed: {e}")
        sys.exit(1)

def create_migration_tracking_table(cursor: psycopg2.extensions.cursor):
    """Create table to track applied migrations"""
    sql = """
    CREATE TABLE IF NOT EXISTS public.schema_migrations (
        id SERIAL PRIMARY KEY,
        migration_number VARCHAR(10) UNIQUE NOT NULL,
        migration_name VARCHAR(255) NOT NULL,
        applied_at TIMESTAMP DEFAULT NOW() NOT NULL,
        checksum VARCHAR(64),
        execution_time_ms INTEGER,
        applied_by VARCHAR(100) DEFAULT current_user
    );

    CREATE INDEX IF NOT EXISTS idx_migrations_number ON public.schema_migrations(migration_number);
    CREATE INDEX IF NOT EXISTS idx_migrations_applied_at ON public.schema_migrations(applied_at);

    COMMENT ON TABLE public.schema_migrations IS 'Tracks applied database migrations';
    """

    try:
        cursor.execute(sql)
        print(f"{Colors.GREEN}✓{Colors.NC} Migration tracking table created")
    except psycopg2.Error as e:
        print(f"{Colors.YELLOW}⚠{Colors.NC} Migration tracking table may already exist")

def get_migration_checksum(migration_path: Path) -> str:
    """Calculate checksum of migration file"""
    content = migration_path.read_text()
    return hashlib.sha256(content.encode()).hexdigest()

def is_migration_applied(cursor: psycopg2.extensions.cursor, migration_num: str) -> bool:
    """Check if migration has been applied"""
    try:
        cursor.execute(
            "SELECT COUNT(*) FROM public.schema_migrations WHERE migration_number = %s",
            (migration_num,)
        )
        return cursor.fetchone()[0] > 0
    except psycopg2.Error:
        return False

def apply_migration(
    cursor: psycopg2.extensions.cursor,
    migration_path: Path
) -> Tuple[bool, Optional[int]]:
    """Apply a single migration"""
    filename = migration_path.name
    migration_num = filename[:3]
    migration_name = filename[:-4]  # Remove .sql

    # Check if already applied
    if is_migration_applied(cursor, migration_num):
        print(f"{Colors.BLUE}⊙{Colors.NC} {filename} (already applied)")
        return True, None

    print(f"{Colors.YELLOW}→{Colors.NC} Applying {filename}...")

    # Read migration SQL
    migration_sql = migration_path.read_text()
    checksum = get_migration_checksum(migration_path)

    try:
        start_time = time.time()
        cursor.execute(migration_sql)
        execution_time = int((time.time() - start_time) * 1000)

        # Record successful migration
        cursor.execute(
            """
            INSERT INTO public.schema_migrations
            (migration_number, migration_name, execution_time_ms, checksum)
            VALUES (%s, %s, %s, %s)
            """,
            (migration_num, migration_name, execution_time, checksum)
        )

        print(f"{Colors.GREEN}✓{Colors.NC} {filename} applied successfully ({execution_time}ms)")
        return True, execution_time

    except psycopg2.Error as e:
        print(f"{Colors.RED}✗{Colors.NC} {filename} failed: {e}")
        return False, None

def get_database_stats(cursor: psycopg2.extensions.cursor) -> dict:
    """Get database statistics"""
    stats = {}

    try:
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.schemata
            WHERE schema_name NOT IN ('pg_catalog', 'information_schema')
        """)
        stats['schemas'] = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        """)
        stats['tables'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM public.schema_migrations")
        stats['migrations_applied'] = cursor.fetchone()[0]

    except psycopg2.Error:
        pass

    return stats

def main():
    print_header()

    # Configuration
    project_root = Path("/Users/MD/AI-Platform-ISO")
    db_dir = project_root / "infrastructure" / "database"
    migrations_dir = db_dir / "migrations_source"
    postgresql_migrations_dir = db_dir / "postgresql" / "migrations_source"

    # Load environment
    env_file = project_root / ".env"
    env_vars = load_env_file(env_file)

    # Get database URL
    database_url = env_vars.get('DATABASE_URL') or os.getenv('DATABASE_URL')

    if not database_url:
        print(f"{Colors.RED}✗{Colors.NC} DATABASE_URL not set")
        print("\nPlease set DATABASE_URL in .env or environment")
        print("Example: postgresql://user:password@localhost:5432/dbname")
        sys.exit(1)

    print(f"{Colors.GREEN}✓{Colors.NC} Database URL configured")
    print(f"  Connection: {database_url.split('@')[0]}@***")
    print()

    # Connect to database
    print(f"{Colors.BLUE}[1/5] Connecting to Database{Colors.NC}")
    print("─" * 64)
    conn = get_db_connection(database_url)
    cursor = conn.cursor()
    print(f"{Colors.GREEN}✓{Colors.NC} Connection successful")
    print()

    # Check migration files
    print(f"{Colors.BLUE}[2/5] Analyzing Migration Status{Colors.NC}")
    print("─" * 64)

    migrations = sorted(migrations_dir.glob("*.sql"))
    total_migrations = len(migrations)

    print(f"{Colors.GREEN}✓{Colors.NC} Found {total_migrations} migration files")
    print()
    print("Available migrations:")
    for i, migration in enumerate(migrations[:10], 1):
        migration_num = migration.name[:3]
        print(f"  {migration_num}: {migration.name}")
    if total_migrations > 10:
        print(f"  ... and {total_migrations - 10} more")
    print()

    # Setup tracking
    print(f"{Colors.BLUE}[3/5] Setting Up Migration Tracking{Colors.NC}")
    print("─" * 64)
    create_migration_tracking_table(cursor)
    print()

    # Apply migrations
    print(f"{Colors.BLUE}[4/5] Applying Migrations{Colors.NC}")
    print("─" * 64)

    success_count = 0
    fail_count = 0
    total_time = 0

    for migration in migrations:
        success, exec_time = apply_migration(cursor, migration)
        if success:
            success_count += 1
            if exec_time:
                total_time += exec_time
        else:
            fail_count += 1
            print(f"{Colors.YELLOW}⚠{Colors.NC} Continuing with next migration...")

    # Apply PostgreSQL specific migrations if they exist
    if postgresql_migrations_dir.exists():
        postgres_migrations = sorted(postgresql_migrations_dir.glob("*.sql"))
        if postgres_migrations:
            print()
            print("Applying PostgreSQL-specific migrations...")
            for migration in postgres_migrations:
                success, exec_time = apply_migration(cursor, migration)
                if success:
                    success_count += 1
                    if exec_time:
                        total_time += exec_time
                else:
                    fail_count += 1

    print()

    # Summary
    print(f"{Colors.BLUE}[5/5] Migration Summary{Colors.NC}")
    print("─" * 64)
    print(f"  Total available:  {total_migrations}")
    print(f"  {Colors.GREEN}Successfully applied: {success_count}{Colors.NC}")
    if fail_count > 0:
        print(f"  {Colors.RED}Failed: {fail_count}{Colors.NC}")
    print(f"  Total execution time: {total_time}ms")
    print()

    # Database stats
    stats = get_database_stats(cursor)
    if stats:
        print("Database status:")
        print(f"  Schemas:   {stats.get('schemas', '?')}")
        print(f"  Tables:    {stats.get('tables', '?')}")
        print(f"  Migrations: {stats.get('migrations_applied', '?')}")
        print()

    # Cleanup
    cursor.close()
    conn.close()

    # Final status
    if fail_count == 0:
        print(f"{Colors.GREEN}╔════════════════════════════════════════════════════════════════╗{Colors.NC}")
        print(f"{Colors.GREEN}║   ✓ Database setup completed successfully!                     ║{Colors.NC}")
        print(f"{Colors.GREEN}╚════════════════════════════════════════════════════════════════╝{Colors.NC}")
        sys.exit(0)
    else:
        print(f"{Colors.YELLOW}╔════════════════════════════════════════════════════════════════╗{Colors.NC}")
        print(f"{Colors.YELLOW}║   ⚠ Database setup completed with {fail_count} failures                ║{Colors.NC}")
        print(f"{Colors.YELLOW}╚════════════════════════════════════════════════════════════════╝{Colors.NC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
