"""
Integration: AI Event Manager ↔ МиО Manager

Координация между AI Event Manager и МиО Manager:
- AI Event Manager специализируется на событиях
- МиО Manager координирует все AI-office работы
- Взаимный обмен insights и задачами
"""

import logging
import httpx
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class MioIntegration:
    """
    Интеграция с МиО Manager

    МиО Manager - правая рука, координатор всех задач
    AI Event Manager - специалист по событиям
    """

    def __init__(self, mio_url: str = "http://localhost:8046"):
        self.mio_url = mio_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def report_event_insights(self, insights: Dict) -> bool:
        """
        Отчитывается МиО Manager о находках по событиям

        Args:
            insights: {
                "critical_gaps": int,
                "recommendations": List,
                "predictions": List
            }
        """
        try:
            logger.info(f" Reporting event insights to МиО Manager...")

            # Формируем отчёт
            report = {
                "source": "ai-event-manager",
                "type": "event_intelligence_insights",
                "severity": self._calculate_severity(insights),
                "data": insights,
                "recommendations": self._format_recommendations(insights)
            }

            # Отправляем МиО Manager
            response = await self.client.post(
                f"{self.mio_url}/api/insights/receive",
                json=report
            )

            if response.status_code == 200:
                logger.info(" Insights delivered to МиО Manager")
                return True
            else:
                logger.warning(f"️ МиО Manager response: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f" Error reporting to МиО: {e}")
            return False

    async def request_task_execution(self, task: Dict) -> Optional[str]:
        """
        Запрашивает выполнение задачи через МиО Manager

        МиО Manager решит:
        - Выполнить самому
        - Делегировать Orchestrator
        - Запросить одобрение человека

        Returns:
            task_id или None
        """
        try:
            logger.info(f" Requesting task execution: {task.get('title')}")

            response = await self.client.post(
                f"{self.mio_url}/api/tasks/delegate",
                json={
                    "source": "ai-event-manager",
                    "task": task,
                    "priority": task.get("priority", "medium")
                }
            )

            if response.status_code == 200:
                result = response.json()
                task_id = result.get("task_id")
                logger.info(f" Task delegated: {task_id}")
                return task_id

        except Exception as e:
            logger.error(f" Error delegating task: {e}")

        return None

    async def get_coordination_context(self) -> Dict:
        """
        Получает контекст от МиО Manager

        Returns:
            {
                "active_tasks": List,
                "system_health": str,
                "priorities": List
            }
        """
        try:
            response = await self.client.get(
                f"{self.mio_url}/api/context"
            )

            if response.status_code == 200:
                return response.json()

        except Exception as e:
            logger.warning(f"️ Could not get context from МиО: {e}")

        return {"active_tasks": [], "system_health": "unknown", "priorities": []}

    def _calculate_severity(self, insights: Dict) -> str:
        """Вычисляет severity для МиО Manager"""
        critical_gaps = insights.get("critical_gaps", 0)

        if critical_gaps > 5:
            return "critical"
        elif critical_gaps > 2:
            return "warning"
        else:
            return "info"

    def _format_recommendations(self, insights: Dict) -> list:
        """Форматирует рекомендации для МиО Manager"""
        recommendations = insights.get("recommendations", [])

        formatted = []
        for rec in recommendations[:5]:  # Top 5
            formatted.append({
                "event_name": rec.get("event_name"),
                "action": "implement" if rec.get("importance", 0) > 0.7 else "review",
                "priority": "high" if rec.get("importance", 0) > 0.8 else "medium"
            })

        return formatted

    async def close(self):
        """Закрывает клиент"""
        await self.client.aclose()


# ============================================================================
# Integration Endpoint для МиО Manager
# ============================================================================

async def handle_mio_request(request_type: str, data: Dict) -> Dict:
    """
    Обрабатывает запросы от МиО Manager

    МиО может запросить:
    - event_analysis: анализ конкретного события
    - recommendations: топ рекомендации
    - predictions: предсказания
    - learning_status: состояние обучения
    """

    if request_type == "event_analysis":
        # Анализируем событие
        from intelligent_core.event_intelligence import EventAnalyzer

        analyzer = EventAnalyzer()
        analysis = await analyzer.analyze_event(
            event_name=data.get("event_name"),
            publishers=data.get("publishers", []),
            subscribers=data.get("subscribers", [])
        )

        return {
            "status": "success",
            "analysis": {
                "importance": analysis.importance_score,
                "pattern": analysis.usage_pattern,
                "recommendations": analysis.recommendations,
                "insights": analysis.ai_insights
            }
        }

    elif request_type == "recommendations":
        # Возвращаем рекомендации
        # (используем существующий endpoint)
        return {
            "status": "success",
            "message": "Use GET /recommendations endpoint"
        }

    elif request_type == "health_check":
        return {
            "status": "healthy",
            "service": "ai-event-manager",
            "capabilities": [
                "event_analysis",
                "learning",
                "predictions",
                "recommendations"
            ]
        }

    else:
        return {
            "status": "error",
            "message": f"Unknown request type: {request_type}"
        }
