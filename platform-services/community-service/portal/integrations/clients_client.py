"""
Clients Service Integration
Handles authentication and user profile retrieval
"""

import os
from typing import Optional
import httpx
from fastapi import HTTPException


class ClientsClient:
    """
    HTTP client for Clients Service (Port 8030)

    Responsibilities:
    - JWT token validation
    - User profile retrieval
    - Tenant access verification
    """

    def __init__(self):
        self.base_url = os.getenv("CLIENTS_SERVICE_URL", "http://localhost:8030")
        self.timeout = 10.0

    async def validate_token(self, token: str) -> dict:
        """
        Validate JWT token and extract user information

        Args:
            token: JWT token (without "Bearer " prefix)

        Returns:
            dict with user_id, tenant_id, role, etc.

        Raises:
            HTTPException 401 if token is invalid
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/clients/auth/validate-token",
                    headers={"Authorization": f"Bearer {token}"}
                )

                if response.status_code == 401:
                    raise HTTPException(status_code=401, detail="Invalid or expired token")

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise HTTPException(status_code=401, detail="Invalid or expired token")
                raise HTTPException(
                    status_code=502,
                    detail=f"Clients service error: {e.response.status_code}"
                )
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=503,
                    detail="Clients service unavailable"
                )

    async def get_user(self, user_id: str, token: str) -> Optional[dict]:
        """
        Get user profile information

        Args:
            user_id: User ID
            token: JWT token for authorization

        Returns:
            User profile dict or None if not found
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/clients/users/{user_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return None
                return None
            except httpx.RequestError:
                return None

    async def get_specialist(self, specialist_id: str, token: str) -> Optional[dict]:
        """
        Get specialist profile information

        Args:
            specialist_id: Specialist ID
            token: JWT token for authorization

        Returns:
            Specialist profile dict or None if not found
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/clients/specialists/{specialist_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return None
                return None
            except httpx.RequestError:
                return None

    async def check_tenant_access(
        self,
        tenant_id: str,
        user_id: str,
        token: str
    ) -> bool:
        """
        Check if user has access to specific tenant

        Args:
            tenant_id: Tenant ID
            user_id: User ID
            token: JWT token

        Returns:
            True if user has access, False otherwise
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/clients/tenants/{tenant_id}/users/{user_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )

                return response.status_code == 200

            except (httpx.HTTPStatusError, httpx.RequestError):
                return False

    async def is_specialist(self, user_id: str, token: str) -> bool:
        """
        Check if user is a specialist

        Args:
            user_id: User ID
            token: JWT token

        Returns:
            True if user is specialist, False otherwise
        """
        specialist = await self.get_specialist(user_id, token)
        return specialist is not None
