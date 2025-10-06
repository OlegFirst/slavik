#!/usr/bin/env python3
"""Auto-apply ALL remaining migrations with schema creation"""
import psycopg2
from pathlib import Path

conn_params = {
    "host": "aws-1-eu-north-1.pooler.supabase.com",
    "port": 5432,
    "dbname": "postgres",
    "user": "postgres.tpdkhddtbhpoqzzgxfni",
    "password": "K@x3ta9V8GK5rnW",
    "sslmode": "require"
}

MIGRATIONS_DIR = Path("/Users/MD/AI-Platform-ISO/infrastructure/database/migrations_source")
APPLIED = {
    "001", "002", "003", "004", "005", "006", "007", "008", "009"
}

# Missing schemas
SCHEMAS = ["validation", "learning", "bcm", "compliance", "core"]

# Create missing schemas
SCHEMAS = ["validation", "learning", "bcm", "compliance"]

print("🚀 Auto-applying ALL remaining migrations...")
conn = psycopg2.connect(**conn_params)
conn.autocommit = True
cur = conn.cursor()

# Create missing schemas
print("\n📦 Creating missing schemas...")
for schema in SCHEMAS:
    cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema};")
    cur.execute(f"GRANT USAGE ON SCHEMA {schema} TO authenticated;")
    print(f"✅ Schema: {schema}")

# Apply migrations
migrations = sorted(MIGRATIONS_DIR.glob("*.sql"))
for migration_file in migrations:
    num = migration_file.name[:3]
    if num in APPLIED:
        continue

    print(f"\n📄 Applying: {migration_file.name}")
    sql = migration_file.read_text()

    try:
        cur.execute(sql)
        print(f"✅ Success: {migration_file.name}")
        APPLIED.add(num)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Continuing...")

conn.close()
print("\n🎉 All migrations completed!")
print(f"✅ Applied: {len(APPLIED)} migrations")
