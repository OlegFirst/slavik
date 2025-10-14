"""
Strategic Analyzers Tests

Tests for all 10 analyzer endpoints:
1. Compliance Analyzer
2. Risk Analyzer
3. Governance Analyzer
4. Lifecycle Analyzer
5. Learning Analyzer
6. Performance Analyzer
7. Emergency Analyzer
8. Impact Analyzer
9. Plan Analyzer
10. Scenario Analyzer
"""

import pytest
import httpx

BASE_URL = "http://localhost:8035"


def get_sample_request(query: str, context: dict = None):
    """Helper to create sample request"""
    return {
        "query": query,
        "context": context or {},
        "organization_id": "test-org"
    }


# ==================== Compliance Analyzer Tests ====================

@pytest.mark.asyncio
async def test_compliance_analyzer():
    """Test Compliance Analyzer endpoint"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = get_sample_request(
            "Analyze ISO 22301 compliance status",
            {"standard": "iso22301", "scope": "full"}
        )
        response = await client.post(
            f"{BASE_URL}/expertise/analyzers/compliance/analyze",
            json=request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["analyzer"] == "compliance_analyzer"
        assert "response" in data
        assert "metadata" in data


# ==================== Risk Analyzer Tests ====================

@pytest.mark.asyncio
async def test_risk_analyzer():
    """Test Risk Analyzer endpoint"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = get_sample_request(
            "Analyze enterprise risk landscape",
            {"scope": "enterprise", "timeframe": "annual"}
        )
        response = await client.post(
            f"{BASE_URL}/expertise/analyzers/risk/analyze",
            json=request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["analyzer"] == "risk_analyzer"
        assert "response" in data


# ==================== Governance Analyzer Tests ====================

@pytest.mark.asyncio
async def test_governance_analyzer():
    """Test Governance Analyzer endpoint"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = get_sample_request(
            "Analyze BCM governance effectiveness",
            {"organization_type": "corporate", "maturity": "developing"}
        )
        response = await client.post(
            f"{BASE_URL}/expertise/analyzers/governance/analyze",
            json=request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["analyzer"] == "governance_analyzer"
        assert "response" in data


# ==================== Lifecycle Analyzer Tests ====================

@pytest.mark.asyncio
async def test_lifecycle_analyzer():
    """Test Lifecycle Analyzer endpoint"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = get_sample_request(
            "Analyze BCM lifecycle stage",
            {"current_activities": ["BIA", "Planning", "Testing"]}
        )
        response = await client.post(
            f"{BASE_URL}/expertise/analyzers/lifecycle/analyze",
            json=request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["analyzer"] == "lifecycle_analyzer"
        assert "response" in data


# ==================== Learning Analyzer Tests ====================

@pytest.mark.asyncio
async def test_learning_analyzer():
    """Test Learning Analyzer endpoint"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = get_sample_request(
            "Analyze training effectiveness",
            {
                "training_programs": ["awareness", "response_team"],
                "metrics": {"completion_rate": 0.85}
            }
        )
        response = await client.post(
            f"{BASE_URL}/expertise/analyzers/learning/analyze",
            json=request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["analyzer"] == "learning_analyzer"
        assert "response" in data


# ==================== Performance Analyzer Tests ====================

@pytest.mark.asyncio
async def test_performance_analyzer():
    """Test Performance Analyzer endpoint"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = get_sample_request(
            "Analyze BCM program performance",
            {
                "kpis": {
                    "exercise_frequency": "quarterly",
                    "incident_response_time": "2h"
                }
            }
        )
        response = await client.post(
            f"{BASE_URL}/expertise/analyzers/performance/analyze",
            json=request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["analyzer"] == "performance_analyzer"
        assert "response" in data


# ==================== Emergency Analyzer Tests ====================

@pytest.mark.asyncio
async def test_emergency_analyzer():
    """Test Emergency Analyzer endpoint"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = get_sample_request(
            "Analyze emergency response capability",
            {
                "response_teams": ["IT", "Operations", "Communications"],
                "recent_incidents": 3
            }
        )
        response = await client.post(
            f"{BASE_URL}/expertise/analyzers/emergency/analyze",
            json=request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["analyzer"] == "emergency_analyzer"
        assert "response" in data


# ==================== Impact Analyzer Tests ====================

@pytest.mark.asyncio
async def test_impact_analyzer():
    """Test Impact Analyzer endpoint"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = get_sample_request(
            "Analyze business impact of disruption",
            {
                "disruption_type": "system_outage",
                "affected_processes": ["order_processing", "customer_service"]
            }
        )
        response = await client.post(
            f"{BASE_URL}/expertise/analyzers/impact/analyze",
            json=request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["analyzer"] == "impact_analyzer"
        assert "response" in data


# ==================== Plan Analyzer Tests ====================

@pytest.mark.asyncio
async def test_plan_analyzer():
    """Test Plan Analyzer endpoint"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = get_sample_request(
            "Analyze BCM plan quality",
            {
                "plan_type": "IT_DR",
                "last_update": "2024-01-15",
                "test_results": "successful"
            }
        )
        response = await client.post(
            f"{BASE_URL}/expertise/analyzers/plan/analyze",
            json=request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["analyzer"] == "plan_analyzer"
        assert "response" in data


# ==================== Scenario Analyzer Tests ====================

@pytest.mark.asyncio
async def test_scenario_analyzer():
    """Test Scenario Analyzer endpoint"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = get_sample_request(
            "Analyze scenario plausibility",
            {
                "scenario": "cyber_attack",
                "parameters": {
                    "severity": "high",
                    "duration": "extended"
                }
            }
        )
        response = await client.post(
            f"{BASE_URL}/expertise/analyzers/scenario/analyze",
            json=request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["analyzer"] == "scenario_analyzer"
        assert "response" in data


# ==================== Cross-Analyzer Tests ====================

@pytest.mark.asyncio
async def test_multiple_analyzers_sequential():
    """Test calling multiple analyzers sequentially"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        # First analyzer
        request1 = get_sample_request("Analyze compliance", {"standard": "iso22301"})
        response1 = await client.post(
            f"{BASE_URL}/expertise/analyzers/compliance/analyze",
            json=request1
        )
        assert response1.status_code == 200

        # Second analyzer
        request2 = get_sample_request("Analyze risks", {"scope": "enterprise"})
        response2 = await client.post(
            f"{BASE_URL}/expertise/analyzers/risk/analyze",
            json=request2
        )
        assert response2.status_code == 200

        # Responses should be independent
        data1 = response1.json()
        data2 = response2.json()
        assert data1["analyzer"] != data2["analyzer"]


# ==================== Edge Cases ====================

@pytest.mark.asyncio
async def test_analyzer_with_empty_context():
    """Test analyzer with empty context"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = {"query": "Analyze compliance"}
        response = await client.post(
            f"{BASE_URL}/expertise/analyzers/compliance/analyze",
            json=request
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_analyzer_with_complex_data():
    """Test analyzer with complex nested data"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = get_sample_request(
            "Deep analysis",
            {
                "metrics": {
                    "quantitative": {
                        "rto": "4h",
                        "rpo": "1h"
                    },
                    "qualitative": {
                        "maturity": "developing"
                    }
                },
                "historical_data": [
                    {"date": "2024-01", "value": 85},
                    {"date": "2024-02", "value": 90}
                ]
            }
        )
        response = await client.post(
            f"{BASE_URL}/expertise/analyzers/performance/analyze",
            json=request
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_analyzer_response_structure():
    """Test that analyzer response has consistent structure"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = get_sample_request("Test analysis")
        response = await client.post(
            f"{BASE_URL}/expertise/analyzers/compliance/analyze",
            json=request
        )
        assert response.status_code == 200
        data = response.json()

        # Verify required fields
        assert "analyzer" in data
        assert "response" in data
        assert "confidence" in data
        assert "sources" in data
        assert "metadata" in data

        # Verify types
        assert isinstance(data["analyzer"], str)
        assert isinstance(data["response"], str)
        assert isinstance(data["confidence"], (int, float))
        assert isinstance(data["sources"], list)
        assert isinstance(data["metadata"], dict)
