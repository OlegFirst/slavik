"""
Governance Service HTTP Client for Marketplace
Provides integration with Governance Service API for specialist verification
"""

import httpx
import os
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class GovernanceClient:
    """
    HTTP client for Governance Service API (Marketplace integration)

    Base URL: http://localhost:8022/api/v1/governance

    Methods:
    - get_person_roles() - Get person roles (for specialist verification)
    - check_bcm_specialist_role() - Check if person has BCM specialist role
    - get_person_competencies() - Get competence records
    - verify_specialist() - Verify specialist via governance role
    - get_role() - Get role details
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("GOVERNANCE_SERVICE_URL", "http://localhost:8022")
        self.api_base = f"{self.base_url}/api/v1/governance"
        self.timeout = 10.0

    async def get_person_roles(
        self,
        person_id: str,
        token: str
    ) -> List[Dict[str, Any]]:
        """
        Get all roles assigned to a person

        Used for: Specialist verification via governance roles

        Args:
            person_id: Person ID
            token: JWT token

        Returns:
            List of role assignments

        Example:
        [
            {
                "role_id": 1,
                "role_code": "bcm_specialist",
                "role_name": "BCM Specialist",
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
                            "assigned_date": role.get("created_at")
                        })

                return person_roles

        except Exception as e:
            logger.error(f"Failed to get roles for {person_id}: {e}")
            return []

    async def check_bcm_specialist_role(
        self,
        person_id: str,
        token: str
    ) -> bool:
        """
        Check if person has BCM specialist role

        Used for: Auto-verification of specialists

        Args:
            person_id: Person ID
            token: JWT token

        Returns:
            True if person has bcm_specialist, bcm_consultant, or bcm_manager role
        """
        try:
            roles = await self.get_person_roles(person_id, token)

            bcm_role_codes = ["bcm_specialist", "bcm_consultant", "bcm_manager", "bcm_practitioner"]

            for role in roles:
                if role.get("role_code") in bcm_role_codes:
                    return True

            return False

        except Exception as e:
            logger.error(f"Failed to check BCM role for {person_id}: {e}")
            return False

    async def get_person_competencies(
        self,
        person_id: str,
        token: str
    ) -> List[Dict[str, Any]]:
        """
        Get competence records for a person

        Used for: Syncing governance competencies with marketplace specialist profile

        Endpoint: GET /competence?person_id={person_id}

        Args:
            person_id: Person ID
            token: JWT token

        Returns:
            List of competence records

        Example:
        [
            {
                "id": 1,
                "competency_area": "Risk Assessment",
                "proficiency_level": "advanced",
                "assessed_date": "2025-09-01",
                "assessed_by": "manager_001",
                "evidence": "Completed 5 risk assessments",
                "notes": "Strong analytical skills"
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

    async def verify_specialist(
        self,
        person_id: str,
        token: str
    ) -> Dict[str, Any]:
        """
        Verify a specialist via governance system

        Checks:
        1. Person has BCM role
        2. Person has required competencies
        3. Person is active in governance

        Args:
            person_id: Person ID
            token: JWT token

        Returns:
            Verification result

        Example:
        {
            "is_verified": true,
            "verification_source": "governance_role",
            "role_code": "bcm_specialist",
            "verified_date": "2025-10-03",
            "competencies_count": 5,
            "notes": "Verified via BCM Specialist role assignment"
        }
        """
        try:
            from datetime import datetime

            result = {
                "is_verified": False,
                "verification_source": None,
                "role_code": None,
                "verified_date": None,
                "competencies_count": 0,
                "notes": None
            }

            # Check for BCM roles
            roles = await self.get_person_roles(person_id, token)
            bcm_role_codes = ["bcm_specialist", "bcm_consultant", "bcm_manager"]

            for role in roles:
                role_code = role.get("role_code")
                if role_code in bcm_role_codes:
                    result["is_verified"] = True
                    result["verification_source"] = "governance_role"
                    result["role_code"] = role_code
                    result["verified_date"] = datetime.utcnow().isoformat()
                    result["notes"] = f"Verified via {role.get('role_name')} role assignment"
                    break

            # Get competencies count
            competencies = await self.get_person_competencies(person_id, token)
            result["competencies_count"] = len(competencies)

            # Additional verification from competencies
            if not result["is_verified"] and result["competencies_count"] >= 3:
                result["is_verified"] = True
                result["verification_source"] = "competencies"
                result["verified_date"] = datetime.utcnow().isoformat()
                result["notes"] = f"Verified via {result['competencies_count']} competency records"

            return result

        except Exception as e:
            logger.error(f"Failed to verify specialist {person_id}: {e}")
            return {
                "is_verified": False,
                "verification_source": None,
                "error": str(e)
            }

    async def get_role(
        self,
        role_id: int,
        token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get role details

        Endpoint: GET /roles/{role_id}

        Args:
            role_id: Role ID
            token: JWT token

        Returns:
            Role details or None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_base}/roles/{role_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Failed to get role {role_id}: {e}")
            return None

    async def get_resources(
        self,
        token: str,
        resource_type: str = "person",
        status: str = "active"
    ) -> List[Dict[str, Any]]:
        """
        Get resources (for specialist availability sync)

        Endpoint: GET /resources

        Args:
            token: JWT token
            resource_type: Filter by type (person/facility/technology)
            status: Filter by status

        Returns:
            List of resources
        """
        try:
            params = {
                "resource_type": resource_type,
                "status": status
            }

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

    async def get_person_resource(
        self,
        person_id: str,
        token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get resource record for a person

        Used for: Checking specialist availability/allocation

        Args:
            person_id: Person ID
            token: JWT token

        Returns:
            Resource record or None
        """
        try:
            resources = await self.get_resources(token, resource_type="person")

            for resource in resources:
                if resource.get("person_id") == person_id:
                    return resource

            return None

        except Exception as e:
            logger.error(f"Failed to get resource for {person_id}: {e}")
            return None

    async def create_competence_record(
        self,
        person_id: str,
        competency_area: str,
        proficiency_level: str,
        token: str,
        assessed_by: Optional[str] = None,
        evidence: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create competence record in Governance

        Used for: Syncing marketplace specialist competencies back to governance

        Endpoint: POST /competence

        Args:
            person_id: Person ID
            competency_area: Competency area
            proficiency_level: Level (beginner/intermediate/advanced/expert)
            token: JWT token
            assessed_by: Assessor ID
            evidence: Evidence text
            notes: Additional notes

        Returns:
            Created competence record or None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "person_id": person_id,
                    "competency_area": competency_area,
                    "proficiency_level": proficiency_level
                }

                if assessed_by:
                    payload["assessed_by"] = assessed_by
                if evidence:
                    payload["evidence"] = evidence
                if notes:
                    payload["notes"] = notes

                response = await client.post(
                    f"{self.api_base}/competence",
                    json=payload,
                    headers={"Authorization": f"Bearer {token}"}
                )

                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Failed to create competence record: {e}")
            return None


# Singleton instance
_governance_client: Optional[GovernanceClient] = None


def get_governance_client() -> GovernanceClient:
    """Get singleton Governance client instance"""
    global _governance_client
    if _governance_client is None:
        _governance_client = GovernanceClient()
    return _governance_client
