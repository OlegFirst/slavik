"""
Workflow Analysis Tests

Tests for workflow analysis and ML recommendation endpoints.
"""

import pytest
import httpx

BASE_URL = "http://localhost:8037"


# ==================== Workflow Analysis Tests ====================

@pytest.mark.asyncio
async def test_analyze_workflow_basic():
    """Test basic workflow analysis"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = {
            "workflow_id": "test-workflow-001",
            "workflow_data": {
                "steps": ["step1", "step2", "step3"],
                "type": "sequential"
            }
        }
        response = await client.post(
            f"{BASE_URL}/analyze",
            json=request
        )
        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert data["workflow_id"] == "test-workflow-001"
        assert "analysis" in data
        assert "recommendations" in data
        assert "confidence" in data

        # Verify data types
        assert isinstance(data["analysis"], dict)
        assert isinstance(data["recommendations"], list)
        assert isinstance(data["confidence"], (int, float))


@pytest.mark.asyncio
async def test_analyze_workflow_with_context():
    """Test workflow analysis with context"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = {
            "workflow_id": "workflow-with-context",
            "workflow_data": {
                "name": "BIA Workflow",
                "complexity": "high"
            },
            "context": {
                "industry": "finance",
                "organization_size": "large",
                "priority": "critical"
            }
        }
        response = await client.post(
            f"{BASE_URL}/analyze",
            json=request
        )
        assert response.status_code == 200
        data = response.json()
        assert "analysis" in data


@pytest.mark.asyncio
async def test_analyze_complex_workflow():
    """Test analysis of complex workflow"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = {
            "workflow_id": "complex-workflow",
            "workflow_data": {
                "steps": [
                    {
                        "id": "step1",
                        "type": "data_collection",
                        "dependencies": []
                    },
                    {
                        "id": "step2",
                        "type": "analysis",
                        "dependencies": ["step1"]
                    },
                    {
                        "id": "step3",
                        "type": "validation",
                        "dependencies": ["step2"]
                    },
                    {
                        "id": "step4",
                        "type": "reporting",
                        "dependencies": ["step2", "step3"]
                    }
                ],
                "parallel_execution": True,
                "estimated_duration": "30m"
            },
            "context": {
                "module": "bia",
                "automation_level": "partial"
            }
        }
        response = await client.post(
            f"{BASE_URL}/analyze",
            json=request
        )
        assert response.status_code == 200
        data = response.json()

        # Should have analysis
        assert "complexity" in data["analysis"]
        assert len(data["recommendations"]) > 0


@pytest.mark.asyncio
async def test_analyze_different_workflow_types():
    """Test analysis of different workflow types"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        workflow_types = [
            "bia_assessment",
            "risk_analysis",
            "incident_response",
            "compliance_check",
            "plan_generation"
        ]

        for wf_type in workflow_types:
            request = {
                "workflow_id": f"{wf_type}-workflow",
                "workflow_data": {
                    "type": wf_type,
                    "steps": ["init", "execute", "validate"]
                }
            }
            response = await client.post(
                f"{BASE_URL}/analyze",
                json=request
            )
            assert response.status_code == 200


# ==================== Recommendations Tests ====================

@pytest.mark.asyncio
async def test_get_recommendations_basic():
    """Test getting basic recommendations"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        workflow_data = {
            "type": "data_processing",
            "current_performance": "slow"
        }
        response = await client.post(
            f"{BASE_URL}/recommend",
            json=workflow_data
        )
        assert response.status_code == 200
        data = response.json()

        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)

        # Check recommendation structure
        if len(data["recommendations"]) > 0:
            rec = data["recommendations"][0]
            assert "type" in rec
            assert "priority" in rec
            assert "description" in rec


@pytest.mark.asyncio
async def test_get_recommendations_with_metrics():
    """Test recommendations with performance metrics"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        workflow_data = {
            "type": "automated_workflow",
            "metrics": {
                "avg_execution_time": "15m",
                "success_rate": 0.85,
                "error_rate": 0.15
            },
            "bottlenecks": ["data_loading", "validation"]
        }
        response = await client.post(
            f"{BASE_URL}/recommend",
            json=workflow_data
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["recommendations"]) > 0


@pytest.mark.asyncio
async def test_recommendations_for_optimization():
    """Test recommendations focused on optimization"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        workflow_data = {
            "type": "workflow_optimization",
            "current_state": {
                "execution_time": "30m",
                "resource_usage": "high",
                "parallel_steps": 0
            },
            "desired_state": {
                "execution_time": "10m",
                "resource_usage": "medium"
            }
        }
        response = await client.post(
            f"{BASE_URL}/recommend",
            json=workflow_data
        )
        assert response.status_code == 200
        data = response.json()

        # Should have optimization recommendations
        recommendations = data["recommendations"]
        assert any("optimization" in r.get("type", "").lower() for r in recommendations)


# ==================== Integration Tests ====================

@pytest.mark.asyncio
async def test_analyze_and_recommend_workflow():
    """Test complete analyze + recommend workflow"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Step 1: Analyze workflow
        analyze_request = {
            "workflow_id": "integration-test-workflow",
            "workflow_data": {
                "steps": ["collect", "analyze", "report"],
                "complexity": "medium"
            }
        }
        analyze_response = await client.post(
            f"{BASE_URL}/analyze",
            json=analyze_request
        )
        assert analyze_response.status_code == 200
        analysis = analyze_response.json()

        # Step 2: Get recommendations based on analysis
        recommend_request = {
            "type": "workflow_improvement",
            "analysis_results": analysis["analysis"]
        }
        recommend_response = await client.post(
            f"{BASE_URL}/recommend",
            json=recommend_request
        )
        assert recommend_response.status_code == 200
        recommendations = recommend_response.json()

        assert len(recommendations["recommendations"]) > 0


@pytest.mark.asyncio
async def test_multiple_workflow_analyses():
    """Test analyzing multiple workflows"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        workflows = [
            {"id": "wf1", "type": "bia"},
            {"id": "wf2", "type": "risk"},
            {"id": "wf3", "type": "compliance"}
        ]

        for wf in workflows:
            request = {
                "workflow_id": wf["id"],
                "workflow_data": {
                    "type": wf["type"],
                    "steps": ["init", "process", "complete"]
                }
            }
            response = await client.post(
                f"{BASE_URL}/analyze",
                json=request
            )
            assert response.status_code == 200


# ==================== Edge Cases ====================

@pytest.mark.asyncio
async def test_analyze_empty_workflow():
    """Test analyzing workflow with minimal data"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = {
            "workflow_id": "empty-workflow",
            "workflow_data": {}
        }
        response = await client.post(
            f"{BASE_URL}/analyze",
            json=request
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_recommend_empty_data():
    """Test recommendations with empty workflow data"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/recommend",
            json={}
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_analyze_large_workflow():
    """Test analyzing workflow with many steps"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = {
            "workflow_id": "large-workflow",
            "workflow_data": {
                "steps": [f"step_{i}" for i in range(100)],
                "metadata": {f"key_{i}": f"value_{i}" for i in range(50)}
            }
        }
        response = await client.post(
            f"{BASE_URL}/analyze",
            json=request
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_concurrent_analyses():
    """Test concurrent workflow analyses"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        import asyncio

        async def analyze_workflow(index):
            request = {
                "workflow_id": f"concurrent-wf-{index}",
                "workflow_data": {
                    "index": index,
                    "steps": ["step1", "step2"]
                }
            }
            return await client.post(
                f"{BASE_URL}/analyze",
                json=request
            )

        # Analyze 5 workflows concurrently
        tasks = [analyze_workflow(i) for i in range(5)]
        responses = await asyncio.gather(*tasks)

        # All should succeed
        for response in responses:
            assert response.status_code == 200


@pytest.mark.asyncio
async def test_analysis_response_consistency():
    """Test that analysis responses have consistent structure"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = {
            "workflow_id": "consistency-test",
            "workflow_data": {"type": "test"}
        }

        # Analyze same workflow multiple times
        responses = []
        for _ in range(3):
            response = await client.post(
                f"{BASE_URL}/analyze",
                json=request
            )
            assert response.status_code == 200
            responses.append(response.json())

        # All should have same structure
        for data in responses:
            assert "workflow_id" in data
            assert "analysis" in data
            assert "recommendations" in data
            assert "confidence" in data


@pytest.mark.asyncio
async def test_recommendation_priority_levels():
    """Test that recommendations have valid priority levels"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/recommend",
            json={"type": "test"}
        )
        assert response.status_code == 200
        data = response.json()

        valid_priorities = ["low", "medium", "high", "critical"]
        for rec in data["recommendations"]:
            if "priority" in rec:
                assert rec["priority"] in valid_priorities
