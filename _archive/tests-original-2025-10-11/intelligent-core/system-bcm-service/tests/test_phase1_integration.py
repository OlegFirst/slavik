"""
Phase 1 Integration Test - Survival Instinct + Memory System

Tests complete integration:
1. Memory System initialization
2. Survival Instinct with Memory
3. Pattern learning and recall
4. Short-term and long-term memory coordination
"""

import asyncio
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ai-foundation"))

from memory.memory_system import create_memory_system, MemorySystem
from instincts.survival import SurvivalInstinct, ImbalanceDetection, ImbalanceLevel


@pytest.mark.asyncio
async def test_memory_system_initialization():
    """Test Memory System initializes correctly"""
    memory = await create_memory_system(
        short_term_max_size=100,
        short_term_ttl=60.0,
        long_term_storage_path="/tmp/test_memory.json",
        enable_vector_db=False
    )

    assert memory is not None
    assert memory.short_term is not None
    assert memory.long_term is not None
    assert memory.is_running

    memory.stop()


@pytest.mark.asyncio
async def test_short_term_memory():
    """Test short-term memory operations"""
    memory = await create_memory_system(
        short_term_max_size=10,
        short_term_ttl=1.0,
        enable_vector_db=False
    )

    # Store values
    memory.remember_short_term("key1", "value1")
    memory.remember_short_term("key2", {"data": "value2"})

    # Recall values
    assert memory.recall_short_term("key1") == "value1"
    assert memory.recall_short_term("key2")["data"] == "value2"

    # Non-existent key
    assert memory.recall_short_term("key3") is None

    memory.stop()


@pytest.mark.asyncio
async def test_pattern_learning():
    """Test pattern learning in long-term memory"""
    memory = await create_memory_system(
        long_term_storage_path="/tmp/test_patterns.json",
        enable_vector_db=False
    )

    # Remember successful pattern
    pattern1 = memory.remember_pattern(
        state_signature="cpu_80_mem_70",
        action_type="throttle",
        success=True,
        context={"cpu": 85, "memory": 75}
    )

    assert pattern1.success_count == 1
    assert pattern1.failure_count == 0
    assert pattern1.success_rate == 1.0

    # Remember same pattern again (success)
    pattern2 = memory.remember_pattern(
        state_signature="cpu_80_mem_70",
        action_type="throttle",
        success=True
    )

    assert pattern2.success_count == 2
    assert pattern2.success_rate == 1.0

    # Remember same pattern (failure)
    pattern3 = memory.remember_pattern(
        state_signature="cpu_80_mem_70",
        action_type="throttle",
        success=False
    )

    assert pattern3.success_count == 2
    assert pattern3.failure_count == 1
    assert 0.5 < pattern3.success_rate < 1.0

    memory.stop()


@pytest.mark.asyncio
async def test_pattern_matching():
    """Test finding matching patterns"""
    memory = await create_memory_system(
        long_term_storage_path="/tmp/test_matching.json",
        enable_vector_db=False
    )

    # Store patterns
    memory.remember_pattern("cpu_80_mem_70", "throttle", True)
    memory.remember_pattern("cpu_80_mem_70", "throttle", True)
    memory.remember_pattern("cpu_90_mem_80", "scale_up", True)

    # Find patterns
    patterns = memory.find_matching_patterns("cpu_80_mem_70", min_success_rate=0.5)

    assert len(patterns) > 0
    assert patterns[0].state_signature == "cpu_80_mem_70"

    memory.stop()


@pytest.mark.asyncio
async def test_survival_with_memory():
    """Test Survival Instinct integrated with Memory System"""
    memory = await create_memory_system(
        long_term_storage_path="/tmp/test_survival_memory.json",
        enable_vector_db=False
    )

    survival = SurvivalInstinct(
        module_name="test-module",
        check_interval_seconds=60,
        memory_system=memory
    )

    # Load default KPIs
    survival.load_my_kpis()

    assert len(survival.my_kpis) > 0
    assert survival.memory_system is not None

    # Create imbalance
    imbalance = ImbalanceDetection(
        kpi_name="cpu_utilization_percent",
        current_value=95.0,
        target_value=70.0,
        level=ImbalanceLevel.SEVERE,
        timestamp=asyncio.get_event_loop().time()
    )

    # Trigger correction (will use memory)
    action = survival.trigger_my_correction(imbalance)
    assert action is not None

    # Execute action (will record in memory)
    success = await survival._execute_correction_action(action, imbalance)

    # Check pattern was learned
    stats = memory.long_term.get_stats()
    assert stats['patterns_stored'] > 0

    memory.stop()


@pytest.mark.asyncio
async def test_memory_persistence():
    """Test memory persists to disk"""
    storage_path = "/tmp/test_persistence.json"

    # Create memory and store pattern
    memory1 = await create_memory_system(
        long_term_storage_path=storage_path,
        enable_vector_db=False
    )

    memory1.remember_pattern("state_1", "action_1", True)
    memory1.stop()

    # Create new memory from same file
    memory2 = await create_memory_system(
        long_term_storage_path=storage_path,
        enable_vector_db=False
    )

    # Check pattern was loaded
    patterns = memory2.find_matching_patterns("state_1")
    assert len(patterns) > 0

    memory2.stop()


@pytest.mark.asyncio
async def test_memory_stats():
    """Test memory statistics"""
    memory = await create_memory_system(
        short_term_max_size=10,
        enable_vector_db=False
    )

    # Store some data
    memory.remember_short_term("key1", "val1")
    memory.remember_short_term("key2", "val2")
    memory.remember_pattern("state1", "action1", True)

    # Get stats
    stats = memory.get_system_stats()

    assert "short_term" in stats
    assert "long_term" in stats
    assert stats["short_term"]["current_size"] == 2
    assert stats["long_term"]["total_patterns"] > 0

    memory.stop()


@pytest.mark.asyncio
async def test_pattern_success_rate():
    """Test pattern success rate calculation"""
    memory = await create_memory_system(
        long_term_storage_path="/tmp/test_success_rate.json",
        enable_vector_db=False
    )

    # Record multiple outcomes
    for i in range(7):
        memory.remember_pattern("state_test", "action_test", success=True)

    for i in range(3):
        memory.remember_pattern("state_test", "action_test", success=False)

    # Get pattern
    pattern = memory.long_term.get_pattern("state_test", "action_test")

    assert pattern is not None
    assert pattern.success_count == 7
    assert pattern.failure_count == 3
    assert pattern.success_rate == 0.7

    memory.stop()


@pytest.mark.asyncio
async def test_best_patterns():
    """Test getting best performing patterns"""
    memory = await create_memory_system(
        long_term_storage_path="/tmp/test_best_patterns.json",
        enable_vector_db=False
    )

    # Create patterns with different success rates
    for i in range(10):
        memory.remember_pattern("high_success", "action1", success=True)

    for i in range(5):
        memory.remember_pattern("medium_success", "action2", success=True)
    for i in range(5):
        memory.remember_pattern("medium_success", "action2", success=False)

    # Get best patterns
    best = memory.long_term.get_best_patterns(
        min_success_rate=0.8,
        min_use_count=5
    )

    assert len(best) > 0
    assert best[0].success_rate >= 0.8

    memory.stop()


if __name__ == "__main__":
    asyncio.run(test_memory_system_initialization())
    asyncio.run(test_short_term_memory())
    asyncio.run(test_pattern_learning())
    asyncio.run(test_pattern_matching())
    asyncio.run(test_survival_with_memory())
    asyncio.run(test_memory_persistence())
    asyncio.run(test_memory_stats())
    asyncio.run(test_pattern_success_rate())
    asyncio.run(test_best_patterns())

    print("✅ All Phase 1 integration tests passed")
