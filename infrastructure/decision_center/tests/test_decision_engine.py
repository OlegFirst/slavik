"""
Tests for Decision Engine
"""

import pytest
from datetime import datetime
from core.policy_engine import PolicyEngine
from core.decision_engine import DecisionEngine
from models.decision import DecisionRequest, DecisionOutcome, DecisionType


@pytest.fixture
def policy_engine():
    """Create policy engine fixture"""
    return PolicyEngine(policy_file="policies.yaml")


@pytest.fixture
def decision_engine(policy_engine):
    """Create decision engine fixture"""
    return DecisionEngine(
        policy_engine=policy_engine,
        escalation_manager=None,  # MVP: no escalation manager in tests
        audit_logger=None,        # MVP: no audit logger in tests
        ai_hub=None               # MVP: no AI hub in tests
    )


@pytest.mark.asyncio
async def test_auto_approve_restart_first_attempt(decision_engine):
    """Test auto-approval of first restart attempt"""
    # Create request
    request = DecisionRequest.create(
        service="redis",
        action="restart",
        reason="High memory usage detected",
        priority=2,
        context={"recovery_attempts": 0},
        requester="test"
    )

    # Make decision
    decision = await decision_engine.make_decision(request)

    # Assert
    assert decision.outcome == DecisionOutcome.APPROVED
    assert decision.decision_type == DecisionType.AUTO_APPROVED
    assert "Auto-approved" in decision.justification


@pytest.mark.asyncio
async def test_auto_approve_restart_within_limit(decision_engine):
    """Test auto-approval of restart within max_attempts"""
    # Create request (2nd attempt, max is 3)
    request = DecisionRequest.create(
        service="redis",
        action="restart",
        reason="Service unhealthy",
        priority=3,
        context={"recovery_attempts": 2},
        requester="test"
    )

    # Make decision
    decision = await decision_engine.make_decision(request)

    # Assert
    assert decision.outcome == DecisionOutcome.APPROVED
    assert decision.decision_type == DecisionType.AUTO_APPROVED


@pytest.mark.asyncio
async def test_reject_restart_exceeds_attempts(decision_engine):
    """Test rejection when max_attempts exceeded"""
    # Create request (4th attempt, max is 3)
    request = DecisionRequest.create(
        service="redis",
        action="restart",
        reason="Service unhealthy",
        priority=3,
        context={"recovery_attempts": 4},
        requester="test"
    )

    # Make decision
    decision = await decision_engine.make_decision(request)

    # Assert (should be rejected since no escalation manager)
    assert decision.outcome == DecisionOutcome.REJECTED
    assert "Escalation" in decision.justification or "required" in decision.justification.lower()


@pytest.mark.asyncio
async def test_auto_approve_failover(decision_engine):
    """Test auto-approval of failover"""
    # Create request
    request = DecisionRequest.create(
        service="database",
        action="failover",
        reason="Primary instance unhealthy",
        priority=1,
        context={"recovery_attempts": 0},
        requester="test"
    )

    # Make decision
    decision = await decision_engine.make_decision(request)

    # Assert
    assert decision.outcome == DecisionOutcome.APPROVED
    assert decision.decision_type == DecisionType.AUTO_APPROVED


@pytest.mark.asyncio
async def test_auto_approve_scale_down(decision_engine):
    """Test auto-approval of scale_down"""
    # Create request
    request = DecisionRequest.create(
        service="api_gateway",
        action="scale_down",
        reason="Low load detected",
        priority=4,
        context={},
        requester="test"
    )

    # Make decision
    decision = await decision_engine.make_decision(request)

    # Assert
    assert decision.outcome == DecisionOutcome.APPROVED
    assert decision.decision_type == DecisionType.AUTO_APPROVED


@pytest.mark.asyncio
async def test_reject_scale_up(decision_engine):
    """Test rejection of scale_up (requires manual approval)"""
    # Create request
    request = DecisionRequest.create(
        service="api_gateway",
        action="scale_up",
        reason="High load detected",
        priority=2,
        context={},
        requester="test"
    )

    # Make decision
    decision = await decision_engine.make_decision(request)

    # Assert (should be pending or rejected since no approval system)
    assert decision.outcome in [DecisionOutcome.PENDING, DecisionOutcome.REJECTED]


@pytest.mark.asyncio
async def test_reject_configuration_change(decision_engine):
    """Test rejection of configuration_change (requires approval)"""
    # Create request
    request = DecisionRequest.create(
        service="database",
        action="configuration_change",
        reason="Optimize performance",
        priority=3,
        context={},
        requester="test"
    )

    # Make decision
    decision = await decision_engine.make_decision(request)

    # Assert
    assert decision.outcome in [DecisionOutcome.PENDING, DecisionOutcome.REJECTED]


@pytest.mark.asyncio
async def test_decision_metadata(decision_engine):
    """Test that decision includes proper metadata"""
    # Create request
    request = DecisionRequest.create(
        service="redis",
        action="restart",
        reason="Test",
        priority=3,
        context={"recovery_attempts": 1},
        requester="test"
    )

    # Make decision
    decision = await decision_engine.make_decision(request)

    # Assert metadata
    assert decision.decision_id is not None
    assert decision.request_id == request.request_id
    assert decision.decided_at is not None
    assert decision.decided_by == "system"
    assert "policy_version" in decision.metadata


@pytest.mark.asyncio
async def test_unknown_action_rejected(decision_engine):
    """Test that unknown actions are rejected"""
    # Create request with unknown action
    request = DecisionRequest.create(
        service="redis",
        action="unknown_action",
        reason="Test unknown action",
        priority=3,
        context={},
        requester="test"
    )

    # Make decision
    decision = await decision_engine.make_decision(request)

    # Assert
    assert decision.outcome == DecisionOutcome.REJECTED
    assert "No matching policy" in decision.justification or "safe rejection" in decision.justification.lower()


def test_can_auto_approve_logic(decision_engine):
    """Test _can_auto_approve logic directly"""
    policies = {
        "max_auto_attempts": 3,
        "auto_approval": {
            "failover_allowed": True,
            "scale_down_requires_approval": False
        }
    }

    # Test restart within attempts
    request_restart = DecisionRequest.create(
        service="test",
        action="restart",
        reason="Test",
        context={"recovery_attempts": 1}
    )
    assert decision_engine._can_auto_approve(request_restart, policies) is True

    # Test restart exceeds attempts
    request_restart_exceed = DecisionRequest.create(
        service="test",
        action="restart",
        reason="Test",
        context={"recovery_attempts": 3}
    )
    assert decision_engine._can_auto_approve(request_restart_exceed, policies) is False

    # Test failover allowed
    request_failover = DecisionRequest.create(
        service="test",
        action="failover",
        reason="Test",
        context={}
    )
    assert decision_engine._can_auto_approve(request_failover, policies) is True

    # Test configuration change (not allowed)
    request_config = DecisionRequest.create(
        service="test",
        action="configuration_change",
        reason="Test",
        context={}
    )
    assert decision_engine._can_auto_approve(request_config, policies) is False


def test_requires_escalation_logic(decision_engine):
    """Test _requires_escalation logic directly"""
    policies = {
        "max_auto_attempts": 3,
        "rto": 300,
        "escalate_immediately": False
    }

    # Test max attempts exceeded
    request_exceed = DecisionRequest.create(
        service="test",
        action="restart",
        reason="Test",
        context={"recovery_attempts": 3}
    )
    assert decision_engine._requires_escalation(request_exceed, policies) is True

    # Test escalate_immediately policy
    policies_escalate = {"escalate_immediately": True}
    request = DecisionRequest.create(
        service="test",
        action="restart",
        reason="Test",
        context={}
    )
    assert decision_engine._requires_escalation(request, policies_escalate) is True

    # Test RTO violation imminent
    request_rto = DecisionRequest.create(
        service="test",
        action="restart",
        reason="Test",
        context={"downtime_seconds": 250, "recovery_attempts": 1}
    )
    assert decision_engine._requires_escalation(request_rto, policies) is True


def test_detect_failure_pattern(decision_engine):
    """Test _detect_failure_pattern logic"""
    # Pattern detected (5+ recent failures)
    request_pattern = DecisionRequest.create(
        service="test",
        action="restart",
        reason="Test",
        context={
            "recent_failures": [1, 2, 3, 4, 5]
        }
    )
    assert decision_engine._detect_failure_pattern(request_pattern) is True

    # No pattern (< 5 failures)
    request_no_pattern = DecisionRequest.create(
        service="test",
        action="restart",
        reason="Test",
        context={
            "recent_failures": [1, 2]
        }
    )
    assert decision_engine._detect_failure_pattern(request_no_pattern) is False
