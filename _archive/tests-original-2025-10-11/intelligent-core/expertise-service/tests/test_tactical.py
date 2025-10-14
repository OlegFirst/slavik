"""
Tactical Assistants Tests

Tests for all 12 tactical assistant endpoints:
1. BIA Specialist
2. Risk Analyst
3. Compliance Copilot
4. Incident Advisor
5. Plan Generator
6. Exercise Designer
7. Project Manager
8. Documents Specialist
9. Governance Specialist
10. Learning Specialist
11. Validation Specialist
12. Community Specialist
"""

import pytest
import httpx

BASE_URL = "http://localhost:8035"


# ==================== Test Data ====================

def get_sample_request(query: str, context: dict = None):
    """Helper to create sample request"""
    return {
        "query": query,
        "context": context or {},
        "organization_id": "test-org"
    }


# ==================== BIA Specialist Tests ====================

@pytest.mark.asyncio
async def test_bia_specialist_analyze():
    """Test BIA Specialist analysis endpoint"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = get_sample_request(
            "Analyze impact of email system outage",
            {"industry": "finance", "organization_size": "medium"}
        )
        response = await client.post(
            f"{BASE_URL}/expertise/tactical/bia/analyze",
            json=request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["expert"] == "bia_specialist"
        assert "response" in data
        assert "metadata" in data


# ==================== Risk Analyst Tests ====================

@pytest.mark.asyncio
async def test_risk_analyst_assess():
    """Test Risk Analyst assessment endpoint"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = get_sample_request(
            "Assess ransomware risk for our organization",
            {"industry": "healthcare", "security_maturity": "medium"}
        )
        response = await client.post(
            f"{BASE_URL}/expertise/tactical/risk/assess",
            json=request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["expert"] == "risk_analyst"
        assert "response" in data


# ==================== Compliance Copilot Tests ====================

@pytest.mark.asyncio
async def test_compliance_copilot_check():
    """Test Compliance Copilot check endpoint"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = get_sample_request(
            "Check compliance with ISO 22301 clause 8.2",
            {
                "standard": "iso22301",
                "current_practices": ["BIA conducted", "Plans documented"]
            }
        )
        response = await client.post(
            f"{BASE_URL}/expertise/tactical/compliance/check",
            json=request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["expert"] == "compliance_copilot"
        assert "response" in data


# ==================== Incident Advisor Tests ====================

@pytest.mark.asyncio
async def test_incident_advisor_advise():
    """Test Incident Advisor advice endpoint"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = get_sample_request(
            "Data center fire - immediate actions?",
            {
                "incident_type": "fire",
                "severity": "critical",
                "affected_systems": ["primary_datacenter"]
            }
        )
        response = await client.post(
            f"{BASE_URL}/expertise/tactical/incident/advise",
            json=request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["expert"] == "incident_advisor"
        assert "response" in data


# ==================== Plan Generator Tests ====================

@pytest.mark.asyncio
async def test_plan_generator_generate():
    """Test Plan Generator generation endpoint"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = get_sample_request(
            "Generate IT disaster recovery plan",
            {
                "plan_type": "IT_DR",
                "scope": "all_it_systems",
                "rto": "4_hours"
            }
        )
        response = await client.post(
            f"{BASE_URL}/expertise/tactical/plan/generate",
            json=request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["expert"] == "plan_generator"
        assert "response" in data


# ==================== Exercise Designer Tests ====================

@pytest.mark.asyncio
async def test_exercise_designer_design():
    """Test Exercise Designer design endpoint"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = get_sample_request(
            "Design tabletop exercise for ransomware",
            {
                "exercise_type": "tabletop",
                "scenario": "ransomware",
                "participants": ["IT", "Security", "Management"]
            }
        )
        response = await client.post(
            f"{BASE_URL}/expertise/tactical/exercise/design",
            json=request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["expert"] == "exercise_designer"
        assert "response" in data


# ==================== Project Manager Tests ====================

@pytest.mark.asyncio
async def test_project_manager_manage():
    """Test Project Manager management endpoint"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = get_sample_request(
            "Create BCM implementation roadmap",
            {
                "organization_maturity": "initial",
                "timeline": "12_months",
                "resources": ["1_bcm_manager", "budget_100k"]
            }
        )
        response = await client.post(
            f"{BASE_URL}/expertise/tactical/project/manage",
            json=request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["expert"] == "project_manager"
        assert "response" in data


# ==================== Documents Specialist Tests ====================

@pytest.mark.asyncio
async def test_documents_specialist_create():
    """Test Documents Specialist creation endpoint"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = get_sample_request(
            "Create BCM policy template",
            {
                "document_type": "policy",
                "industry": "finance",
                "regulations": ["ISO22301", "PCI_DSS"]
            }
        )
        response = await client.post(
            f"{BASE_URL}/expertise/tactical/documents/create",
            json=request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["expert"] == "documents_specialist"
        assert "response" in data


# ==================== Governance Specialist Tests ====================

@pytest.mark.asyncio
async def test_governance_specialist_analyze():
    """Test Governance Specialist analysis endpoint"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = get_sample_request(
            "Assess BCM governance structure",
            {
                "organization_type": "corporate",
                "size": "large"
            }
        )
        response = await client.post(
            f"{BASE_URL}/expertise/tactical/governance/analyze",
            json=request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["expert"] == "governance_specialist"
        assert "response" in data


# ==================== Learning Specialist Tests ====================

@pytest.mark.asyncio
async def test_learning_specialist_design():
    """Test Learning Specialist design endpoint"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = get_sample_request(
            "Design awareness training for all staff",
            {
                "audience": "all_staff",
                "delivery": "online",
                "duration": "30_minutes"
            }
        )
        response = await client.post(
            f"{BASE_URL}/expertise/tactical/learning/design",
            json=request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["expert"] == "learning_specialist"
        assert "response" in data


# ==================== Validation Specialist Tests ====================

@pytest.mark.asyncio
async def test_validation_specialist_validate():
    """Test Validation Specialist validation endpoint"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = get_sample_request(
            "Validate our BCM program readiness",
            {
                "validation_scope": "full_program",
                "standards": ["ISO22301"]
            }
        )
        response = await client.post(
            f"{BASE_URL}/expertise/tactical/validation/validate",
            json=request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["expert"] == "validation_specialist"
        assert "response" in data


# ==================== Community Specialist Tests ====================

@pytest.mark.asyncio
async def test_community_specialist_engage():
    """Test Community Specialist engagement endpoint"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = get_sample_request(
            "Build BCM community of practice",
            {
                "organization_size": "large",
                "distributed": True,
                "current_engagement": "low"
            }
        )
        response = await client.post(
            f"{BASE_URL}/expertise/tactical/community/engage",
            json=request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["expert"] == "community_specialist"
        assert "response" in data


# ==================== Generic Query Tests ====================

@pytest.mark.asyncio
async def test_generic_expert_query():
    """Test generic expert query endpoint"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = {
            "expert_type": "bia_specialist",
            "query": "What are critical processes for healthcare?",
            "context": {"industry": "healthcare"}
        }
        response = await client.post(
            f"{BASE_URL}/expertise/query",
            json=request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["expert"] == "bia_specialist"
        assert "response" in data
        assert "confidence" in data
        assert "sources" in data
        assert "metadata" in data


@pytest.mark.asyncio
async def test_invalid_expert_query():
    """Test query with invalid expert type"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = {
            "expert_type": "nonexistent_expert",
            "query": "Test query"
        }
        response = await client.post(
            f"{BASE_URL}/expertise/query",
            json=request
        )
        assert response.status_code in [404, 500]


# ==================== Edge Cases ====================

@pytest.mark.asyncio
async def test_empty_query():
    """Test handling of empty query"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = get_sample_request("")
        response = await client.post(
            f"{BASE_URL}/expertise/tactical/bia/analyze",
            json=request
        )
        # Should still process, might return generic response
        assert response.status_code in [200, 400, 422]


@pytest.mark.asyncio
async def test_missing_context():
    """Test query without context parameter"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = {"query": "Test query"}
        response = await client.post(
            f"{BASE_URL}/expertise/tactical/bia/analyze",
            json=request
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_complex_context():
    """Test query with complex nested context"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = get_sample_request(
            "Complex analysis",
            {
                "industry": "finance",
                "nested": {
                    "level1": {
                        "level2": "deep_value"
                    }
                },
                "list_data": [1, 2, 3]
            }
        )
        response = await client.post(
            f"{BASE_URL}/expertise/tactical/bia/analyze",
            json=request
        )
        assert response.status_code == 200
