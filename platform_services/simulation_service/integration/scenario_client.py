"""
Scenario Intelligence Client for Simulation Service

Интегрирует Simulation Service со Scenario Intelligence для:
- Получения сценариев для конвертации в exercises
- Отправки результатов симуляций обратно для обучения
- Запроса scenario metadata
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class ScenarioIntelligenceClient:
    """
    Client для интеграции со Scenario Intelligence

    Provides:
    - Scenario retrieval
    - Result submission for learning
    - Scenario metadata queries
    """

    def __init__(self, scenario_url: str = "http://scenario-intelligence:8060"):
        """
        Initialize Scenario Intelligence client

        Args:
            scenario_url: URL scenario intelligence service
        """
        self.scenario_url = scenario_url
        logger.info(f"Initialized ScenarioIntelligenceClient: {scenario_url}")

    async def get_scenario(
        self,
        scenario_id: str
    ) -> Dict[str, Any]:
        """
        Получить сценарий по ID

        Args:
            scenario_id: ID сценария

        Returns:
            Dict with scenario data:
                - scenario_id: str
                - name: str
                - level: int (1-4)
                - type: str
                - steps: List[Dict]
                - metadata: Dict
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.scenario_url}/api/v1/scenarios/{scenario_id}",
                    timeout=30.0
                )

                if response.status_code == 200:
                    scenario = response.json()
                    logger.info(
                        f"Got scenario {scenario_id}: "
                        f"name={scenario.get('name', 'N/A')}, "
                        f"level={scenario.get('level', 0)}"
                    )
                    return scenario
                else:
                    logger.error(
                        f"Scenario Intelligence error: {response.status_code}"
                    )
                    return {
                        "scenario_id": scenario_id,
                        "name": "Unknown",
                        "level": 0,
                        "type": "unknown",
                        "steps": [],
                        "metadata": {}
                    }

        except Exception as e:
            logger.error(f"Failed to get scenario: {e}")
            return {
                "scenario_id": scenario_id,
                "name": "Unknown",
                "level": 0,
                "type": "unknown",
                "steps": [],
                "metadata": {},
                "error": str(e)
            }

    async def submit_simulation_result(
        self,
        scenario_id: str,
        simulation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Отправить результат симуляции обратно для обучения

        Args:
            scenario_id: ID сценария
            simulation_result: Результат симуляции

        Returns:
            Dict with:
                - accepted: bool принят ли результат
                - learning_id: str ID созданной записи обучения
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.scenario_url}/api/v1/learning/submit",
                    json={
                        "scenario_id": scenario_id,
                        "result": simulation_result,
                        "source": "simulation-service"
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"Submitted simulation result for {scenario_id}: "
                        f"learning_id={result.get('learning_id', 'N/A')}"
                    )
                    return result
                else:
                    return {
                        "accepted": False,
                        "learning_id": None
                    }

        except Exception as e:
            logger.error(f"Failed to submit simulation result: {e}")
            return {
                "accepted": False,
                "learning_id": None,
                "error": str(e)
            }

    async def get_l3_scenarios(
        self,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Получить все L3 сценарии для конвертации в exercises

        Args:
            limit: Максимальное количество сценариев

        Returns:
            List of L3 scenarios
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.scenario_url}/api/v1/scenarios",
                    params={
                        "level": 3,
                        "limit": limit
                    },
                    timeout=60.0
                )

                if response.status_code == 200:
                    scenarios = response.json()
                    logger.info(f"Got {len(scenarios)} L3 scenarios")
                    return scenarios
                else:
                    return []

        except Exception as e:
            logger.error(f"Failed to get L3 scenarios: {e}")
            return []

    async def notify_exercise_created(
        self,
        scenario_id: str,
        exercise_id: str,
        exercise_type: str
    ) -> Dict[str, Any]:
        """
        Уведомить Scenario Intelligence о создании exercise

        Args:
            scenario_id: ID сценария
            exercise_id: ID созданного exercise
            exercise_type: Тип exercise

        Returns:
            Dict with acknowledgment
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.scenario_url}/api/v1/scenarios/{scenario_id}/exercises",
                    json={
                        "exercise_id": exercise_id,
                        "exercise_type": exercise_type,
                        "created_by": "simulation-service"
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"Notified about exercise {exercise_id} "
                        f"for scenario {scenario_id}"
                    )
                    return result
                else:
                    return {"acknowledged": False}

        except Exception as e:
            logger.error(f"Failed to notify exercise creation: {e}")
            return {"acknowledged": False, "error": str(e)}

    async def get_scenario_recommendations(
        self,
        scenario_id: str
    ) -> Dict[str, Any]:
        """
        Получить рекомендации по сценарию

        Args:
            scenario_id: ID сценария

        Returns:
            Dict with recommendations:
                - optimizations: List[str]
                - best_practices: List[str]
                - similar_scenarios: List[str]
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.scenario_url}/api/v1/scenarios/{scenario_id}/recommendations",
                    timeout=30.0
                )

                if response.status_code == 200:
                    recommendations = response.json()
                    logger.info(
                        f"Got recommendations for scenario {scenario_id}"
                    )
                    return recommendations
                else:
                    return {
                        "optimizations": [],
                        "best_practices": [],
                        "similar_scenarios": []
                    }

        except Exception as e:
            logger.error(f"Failed to get scenario recommendations: {e}")
            return {
                "optimizations": [],
                "best_practices": [],
                "similar_scenarios": [],
                "error": str(e)
            }


# Global instance
_client: Optional[ScenarioIntelligenceClient] = None


def get_scenario_client() -> ScenarioIntelligenceClient:
    """Get global Scenario Intelligence client instance"""
    global _client
    if _client is None:
        _client = ScenarioIntelligenceClient()
    return _client
