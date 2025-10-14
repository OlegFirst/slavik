"""
Simulation Service Adapter for Scenario Intelligence

Интегрирует Scenario Intelligence с Simulation Service для:
- Конвертации L3 сценариев в BCM exercises
- Получения результатов симуляций для обучения
- Запуска симуляций на основе сценариев
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class ScenarioSimulationAdapter:
    """
    Адаптер для интеграции с Simulation Service

    Provides:
    - Scenario → Exercise conversion
    - Simulation execution
    - Result retrieval for learning
    """

    def __init__(self, simulation_url: str = "http://simulation-service:8095"):
        """
        Initialize Simulation Service adapter

        Args:
            simulation_url: URL simulation service
        """
        self.simulation_url = simulation_url
        logger.info(f"Initialized ScenarioSimulationAdapter: {simulation_url}")

    async def convert_scenario_to_exercise(
        self,
        scenario_id: str,
        exercise_type: str = "bcm_drill",
        duration_minutes: int = 240
    ) -> Dict[str, Any]:
        """
        Конвертировать L3 сценарий в BCM exercise

        Args:
            scenario_id: ID сценария
            exercise_type: Тип упражнения (bcm_drill, tabletop, simulation)
            duration_minutes: Длительность упражнения

        Returns:
            Dict with:
                - exercise_id: str ID созданного упражнения
                - success: bool успешно ли создано
                - exercise_type: str тип упражнения
                - estimated_duration_ms: int оценочная длительность
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.simulation_url}/api/v1/exercises/from-scenario",
                    json={
                        "scenario_id": scenario_id,
                        "exercise_type": exercise_type,
                        "duration_minutes": duration_minutes,
                        "source": "scenario-intelligence"
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"Converted scenario {scenario_id} to exercise: "
                        f"exercise_id={result.get('exercise_id', 'N/A')}"
                    )
                    return result
                else:
                    logger.error(
                        f"Simulation Service error: {response.status_code}"
                    )
                    return {
                        "exercise_id": None,
                        "success": False,
                        "exercise_type": exercise_type,
                        "estimated_duration_ms": 0
                    }

        except Exception as e:
            logger.error(f"Failed to convert scenario to exercise: {e}")
            return {
                "exercise_id": None,
                "success": False,
                "exercise_type": exercise_type,
                "estimated_duration_ms": 0,
                "error": str(e)
            }

    async def run_simulation(
        self,
        scenario_id: str,
        engine: str = "scenario_engine",
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Запустить симуляцию на основе сценария

        Args:
            scenario_id: ID сценария
            engine: Simulation engine (jaamsim, monte_carlo, scenario_engine, what_if)
            parameters: Параметры симуляции

        Returns:
            Dict with:
                - simulation_id: str ID симуляции
                - status: str статус (running, completed, failed)
                - result: Dict результаты (если completed)
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.simulation_url}/api/v1/simulations",
                    json={
                        "scenario_id": scenario_id,
                        "engine": engine,
                        "parameters": parameters or {},
                        "auto_start": True
                    },
                    timeout=60.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"Started simulation for scenario {scenario_id}: "
                        f"simulation_id={result.get('simulation_id', 'N/A')}, "
                        f"engine={engine}"
                    )
                    return result
                else:
                    return {
                        "simulation_id": None,
                        "status": "failed",
                        "result": None
                    }

        except Exception as e:
            logger.error(f"Failed to run simulation: {e}")
            return {
                "simulation_id": None,
                "status": "failed",
                "result": None,
                "error": str(e)
            }

    async def get_simulation_result(
        self,
        simulation_id: str
    ) -> Dict[str, Any]:
        """
        Получить результат симуляции

        Args:
            simulation_id: ID симуляции

        Returns:
            Dict with:
                - simulation_id: str
                - status: str (running, completed, failed)
                - result: Dict результаты симуляции
                - metrics: Dict метрики
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.simulation_url}/api/v1/simulations/{simulation_id}",
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"Got simulation result for {simulation_id}: "
                        f"status={result.get('status', 'unknown')}"
                    )
                    return result
                else:
                    return {
                        "simulation_id": simulation_id,
                        "status": "unknown",
                        "result": None,
                        "metrics": {}
                    }

        except Exception as e:
            logger.error(f"Failed to get simulation result: {e}")
            return {
                "simulation_id": simulation_id,
                "status": "error",
                "result": None,
                "metrics": {},
                "error": str(e)
            }

    async def get_exercise_results(
        self,
        exercise_id: str
    ) -> Dict[str, Any]:
        """
        Получить результаты BCM exercise для обучения

        Args:
            exercise_id: ID упражнения

        Returns:
            Dict with:
                - exercise_id: str
                - scenario_id: str исходный сценарий
                - effectiveness: float (0-1) эффективность
                - learning_points: List[str] уроки
                - metrics: Dict метрики выполнения
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.simulation_url}/api/v1/exercises/{exercise_id}/results",
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"Got exercise results for {exercise_id}: "
                        f"effectiveness={result.get('effectiveness', 0):.2f}"
                    )
                    return result
                else:
                    return {
                        "exercise_id": exercise_id,
                        "scenario_id": None,
                        "effectiveness": 0.0,
                        "learning_points": [],
                        "metrics": {}
                    }

        except Exception as e:
            logger.error(f"Failed to get exercise results: {e}")
            return {
                "exercise_id": exercise_id,
                "scenario_id": None,
                "effectiveness": 0.0,
                "learning_points": [],
                "metrics": {},
                "error": str(e)
            }

    async def get_simulation_recommendations(
        self,
        scenario_id: str
    ) -> Dict[str, Any]:
        """
        Получить рекомендации по симуляции для сценария

        Args:
            scenario_id: ID сценария

        Returns:
            Dict with:
                - recommended_engine: str рекомендуемый движок
                - reasoning: str почему
                - parameters: Dict рекомендуемые параметры
                - estimated_duration_minutes: int оценка времени
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.simulation_url}/api/v1/recommendations",
                    json={"scenario_id": scenario_id},
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"Got simulation recommendations for {scenario_id}: "
                        f"engine={result.get('recommended_engine', 'N/A')}"
                    )
                    return result
                else:
                    return {
                        "recommended_engine": "scenario_engine",  # Default
                        "reasoning": "Default recommendation",
                        "parameters": {},
                        "estimated_duration_minutes": 60
                    }

        except Exception as e:
            logger.error(f"Failed to get simulation recommendations: {e}")
            return {
                "recommended_engine": "scenario_engine",
                "reasoning": f"Error: {str(e)}",
                "parameters": {},
                "estimated_duration_minutes": 60
            }

    async def list_available_engines(self) -> List[Dict[str, Any]]:
        """
        Получить список доступных simulation engines

        Returns:
            List of engines with:
                - engine_name: str
                - description: str
                - capabilities: List[str]
                - available: bool
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.simulation_url}/api/v1/engines",
                    timeout=30.0
                )

                if response.status_code == 200:
                    engines = response.json()
                    logger.info(f"Got {len(engines)} available engines")
                    return engines
                else:
                    return []

        except Exception as e:
            logger.error(f"Failed to list available engines: {e}")
            return []


# Global instance
_adapter: Optional[ScenarioSimulationAdapter] = None


def get_simulation_adapter() -> ScenarioSimulationAdapter:
    """Get global Simulation adapter instance"""
    global _adapter
    if _adapter is None:
        _adapter = ScenarioSimulationAdapter()
    return _adapter
