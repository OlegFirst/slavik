"""
Event Intelligence Adapter for Scenario Intelligence

Интегрирует Scenario Intelligence с Event Intelligence для:
- Анализа событий выполнения сценариев
- Complex Event Processing (CEP)
- Pattern detection в событиях сценариев
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class ScenarioEventIntelligenceAdapter:
    """
    Адаптер для интеграции с Event Intelligence модулем

    Provides:
    - Scenario event analysis
    - CEP for scenario patterns
    - Anomaly detection in scenario executions
    """

    def __init__(self, event_intel_url: str = "http://event-intelligence:8035"):
        """
        Initialize Event Intelligence adapter

        Args:
            event_intel_url: URL event intelligence service
        """
        self.event_intel_url = event_intel_url
        logger.info(f"Initialized ScenarioEventIntelligenceAdapter: {event_intel_url}")

    async def analyze_scenario_events(
        self,
        scenario_id: str,
        time_window: str = "24h"
    ) -> Dict[str, Any]:
        """
        Анализировать события сценария

        Args:
            scenario_id: ID сценария
            time_window: Временное окно (1h, 24h, 7d, etc.)

        Returns:
            Dict with:
                - events_count: int количество событий
                - patterns: List[Dict] найденные паттерны
                - anomalies: List[Dict] обнаруженные аномалии
                - trends: Dict тренды
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.event_intel_url}/api/v1/analyze",
                    json={
                        "event_types": [
                            "scenario.execution.started",
                            "scenario.execution.completed",
                            "scenario.execution.failed",
                            "scenario.step.started",
                            "scenario.step.completed"
                        ],
                        "filters": {"scenario_id": scenario_id},
                        "time_window": time_window,
                        "include_patterns": True,
                        "include_anomalies": True
                    },
                    timeout=60.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"Analyzed events for {scenario_id}: "
                        f"{result.get('events_count', 0)} events, "
                        f"{len(result.get('patterns', []))} patterns, "
                        f"{len(result.get('anomalies', []))} anomalies"
                    )
                    return result
                else:
                    logger.error(
                        f"Event Intelligence service error: {response.status_code}"
                    )
                    return {
                        "events_count": 0,
                        "patterns": [],
                        "anomalies": [],
                        "trends": {}
                    }

        except Exception as e:
            logger.error(f"Failed to analyze scenario events: {e}")
            return {
                "events_count": 0,
                "patterns": [],
                "anomalies": [],
                "trends": {}
            }

    async def detect_anomalies(
        self,
        scenario_ids: List[str],
        time_window: str = "24h"
    ) -> List[Dict[str, Any]]:
        """
        Обнаружить аномалии в выполнении сценариев

        Args:
            scenario_ids: Список ID сценариев
            time_window: Временное окно

        Returns:
            List of anomalies:
                - scenario_id: str
                - anomaly_type: str (duration, failure_rate, pattern, etc.)
                - severity: str (low, medium, high, critical)
                - description: str
                - detected_at: str timestamp
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.event_intel_url}/api/v1/anomalies/detect",
                    json={
                        "filters": {"scenario_id": {"$in": scenario_ids}},
                        "time_window": time_window,
                        "detection_types": [
                            "duration_spike",
                            "failure_rate_increase",
                            "unexpected_pattern"
                        ]
                    },
                    timeout=60.0
                )

                if response.status_code == 200:
                    anomalies = response.json()
                    logger.info(
                        f"Detected {len(anomalies)} anomalies "
                        f"in {len(scenario_ids)} scenarios"
                    )
                    return anomalies
                else:
                    return []

        except Exception as e:
            logger.error(f"Failed to detect anomalies: {e}")
            return []

    async def subscribe_to_scenario_events(
        self,
        scenario_id: str,
        callback_url: str,
        event_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Подписаться на события сценария

        Args:
            scenario_id: ID сценария
            callback_url: URL для callback
            event_types: Типы событий или None для всех

        Returns:
            Dict with:
                - subscription_id: str ID подписки
                - subscribed: bool успешно ли подписались
                - event_types: List[str] типы событий
        """
        try:
            import httpx

            if event_types is None:
                event_types = [
                    "scenario.execution.started",
                    "scenario.execution.completed",
                    "scenario.execution.failed"
                ]

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.event_intel_url}/api/v1/subscriptions",
                    json={
                        "event_types": event_types,
                        "filters": {"scenario_id": scenario_id},
                        "callback_url": callback_url,
                        "delivery_mode": "webhook"
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"Subscribed to events for {scenario_id}: "
                        f"subscription_id={result.get('subscription_id', 'N/A')}"
                    )
                    return result
                else:
                    return {
                        "subscription_id": None,
                        "subscribed": False,
                        "event_types": []
                    }

        except Exception as e:
            logger.error(f"Failed to subscribe to scenario events: {e}")
            return {
                "subscription_id": None,
                "subscribed": False,
                "event_types": []
            }

    async def get_event_patterns(
        self,
        time_window: str = "7d",
        min_occurrences: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Получить паттерны событий сценариев

        Args:
            time_window: Временное окно
            min_occurrences: Минимальное количество повторений

        Returns:
            List of patterns:
                - pattern_id: str
                - description: str описание паттерна
                - frequency: int как часто встречается
                - scenarios: List[str] ID сценариев с этим паттерном
                - confidence: float уверенность
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.event_intel_url}/api/v1/patterns",
                    params={
                        "time_window": time_window,
                        "min_occurrences": min_occurrences,
                        "event_type_filter": "scenario.*"
                    },
                    timeout=60.0
                )

                if response.status_code == 200:
                    patterns = response.json()
                    logger.info(
                        f"Got {len(patterns)} event patterns "
                        f"in {time_window}"
                    )
                    return patterns
                else:
                    return []

        except Exception as e:
            logger.error(f"Failed to get event patterns: {e}")
            return []


# Global instance
_adapter: Optional[ScenarioEventIntelligenceAdapter] = None


def get_event_intelligence_adapter() -> ScenarioEventIntelligenceAdapter:
    """Get global Event Intelligence adapter instance"""
    global _adapter
    if _adapter is None:
        _adapter = ScenarioEventIntelligenceAdapter()
    return _adapter
