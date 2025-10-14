"""
Health Check Tests for Workflow Intelligence Service
"""

import pytest
import httpx

BASE_URL = "http://localhost:8037"


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint returns service info"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "workflow-intelligence"
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
        assert data["service"] == "workflow-intelligence"
        assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_info_endpoint():
    """Test service info endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/info")
        assert response.status_code == 200
        data = response.json()

        assert data["service"] == "workflow-intelligence"
        assert data["version"] == "1.0.0"
        assert data["status"] == "available"

        # Check features
        assert "features" in data
        assert len(data["features"]) > 0
        assert "Case Library Management" in data["features"]
        assert "Workflow Analysis" in data["features"]

        # Check endpoints
        assert "endpoints" in data
        assert "cases" in data["endpoints"]
        assert "analysis" in data["endpoints"]


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
