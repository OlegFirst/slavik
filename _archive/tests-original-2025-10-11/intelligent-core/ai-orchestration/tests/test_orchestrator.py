"""
Tests for Main Orchestrator
===========================
"""

import pytest
from datetime import datetime
from . import AIOrchestrator, ActionType, PriorityLevel


@pytest.mark.asyncio
async def test_orchestrator_initialization():
    """Test orchestrator can be initialized."""
    orchestrator = AIOrchestrator(event_bus_backend='memory', enable_safety=False, enable_evolution=False)

    assert orchestrator is not None
    assert not orchestrator.initialized

    # Initialize
    await orchestrator.initialize()

    assert orchestrator.initialized

    # Cleanup
    await orchestrator.shutdown()


@pytest.mark.asyncio
async def test_orchestrator_decide():
    """Test orchestrator can make decisions."""
    orchestrator = AIOrchestrator(event_bus_backend='memory', enable_safety=False, enable_evolution=False)
    await orchestrator.initialize()

    # Simple situation
    situation = {
        'workflow_stuck': True,
        'workflow_id': 'test_workflow_001',
        'stuck_duration_minutes': 30
    }

    # Make decision
    decision = await orchestrator.decide(situation, tenant_id='test_tenant')

    # Verify decision
    assert decision is not None
    assert decision.action is not None
    assert decision.rationale is not None
    assert decision.priority in PriorityLevel
    assert 0 <= decision.confidence <= 1

    # Check stats
    stats = orchestrator.get_stats()
    assert stats['decisions_made'] == 1

    # Cleanup
    await orchestrator.shutdown()


@pytest.mark.asyncio
async def test_orchestrator_execute():
    """Test orchestrator can execute decisions."""
    orchestrator = AIOrchestrator(event_bus_backend='memory', enable_safety=False, enable_evolution=False)
    await orchestrator.initialize()

    situation = {
        'workflow_stuck': True,
        'workflow_id': 'test_workflow_001'
    }

    # Make and execute decision
    decision = await orchestrator.decide(situation, tenant_id='test_tenant')
    result = await orchestrator.execute(decision)

    # Verify execution result
    assert result is not None
    assert 'success' in result
    assert 'action' in result

    # Cleanup
    await orchestrator.shutdown()


@pytest.mark.asyncio
async def test_orchestrator_with_safety():
    """Test orchestrator with safety monitoring enabled."""
    orchestrator = AIOrchestrator(event_bus_backend='memory', enable_safety=True, enable_evolution=False)
    await orchestrator.initialize()

    # Low confidence situation - should trigger safety escalation
    situation = {
        'unknown_error': True,
        'error_type': 'mysterious'
    }

    decision = await orchestrator.decide(situation, tenant_id='test_tenant')

    # With safety, low confidence should escalate
    assert decision.safety_approved is not None

    # Cleanup
    await orchestrator.shutdown()


@pytest.mark.asyncio
async def test_orchestrator_stats():
    """Test orchestrator statistics tracking."""
    orchestrator = AIOrchestrator(event_bus_backend='memory', enable_safety=False, enable_evolution=False)
    await orchestrator.initialize()

    # Make multiple decisions
    for i in range(3):
        situation = {'test': True, 'iteration': i}
        await orchestrator.decide(situation, tenant_id='test_tenant')

    # Check stats
    stats = orchestrator.get_stats()
    assert stats['decisions_made'] == 3
    assert 'memory_stats' in stats

    # Cleanup
    await orchestrator.shutdown()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
