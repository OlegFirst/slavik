"""
Database Initialization Script

Creates all tables in the database using SQLAlchemy models
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine
from storage.models import Base


async def init_database():
    """Initialize database tables"""

    # Get database URL from environment
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/digital_twin"
    )

    print(f"Connecting to: {database_url}")

    # Create engine
    engine = create_async_engine(database_url, echo=True)

    try:
        # Create all tables
        async with engine.begin() as conn:
            print("\n Creating all tables...")
            await conn.run_sync(Base.metadata.create_all)
            print(" All tables created successfully!\n")

        # Show created tables
        async with engine.connect() as conn:
            result = await conn.execute(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
            )
            tables = result.fetchall()

            print(" Created tables:")
            for table in tables:
                print(f"   - {table[0]}")

    except Exception as e:
        print(f" Error creating tables: {e}")
        raise

    finally:
        await engine.dispose()


async def drop_database():
    """Drop all tables (DANGEROUS!)"""

    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/digital_twin"
    )

    print(f"️  WARNING: Dropping all tables from: {database_url}")
    confirm = input("Are you sure? Type 'yes' to confirm: ")

    if confirm.lower() != 'yes':
        print("Aborted.")
        return

    engine = create_async_engine(database_url, echo=True)

    try:
        async with engine.begin() as conn:
            print("\n Dropping all tables...")
            await conn.run_sync(Base.metadata.drop_all)
            print(" All tables dropped!\n")

    finally:
        await engine.dispose()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        asyncio.run(drop_database())
    else:
        asyncio.run(init_database())
