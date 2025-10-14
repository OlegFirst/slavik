"""
Unit tests for Meta-Learning Engine
"""

import pytest
import asyncio
from datetime import datetime
from core.learning import MetaLearningEngine


@pytest.fixture
def meta_learning():
    """Fixture for MetaLearningEngine"""
    return MetaLearningEngine()


@pytest.mark.asyncio
async def test_record_interaction(meta_learning):
    """Test recording an interaction"""
    result = await meta_learning.record_interaction(
        query="What are our top risks?",
        colleague_used="risk_analyst",
        intent_detected="analyze_risk",
        routing_confidence=0.95,
        response_confidence=0.88,
        actions_taken=3
    )
    
    assert result["recorded"] == True
    assert result["total_interactions"] == 1
    assert len(meta_learning.interaction_history) == 1


@pytest.mark.asyncio
async def test_routing_accuracy_calculation(meta_learning):
    """Test routing accuracy calculation"""
    # Record 10 successful interactions
    for i in range(10):
        await meta_learning.record_interaction(
            query=f"Test query {i}",
            colleague_used="risk_analyst",
            intent_detected="analyze_risk",
            routing_confidence=0.9,
            response_confidence=0.85
        )
    
    # Initial accuracy should be 100% (no corrections)
    accuracy = await meta_learning.get_routing_accuracy()
    assert accuracy == 1.0
    
    # Record a correction
    await meta_learning.record_user_feedback(
        interaction_id=0,
        feedback_score=0.3,
        correct_colleague="bia_specialist"
    )
    
    # Accuracy should drop
    accuracy_after = await meta_learning.get_routing_accuracy()
    assert accuracy_after < 1.0
    assert accuracy_after == 0.9  # 1 correction out of 10


@pytest.mark.asyncio
async def test_user_feedback_recording(meta_learning):
    """Test recording user feedback"""
    # Record interaction first
    await meta_learning.record_interaction(
        query="Test query",
        colleague_used="risk_analyst",
        intent_detected="analyze_risk",
        routing_confidence=0.9,
        response_confidence=0.85
    )
    
    # Record feedback
    result = await meta_learning.record_user_feedback(
        interaction_id=0,
        feedback_score=0.8
    )
    
    assert result["feedback_recorded"] == True
    assert result["total_feedback"] == 1
    assert meta_learning.learning_stats["total_feedback_received"] == 1


@pytest.mark.asyncio
async def test_routing_recommendation(meta_learning):
    """Test ML-based routing recommendation"""
    # Record multiple interactions for same intent
    for i in range(5):
        await meta_learning.record_interaction(
            query="Analyze risk",
            colleague_used="risk_analyst",
            intent_detected="analyze_risk",
            routing_confidence=0.9,
            response_confidence=0.88
        )
    
    # Get recommendation
    recommendation = await meta_learning.get_routing_recommendation(
        query="New risk query",
        intent="analyze_risk"
    )
    
    assert recommendation == "risk_analyst"


@pytest.mark.asyncio
async def test_performance_insights(meta_learning):
    """Test performance insights retrieval"""
    # Record interactions for a colleague
    for i in range(5):
        await meta_learning.record_interaction(
            query=f"Risk query {i}",
            colleague_used="risk_analyst",
            intent_detected="analyze_risk",
            routing_confidence=0.9,
            response_confidence=0.85 + i * 0.01
        )
    
    # Get performance insights
    insights = await meta_learning.get_performance_insights("risk_analyst")
    
    assert insights["colleague"] == "risk_analyst"
    assert insights["total_queries"] == 5
    assert insights["avg_response_confidence"] > 0.85


@pytest.mark.asyncio
async def test_learning_insights(meta_learning):
    """Test overall learning insights"""
    # Record various interactions
    colleagues = ["risk_analyst", "bia_specialist", "compliance_copilot"]
    for i in range(15):
        await meta_learning.record_interaction(
            query=f"Query {i}",
            colleague_used=colleagues[i % 3],
            intent_detected="query_info",
            routing_confidence=0.8 + (i % 10) * 0.01,
            response_confidence=0.85
        )
    
    insights = await meta_learning.get_learning_insights()
    
    assert insights["total_interactions"] == 15
    assert insights["routing_accuracy"] >= 0.0
    assert insights["intent_patterns_learned"] > 0


def test_intent_pattern_update(meta_learning):
    """Test intent pattern tracking"""
    # Create a mock record
    class MockRecord:
        def __init__(self):
            self.intent_detected = "analyze_risk"
            self.colleague_used = "risk_analyst"
            self.routing_confidence = 0.9
            self.response_confidence = 0.85
            self.query = "What are the top risks?"
    
    record = MockRecord()
    meta_learning._update_intent_patterns(record)
    
    assert "analyze_risk" in meta_learning.intent_patterns
    assert meta_learning.intent_patterns["analyze_risk"]["total_queries"] == 1
    assert meta_learning.intent_patterns["analyze_risk"]["colleagues_used"]["risk_analyst"] == 1


def test_colleague_performance_update(meta_learning):
    """Test colleague performance tracking"""
    class MockRecord:
        def __init__(self):
            self.colleague_used = "risk_analyst"
            self.response_confidence = 0.88
            self.intent_detected = "analyze_risk"
            self.timestamp = datetime.utcnow()
    
    record = MockRecord()
    meta_learning._update_colleague_performance(record)
    
    assert "risk_analyst" in meta_learning.colleague_performance
    perf = meta_learning.colleague_performance["risk_analyst"]
    assert perf["total_queries"] == 1
    assert len(perf["avg_response_confidence"]) == 1


def test_get_stats(meta_learning):
    """Test quick stats retrieval"""
    stats = meta_learning.get_stats()
    
    assert "meta_learning_engine" in stats
    assert stats["meta_learning_engine"] == "active"
    assert "total_interactions" in stats
    assert "intents_tracked" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
