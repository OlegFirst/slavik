"""
Tests for Evolution Engine
===========================
"""

import pytest
from intelligent_core.ai_orchestration.evolution import (
    EvolutionEngine, DataEvolution, ModelEvolution, CodeEvolution
)
from intelligent_core.ai_orchestration.memory import DistributedMemory


@pytest.mark.asyncio
async def test_data_evolution():
    """Test data evolution."""
    memory = DistributedMemory()
    await memory.initialize()

    evolution = DataEvolution()
    await evolution.initialize(memory)

    result = await evolution.evolve()

    assert result['ran'] is True
    assert 'items_learned' in result
    assert 'cases_added' in result
    assert 'patterns_extracted' in result
    assert 'old_data_cleaned' in result

    await memory.close()


@pytest.mark.asyncio
async def test_model_evolution():
    """Test model evolution."""
    memory = DistributedMemory()
    await memory.initialize()

    evolution = ModelEvolution()
    await evolution.initialize(memory)

    result = await evolution.evolve()

    assert result['ran'] is True
    assert 'models_updated' in result
    assert 'models_rolled_back' in result

    await memory.close()


@pytest.mark.asyncio
async def test_code_evolution():
    """Test code evolution (human review required)."""
    memory = DistributedMemory()
    await memory.initialize()

    evolution = CodeEvolution()
    await evolution.initialize(memory)

    result = await evolution.evolve()

    assert result['ran'] is True
    assert result['review_required'] is True
    assert result['auto_deploy'] is False  # Never auto-deploy code
    assert 'pull_requests' in result

    await memory.close()


@pytest.mark.asyncio
async def test_evolution_engine_integration():
    """Test full evolution engine."""
    memory = DistributedMemory()
    await memory.initialize()

    engine = EvolutionEngine()
    await engine.initialize(memory)

    # Get stats
    stats = engine.get_stats()
    assert 'data_cycles' in stats
    assert 'model_cycles' in stats
    assert 'code_cycles' in stats

    await engine.shutdown()
    await memory.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
