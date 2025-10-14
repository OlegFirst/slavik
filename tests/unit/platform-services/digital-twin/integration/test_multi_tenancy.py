"""
Integration Tests: Multi-Tenancy Isolation
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4


class TestMultiTenancy:
    """Test multi-tenant data isolation"""

    @pytest.mark.asyncio
    async def test_tenant_creation_on_register(self, client: AsyncClient, storage):
        """Test that tenant is created automatically on user registration"""
        # Count tenants before
        # (We can't easily count without adding method, so we just verify creation)

        # Register user
        register_data = {
            "email": f"tenant-test-{uuid4().hex[:8]}@example.com",
            "password": "SecurePass123!",
            "full_name": "Tenant Test User",
            "tenant_name": "Test Tenant Co"
        }

        response = await client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 201

        # Login and get user info
        tokens = response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200

        data = response.json()

        # Should have tenant
        assert data["tenant"] is not None
        assert data["tenant"]["name"] == "Test Tenant Co"
        assert data["tenant"]["plan"] == "free"
        assert data["tenant"]["is_trial"] is True

    @pytest.mark.asyncio
    async def test_first_user_is_admin(self, client: AsyncClient):
        """Test that first user in tenant gets admin role"""
        register_data = {
            "email": f"admin-test-{uuid4().hex[:8]}@example.com",
            "password": "SecurePass123!",
            "full_name": "Admin User"
        }

        response = await client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 201

        tokens = response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        response = await client.get("/api/v1/auth/me", headers=headers)
        data = response.json()

        # First user should be admin
        assert data["user"]["role"] == "admin"

    @pytest.mark.asyncio
    async def test_users_from_different_tenants(self, client: AsyncClient):
        """Test that users from different tenants are isolated"""
        # Create Tenant 1 + User 1
        register_data_1 = {
            "email": f"user1-{uuid4().hex[:8]}@example.com",
            "password": "SecurePass123!",
            "full_name": "User 1",
            "tenant_name": "Tenant 1"
        }

        response = await client.post("/api/v1/auth/register", json=register_data_1)
        assert response.status_code == 201
        tokens_1 = response.json()

        # Create Tenant 2 + User 2
        register_data_2 = {
            "email": f"user2-{uuid4().hex[:8]}@example.com",
            "password": "SecurePass123!",
            "full_name": "User 2",
            "tenant_name": "Tenant 2"
        }

        response = await client.post("/api/v1/auth/register", json=register_data_2)
        assert response.status_code == 201
        tokens_2 = response.json()

        # Get user 1 info
        headers_1 = {"Authorization": f"Bearer {tokens_1['access_token']}"}
        response = await client.get("/api/v1/auth/me", headers=headers_1)
        user_1_data = response.json()

        # Get user 2 info
        headers_2 = {"Authorization": f"Bearer {tokens_2['access_token']}"}
        response = await client.get("/api/v1/auth/me", headers=headers_2)
        user_2_data = response.json()

        # Should have different tenants
        assert user_1_data["tenant"]["id"] != user_2_data["tenant"]["id"]
        assert user_1_data["tenant"]["name"] == "Tenant 1"
        assert user_2_data["tenant"]["name"] == "Tenant 2"

        # Should have different user IDs
        assert user_1_data["user"]["id"] != user_2_data["user"]["id"]

    @pytest.mark.asyncio
    async def test_tenant_slug_generation(self, client: AsyncClient):
        """Test that tenant slug is generated from name"""
        register_data = {
            "email": f"slug-test-{uuid4().hex[:8]}@example.com",
            "password": "SecurePass123!",
            "tenant_name": "My Test Company Ltd"
        }

        response = await client.post("/api/v1/auth/register", json=register_data)
        tokens = response.json()

        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        data = response.json()

        # Slug should be lowercase with dashes
        slug = data["tenant"]["slug"]
        assert slug == "my-test-company-ltd"
        assert slug.islower()
        assert " " not in slug

    @pytest.mark.asyncio
    async def test_tenant_subscription_limits(self, client: AsyncClient):
        """Test that tenant has subscription limits"""
        register_data = {
            "email": f"limits-test-{uuid4().hex[:8]}@example.com",
            "password": "SecurePass123!"
        }

        response = await client.post("/api/v1/auth/register", json=register_data)
        tokens = response.json()

        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        data = response.json()

        tenant = data["tenant"]

        # Should have default limits for free plan
        assert "max_users" in tenant
        assert "max_digital_twins" in tenant
        assert "max_simulations_per_month" in tenant

        # Free plan defaults
        assert tenant["max_users"] >= 5
        assert tenant["max_digital_twins"] >= 10
        assert tenant["max_simulations_per_month"] >= 50
