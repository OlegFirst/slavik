"""
Predictive Intelligence Adapter for Scenario Intelligence

Интегрирует Scenario Intelligence с Predictive модулем для:
- Предсказания вероятности ошибок в сценариях
- Прогнозирования времени выполнения
- Оптимизации на основе исторических данных
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ScenarioPredictiveAdapter:
    """
    Адаптер для интеграции с Predictive Intelligence модулем

    Provides:
    - Scenario failure prediction
    - Execution time forecasting
    - Pattern-based optimization
    """

    def __init__(self, predictive_url: str = "http://predictive:8030"):
        """
        Initialize Predictive adapter

        Args:
            predictive_url: URL predictive service
        """
        self.predictive_url = predictive_url
        logger.info(f"Initialized ScenarioPredictiveAdapter: {predictive_url}")

    async def predict_scenario_failure(
        self,
        scenario_id: str,
        historical_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Предсказать вероятность ошибки сценария

        Args:
            scenario_id: ID сценария
            historical_data: Исторические данные выполнения

        Returns:
            Dict with:
                - probability: float (0-1) вероятность ошибки
                - confidence: float (0-1) уверенность в предсказании
                - factors: List[str] факторы риска
                - recommendation: str рекомендация
        """
        try:
            import httpx

            # Если нет исторических данных, получить из learner
            if historical_data is None:
                # TODO: Получить из ScenarioLearner
                historical_data = {
                    "scenario_id": scenario_id,
                    "executions": []
                }

            # Запросить предсказание
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.predictive_url}/api/v1/predict",
                    json={
                        "type": "scenario_failure",
                        "scenario_id": scenario_id,
                        "data": historical_data
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"Predicted failure for {scenario_id}: "
                        f"probability={result.get('probability', 0):.2f}"
                    )
                    return result
                else:
                    logger.error(
                        f"Predictive service error: {response.status_code}"
                    )
                    return {
                        "probability": 0.0,
                        "confidence": 0.0,
                        "factors": [],
                        "recommendation": "Unable to predict (service unavailable)"
                    }

        except Exception as e:
            logger.error(f"Failed to predict scenario failure: {e}")
            return {
                "probability": 0.0,
                "confidence": 0.0,
                "factors": ["prediction_error"],
                "recommendation": f"Prediction failed: {str(e)}"
            }

    async def forecast_execution_time(
        self,
        scenario_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Прогнозировать время выполнения сценария

        Args:
            scenario_id: ID сценария
            context: Контекст выполнения (load, environment, etc.)

        Returns:
            Dict with:
                - predicted_duration_ms: int прогноз времени (мс)
                - min_duration_ms: int минимальное время
                - max_duration_ms: int максимальное время
                - confidence: float уверенность
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.predictive_url}/api/v1/forecast",
                    json={
                        "type": "execution_time",
                        "scenario_id": scenario_id,
                        "context": context or {}
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"Forecasted execution time for {scenario_id}: "
                        f"{result.get('predicted_duration_ms', 0)}ms"
                    )
                    return result
                else:
                    return {
                        "predicted_duration_ms": 5000,  # Default 5s
                        "min_duration_ms": 1000,
                        "max_duration_ms": 10000,
                        "confidence": 0.0
                    }

        except Exception as e:
            logger.error(f"Failed to forecast execution time: {e}")
            return {
                "predicted_duration_ms": 5000,
                "min_duration_ms": 1000,
                "max_duration_ms": 10000,
                "confidence": 0.0
            }

    async def get_optimization_suggestions(
        self,
        scenario_id: str
    ) -> List[Dict[str, Any]]:
        """
        Получить рекомендации по оптимизации сценария

        Args:
            scenario_id: ID сценария

        Returns:
            List of suggestions:
                - type: str тип оптимизации
                - description: str описание
                - impact: str (high/medium/low) влияние
                - implementation: str как реализовать
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.predictive_url}/api/v1/optimize/{scenario_id}",
                    timeout=30.0
                )

                if response.status_code == 200:
                    suggestions = response.json()
                    logger.info(
                        f"Got {len(suggestions)} optimization suggestions "
                        f"for {scenario_id}"
                    )
                    return suggestions
                else:
                    return []

        except Exception as e:
            logger.error(f"Failed to get optimization suggestions: {e}")
            return []

    async def analyze_patterns(
        self,
        scenario_ids: List[str],
        time_window: str = "7d"
    ) -> Dict[str, Any]:
        """
        Анализировать паттерны в выполнении сценариев

        Args:
            scenario_ids: Список ID сценариев
            time_window: Временное окно (7d, 30d, etc.)

        Returns:
            Dict with:
                - patterns: List[Dict] найденные паттерны
                - anomalies: List[Dict] аномалии
                - trends: Dict тренды
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.predictive_url}/api/v1/patterns",
                    json={
                        "scenario_ids": scenario_ids,
                        "time_window": time_window
                    },
                    timeout=60.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"Analyzed patterns for {len(scenario_ids)} scenarios: "
                        f"{len(result.get('patterns', []))} patterns found"
                    )
                    return result
                else:
                    return {
                        "patterns": [],
                        "anomalies": [],
                        "trends": {}
                    }

        except Exception as e:
            logger.error(f"Failed to analyze patterns: {e}")
            return {
                "patterns": [],
                "anomalies": [],
                "trends": {}
            }


# Global instance
_adapter: Optional[ScenarioPredictiveAdapter] = None


def get_predictive_adapter() -> ScenarioPredictiveAdapter:
    """Get global Predictive adapter instance"""
    global _adapter
    if _adapter is None:
        _adapter = ScenarioPredictiveAdapter()
    return _adapter
