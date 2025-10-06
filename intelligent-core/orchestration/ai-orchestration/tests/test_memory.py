"""
Tests for Memory System
========================
"""

import pytest
from datetime import datetime
from intelligent_core.ai_orchestration.memory import (
    DistributedMemory, WorkingMemory, ShortTermMemory,
    LongTermMemory, ProceduralMemory
)
from intelligent_core.ai_orchestration.models import MemoryType


@pytest.mark.asyncio
async def test_working_memory():
    """Test working memory operations."""
    memory = WorkingMemory()
    await memory.initialize()

    # Store and retrieve
    await memory.store('test_key', {'data': 'test_value'})
    value = await memory.retrieve('test_key')

    assert value is not None
    assert value['data'] == 'test_value'

    # Non-existent key
    value = await memory.retrieve('nonexistent')
    assert value is None

    await memory.close()


@pytest.mark.asyncio
async def test_distributed_memory():
    """Test distributed memory integration."""
    memory = DistributedMemory()
    await memory.initialize()

    # Store in working memory
    success = await memory.store(
        MemoryType.WORKING,
        'test_key',
        {'data': 'test_value'}
    )
    assert success

    # Retrieve from working memory
    value = await memory.retrieve(MemoryType.WORKING, 'test_key')
    assert value is not None
    assert value['data'] == 'test_value'

    await memory.close()


@pytest.mark.asyncio
async def test_memory_stats():
    """Test memory statistics."""
    memory = DistributedMemory()
    await memory.initialize()

    stats = memory.get_stats()

    assert 'working' in stats
    assert 'short_term' in stats
    assert 'long_term' in stats
    assert 'procedural' in stats

    await memory.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
