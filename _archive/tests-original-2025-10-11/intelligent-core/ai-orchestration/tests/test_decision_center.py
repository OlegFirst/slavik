"""
Tests for Decision Center
==========================
"""

import pytest
from .models import FullContext, Priority, PriorityLevel
from .decision_center import (
    ContextAggregator, PriorityEngine, StrategySelector
)


@pytest.mark.asyncio
async def test_context_aggregator():
    """Test context aggregation."""
    aggregator = ContextAggregator()
    await aggregator.initialize()

    situation = {'test': True}
    context = await aggregator.aggregate(situation, 'test_tenant')

    assert isinstance(context, FullContext)
    assert context.platform_state is not None
    assert isinstance(context.workflows, list)
    assert isinstance(context.recent_events, list)


@pytest.mark.asyncio
async def test_priority_engine():
    """Test priority assessment."""
    engine = PriorityEngine()

    # Create test context
    context = FullContext(
        platform_state={'status': 'operational'},
        workflows=[],
        recent_events=[],
        similar_situations=[]
    )

    priority = await engine.assess_priority(context)

    assert isinstance(priority, Priority)
    assert priority.level in PriorityLevel
    assert 0 <= priority.score <= 100
    assert 'business_impact' in priority.reasoning


@pytest.mark.asyncio
async def test_priority_levels():
    """Test different priority levels."""
    engine = PriorityEngine()

    # Low priority context
    low_context = FullContext(
        platform_state={'status': 'operational'},
        workflows=[],
        recent_events=[],
        similar_situations=[]
    )

    low_priority = await engine.assess_priority(low_context)
    assert low_priority.level in [PriorityLevel.LOW, PriorityLevel.MEDIUM]

    # High priority context
    high_context = FullContext(
        platform_state={'status': 'degraded'},
        workflows=[{'priority': 'critical'} for _ in range(15)],
        recent_events=[{'type': 'security'} for _ in range(50)],
        similar_situations=[]
    )

    high_priority = await engine.assess_priority(high_context)
    assert high_priority.level in [PriorityLevel.HIGH, PriorityLevel.CRITICAL]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
