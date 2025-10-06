"""
Integration Tests: Tenant Isolation Security
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4


class TestTenantIsolation:
    """Test that tenants cannot access each other's data"""

    @pytest.mark.asyncio
    async def test_users_cannot_see_other_tenants_organizations(self, client: AsyncClient, storage):
        """Test that user A cannot see user B's organizations"""
        # Create Tenant A + User A
        response_a = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"user-a-{uuid4().hex[:8]}@test.com",
                "password": "TestPass123!",
                "full_name": "User A",
                "tenant_name": "Tenant A"
            }
        )
        assert response_a.status_code == 201
        tokens_a = response_a.json()
        token_a = tokens_a["access_token"]

        # Create Tenant B + User B
        response_b = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"user-b-{uuid4().hex[:8]}@test.com",
                "password": "TestPass123!",
                "full_name": "User B",
                "tenant_name": "Tenant B"
            }
        )
        assert response_b.status_code == 201
        tokens_b = response_b.json()
        token_b = tokens_b["access_token"]

        # User A creates organization
        org_a_id = f"org-a-{uuid4().hex[:12]}"
        twin_a_id = f"twin-a-{uuid4().hex[:12]}"

        response = await client.post(
            "/api/v1/organizations/",
            headers={"Authorization": f"Bearer {token_a}"},
            json={
                "id": org_a_id,
                "twin_id": twin_a_id,
                "name": "Organization A",
                "org_type": "corporate",
                "industry": "Technology"
            }
        )
        assert response.status_code == 201

        # User B creates organization
        org_b_id = f"org-b-{uuid4().hex[:12]}"
        twin_b_id = f"twin-b-{uuid4().hex[:12]}"

        response = await client.post(
            "/api/v1/organizations/",
            headers={"Authorization": f"Bearer {token_b}"},
            json={
                "id": org_b_id,
                "twin_id": twin_b_id,
                "name": "Organization B",
                "org_type": "corporate",
                "industry": "Finance"
            }
        )
        assert response.status_code == 201

        # User A lists organizations - should only see org A
        response = await client.get(
            "/api/v1/organizations/",
            headers={"Authorization": f"Bearer {token_a}"}
        )
        assert response.status_code == 200
        data = response.json()

        org_ids = [org["id"] for org in data["items"]]
        assert org_a_id in org_ids
        assert org_b_id not in org_ids  # User A cannot see User B's org

        # User B lists organizations - should only see org B
        response = await client.get(
            "/api/v1/organizations/",
            headers={"Authorization": f"Bearer {token_b}"}
        )
        assert response.status_code == 200
        data = response.json()

        org_ids = [org["id"] for org in data["items"]]
        assert org_b_id in org_ids
        assert org_a_id not in org_ids  # User B cannot see User A's org

    @pytest.mark.asyncio
    async def test_user_cannot_access_other_tenant_organization_by_id(self, client: AsyncClient):
        """Test that user A cannot GET user B's organization by ID"""
        # Create Tenant A + User A
        response_a = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"user-a-{uuid4().hex[:8]}@test.com",
                "password": "TestPass123!",
                "tenant_name": "Tenant A"
            }
        )
        token_a = response_a.json()["access_token"]

        # Create Tenant B + User B
        response_b = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"user-b-{uuid4().hex[:8]}@test.com",
                "password": "TestPass123!",
                "tenant_name": "Tenant B"
            }
        )
        token_b = response_b.json()["access_token"]

        # User B creates organization
        org_b_id = f"org-b-{uuid4().hex[:12]}"
        twin_b_id = f"twin-b-{uuid4().hex[:12]}"

        response = await client.post(
            "/api/v1/organizations/",
            headers={"Authorization": f"Bearer {token_b}"},
            json={
                "id": org_b_id,
                "twin_id": twin_b_id,
                "name": "Secret Organization",
                "org_type": "corporate"
            }
        )
        assert response.status_code == 201

        # User A tries to get User B's organization → 403
        response = await client.get(
            f"/api/v1/organizations/{org_b_id}",
            headers={"Authorization": f"Bearer {token_a}"}
        )
        assert response.status_code == 403
        assert "not authorized" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_user_cannot_update_other_tenant_organization(self, client: AsyncClient):
        """Test that user A cannot UPDATE user B's organization"""
        # Create Tenant A + User A
        response_a = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"user-a-{uuid4().hex[:8]}@test.com",
                "password": "TestPass123!",
                "tenant_name": "Tenant A"
            }
        )
        token_a = response_a.json()["access_token"]

        # Create Tenant B + User B
        response_b = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"user-b-{uuid4().hex[:8]}@test.com",
                "password": "TestPass123!",
                "tenant_name": "Tenant B"
            }
        )
        token_b = response_b.json()["access_token"]

        # User B creates organization
        org_b_id = f"org-b-{uuid4().hex[:12]}"
        twin_b_id = f"twin-b-{uuid4().hex[:12]}"

        response = await client.post(
            "/api/v1/organizations/",
            headers={"Authorization": f"Bearer {token_b}"},
            json={
                "id": org_b_id,
                "twin_id": twin_b_id,
                "name": "Original Name",
                "org_type": "corporate"
            }
        )
        assert response.status_code == 201

        # User A tries to update User B's organization → 403
        response = await client.put(
            f"/api/v1/organizations/{org_b_id}",
            headers={"Authorization": f"Bearer {token_a}"},
            json={"name": "Hacked Name"}
        )
        assert response.status_code == 403
        assert "not authorized" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_user_cannot_delete_other_tenant_organization(self, client: AsyncClient):
        """Test that user A cannot DELETE user B's organization (even as admin)"""
        # Create Tenant A + User A (admin)
        response_a = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"admin-a-{uuid4().hex[:8]}@test.com",
                "password": "TestPass123!",
                "tenant_name": "Tenant A"
            }
        )
        token_a = response_a.json()["access_token"]

        # Create Tenant B + User B (admin)
        response_b = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"admin-b-{uuid4().hex[:8]}@test.com",
                "password": "TestPass123!",
                "tenant_name": "Tenant B"
            }
        )
        token_b = response_b.json()["access_token"]

        # User B creates organization
        org_b_id = f"org-b-{uuid4().hex[:12]}"
        twin_b_id = f"twin-b-{uuid4().hex[:12]}"

        response = await client.post(
            "/api/v1/organizations/",
            headers={"Authorization": f"Bearer {token_b}"},
            json={
                "id": org_b_id,
                "twin_id": twin_b_id,
                "name": "Organization B",
                "org_type": "corporate"
            }
        )
        assert response.status_code == 201

        # User A (admin of Tenant A) tries to delete User B's organization → 403
        response = await client.delete(
            f"/api/v1/organizations/{org_b_id}",
            headers={"Authorization": f"Bearer {token_a}"}
        )
        assert response.status_code == 403
        assert "not authorized" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_simulations_tenant_isolation(self, client: AsyncClient):
        """Test that users cannot see other tenant's simulations"""
        # Create Tenant A + User A
        response_a = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"user-a-{uuid4().hex[:8]}@test.com",
                "password": "TestPass123!",
                "tenant_name": "Tenant A"
            }
        )
        token_a = response_a.json()["access_token"]

        # Create Tenant B + User B
        response_b = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"user-b-{uuid4().hex[:8]}@test.com",
                "password": "TestPass123!",
                "tenant_name": "Tenant B"
            }
        )
        token_b = response_b.json()["access_token"]

        # User A creates organization
        org_a_id = f"org-a-{uuid4().hex[:12]}"
        twin_a_id = f"twin-a-{uuid4().hex[:12]}"

        await client.post(
            "/api/v1/organizations/",
            headers={"Authorization": f"Bearer {token_a}"},
            json={
                "id": org_a_id,
                "twin_id": twin_a_id,
                "name": "Org A",
                "org_type": "corporate"
            }
        )

        # User B creates organization
        org_b_id = f"org-b-{uuid4().hex[:12]}"
        twin_b_id = f"twin-b-{uuid4().hex[:12]}"

        await client.post(
            "/api/v1/organizations/",
            headers={"Authorization": f"Bearer {token_b}"},
            json={
                "id": org_b_id,
                "twin_id": twin_b_id,
                "name": "Org B",
                "org_type": "corporate"
            }
        )

        # User A creates simulation
        sim_a_id = f"sim-a-{uuid4().hex[:12]}"
        response = await client.post(
            "/api/v1/simulations/",
            headers={"Authorization": f"Bearer {token_a}"},
            json={
                "id": sim_a_id,
                "twin_id": twin_a_id,
                "scenario": "earthquake",
                "parameters": {"magnitude": 7.0}
            }
        )
        assert response.status_code == 201

        # User B creates simulation
        sim_b_id = f"sim-b-{uuid4().hex[:12]}"
        response = await client.post(
            "/api/v1/simulations/",
            headers={"Authorization": f"Bearer {token_b}"},
            json={
                "id": sim_b_id,
                "twin_id": twin_b_id,
                "scenario": "fire",
                "parameters": {"intensity": "high"}
            }
        )
        assert response.status_code == 201

        # User A lists simulations - should only see sim A
        response = await client.get(
            "/api/v1/simulations/",
            headers={"Authorization": f"Bearer {token_a}"}
        )
        assert response.status_code == 200
        data = response.json()

        sim_ids = [sim["id"] for sim in data["items"]]
        assert sim_a_id in sim_ids
        assert sim_b_id not in sim_ids

        # User B lists simulations - should only see sim B
        response = await client.get(
            "/api/v1/simulations/",
            headers={"Authorization": f"Bearer {token_b}"}
        )
        assert response.status_code == 200
        data = response.json()

        sim_ids = [sim["id"] for sim in data["items"]]
        assert sim_b_id in sim_ids
        assert sim_a_id not in sim_ids
