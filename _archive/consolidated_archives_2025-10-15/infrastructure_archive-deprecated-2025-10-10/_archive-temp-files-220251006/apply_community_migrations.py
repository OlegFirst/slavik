#!/usr/bin/env python3
"""
Apply Community Intelligence Migrations to Supabase
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Load environment
load_dotenv()

# Migrations to apply
COMMUNITY_MIGRATIONS = [
    '037_community_intelligence.sql',
    '040_community_intelligence.sql', 
    '041_collective_agents.sql'
]

async def apply_migrations():
    """Apply community intelligence migrations"""
    
    # Get database URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print('❌ DATABASE_URL not found in .env')
        sys.exit(1)
    
    # Convert to async URL
    async_db_url = database_url.replace('postgresql://', 'postgresql+asyncpg://')
    
    print(f'📊 Connecting to Supabase...')
    engine = create_async_engine(async_db_url, echo=False)
    
    try:
        async with engine.begin() as conn:
            # Create migrations table if not exists
            await conn.execute(text('''
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id SERIAL PRIMARY KEY,
                    migration_name VARCHAR(255) NOT NULL UNIQUE,
                    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            '''))
            print('✅ Migrations table ready')
            
            # Get already applied migrations
            result = await conn.execute(text(
                'SELECT migration_name FROM schema_migrations'
            ))
            applied = {row[0] for row in result}
            print(f'📋 Found {len(applied)} applied migrations')
            
            # Apply each migration
            migrations_dir = Path(__file__).parent / 'migrations_source'
            
            for migration_file in COMMUNITY_MIGRATIONS:
                if migration_file in applied:
                    print(f'⏭️  Skipping {migration_file} (already applied)')
                    continue
                
                migration_path = migrations_dir / migration_file
                
                if not migration_path.exists():
                    print(f'⚠️  Migration file not found: {migration_file}')
                    continue
                
                print(f'🚀 Applying {migration_file}...')
                
                # Read migration SQL
                with open(migration_path, 'r') as f:
                    sql = f.read()
                
                try:
                    # Execute migration
                    await conn.execute(text(sql))
                    
                    # Record as applied
                    await conn.execute(
                        text('INSERT INTO schema_migrations (migration_name) VALUES (:name)'),
                        {'name': migration_file}
                    )
                    
                    print(f'   ✅ {migration_file} applied successfully')
                    
                except Exception as e:
                    print(f'   ❌ Failed to apply {migration_file}')
                    print(f'   Error: {str(e)}')
                    raise
            
            print('\n✨ All community intelligence migrations applied!')
            
            # Show created tables
            result = await conn.execute(text('''
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN (
                    'case_contributions',
                    'peer_reviews',
                    'user_reputation',
                    'reputation_transactions',
                    'community_annotations',
                    'synthesized_guidance',
                    'collective_agents',
                    'stuck_organizations',
                    'agent_interactions'
                )
                ORDER BY table_name
            '''))
            
            tables = [row[0] for row in result]
            print(f'\n📊 Community Intelligence tables ({len(tables)}):')
            for table in tables:
                print(f'   • {table}')
            
    finally:
        await engine.dispose()

if __name__ == '__main__':
    asyncio.run(apply_migrations())
