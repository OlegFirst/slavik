"""
End-to-End Tests for Decision Center + AI Hub Integration

Tests the full integration between Decision Center and AI Intelligence Hub,
including real Anthropic API calls and fallback mechanisms.
"""

import pytest
import os
from datetime import datetime

# Add parent directory to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.policy_engine import PolicyEngine
from core.decision_engine import DecisionEngine
from integrations.ai_hub_v2 import AIIntelligenceHub, AITier
from models.decision import DecisionRequest, DecisionOutcome, DecisionType


@pytest.fixture
def policy_engine():
    """Create policy engine fixture"""
    return PolicyEngine(policy_file="policies.yaml")


@pytest.fixture
def ai_hub_with_api():
    """Create AI Hub with real Anthropic API (if key available)"""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    return AIIntelligenceHub(
        anthropic_api_key=api_key,
        tier1_enabled=False,  # Expensive, disabled for tests
        tier2_enabled=True,   # Claude Sonnet
        tier3_enabled=True,   # Claude Haiku
        enable_fallback=True  # Always have fallback
    )


@pytest.fixture
def ai_hub_fallback_only():
    """Create AI Hub with only fallback (no API key)"""
    return AIIntelligenceHub(
        anthropic_api_key=None,
        tier1_enabled=False,
        tier2_enabled=False,
        tier3_enabled=False,
        enable_fallback=True
    )


@pytest.fixture
def decision_engine_with_ai(policy_engine, ai_hub_with_api):
    """Create decision engine with AI Hub"""
    return DecisionEngine(
        policy_engine=policy_engine,
        escalation_manager=None,
        audit_logger=None,
        ai_hub=ai_hub_with_api
    )


@pytest.fixture
def decision_engine_fallback(policy_engine, ai_hub_fallback_only):
    """Create decision engine with fallback-only AI Hub"""
    return DecisionEngine(
        policy_engine=policy_engine,
        escalation_manager=None,
        audit_logger=None,
        ai_hub=ai_hub_fallback_only
    )


# ============================================================================
# AI Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_ai_consultation_triggered_on_complex_issue(decision_engine_with_ai):
    """
    Test that AI consultation is triggered for complex/unknown issues
    """
    # Create request with complex issue (triggers AI consultation)
    request = DecisionRequest.create(
        service="database",
        action="restart",
        reason="repeated failure with unknown root cause",  # Triggers AI
        priority=2,
        context={
            "recovery_attempts": 2,
            "downtime_seconds": 180,
            "memory_percent": 95,
            "recent_failures": [
                {"timestamp": "2025-01-15T10:00:00Z", "type": "high_memory"},
                {"timestamp": "2025-01-15T10:05:00Z", "type": "high_memory"}
            ]
        },
        requester="test"
    )

    # Make decision
    decision = await decision_engine_with_ai.make_decision(request)

    # Assert AI was consulted
    assert decision.decision_type == DecisionType.AI_CONSULTED
    assert decision.decided_by == "ai"
    assert "ai_model" in decision.metadata
    assert "confidence" in decision.metadata

    # Should be approved or escalated based on AI confidence
    assert decision.outcome in [DecisionOutcome.APPROVED, DecisionOutcome.ESCALATED]

    print(f" AI Consultation Test:")
    print(f"   Model: {decision.metadata.get('ai_model')}")
    print(f"   Confidence: {decision.metadata.get('confidence')}")
    print(f"   Outcome: {decision.outcome.value}")
    print(f"   Justification: {decision.justification[:100]}...")


@pytest.mark.asyncio
async def test_ai_hub_tier_selection(ai_hub_with_api):
    """
    Test AI Hub tier selection logic based on complexity
    """
    # High complexity → Tier 2 (Tier 1 disabled in tests)
    tier_high = ai_hub_with_api._select_tier("high", {"recovery_attempts": 0})
    assert tier_high == AITier.TIER2_OPERATIONAL

    # Medium complexity → Tier 2
    tier_medium = ai_hub_with_api._select_tier("medium", {"recovery_attempts": 0})
    assert tier_medium == AITier.TIER2_OPERATIONAL

    # Low complexity → Tier 3
    tier_low = ai_hub_with_api._select_tier("low", {"recovery_attempts": 0})
    assert tier_medium == AITier.TIER3_QUICK

    # High attempts → upgrade to high complexity → Tier 2
    tier_attempts = ai_hub_with_api._select_tier("low", {"recovery_attempts": 5})
    assert tier_attempts == AITier.TIER2_OPERATIONAL

    print(f" Tier Selection Test:")
    print(f"   High complexity: {tier_high.value}")
    print(f"   Medium complexity: {tier_medium.value}")
    print(f"   Low complexity: {tier_low.value}")
    print(f"   High attempts (upgraded): {tier_attempts.value}")


@pytest.mark.asyncio
async def test_ai_consultation_with_real_api(ai_hub_with_api):
    """
    Test real Anthropic API call (only if API key available)
    """
    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        pytest.skip("ANTHROPIC_API_KEY not set - skipping real API test")

    # Make AI consultation request
    response = await ai_hub_with_api.consult(
        problem="Database repeatedly failing after restart",
        context={
            "recovery_attempts": 3,
            "downtime_seconds": 300,
            "failure_type": "high_memory",
            "recent_failures": [
                {"type": "high_memory", "timestamp": "2025-01-15T10:00:00Z"},
                {"type": "high_memory", "timestamp": "2025-01-15T10:05:00Z"},
                {"type": "high_memory", "timestamp": "2025-01-15T10:10:00Z"}
            ]
        },
        service="database",
        action="restart",
        complexity="high"
    )

    # Assert response
    assert response.recommendation in [
        "approve_restart", "escalate", "investigate", "wait_and_retry"
    ]
    assert 0.0 <= response.confidence <= 1.0
    assert len(response.reasoning) > 0
    assert response.model_used.startswith("claude-")
    assert response.tier in [AITier.TIER2_OPERATIONAL, AITier.TIER3_QUICK]
    assert response.latency_ms > 0
    assert response.cost_usd > 0

    print(f" Real API Test:")
    print(f"   Model: {response.model_used}")
    print(f"   Tier: {response.tier.value}")
    print(f"   Recommendation: {response.recommendation}")
    print(f"   Confidence: {response.confidence}")
    print(f"   Latency: {response.latency_ms}ms")
    print(f"   Cost: ${response.cost_usd:.4f}")
    print(f"   Reasoning: {response.reasoning[:150]}...")


@pytest.mark.asyncio
async def test_fallback_when_no_api_key(ai_hub_fallback_only):
    """
    Test that fallback works when no API key is available
    """
    # Make consultation request (should use heuristics)
    response = await ai_hub_fallback_only.consult(
        problem="High memory usage detected",
        context={"recovery_attempts": 1},
        service="database",
        action="restart",
        complexity="medium"
    )

    # Assert fallback response
    assert response.recommendation == "approve_restart"
    assert response.model_used == "heuristic_fallback"
    assert "[HEURISTIC FALLBACK]" in response.reasoning
    assert response.cost_usd == 0.0
    assert response.latency_ms < 50  # Very fast

    print(f" Fallback Test:")
    print(f"   Model: {response.model_used}")
    print(f"   Recommendation: {response.recommendation}")
    print(f"   Confidence: {response.confidence}")
    print(f"   Reasoning: {response.reasoning[:100]}...")


@pytest.mark.asyncio
async def test_heuristic_escalation_logic(ai_hub_fallback_only):
    """
    Test heuristic escalation after max attempts
    """
    # Request with high recovery attempts → should escalate
    response = await ai_hub_fallback_only.consult(
        problem="Repeated failure after multiple restarts",
        context={"recovery_attempts": 3},
        service="database",
        action="restart",
        complexity="high"
    )

    # Should recommend escalation
    assert response.recommendation == "escalate"
    assert "Repeated failures" in response.reasoning or "attempts" in response.reasoning

    print(f" Heuristic Escalation Test:")
    print(f"   Recommendation: {response.recommendation}")
    print(f"   Reasoning: {response.reasoning}")


@pytest.mark.asyncio
async def test_ai_hub_cost_tracking(ai_hub_with_api):
    """
    Test AI Hub usage statistics and cost tracking
    """
    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        pytest.skip("ANTHROPIC_API_KEY not set - skipping cost tracking test")

    # Get initial stats
    initial_stats = ai_hub_with_api.get_usage_stats()
    initial_requests = initial_stats.get("total_requests", 0)
    initial_cost = initial_stats.get("total_cost_usd", 0.0)

    # Make a request
    await ai_hub_with_api.consult(
        problem="CPU usage high",
        context={"recovery_attempts": 1},
        service="api_gateway",
        action="scale_up",
        complexity="medium"
    )

    # Get updated stats
    updated_stats = ai_hub_with_api.get_usage_stats()

    # Assert stats were updated
    assert updated_stats["total_requests"] == initial_requests + 1
    assert updated_stats["total_cost_usd"] > initial_cost

    print(f" Cost Tracking Test:")
    print(f"   Requests: {initial_requests} → {updated_stats['total_requests']}")
    print(f"   Cost: ${initial_cost:.4f} → ${updated_stats['total_cost_usd']:.4f}")
    print(f"   Avg cost/request: ${updated_stats['average_cost_per_request']:.4f}")


@pytest.mark.asyncio
async def test_tier_status_endpoint(ai_hub_with_api):
    """
    Test AI Hub tier status API
    """
    status = await ai_hub_with_api.get_tier_status()

    # Assert status structure
    assert "tier1_strategic" in status
    assert "tier2_operational" in status
    assert "tier3_quick" in status
    assert "tier4_custom" in status
    assert "api_available" in status

    # Check tier configurations
    assert status["tier1_strategic"]["enabled"] is False  # Disabled in tests
    assert status["tier2_operational"]["enabled"] is True
    assert status["tier3_quick"]["enabled"] is True
    assert status["tier4_custom"]["enabled"] is False  # Future

    # Check API availability
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        assert status["api_available"] is True
        assert "usage" in status
    else:
        assert status["api_available"] is False
        assert status.get("fallback_mode") == "heuristics"

    print(f" Tier Status Test:")
    print(f"   API Available: {status['api_available']}")
    print(f"   Tier 1: {status['tier1_strategic']['enabled']}")
    print(f"   Tier 2: {status['tier2_operational']['enabled']}")
    print(f"   Tier 3: {status['tier3_quick']['enabled']}")
    if "usage" in status:
        print(f"   Total requests: {status['usage']['total_requests']}")
        print(f"   Total cost: ${status['usage']['total_cost_usd']:.4f}")


# ============================================================================
# E2E Recovery Flow Tests
# ============================================================================

@pytest.mark.asyncio
async def test_e2e_recovery_flow_with_ai(decision_engine_with_ai):
    """
    Test complete recovery flow: failure → decision → AI consultation → approval
    """
    # Simulate service failure scenario
    request = DecisionRequest.create(
        service="database",
        action="restart",
        reason="performance degradation with unknown root cause",  # Triggers AI
        priority=2,
        context={
            "recovery_attempts": 1,
            "downtime_seconds": 120,
            "cpu_percent": 85,
            "memory_percent": 90,
            "recent_failures": [
                {"type": "performance_degradation", "timestamp": "2025-01-15T10:00:00Z"}
            ]
        },
        requester="auto_recovery_handler"
    )

    # Make decision (full flow)
    decision = await decision_engine_with_ai.make_decision(request)

    # Assert complete flow
    assert decision.request_id == request.request_id
    assert decision.service == "database"
    assert decision.action == "restart"
    assert decision.decided_at is not None
    assert decision.justification is not None

    # Should either be AI-consulted or auto-approved
    assert decision.decision_type in [DecisionType.AI_CONSULTED, DecisionType.AUTO_APPROVED]

    # If AI was consulted, check metadata
    if decision.decision_type == DecisionType.AI_CONSULTED:
        assert "ai_model" in decision.metadata
        assert "confidence" in decision.metadata
        print(f"    AI consultation used: {decision.metadata['ai_model']}")
    else:
        print(f"    Auto-approved without AI")

    print(f" E2E Recovery Flow Test:")
    print(f"   Decision ID: {decision.decision_id}")
    print(f"   Decision Type: {decision.decision_type.value}")
    print(f"   Outcome: {decision.outcome.value}")
    print(f"   Justification: {decision.justification[:100]}...")


@pytest.mark.asyncio
async def test_e2e_recovery_flow_fallback(decision_engine_fallback):
    """
    Test complete recovery flow with fallback (no API key)
    """
    request = DecisionRequest.create(
        service="redis",
        action="restart",
        reason="unknown issue detected",  # Would trigger AI, but uses fallback
        priority=3,
        context={"recovery_attempts": 1},
        requester="auto_recovery_handler"
    )

    decision = await decision_engine_fallback.make_decision(request)

    # Should work with fallback
    assert decision.outcome is not None
    assert decision.justification is not None

    print(f" E2E Fallback Flow Test:")
    print(f"   Outcome: {decision.outcome.value}")
    print(f"   Justification: {decision.justification[:100]}...")


# ============================================================================
# Helper function to run tests manually
# ============================================================================

if __name__ == "__main__":
    """
    Run tests manually with:

    # With API key (real AI tests):
    export ANTHROPIC_API_KEY="sk-ant-..."
    python test_ai_integration_e2e.py

    # Without API key (fallback tests only):
    python test_ai_integration_e2e.py
    """
    import asyncio

    print("=" * 80)
    print("Running AI Integration E2E Tests")
    print("=" * 80)

    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        print(f" ANTHROPIC_API_KEY detected - will test real AI")
    else:
        print(f"️  ANTHROPIC_API_KEY not set - will test fallback only")

    print("=" * 80)

    # Run with pytest
    pytest.main([__file__, "-v", "-s"])
