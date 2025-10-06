"""
Learning Service HTTP Client
Provides integration with Learning Service API
"""

import httpx
import os
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class LearningClient:
    """
    HTTP client for Learning Service API

    Base URL: http://localhost:8021/api/v1/learning

    Methods:
    - get_person_competencies() - Get user competencies for forum display
    - get_person_certifications() - Get user certifications
    - get_person_enrollments() - Get training history
    - get_person_achievements() - Get gamification achievements
    - get_program() - Get training program details
    - get_programs() - List training programs
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("LEARNING_SERVICE_URL", "http://localhost:8021")
        self.api_base = f"{self.base_url}/api/v1/learning"
        self.timeout = 10.0

    async def get_person_competencies(
        self,
        person_id: str,
        token: str
    ) -> List[Dict[str, Any]]:
        """
        Get competencies for a person (for forum profile display)

        Args:
            person_id: Person ID
            token: JWT token for authorization

        Returns:
            List of competency records with proficiency levels

        Example response:
        [
            {
                "competency_area": "Business Continuity Planning",
                "proficiency_level": "advanced",
                "last_assessed": "2025-10-01"
            }
        ]
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Note: Learning Service doesn't have dedicated competencies endpoint yet
                # We'll derive from enrollments and achievements
                enrollments = await self.get_person_enrollments(person_id, token)

                # Build competency map from completed trainings
                competencies = {}
                for enrollment in enrollments:
                    if enrollment.get("status") in ["completed", "certified"]:
                        program_type = enrollment.get("program_type", "general")
                        if program_type not in competencies:
                            competencies[program_type] = {
                                "competency_area": program_type.replace("_", " ").title(),
                                "proficiency_level": "intermediate",
                                "trainings_completed": 0
                            }
                        competencies[program_type]["trainings_completed"] += 1

                # Adjust proficiency based on count
                result = []
                for comp_data in competencies.values():
                    count = comp_data["trainings_completed"]
                    if count >= 5:
                        comp_data["proficiency_level"] = "expert"
                    elif count >= 3:
                        comp_data["proficiency_level"] = "advanced"

                    del comp_data["trainings_completed"]
                    result.append(comp_data)

                return result

        except httpx.HTTPError as e:
            logger.error(f"Failed to get competencies for {person_id}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting competencies: {e}")
            return []

    async def get_person_certifications(
        self,
        person_id: str,
        token: str
    ) -> List[Dict[str, Any]]:
        """
        Get certifications for a person

        Args:
            person_id: Person ID
            token: JWT token

        Returns:
            List of certifications

        Example:
        [
            {
                "certification_number": "BCM-2025-001",
                "certification_name": "BCM Practitioner",
                "issued_date": "2025-10-01",
                "expiry_date": "2027-10-01",
                "program_name": "BCM Foundation"
            }
        ]
        """
        try:
            enrollments = await self.get_person_enrollments(person_id, token)

            certifications = []
            for enrollment in enrollments:
                if enrollment.get("certification_issued"):
                    certifications.append({
                        "certification_number": enrollment.get("certification_number"),
                        "certification_name": enrollment.get("certification_name", "Professional Certification"),
                        "issued_date": enrollment.get("certification_date"),
                        "expiry_date": enrollment.get("certification_expiry_date"),
                        "program_name": enrollment.get("program_name"),
                        "program_code": enrollment.get("program_code")
                    })

            return certifications

        except Exception as e:
            logger.error(f"Failed to get certifications for {person_id}: {e}")
            return []

    async def get_person_enrollments(
        self,
        person_id: str,
        token: str
    ) -> List[Dict[str, Any]]:
        """
        Get training enrollments for a person

        Endpoint: GET /persons/{person_id}/enrollments

        Args:
            person_id: Person ID
            token: JWT token

        Returns:
            List of enrollments
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_base}/persons/{person_id}/enrollments",
                    headers={"Authorization": f"Bearer {token}"}
                )

                if response.status_code == 404:
                    return []

                response.raise_for_status()
                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Failed to get enrollments for {person_id}: {e}")
            return []

    async def get_person_achievements(
        self,
        person_id: str,
        token: str
    ) -> List[Dict[str, Any]]:
        """
        Get gamification achievements for a person

        Endpoint: GET /persons/{person_id}/achievements

        Args:
            person_id: Person ID
            token: JWT token

        Returns:
            List of achievements
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_base}/persons/{person_id}/achievements",
                    headers={"Authorization": f"Bearer {token}"}
                )

                if response.status_code == 404:
                    return []

                response.raise_for_status()
                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Failed to get achievements for {person_id}: {e}")
            return []

    async def get_person_points(
        self,
        person_id: str,
        token: str
    ) -> int:
        """
        Get gamification points for a person

        Endpoint: GET /persons/{person_id}/points

        Args:
            person_id: Person ID
            token: JWT token

        Returns:
            Total points (default 0 if error)
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_base}/persons/{person_id}/points",
                    headers={"Authorization": f"Bearer {token}"}
                )

                if response.status_code == 404:
                    return 0

                response.raise_for_status()
                data = response.json()
                return data.get("total_points", 0)

        except Exception as e:
            logger.error(f"Failed to get points for {person_id}: {e}")
            return 0

    async def get_program(
        self,
        program_id: int,
        token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get training program details

        Endpoint: GET /programs/{program_id}

        Args:
            program_id: Program ID
            token: JWT token

        Returns:
            Program details or None if not found
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_base}/programs/{program_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Failed to get program {program_id}: {e}")
            return None

    async def get_programs(
        self,
        token: str,
        status: Optional[str] = "published",
        program_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List training programs

        Endpoint: GET /programs?status=published

        Args:
            token: JWT token
            status: Filter by status (draft/published/archived)
            program_type: Filter by type
            limit: Max results

        Returns:
            List of programs
        """
        try:
            params = {}
            if status:
                params["status"] = status
            if program_type:
                params["program_type"] = program_type
            if limit:
                params["limit"] = limit

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_base}/programs",
                    params=params,
                    headers={"Authorization": f"Bearer {token}"}
                )

                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Failed to get programs: {e}")
            return []


# Singleton instance
_learning_client: Optional[LearningClient] = None


def get_learning_client() -> LearningClient:
    """Get singleton Learning client instance"""
    global _learning_client
    if _learning_client is None:
        _learning_client = LearningClient()
    return _learning_client
