"""
API Tests: Organization Endpoints
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4


class TestOrganizationEndpoints:
    """Test organization API endpoints"""

    @pytest.mark.asyncio
    async def test_create_organization_authenticated(
        self, authenticated_client: AsyncClient, test_tenant
    ):
        """Test POST /api/v1/organizations/ - authenticated"""
        org_id = f"org-{uuid4().hex[:12]}"
        twin_id = f"twin-{uuid4().hex[:12]}"

        response = await authenticated_client.post(
            "/api/v1/organizations/",
            json={
                "id": org_id,
                "twin_id": twin_id,
                "name": "Test Organization",
                "org_type": "corporate",
                "industry": "Technology"
            }
        )

        assert response.status_code == 201
        data = response.json()

        assert data["id"] == org_id
        assert data["name"] == "Test Organization"

    @pytest.mark.asyncio
    async def test_create_organization_unauthenticated(self, client: AsyncClient):
        """Test POST /api/v1/organizations/ - no auth"""
        response = await client.post(
            "/api/v1/organizations/",
            json={
                "id": "org-123",
                "twin_id": "twin-123",
                "name": "Test Org",
                "org_type": "corporate"
            }
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_organization_authenticated(
        self, authenticated_client: AsyncClient, test_organization
    ):
        """Test GET /api/v1/organizations/{org_id} - authenticated"""
        response = await authenticated_client.get(
            f"/api/v1/organizations/{test_organization.id}"
        )

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == test_organization.id
        assert data["name"] == test_organization.name

    @pytest.mark.asyncio
    async def test_get_organization_unauthenticated(
        self, client: AsyncClient, test_organization
    ):
        """Test GET /api/v1/organizations/{org_id} - no auth"""
        response = await client.get(
            f"/api/v1/organizations/{test_organization.id}"
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_list_organizations_authenticated(
        self, authenticated_client: AsyncClient, test_organization
    ):
        """Test GET /api/v1/organizations/ - authenticated"""
        response = await authenticated_client.get("/api/v1/organizations/")

        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    @pytest.mark.asyncio
    async def test_list_organizations_unauthenticated(self, client: AsyncClient):
        """Test GET /api/v1/organizations/ - no auth"""
        response = await client.get("/api/v1/organizations/")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_organization_authenticated(
        self, authenticated_client: AsyncClient, test_organization
    ):
        """Test PUT /api/v1/organizations/{org_id} - authenticated"""
        response = await authenticated_client.put(
            f"/api/v1/organizations/{test_organization.id}",
            json={"name": "Updated Organization Name"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == test_organization.id
        assert data["name"] == "Updated Organization Name"

    @pytest.mark.asyncio
    async def test_update_organization_unauthenticated(
        self, client: AsyncClient, test_organization
    ):
        """Test PUT /api/v1/organizations/{org_id} - no auth"""
        response = await client.put(
            f"/api/v1/organizations/{test_organization.id}",
            json={"name": "Hacker Name"}
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_organization_admin(
        self, authenticated_client: AsyncClient, test_organization
    ):
        """Test DELETE /api/v1/organizations/{org_id} - admin only"""
        # Test user is admin (from fixture)
        response = await authenticated_client.delete(
            f"/api/v1/organizations/{test_organization.id}"
        )

        # Should succeed (admin user)
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_organization_unauthenticated(
        self, client: AsyncClient, test_organization
    ):
        """Test DELETE /api/v1/organizations/{org_id} - no auth"""
        response = await client.delete(
            f"/api/v1/organizations/{test_organization.id}"
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_organization_404(self, authenticated_client: AsyncClient):
        """Test GET /api/v1/organizations/{org_id} - not found"""
        response = await authenticated_client.get(
            "/api/v1/organizations/nonexistent-org-123"
        )

        assert response.status_code == 404
