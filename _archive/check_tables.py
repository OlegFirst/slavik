#!/usr/bin/env python3
"""
Quick script to check if database tables exist
"""
import asyncio
import asyncpg
import os
from pathlib import Path

# Load .env
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#') and '=' in line:
                key, val = line.strip().split('=', 1)
                os.environ[key] = val

async def check_tables():
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print('❌ DATABASE_URL not found in .env')
        return

    print(f'🔍 Connecting to database...')
    print(f'   URL: {db_url[:50]}...')

    try:
        conn = await asyncpg.connect(db_url)
        print('✅ Connection successful!\n')

        # Check schemas
        schemas = await conn.fetch("""
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name IN ('auth', 'learning', 'governance', 'portal', 'marketplace')
            ORDER BY schema_name
        """)

        print('📊 Existing schemas:')
        for s in schemas:
            print(f'   ✅ {s["schema_name"]}')

        if not schemas:
            print('   ❌ No service schemas found!')
            print('\n⚠️  Need to run migrations!')
            await conn.close()
            return

        print()

        # Check tables in each schema
        for schema in schemas:
            schema_name = schema['schema_name']
            tables = await conn.fetch(f"""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = '{schema_name}'
                ORDER BY table_name
            """)

            print(f'📋 {schema_name} schema tables:')
            if tables:
                for t in tables:
                    # Count rows
                    count = await conn.fetchval(f'SELECT COUNT(*) FROM {schema_name}.{t["table_name"]}')
                    print(f'   ✅ {t["table_name"]:<40} ({count} rows)')
            else:
                print(f'   ❌ No tables found')
            print()

        await conn.close()
        print('✅ Database check complete!')

    except Exception as e:
        print(f'❌ Error: {e}')
        print(f'\n⚠️  This probably means:')
        print(f'   1. Database is not accessible (firewall/network)')
        print(f'   2. Tables haven\'t been created yet')
        print(f'   3. Need to run migrations')

if __name__ == '__main__':
    asyncio.run(check_tables())
