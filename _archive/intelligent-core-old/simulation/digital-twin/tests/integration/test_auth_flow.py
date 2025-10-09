"""
Integration Tests: Authentication Flow
"""

import pytest
from httpx import AsyncClient


class TestAuthenticationFlow:
    """Test complete authentication flows"""

    @pytest.mark.asyncio
    async def test_register_login_flow(self, client: AsyncClient):
        """Test full register → login flow"""
        # 1. Register new user
        register_data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "full_name": "New User",
            "tenant_name": "New Tenant"
        }

        response = await client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 201

        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

        # 2. Login with same credentials
        login_data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!"
        }

        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient):
        """Test registering with duplicate email"""
        register_data = {
            "email": "duplicate@example.com",
            "password": "SecurePass123!",
            "full_name": "User 1"
        }

        # First registration - should succeed
        response = await client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 201

        # Second registration with same email - should fail
        response = await client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """Test login with incorrect password"""
        login_data = {
            "email": test_user.email,
            "password": "WrongPassword123!"
        }

        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent email"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123!"
        }

        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_access_protected_endpoint_without_token(self, client: AsyncClient):
        """Test accessing protected endpoint without token"""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 403  # Forbidden (no credentials)

    @pytest.mark.asyncio
    async def test_access_protected_endpoint_with_token(self, authenticated_client: AsyncClient):
        """Test accessing protected endpoint with valid token"""
        response = await authenticated_client.get("/api/v1/auth/me")
        assert response.status_code == 200

        data = response.json()
        assert "user" in data
        assert "tenant" in data
        assert data["user"]["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_refresh_token_flow(self, client: AsyncClient):
        """Test refresh token flow"""
        # 1. Register to get tokens
        register_data = {
            "email": "refresh@example.com",
            "password": "SecurePass123!",
            "full_name": "Refresh User"
        }

        response = await client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 201

        tokens = response.json()
        refresh_token = tokens["refresh_token"]

        # 2. Use refresh token to get new access token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200

        new_tokens = response.json()
        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens

        # New tokens should be different
        assert new_tokens["access_token"] != tokens["access_token"]

    @pytest.mark.asyncio
    async def test_refresh_with_invalid_token(self, client: AsyncClient):
        """Test refresh with invalid token"""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-token-12345"}
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_with_access_token(self, client: AsyncClient, auth_token):
        """Test refresh with access token (should fail)"""
        # Try to use access token as refresh token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": auth_token}
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_complete_user_lifecycle(self, client: AsyncClient):
        """Test complete user lifecycle: register → login → use API → refresh"""
        # 1. Register
        register_data = {
            "email": "lifecycle@example.com",
            "password": "SecurePass123!",
            "full_name": "Lifecycle User",
            "tenant_name": "Lifecycle Tenant"
        }

        response = await client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 201
        tokens = response.json()

        # 2. Access protected endpoint with access token
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200

        user_data = response.json()
        assert user_data["user"]["email"] == "lifecycle@example.com"
        assert user_data["tenant"]["name"] == "Lifecycle Tenant"

        # 3. Refresh tokens
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]}
        )
        assert response.status_code == 200
        new_tokens = response.json()

        # 4. Access API with new access token
        headers = {"Authorization": f"Bearer {new_tokens['access_token']}"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200

        # 5. Login again
        login_data = {
            "email": "lifecycle@example.com",
            "password": "SecurePass123!"
        }

        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
