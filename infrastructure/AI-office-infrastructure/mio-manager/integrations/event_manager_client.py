"""
МиО Manager ↔ AI Event Manager Client

Клиент для взаимодействия с AI Event Manager
"""

import logging
import httpx
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class EventManagerClient:
    """
    Клиент для работы с AI Event Manager

    МиО Manager использует этого специалиста для:
    - Анализа событий
    - Получения рекомендаций по событиям
    - Делегирования event-related задач
    """

    def __init__(self, event_manager_url: str = "http://localhost:8050"):
        self.base_url = event_manager_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_event_recommendations(
        self,
        scope: str = "high-priority"
    ) -> Optional[Dict]:
        """
        Получает рекомендации по событиям

        Args:
            scope: 'all', 'critical', 'workflow', 'high-priority'

        Returns:
            {
                "recommendations": [
                    {
                        "event_name": str,
                        "importance": float,
                        "recommendations": List[str]
                    }
                ]
            }
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/recommendations",
                params={"scope": scope}
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Event Manager returned {response.status_code}")

        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")

        return None

    async def analyze_event(
        self,
        event_name: str,
        publishers: List[str],
        subscribers: List[str]
    ) -> Optional[Dict]:
        """
        Запрашивает AI анализ события

        Returns:
            {
                "analysis": {
                    "importance_score": float,
                    "usage_pattern": str,
                    "recommendations": List,
                    "ai_insights": str
                }
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/analyze/event",
                json={
                    "event_name": event_name,
                    "publishers": publishers,
                    "subscribers": subscribers
                }
            )

            if response.status_code == 200:
                return response.json()

        except Exception as e:
            logger.error(f"Error analyzing event: {e}")

        return None

    async def get_predictions(self) -> Optional[Dict]:
        """
        Получает предсказания о будущих gaps

        Returns:
            {
                "predictions": [
                    {
                        "type": str,
                        "probability": float,
                        "reasoning": str
                    }
                ]
            }
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/predictions/future"
            )

            if response.status_code == 200:
                return response.json()

        except Exception as e:
            logger.error(f"Error getting predictions: {e}")

        return None

    async def get_learning_stats(self) -> Optional[Dict]:
        """
        Получает статистику обучения Event Manager

        Returns:
            {
                "learning": {
                    "total_examples": int,
                    "accuracy": float,
                    "patterns_learned": int
                }
            }
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/learning/stats"
            )

            if response.status_code == 200:
                return response.json()

        except Exception as e:
            logger.error(f"Error getting stats: {e}")

        return None

    async def health_check(self) -> bool:
        """Проверяет, доступен ли Event Manager"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False

    async def close(self):
        """Закрывает клиент"""
        await self.client.aclose()


# ============================================================================
# Helper для МиО Manager
# ============================================================================

async def incorporate_event_insights_into_action_plan(
    event_recommendations: List[Dict]
) -> List[Dict]:
    """
    Конвертирует рекомендации Event Manager в задачи для МиО

    Args:
        event_recommendations: Рекомендации от Event Manager

    Returns:
        List задач для action plan
    """
    tasks = []

    for rec in event_recommendations:
        importance = rec.get("importance", 0)
        event_name = rec.get("event_name")

        # Высокоприоритетные события → немедленные задачи
        if importance > 0.8:
            tasks.append({
                "title": f"Implement high-priority event: {event_name}",
                "type": "event_implementation",
                "priority": "high",
                "source": "ai-event-manager",
                "details": rec.get("recommendations", []),
                "estimated_effort": "medium"
            })

        # Средние → в бэклог
        elif importance > 0.5:
            tasks.append({
                "title": f"Review event: {event_name}",
                "type": "event_review",
                "priority": "medium",
                "source": "ai-event-manager",
                "details": rec.get("recommendations", []),
                "estimated_effort": "low"
            })

    return tasks
