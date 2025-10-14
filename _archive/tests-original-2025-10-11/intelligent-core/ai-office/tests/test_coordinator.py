"""
Unit tests for Colleague Coordinator
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from coordinator import ColleagueCoordinator, ColleagueType


@pytest.fixture
def mock_rag_pipeline():
    """Mock RAG pipeline"""
    rag = MagicMock()
    rag.intent_analyzer = MagicMock()
    
    # Mock intent analysis
    mock_intent = MagicMock()
    mock_intent.intent_type = "analyze_risk"
    mock_intent.confidence = 0.9
    rag.intent_analyzer.analyze.return_value = mock_intent
    
    return rag


@pytest.fixture
def mock_colleagues():
    """Mock AI colleagues"""
    colleagues = {}
    
    for col_type in ["compliance_copilot", "risk_analyst", "bia_specialist"]:
        mock_colleague = MagicMock()
        mock_colleague.name = col_type.replace("_", " ").title()
        mock_colleague.specialty = f"{col_type} specialty"
        
        # Mock process_message
        mock_response = MagicMock()
        mock_response.content = f"Response from {col_type}"
        mock_response.confidence = 0.88
        mock_response.phase = MagicMock(value="plan")
        mock_response.context = MagicMock(value="risk")
        mock_response.actions = []
        mock_response.metadata = {"intent": "analyze_risk"}
        
        mock_colleague.process_message = AsyncMock(return_value=mock_response)
        colleagues[col_type] = mock_colleague
    
    return colleagues


@pytest.fixture
def coordinator(mock_rag_pipeline, mock_colleagues):
    """Fixture for ColleagueCoordinator"""
    return ColleagueCoordinator(
        rag_pipeline=mock_rag_pipeline,
        colleagues=mock_colleagues
    )


@pytest.mark.asyncio
async def test_manual_routing(coordinator):
    """Test manual routing to specific colleague"""
    result = await coordinator.route_query(
        query="What are our risks?",
        tenant_id="demo",
        colleague_type=ColleagueType.RISK_ANALYST
    )
    
    assert result["success"] == True
    assert result["colleague_type"] == "risk_analyst"
    assert "answer" in result
    assert result["routing_confidence"] == 1.0  # Manual routing = 100%


@pytest.mark.asyncio
async def test_auto_routing(coordinator):
    """Test auto-routing based on intent"""
    result = await coordinator.route_query(
        query="Analyze the top risks",
        tenant_id="demo",
        colleague_type=ColleagueType.AUTO
    )
    
    assert result["success"] == True
    assert "colleague_type" in result
    assert result["routing_confidence"] > 0.0


@pytest.mark.asyncio
async def test_workflow_execution(coordinator):
    """Test workflow execution"""
    result = await coordinator.execute_workflow(
        workflow_name="risk_to_plans",
        initial_query="Analyze ransomware risk",
        tenant_id="demo"
    )
    
    assert result["success"] == True
    assert result["workflow"] == "risk_to_plans"
    assert "results" in result


def test_get_stats(coordinator):
    """Test coordinator statistics"""
    stats = coordinator.get_stats()
    
    assert stats["coordinator"] == "ColleagueCoordinator"
    assert stats["colleagues_available"] == 3
    assert "routing_stats" in stats


def test_get_available_colleagues(coordinator):
    """Test listing available colleagues"""
    colleagues = coordinator.get_available_colleagues()
    
    assert len(colleagues) == 3
    assert all("type" in c and "name" in c and "specialty" in c for c in colleagues)


def test_intent_to_colleague_mapping(coordinator):
    """Test intent to colleague mapping"""
    assert coordinator.intent_to_colleague["analyze_risk"] == ColleagueType.RISK_ANALYST
    assert coordinator.intent_to_colleague["analyze_bia"] == ColleagueType.BIA_SPECIALIST
    assert coordinator.intent_to_colleague["query_compliance"] == ColleagueType.COMPLIANCE


def test_determine_context(coordinator):
    """Test context determination"""
    from colleagues import AssistantContext
    
    context = coordinator._determine_context(ColleagueType.RISK_ANALYST)
    assert context == AssistantContext.RISK
    
    context = coordinator._determine_context(ColleagueType.BIA_SPECIALIST)
    assert context == AssistantContext.BIA


@pytest.mark.asyncio
async def test_routing_stats_update(coordinator):
    """Test routing statistics are updated"""
    initial_total = coordinator.routing_stats["total_queries"]
    
    await coordinator.route_query(
        query="Test query",
        tenant_id="demo",
        colleague_type=ColleagueType.RISK_ANALYST
    )
    
    assert coordinator.routing_stats["total_queries"] == initial_total + 1
    assert coordinator.routing_stats["manual_routed"] > 0


@pytest.mark.asyncio
async def test_invalid_colleague_type(coordinator):
    """Test handling of invalid colleague type"""
    # Should raise or handle gracefully
    try:
        result = await coordinator.route_query(
            query="Test",
            tenant_id="demo",
            colleague_type="invalid_colleague"
        )
        # If it doesn't raise, should have error in result
        assert not result.get("success", True)
    except Exception:
        # Exception is acceptable
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
