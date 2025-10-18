"""
Learning Service HTTP Client for Marketplace
Provides integration with Learning Service API for specialist profiles
"""

import httpx
import os
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class LearningClient:
    """
    HTTP client for Learning Service API (Marketplace integration)

    Base URL: http://localhost:8021/api/v1/learning

    Methods:
    - get_person_certifications() - Get specialist certifications
    - get_person_competencies() - Get competency framework data
    - get_person_enrollments() - Get training history
    - get_competency_framework() - Get BCI competency framework
    - verify_certification() - Verify certification is valid
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("LEARNING_SERVICE_URL", "http://localhost:8021")
        self.api_base = f"{self.base_url}/api/v1/learning"
        self.timeout = 10.0

    async def get_person_certifications(
        self,
        person_id: str,
        token: str
    ) -> List[Dict[str, Any]]:
        """
        Get all certifications for a specialist

        Used for: Displaying certifications in specialist profile

        Args:
            person_id: Person ID (same as specialist user_id)
            token: JWT token

        Returns:
            List of certifications with details

        Example:
        [
            {
                "certification_number": "BCM-2025-001",
                "certification_name": "BCM Practitioner",
                "program_name": "BCM Foundation Training",
                "program_code": "BCM-FOUND-001",
                "issued_date": "2025-10-01",
                "expiry_date": "2027-10-01",
                "status": "active"
            }
        ]
        """
        try:
            # Get enrollments and filter certified ones
            enrollments = await self.get_person_enrollments(person_id, token)

            certifications = []
            for enrollment in enrollments:
                if enrollment.get("certification_issued"):
                    cert_date = enrollment.get("certification_date")
                    expiry_date = enrollment.get("certification_expiry_date")

                    # Check if certification is still valid
                    status = "active"
                    if expiry_date:
                        from datetime import datetime
                        try:
                            expiry = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
                            if expiry < datetime.now(expiry.tzinfo):
                                status = "expired"
                        except:
                            pass

                    certifications.append({
                        "certification_number": enrollment.get("certification_number"),
                        "certification_name": enrollment.get("certification_name", "Professional Certification"),
                        "program_name": enrollment.get("program_name"),
                        "program_code": enrollment.get("program_code"),
                        "issued_date": cert_date,
                        "expiry_date": expiry_date,
                        "status": status,
                        "enrollment_id": enrollment.get("id")
                    })

            return certifications

        except Exception as e:
            logger.error(f"Failed to get certifications for {person_id}: {e}")
            return []

    async def get_person_competencies(
        self,
        person_id: str,
        token: str
    ) -> Dict[str, Any]:
        """
        Get competency assessment for a specialist

        Used for: Competency-based specialist matching

        Args:
            person_id: Person ID
            token: JWT token

        Returns:
            Competency scores by area

        Example:
        {
            "business_continuity_planning": {
                "level": "advanced",
                "score": 85,
                "last_training": "2025-09-15",
                "certifications": 2
            },
            "risk_assessment": {
                "level": "intermediate",
                "score": 70,
                "last_training": "2025-08-20",
                "certifications": 1
            }
        }
        """
        try:
            enrollments = await self.get_person_enrollments(person_id, token)

            # Build competency map from completed trainings
            competencies = {}

            for enrollment in enrollments:
                if enrollment.get("status") in ["completed", "certified"]:
                    program_type = enrollment.get("program_type", "general_bcm")

                    if program_type not in competencies:
                        competencies[program_type] = {
                            "level": "beginner",
                            "score": 0,
                            "trainings_count": 0,
                            "certifications": 0,
                            "last_training": None
                        }

                    comp = competencies[program_type]
                    comp["trainings_count"] += 1

                    if enrollment.get("certification_issued"):
                        comp["certifications"] += 1

                    # Update last training date
                    completed_date = enrollment.get("completed_date")
                    if completed_date:
                        if not comp["last_training"] or completed_date > comp["last_training"]:
                            comp["last_training"] = completed_date

            # Calculate scores and levels
            for comp_key, comp_data in competencies.items():
                trainings = comp_data["trainings_count"]
                certs = comp_data["certifications"]

                # Score calculation: training (40%) + certifications (60%)
                training_score = min(trainings * 10, 40)
                cert_score = min(certs * 30, 60)
                comp_data["score"] = training_score + cert_score

                # Level based on score
                score = comp_data["score"]
                if score >= 80:
                    comp_data["level"] = "expert"
                elif score >= 60:
                    comp_data["level"] = "advanced"
                elif score >= 40:
                    comp_data["level"] = "intermediate"
                else:
                    comp_data["level"] = "beginner"

                # Cleanup temporary fields
                del comp_data["trainings_count"]

            return competencies

        except Exception as e:
            logger.error(f"Failed to get competencies for {person_id}: {e}")
            return {}

    async def get_person_enrollments(
        self,
        person_id: str,
        token: str
    ) -> List[Dict[str, Any]]:
        """
        Get all training enrollments for a person

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

    async def get_competency_framework(
        self,
        token: str
    ) -> List[Dict[str, Any]]:
        """
        Get BCI competency framework

        Note: This requires querying reference data tables.
        For now, returns hardcoded framework based on BCI GPG.

        Args:
            token: JWT token

        Returns:
            List of competency areas

        Example:
        [
            {
                "code": "bc_planning",
                "name": "Business Continuity Planning",
                "description": "...",
                "proficiency_levels": ["beginner", "intermediate", "advanced", "expert"]
            }
        ]
        """
        # TODO Phase 5: Query Learning Service for actual competency framework
        # For now, return standard BCI competencies

        return [
            {
                "code": "bc_planning",
                "name": "Business Continuity Planning",
                "description": "Develop and maintain business continuity plans",
                "proficiency_levels": ["beginner", "intermediate", "advanced", "expert"]
            },
            {
                "code": "risk_assessment",
                "name": "Risk Assessment",
                "description": "Identify and assess business continuity risks",
                "proficiency_levels": ["beginner", "intermediate", "advanced", "expert"]
            },
            {
                "code": "bia",
                "name": "Business Impact Analysis",
                "description": "Conduct business impact analysis",
                "proficiency_levels": ["beginner", "intermediate", "advanced", "expert"]
            },
            {
                "code": "crisis_management",
                "name": "Crisis Management",
                "description": "Manage crisis situations and response",
                "proficiency_levels": ["beginner", "intermediate", "advanced", "expert"]
            },
            {
                "code": "testing_exercises",
                "name": "Testing & Exercises",
                "description": "Plan and conduct BCM tests and exercises",
                "proficiency_levels": ["beginner", "intermediate", "advanced", "expert"]
            }
        ]

    async def verify_certification(
        self,
        certification_number: str,
        token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Verify a certification is valid

        Used for: Specialist verification process

        Args:
            certification_number: Certification number to verify
            token: JWT token

        Returns:
            Certification details if valid, None if not found or expired

        Example:
        {
            "certification_number": "BCM-2025-001",
            "person_id": "user_001",
            "person_name": "John Doe",
            "certification_name": "BCM Practitioner",
            "issued_date": "2025-10-01",
            "expiry_date": "2027-10-01",
            "status": "active",
            "is_valid": true
        }
        """
        try:
            # Note: Learning Service doesn't have a direct certification lookup endpoint
            # We'd need to search through enrollments
            # For now, return None - this can be implemented in Phase 5

            logger.warning(f"Certification verification not yet implemented: {certification_number}")
            return None

        except Exception as e:
            logger.error(f"Failed to verify certification {certification_number}: {e}")
            return None

    async def get_program(
        self,
        program_id: int,
        token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get training program details

        Used for: Displaying program info in specialist requirements

        Endpoint: GET /programs/{program_id}

        Args:
            program_id: Program ID
            token: JWT token

        Returns:
            Program details or None
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


# Singleton instance
_learning_client: Optional[LearningClient] = None


def get_learning_client() -> LearningClient:
    """Get singleton Learning client instance"""
    global _learning_client
    if _learning_client is None:
        _learning_client = LearningClient()
    return _learning_client
