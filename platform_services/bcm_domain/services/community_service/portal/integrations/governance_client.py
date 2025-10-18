"""
Governance Service HTTP Client
Provides integration with Governance Service API
"""

import httpx
import os
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class GovernanceClient:
    """
    HTTP client for Governance Service API

    Base URL: http://localhost:8022/api/v1/governance

    Methods:
    - get_policies() - List policies (for article references)
    - get_policy() - Get policy details
    - get_person_roles() - Get person roles (for forum moderation)
    - get_roles() - List all roles
    - get_person_competencies() - Get competence records
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("GOVERNANCE_SERVICE_URL", "http://localhost:8022")
        self.api_base = f"{self.base_url}/api/v1/governance"
        self.timeout = 10.0

    async def get_policies(
        self,
        token: str,
        policy_type: Optional[str] = None,
        iso_clause: Optional[str] = None,
        status: str = "published",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List policies

        Endpoint: GET /policies

        Args:
            token: JWT token
            policy_type: Filter by type (policy/procedure/guideline)
            iso_clause: Filter by ISO 22301 clause
            status: Filter by status (draft/published/archived)
            limit: Max results

        Returns:
            List of policies

        Example:
        [
            {
                "id": 1,
                "policy_code": "POL-001",
                "title": "Business Continuity Policy",
                "policy_type": "policy",
                "iso_clause": "5.2",
                "status": "published",
                "effective_date": "2025-01-01"
            }
        ]
        """
        try:
            params = {"limit": limit}
            if policy_type:
                params["policy_type"] = policy_type
            if iso_clause:
                params["iso_clause"] = iso_clause
            if status:
                params["status"] = status

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_base}/policies",
                    params=params,
                    headers={"Authorization": f"Bearer {token}"}
                )

                response.raise_for_status()
                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Failed to get policies: {e}")
            return []

    async def get_policy(
        self,
        policy_id: int,
        token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get policy details

        Endpoint: GET /policies/{policy_id}

        Args:
            policy_id: Policy ID
            token: JWT token

        Returns:
            Policy details or None if not found
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_base}/policies/{policy_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Failed to get policy {policy_id}: {e}")
            return None

    async def get_person_roles(
        self,
        person_id: str,
        token: str
    ) -> List[Dict[str, Any]]:
        """
        Get roles assigned to a person

        Note: Governance API doesn't have a dedicated endpoint for this yet.
        We query all roles and filter by assigned persons.

        Args:
            person_id: Person ID
            token: JWT token

        Returns:
            List of role assignments

        Example:
        [
            {
                "role_id": 1,
                "role_code": "bcm_manager",
                "role_name": "BCM Manager",
                "assigned_date": "2025-01-01",
                "competencies": ["planning", "risk_assessment"]
            }
        ]
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Get all roles
                response = await client.get(
                    f"{self.api_base}/roles",
                    headers={"Authorization": f"Bearer {token}"}
                )

                if response.status_code == 404:
                    return []

                response.raise_for_status()
                all_roles = response.json()

                # Filter roles where person is assigned
                person_roles = []
                for role in all_roles:
                    assigned_persons = role.get("assigned_to", [])
                    if person_id in assigned_persons:
                        person_roles.append({
                            "role_id": role.get("id"),
                            "role_code": role.get("role_code"),
                            "role_name": role.get("role_name"),
                            "competencies": role.get("required_competencies", []),
                            "assigned_date": role.get("created_at")  # Approximate
                        })

                return person_roles

        except Exception as e:
            logger.error(f"Failed to get roles for {person_id}: {e}")
            return []

    async def get_roles(
        self,
        token: str,
        role_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all roles

        Endpoint: GET /roles

        Args:
            token: JWT token
            role_type: Filter by type

        Returns:
            List of roles
        """
        try:
            params = {}
            if role_type:
                params["role_type"] = role_type

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_base}/roles",
                    params=params,
                    headers={"Authorization": f"Bearer {token}"}
                )

                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Failed to get roles: {e}")
            return []

    async def get_person_competencies(
        self,
        person_id: str,
        token: str
    ) -> List[Dict[str, Any]]:
        """
        Get competence records for a person

        Endpoint: GET /competence?person_id={person_id}

        Args:
            person_id: Person ID
            token: JWT token

        Returns:
            List of competence records

        Example:
        [
            {
                "competency_area": "Risk Assessment",
                "proficiency_level": "advanced",
                "assessed_date": "2025-09-01",
                "assessed_by": "manager_001"
            }
        ]
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_base}/competence",
                    params={"person_id": person_id},
                    headers={"Authorization": f"Bearer {token}"}
                )

                if response.status_code == 404:
                    return []

                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Failed to get competencies for {person_id}: {e}")
            return []

    async def check_person_has_role(
        self,
        person_id: str,
        role_code: str,
        token: str
    ) -> bool:
        """
        Check if person has a specific role

        Args:
            person_id: Person ID
            role_code: Role code (e.g., "bcm_manager", "moderator")
            token: JWT token

        Returns:
            True if person has role, False otherwise
        """
        try:
            roles = await self.get_person_roles(person_id, token)
            return any(r.get("role_code") == role_code for r in roles)

        except Exception as e:
            logger.error(f"Failed to check role for {person_id}: {e}")
            return False

    async def get_policies_by_iso_clause(
        self,
        iso_clause: str,
        token: str
    ) -> List[Dict[str, Any]]:
        """
        Get policies related to specific ISO 22301 clause

        Useful for linking knowledge articles to policies

        Args:
            iso_clause: ISO clause (e.g., "5.2", "7.1")
            token: JWT token

        Returns:
            List of policies
        """
        return await self.get_policies(
            token=token,
            iso_clause=iso_clause,
            status="published"
        )

    async def get_resources(
        self,
        token: str,
        resource_type: Optional[str] = None,
        status: Optional[str] = "active",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List resources

        Endpoint: GET /resources

        Args:
            token: JWT token
            resource_type: Filter by type (person/facility/technology)
            status: Filter by status
            limit: Max results

        Returns:
            List of resources
        """
        try:
            params = {"limit": limit}
            if resource_type:
                params["resource_type"] = resource_type
            if status:
                params["status"] = status

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_base}/resources",
                    params=params,
                    headers={"Authorization": f"Bearer {token}"}
                )

                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Failed to get resources: {e}")
            return []


# Singleton instance
_governance_client: Optional[GovernanceClient] = None


def get_governance_client() -> GovernanceClient:
    """Get singleton Governance client instance"""
    global _governance_client
    if _governance_client is None:
        _governance_client = GovernanceClient()
    return _governance_client
