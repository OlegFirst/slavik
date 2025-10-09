"""
API Tests: Authentication Endpoints
"""

import pytest
from httpx import AsyncClient


class TestAuthEndpoints:
    """Test authentication API endpoints"""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """Test POST /api/v1/auth/register - success"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@test.com",
                "password": "TestPass123!",
                "full_name": "New User",
                "tenant_name": "New Tenant"
            }
        )

        assert response.status_code == 201
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """Test POST /api/v1/auth/register - duplicate email"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "password": "TestPass123!",
                "full_name": "Duplicate User"
            }
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user):
        """Test POST /api/v1/auth/login - success"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "TestPass123!"  # From fixture
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """Test POST /api/v1/auth/login - wrong password"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "WrongPassword123!"
            }
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_me_success(self, authenticated_client: AsyncClient, test_user):
        """Test GET /api/v1/auth/me - success"""
        response = await authenticated_client.get("/api/v1/auth/me")

        assert response.status_code == 200
        data = response.json()

        assert "user" in data
        assert "tenant" in data
        assert data["user"]["email"] == test_user.email

    @pytest.mark.asyncio
    async def test_get_me_unauthorized(self, client: AsyncClient):
        """Test GET /api/v1/auth/me - no token"""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client: AsyncClient):
        """Test POST /api/v1/auth/refresh - success"""
        # First register to get tokens
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "refresh@test.com",
                "password": "TestPass123!"
            }
        )

        tokens = register_response.json()
        refresh_token = tokens["refresh_token"]

        # Use refresh token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Test POST /api/v1/auth/refresh - invalid token"""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-token"}
        )

        assert response.status_code == 401
