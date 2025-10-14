"""
Case Library Tests

Tests for case library management endpoints.
"""

import pytest
import httpx
import uuid

BASE_URL = "http://localhost:8037"


# ==================== Add Case Tests ====================

@pytest.mark.asyncio
async def test_add_case_basic():
    """Test adding a basic case to library"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = {
            "case_data": {
                "title": "Test Case",
                "description": "Test case description",
                "scenario": "test_scenario"
            },
            "module": "bia",
            "source": "community"
        }
        response = await client.post(
            f"{BASE_URL}/cases/add",
            json=request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "case_id" in data
        assert data["message"]


@pytest.mark.asyncio
async def test_add_case_with_metadata():
    """Test adding case with metadata"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = {
            "case_data": {
                "title": "Case with Metadata",
                "details": "Detailed information"
            },
            "module": "risk",
            "source": "expert",
            "metadata": {
                "industry": "finance",
                "severity": "high",
                "tags": ["critical", "regulatory"]
            }
        }
        response = await client.post(
            f"{BASE_URL}/cases/add",
            json=request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


@pytest.mark.asyncio
async def test_add_case_different_modules():
    """Test adding cases for different modules"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        modules = ["bia", "risk", "compliance", "incident", "planning"]

        for module in modules:
            request = {
                "case_data": {
                    "title": f"{module.upper()} Test Case",
                    "content": f"Content for {module}"
                },
                "module": module,
                "source": "community"
            }
            response = await client.post(
                f"{BASE_URL}/cases/add",
                json=request
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"


# ==================== Get Case Tests ====================

@pytest.mark.asyncio
async def test_get_case_by_id():
    """Test retrieving case by ID"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        case_id = "test-case-123"
        response = await client.get(f"{BASE_URL}/cases/{case_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["case_id"] == case_id
        assert "data" in data


@pytest.mark.asyncio
async def test_get_case_different_ids():
    """Test getting cases with different IDs"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        test_ids = [
            str(uuid.uuid4()),
            "case-001",
            "test_case"
        ]

        for case_id in test_ids:
            response = await client.get(f"{BASE_URL}/cases/{case_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["case_id"] == case_id


# ==================== Search Cases Tests ====================

@pytest.mark.asyncio
async def test_search_cases_empty():
    """Test searching with empty query"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        query = {}
        response = await client.post(
            f"{BASE_URL}/cases/search",
            json=query
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total" in data
        assert isinstance(data["results"], list)


@pytest.mark.asyncio
async def test_search_cases_with_filters():
    """Test searching cases with filters"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        query = {
            "module": "bia",
            "industry": "finance",
            "tags": ["critical"]
        }
        response = await client.post(
            f"{BASE_URL}/cases/search",
            json=query
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data


@pytest.mark.asyncio
async def test_search_cases_with_text():
    """Test text-based case search"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        query = {
            "text": "business impact analysis",
            "limit": 10
        }
        response = await client.post(
            f"{BASE_URL}/cases/search",
            json=query
        )
        assert response.status_code == 200


# ==================== Bulk Operations Tests ====================

@pytest.mark.asyncio
async def test_bulk_operations_empty():
    """Test bulk operations with empty list"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        operations = []
        response = await client.post(
            f"{BASE_URL}/cases/bulk",
            json=operations
        )
        assert response.status_code == 200
        data = response.json()
        assert data["processed"] == 0


@pytest.mark.asyncio
async def test_bulk_operations_multiple():
    """Test bulk operations with multiple items"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        operations = [
            {
                "action": "add",
                "case_data": {"title": "Case 1"},
                "module": "bia"
            },
            {
                "action": "add",
                "case_data": {"title": "Case 2"},
                "module": "risk"
            },
            {
                "action": "update",
                "case_id": "case-123",
                "updates": {"status": "active"}
            }
        ]
        response = await client.post(
            f"{BASE_URL}/cases/bulk",
            json=operations
        )
        assert response.status_code == 200
        data = response.json()
        assert data["processed"] == 3
        assert data["status"] == "success"


# ==================== Edge Cases ====================

@pytest.mark.asyncio
async def test_add_case_minimal_data():
    """Test adding case with minimal required data"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = {
            "case_data": {},
            "module": "test"
        }
        response = await client.post(
            f"{BASE_URL}/cases/add",
            json=request
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_add_case_large_data():
    """Test adding case with large data payload"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = {
            "case_data": {
                "title": "Large Case",
                "content": "x" * 10000,  # Large content
                "details": {f"field_{i}": f"value_{i}" for i in range(100)}
            },
            "module": "test",
            "metadata": {
                "large_array": list(range(1000))
            }
        }
        response = await client.post(
            f"{BASE_URL}/cases/add",
            json=request
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_case_data_types():
    """Test cases with various data types"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        request = {
            "case_data": {
                "string": "text",
                "number": 42,
                "float": 3.14,
                "boolean": True,
                "null": None,
                "array": [1, 2, 3],
                "object": {"nested": "value"}
            },
            "module": "test"
        }
        response = await client.post(
            f"{BASE_URL}/cases/add",
            json=request
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_concurrent_case_additions():
    """Test concurrent case additions"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        import asyncio

        async def add_case(index):
            request = {
                "case_data": {
                    "title": f"Concurrent Case {index}"
                },
                "module": "test"
            }
            return await client.post(
                f"{BASE_URL}/cases/add",
                json=request
            )

        # Add 5 cases concurrently
        tasks = [add_case(i) for i in range(5)]
        responses = await asyncio.gather(*tasks)

        # All should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
