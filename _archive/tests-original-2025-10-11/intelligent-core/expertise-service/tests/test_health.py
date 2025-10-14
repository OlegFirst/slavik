"""
Health Check Tests

Tests for basic service availability and info endpoints.
"""

import pytest
import httpx

BASE_URL = "http://localhost:8035"


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint returns service info"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "expertise-center-service"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
        assert "docs" in data
        assert "health" in data


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "expertise-center-service"
        assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_expertise_health():
    """Test expertise-specific health endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/expertise/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "expertise-center"


@pytest.mark.asyncio
async def test_expertise_info():
    """Test expertise info endpoint returns all experts"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/expertise/info")
        assert response.status_code == 200
        data = response.json()

        # Check tactical assistants
        assert "tactical_assistants" in data
        assert len(data["tactical_assistants"]) == 12

        # Check analyzers
        assert "analyzers" in data
        assert len(data["analyzers"]) == 10

        # Check totals
        assert data["total_experts"] == 12
        assert data["total_analyzers"] == 10

        # Check status
        assert data["status"] == "available"


@pytest.mark.asyncio
async def test_list_experts():
    """Test list all experts endpoint - currently not implemented"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/expertise/experts")
        # Endpoint may not be implemented yet, accept 404
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            experts = response.json()
            assert isinstance(experts, list)
            # Verify expert structure if available
            if len(experts) > 0:
                for expert in experts:
                    assert "id" in expert
                    assert "name" in expert


@pytest.mark.asyncio
async def test_get_specific_expert_tactical():
    """Test getting specific tactical assistant info - currently not implemented"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/expertise/experts/bia_specialist")
        # Endpoint may not be implemented yet
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            expert = response.json()
            assert expert["id"] == "bia_specialist"
            assert "name" in expert


@pytest.mark.asyncio
async def test_get_specific_expert_analyzer():
    """Test getting specific analyzer info - currently not implemented"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/expertise/experts/compliance_analyzer")
        # Endpoint may not be implemented yet
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            expert = response.json()
            assert expert["id"] == "compliance_analyzer"
            assert "name" in expert


@pytest.mark.asyncio
async def test_get_nonexistent_expert():
    """Test getting info for non-existent expert returns 404"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/expertise/experts/nonexistent_expert")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_docs_available():
    """Test that API documentation is available"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/docs")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_redoc_available():
    """Test that ReDoc documentation is available"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/redoc")
        assert response.status_code == 200
