"""
Tests for BIA (Business Impact Analysis) API endpoints
"""

import pytest
from httpx import AsyncClient
from datetime import datetime


class TestBIAEndpoints:
    """Test BIA API endpoints"""

    @pytest.mark.asyncio
    async def test_queue_theory_bia_success(self, async_client: AsyncClient, auth_headers: dict):
        """Test Queue Theory BIA endpoint with valid data"""

        # Prepare request data
        request_data = {
            "name": "Order Processing System",
            "arrival_rate": 10.0,      # λ = 10 requests/hour
            "service_rate": 12.0,      # μ = 12 requests/hour
            "num_servers": 2,          # c = 2 servers
            "revenue_per_hour": 50000.0,
            "cost_per_hour": 10000.0,
            "max_wait_hours": 2.0,
            "max_data_loss_hours": 1.0
        }

        # Make request
        response = await async_client.post(
            "/api/v1/bia/queue-theory",
            json=request_data,
            headers=auth_headers
        )

        # Assert response
        assert response.status_code == 201
        data = response.json()

        # Check structure
        assert "id" in data
        assert data["name"] == "Order Processing System"
        assert data["analysis_type"] == "queue_theory"
        assert data["status"] == "completed"

        # Check queue metrics exist
        assert "queue_metrics" in data
        queue_metrics = data["queue_metrics"]
        assert "avg_wait_time_hours" in queue_metrics
        assert "avg_queue_length" in queue_metrics
        assert "utilization" in queue_metrics

        # Check RTO/RPO recommendations
        assert "rto_recommendations" in data
        assert "rpo_recommendations" in data

        # Check financial impact
        assert "financial_impact" in data

    @pytest.mark.asyncio
    async def test_queue_theory_bia_invalid_rates(self, async_client: AsyncClient, auth_headers: dict):
        """Test Queue Theory BIA with invalid arrival/service rates"""

        # Arrival rate > service rate * num_servers (unstable queue)
        request_data = {
            "name": "Unstable System",
            "arrival_rate": 30.0,      # λ = 30 (too high)
            "service_rate": 10.0,      # μ = 10
            "num_servers": 2,          # c = 2 → μc = 20 < λ (UNSTABLE!)
            "revenue_per_hour": 50000.0,
            "cost_per_hour": 10000.0,
            "max_wait_hours": 2.0,
            "max_data_loss_hours": 1.0
        }

        response = await async_client.post(
            "/api/v1/bia/queue-theory",
            json=request_data,
            headers=auth_headers
        )

        # Should still succeed but return warning/high metrics
        assert response.status_code == 201
        data = response.json()

        # Check that utilization is high (>= 1.0 means unstable)
        if "queue_metrics" in data:
            utilization = data["queue_metrics"].get("utilization", 0)
            # Unstable system should have very high or infinite wait times
            assert utilization >= 0.9  # Very high utilization

    @pytest.mark.asyncio
    async def test_queue_theory_bia_zero_arrival_rate(self, async_client: AsyncClient, auth_headers: dict):
        """Test Queue Theory BIA with zero arrival rate (invalid)"""

        request_data = {
            "name": "Zero Arrival System",
            "arrival_rate": 0.0,       # Invalid!
            "service_rate": 10.0,
            "num_servers": 2,
            "revenue_per_hour": 50000.0,
            "cost_per_hour": 10000.0,
            "max_wait_hours": 2.0,
            "max_data_loss_hours": 1.0
        }

        response = await async_client.post(
            "/api/v1/bia/queue-theory",
            json=request_data,
            headers=auth_headers
        )

        # Should fail validation (arrival_rate must be > 0)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_queue_theory_bia_negative_values(self, async_client: AsyncClient, auth_headers: dict):
        """Test Queue Theory BIA with negative values (invalid)"""

        request_data = {
            "name": "Negative Values System",
            "arrival_rate": 10.0,
            "service_rate": -5.0,      # Invalid - negative!
            "num_servers": 2,
            "revenue_per_hour": 50000.0,
            "cost_per_hour": 10000.0,
            "max_wait_hours": 2.0,
            "max_data_loss_hours": 1.0
        }

        response = await async_client.post(
            "/api/v1/bia/queue-theory",
            json=request_data,
            headers=auth_headers
        )

        # Should fail validation
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_queue_theory_bia_unauthorized(self, async_client: AsyncClient):
        """Test Queue Theory BIA without authentication"""

        request_data = {
            "name": "Test System",
            "arrival_rate": 10.0,
            "service_rate": 12.0,
            "num_servers": 2,
            "revenue_per_hour": 50000.0,
            "cost_per_hour": 10000.0,
            "max_wait_hours": 2.0,
            "max_data_loss_hours": 1.0
        }

        response = await async_client.post(
            "/api/v1/bia/queue-theory",
            json=request_data
            # No auth headers!
        )

        # Should require authentication
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_queue_theory_bia_multiple_servers(self, async_client: AsyncClient, auth_headers: dict):
        """Test Queue Theory BIA with varying number of servers"""

        base_request = {
            "name": "Multi-Server System",
            "arrival_rate": 20.0,
            "service_rate": 10.0,
            "revenue_per_hour": 50000.0,
            "cost_per_hour": 10000.0,
            "max_wait_hours": 2.0,
            "max_data_loss_hours": 1.0
        }

        # Test with 1, 3, 5 servers
        for num_servers in [1, 3, 5]:
            request_data = {**base_request, "num_servers": num_servers}

            response = await async_client.post(
                "/api/v1/bia/queue-theory",
                json=request_data,
                headers=auth_headers
            )

            if num_servers == 1:
                # λ=20, μ=10, c=1 → ρ=2 (UNSTABLE - should work but warn)
                assert response.status_code == 201
            else:
                # More servers = stable
                assert response.status_code == 201
                data = response.json()
                assert data["status"] == "completed"

    @pytest.mark.asyncio
    async def test_get_bia_analysis(self, async_client: AsyncClient, auth_headers: dict):
        """Test retrieving BIA analysis by ID"""

        # First create a BIA
        create_request = {
            "name": "Test BIA",
            "arrival_rate": 10.0,
            "service_rate": 12.0,
            "num_servers": 2,
            "revenue_per_hour": 50000.0,
            "cost_per_hour": 10000.0,
            "max_wait_hours": 2.0,
            "max_data_loss_hours": 1.0
        }

        create_response = await async_client.post(
            "/api/v1/bia/queue-theory",
            json=create_request,
            headers=auth_headers
        )
        assert create_response.status_code == 201
        bia_id = create_response.json()["id"]

        # Then retrieve it
        get_response = await async_client.get(
            f"/api/v1/bia/{bia_id}",
            headers=auth_headers
        )

        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == bia_id
        assert data["name"] == "Test BIA"

    @pytest.mark.asyncio
    async def test_list_bia_analyses(self, async_client: AsyncClient, auth_headers: dict):
        """Test listing BIA analyses for organization"""

        # Create test organization first
        org_response = await async_client.post(
            "/api/v1/organizations/",
            json={
                "id": "test-org-bia",
                "twin_id": "twin-bia-001",
                "name": "BIA Test Organization",
                "org_type": "corporate",
                "industry": "Technology"
            },
            headers=auth_headers
        )

        # Create BIA linked to org
        bia_request = {
            "name": "Org BIA Test",
            "arrival_rate": 10.0,
            "service_rate": 12.0,
            "num_servers": 2,
            "revenue_per_hour": 50000.0,
            "cost_per_hour": 10000.0,
            "max_wait_hours": 2.0,
            "max_data_loss_hours": 1.0,
            "organization_id": "test-org-bia"  # Link to org
        }

        await async_client.post(
            "/api/v1/bia/queue-theory",
            json=bia_request,
            headers=auth_headers
        )

        # List BIA analyses
        list_response = await async_client.get(
            "/api/v1/bia/",
            headers=auth_headers
        )

        assert list_response.status_code == 200
        data = list_response.json()
        assert "items" in data
        assert len(data["items"]) > 0
