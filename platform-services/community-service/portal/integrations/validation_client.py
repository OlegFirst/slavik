"""
Validation Module Integration
Handles exercise integration and scenario deployment
"""

import os
from typing import Optional
import httpx
from fastapi import HTTPException


class ValidationClient:
    """
    HTTP client for Validation Module (Port 8022)

    Responsibilities:
    - Deploy scenarios as exercises
    - Retrieve exercise data for AI article generation
    - Get exercise insights and results
    """

    def __init__(self):
        self.base_url = os.getenv("VALIDATION_SERVICE_URL", "http://localhost:8022")
        self.timeout = 30.0  # Longer timeout for exercise creation

    async def deploy_scenario(
        self,
        scenario_id: int,
        scenario_data: dict,
        tenant_id: str,
        token: str
    ) -> dict:
        """
        Deploy a scenario as an exercise in Validation module

        Args:
            scenario_id: Scenario ID from portal
            scenario_data: Full scenario data (name, injects, objectives, etc.)
            tenant_id: Target tenant ID
            token: JWT token for authorization

        Returns:
            Created exercise data

        Raises:
            HTTPException if deployment fails
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Prepare exercise payload
                exercise_payload = {
                    "tenant_id": tenant_id,
                    "exercise_code": f"SCENARIO-{scenario_data['scenario_code']}",
                    "exercise_name": scenario_data['scenario_name'],
                    "exercise_type": scenario_data['scenario_type'],
                    "scenario_description": scenario_data['full_scenario'],
                    "injects": scenario_data['injects'],
                    "objectives": scenario_data['learning_objectives'],
                    "duration_minutes": scenario_data['duration_minutes'],
                    "source_scenario_id": scenario_id,
                }

                response = await client.post(
                    f"{self.base_url}/api/validation/exercises",
                    json=exercise_payload,
                    headers={"Authorization": f"Bearer {token}"}
                )

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Failed to deploy scenario: {e.response.text}"
                )
            except httpx.RequestError:
                raise HTTPException(
                    status_code=503,
                    detail="Validation service unavailable"
                )

    async def get_exercise(self, exercise_id: int, token: str) -> Optional[dict]:
        """
        Get exercise details

        Args:
            exercise_id: Exercise ID
            token: JWT token for authorization

        Returns:
            Exercise data or None if not found
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/validation/exercises/{exercise_id}",
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

    async def get_exercise_insights(
        self,
        exercise_id: int,
        token: str
    ) -> Optional[dict]:
        """
        Get exercise insights for AI article generation

        Args:
            exercise_id: Exercise ID
            token: JWT token for authorization

        Returns:
            Exercise insights including:
            - Lessons learned
            - Performance metrics
            - Key findings
            - Recommendations
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/validation/exercises/{exercise_id}/insights",
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

    async def increment_scenario_deployment(
        self,
        exercise_id: int,
        token: str
    ) -> bool:
        """
        Notify Validation module that scenario was deployed
        (Used for tracking deployment count)

        Args:
            exercise_id: Exercise ID
            token: JWT token

        Returns:
            True if successful, False otherwise
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/validation/exercises/{exercise_id}/track-deployment",
                    headers={"Authorization": f"Bearer {token}"}
                )

                return response.status_code == 200

            except (httpx.HTTPStatusError, httpx.RequestError):
                return False
