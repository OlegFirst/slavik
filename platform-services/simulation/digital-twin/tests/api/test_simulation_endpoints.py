"""
API Tests: Simulation Endpoints
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4


class TestSimulationEndpoints:
    """Test simulation API endpoints"""

    @pytest.mark.asyncio
    async def test_create_simulation_authenticated(
        self, authenticated_client: AsyncClient, test_organization
    ):
        """Test POST /api/v1/simulations/ - authenticated"""
        sim_id = f"sim-{uuid4().hex[:12]}"

        response = await authenticated_client.post(
            "/api/v1/simulations/",
            json={
                "id": sim_id,
                "twin_id": test_organization.twin_id,
                "scenario": "earthquake",
                "parameters": {
                    "magnitude": 7.5,
                    "epicenter": "San Francisco",
                    "duration_seconds": 45
                }
            }
        )

        assert response.status_code == 201
        data = response.json()

        assert data["id"] == sim_id
        assert data["scenario"] == "earthquake"
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_create_simulation_unauthenticated(self, client: AsyncClient):
        """Test POST /api/v1/simulations/ - no auth"""
        response = await client.post(
            "/api/v1/simulations/",
            json={
                "id": "sim-123",
                "twin_id": "twin-123",
                "scenario": "earthquake",
                "parameters": {}
            }
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_list_simulations_authenticated(
        self, authenticated_client: AsyncClient
    ):
        """Test GET /api/v1/simulations/ - authenticated"""
        response = await authenticated_client.get("/api/v1/simulations/")

        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    @pytest.mark.asyncio
    async def test_list_simulations_unauthenticated(self, client: AsyncClient):
        """Test GET /api/v1/simulations/ - no auth"""
        response = await client.get("/api/v1/simulations/")

        assert response.status_code == 403
