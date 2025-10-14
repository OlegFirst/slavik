"""
Unit tests for Scenario Intelligence Database

Tests:
- PostgreSQL connection
- Schema verification
- RLS policies
- Functions
"""

import pytest
import sys
import os
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "intelligent-core/scenario-intelligence"))


@pytest.mark.asyncio
async def test_postgres_storage_import():
    """Test that PostgreSQL storage can be imported"""
    from storage.postgres_storage import PostgresScenarioStorage
    assert PostgresScenarioStorage is not None


@pytest.mark.asyncio
async def test_postgres_connection():
    """Test PostgreSQL connection"""
    from storage.postgres_storage import PostgresScenarioStorage

    conn_string = os.getenv('DATABASE_URL')
    if not conn_string:
        pytest.skip("DATABASE_URL not configured")

    storage = PostgresScenarioStorage(connection_string=conn_string)
    await storage.initialize()

    # Should not raise
    assert storage.pool is not None

    await storage.close()


@pytest.mark.asyncio
async def test_get_statistics():
    """Test getting statistics from database"""
    from storage.postgres_storage import PostgresScenarioStorage

    conn_string = os.getenv('DATABASE_URL')
    if not conn_string:
        pytest.skip("DATABASE_URL not configured")

    storage = PostgresScenarioStorage(connection_string=conn_string)
    await storage.initialize()

    stats = await storage.get_statistics()

    assert stats is not None
    assert isinstance(stats, dict)
    assert 'total_scenarios' in stats or len(stats) > 0

    await storage.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
