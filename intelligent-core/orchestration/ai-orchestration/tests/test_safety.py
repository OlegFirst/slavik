"""
Tests for Safety Monitor
=========================
"""

import pytest
from datetime import datetime
from intelligent_core.ai_orchestration.models import (
    Decision, FullContext, ActionType, PriorityLevel
)
from intelligent_core.ai_orchestration.safety import (
    SafetyMonitor, ConstitutionEnforcer, LoopDetector
)


@pytest.mark.asyncio
async def test_constitution_enforcer():
    """Test constitution rule enforcement."""
    enforcer = ConstitutionEnforcer()
    await enforcer.initialize()

    # Test low confidence - should require escalation
    decision = Decision(
        action=ActionType.AUTO_RESOLVE,
        rationale="Auto-resolving",
        priority=PriorityLevel.MEDIUM,
        confidence=0.5  # Below 0.7 threshold
    )

    context = FullContext(
        platform_state={},
        workflows=[],
        recent_events=[],
        similar_situations=[]
    )

    result = await enforcer.validate(decision, context)

    # Should fail because confidence < 0.7 but action is AUTO_RESOLVE
    assert not result.safe
    assert len(result.concerns) > 0
    assert result.concerns[0].type == 'constitution_violation'


@pytest.mark.asyncio
async def test_constitution_high_confidence():
    """Test constitution with high confidence."""
    enforcer = ConstitutionEnforcer()
    await enforcer.initialize()

    # High confidence - should pass
    decision = Decision(
        action=ActionType.AUTO_RESOLVE,
        rationale="Auto-resolving with high confidence",
        priority=PriorityLevel.MEDIUM,
        confidence=0.95
    )

    context = FullContext(
        platform_state={},
        workflows=[],
        recent_events=[],
        similar_situations=[]
    )

    result = await enforcer.validate(decision, context)

    # Should pass
    assert result.safe
    assert len(result.concerns) == 0


@pytest.mark.asyncio
async def test_loop_detector():
    """Test loop detection."""
    detector = LoopDetector()
    await detector.initialize()

    # Create decision
    decision = Decision(
        action=ActionType.AUTO_RESOLVE,
        rationale="Resolving",
        priority=PriorityLevel.MEDIUM,
        confidence=0.8
    )

    context = FullContext(
        platform_state={},
        workflows=[],
        recent_events=[],
        similar_situations=[]
    )

    # First check - should pass
    result = await detector.check(decision, context)
    assert result.safe

    # Repeat same decision multiple times
    for _ in range(5):
        result = await detector.check(decision, context)

    # Should detect loop
    assert not result.safe
    assert any(c.type == 'infinite_loop' for c in result.concerns)


@pytest.mark.asyncio
async def test_safety_monitor_integration():
    """Test full safety monitor integration."""
    monitor = SafetyMonitor()
    await monitor.initialize()

    # Safe decision
    decision = Decision(
        action=ActionType.DELEGATE,
        rationale="Delegating to specialist",
        priority=PriorityLevel.MEDIUM,
        confidence=0.85
    )

    context = FullContext(
        platform_state={'status': 'operational'},
        workflows=[],
        recent_events=[],
        similar_situations=[]
    )

    result = await monitor.validate(decision, context)

    # Should pass all safety checks
    assert result.safe
    assert result.constitution_check
    assert result.loop_check
    assert result.hallucination_check


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
