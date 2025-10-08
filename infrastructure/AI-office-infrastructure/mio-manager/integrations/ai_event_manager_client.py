#!/usr/bin/env python3
"""
AI Event Manager Client
=======================

Интеграция MIO Manager с AI Event Manager для:
- Получения AI-рекомендаций по EventBus паттернам
- Анализа event-driven архитектуры
- Обучения на основе feedback
- Мониторинга learning stats

Критично для:
- Оптимизации event-driven коммуникации
- Continuous learning от реальных результатов
- Предсказания проблем в event flow
"""

import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AIEventManagerClient:
    """
    Клиент для взаимодействия с AI Event Manager

    AI Event Manager предоставляет:
    - AI-рекомендации по EventBus паттернам
    - Анализ event-driven архитектуры
    - Обучение на основе feedback
    - Мониторинг learning stats
    """

    def __init__(self, base_url: str = "http://localhost:8055"):
        """
        Args:
            base_url: URL AI Event Manager (по умолчанию http://localhost:8055)
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"AIEventManagerClient initialized: {base_url}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Проверить доступность AI Event Manager

        Returns:
            {
                'status': 'healthy',
                'service': 'ai_event_manager',
                'version': '1.0.0',
                'ai_enabled': True,
                'learning_active': True
            }
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/health",
                timeout=5.0
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"AI Event Manager health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

    async def get_recommendations(
        self,
        scope: str = 'all'
    ) -> List[Dict[str, Any]]:
        """
        Получить AI-рекомендации по EventBus паттернам

        Args:
            scope: Область рекомендаций (all, architecture, performance, reliability)

        Returns:
            [
                {
                    'id': 'REC-001',
                    'type': 'architecture',
                    'suggestion': 'Add retry logic for service-deployed events',
                    'reasoning': 'Deployment events have 15% failure rate',
                    'confidence': 0.87,
                    'impact': 'high',
                    'implementation': {
                        'publisher': 'deployment-service',
                        'subscriber': 'mio-manager',
                        'pattern': 'retry_with_backoff',
                        'config': {'max_retries': 3, 'backoff_ms': 1000}
                    }
                }
            ]
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/recommendations",
                params={'scope': scope}
            )
            response.raise_for_status()
            recommendations = response.json()

            if recommendations:
                logger.info(
                    f"📋 Received {len(recommendations)} AI recommendations (scope: {scope})"
                )

            return recommendations

        except Exception as e:
            logger.error(f"Failed to get AI recommendations: {e}")
            return []

    async def record_feedback(
        self,
        suggestion_id: str,
        decision: str,
        outcome: str
    ) -> Dict[str, Any]:
        """
        Записать feedback по рекомендации для обучения AI

        Args:
            suggestion_id: ID рекомендации
            decision: Решение (accepted, rejected, modified)
            outcome: Результат (success, failure, partial)

        Returns:
            {
                'feedback_id': 'FB-001',
                'suggestion_id': 'REC-001',
                'decision': 'accepted',
                'outcome': 'success',
                'learning_updated': True,
                'confidence_delta': 0.05
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/feedback",
                json={
                    'suggestion_id': suggestion_id,
                    'decision': decision,
                    'outcome': outcome,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.info(
                f"✅ Feedback recorded: {suggestion_id} -> {decision}/{outcome} "
                f"(learning_updated: {result.get('learning_updated')})"
            )

            return result

        except Exception as e:
            logger.error(f"Failed to record feedback: {e}")
            return {
                'error': str(e),
                'learning_updated': False
            }

    async def get_learning_stats(self) -> Dict[str, Any]:
        """
        Получить статистику обучения AI

        Returns:
            {
                'total_suggestions': 150,
                'accepted_suggestions': 98,
                'success_rate': 0.85,
                'confidence_improvement': 0.23,
                'patterns_learned': {
                    'retry_patterns': 15,
                    'circuit_breakers': 8,
                    'event_routing': 22
                },
                'recent_performance': {
                    'last_7_days': {
                        'suggestions': 25,
                        'acceptance_rate': 0.88,
                        'success_rate': 0.92
                    }
                }
            }
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/learning/stats"
            )
            response.raise_for_status()
            stats = response.json()

            logger.info(
                f"📊 Learning stats: "
                f"total={stats.get('total_suggestions', 0)}, "
                f"success_rate={stats.get('success_rate', 0):.2f}"
            )

            return stats

        except Exception as e:
            logger.error(f"Failed to get learning stats: {e}")
            return {
                'error': str(e),
                'total_suggestions': 0
            }

    async def analyze_event(
        self,
        event_name: str,
        publishers: List[str],
        subscribers: List[str]
    ) -> Dict[str, Any]:
        """
        Анализ конкретного event паттерна

        Args:
            event_name: Название события
            publishers: Список publishers
            subscribers: Список subscribers

        Returns:
            {
                'event_name': 'service.deployed',
                'analysis': {
                    'risk_level': 'medium',
                    'potential_issues': [
                        'Missing retry logic',
                        'No circuit breaker'
                    ],
                    'recommendations': [
                        {
                            'suggestion': 'Add retry with exponential backoff',
                            'priority': 'high',
                            'confidence': 0.89
                        }
                    ]
                },
                'current_patterns': {
                    'publishers': 2,
                    'subscribers': 5,
                    'avg_processing_time_ms': 150,
                    'failure_rate': 0.05
                },
                'optimization_opportunities': [
                    {
                        'area': 'resilience',
                        'improvement': 'Add circuit breaker',
                        'expected_benefit': 'Reduce cascade failures by 70%'
                    }
                ]
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/analyze/event",
                json={
                    'event_name': event_name,
                    'publishers': publishers,
                    'subscribers': subscribers,
                    'analyzed_at': datetime.utcnow().isoformat()
                }
            )
            response.raise_for_status()
            result = response.json()

            risk_level = result.get('analysis', {}).get('risk_level', 'unknown')
            logger.info(
                f"🔍 Event analysis: {event_name} -> risk_level={risk_level}"
            )

            return result

        except Exception as e:
            logger.error(f"Failed to analyze event: {e}")
            return {
                'event_name': event_name,
                'error': str(e),
                'analysis': {
                    'risk_level': 'unknown',
                    'potential_issues': [],
                    'recommendations': []
                }
            }

    async def get_architecture_insights(
        self,
        timeframe: str = '7d'
    ) -> Dict[str, Any]:
        """
        Получить insights по event-driven архитектуре

        Args:
            timeframe: Период анализа (1d, 7d, 30d)

        Returns:
            {
                'timeframe': '7d',
                'overall_health': 0.82,
                'critical_insights': [
                    {
                        'insight': 'High coupling between services A and B',
                        'severity': 'medium',
                        'recommendation': 'Introduce event mediator'
                    }
                ],
                'event_flow_efficiency': {
                    'avg_latency_ms': 85,
                    'throughput_per_sec': 450,
                    'error_rate': 0.02
                },
                'bottlenecks': [
                    {
                        'location': 'workflow-intelligence subscriber',
                        'impact': 'high',
                        'suggestion': 'Scale horizontally'
                    }
                ]
            }
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/architecture/insights",
                params={'timeframe': timeframe}
            )
            response.raise_for_status()
            insights = response.json()

            logger.info(
                f"🏗️  Architecture insights: "
                f"health={insights.get('overall_health', 0):.2f}, "
                f"critical={len(insights.get('critical_insights', []))}"
            )

            return insights

        except Exception as e:
            logger.error(f"Failed to get architecture insights: {e}")
            return {
                'timeframe': timeframe,
                'error': str(e),
                'overall_health': 0.0,
                'critical_insights': []
            }

    async def predict_event_issues(
        self,
        event_pattern: Dict[str, Any],
        horizon: str = '1h'
    ) -> Dict[str, Any]:
        """
        Предсказать потенциальные проблемы с events

        Args:
            event_pattern: Паттерн события для анализа
            horizon: Горизонт предсказания (1h, 6h, 24h)

        Returns:
            {
                'horizon': '1h',
                'predictions': [
                    {
                        'issue': 'potential_backlog',
                        'probability': 0.75,
                        'estimated_impact': 'high',
                        'preventive_actions': [
                            'Scale up consumers',
                            'Enable rate limiting'
                        ]
                    }
                ],
                'confidence': 0.82
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/predict/issues",
                json={
                    'event_pattern': event_pattern,
                    'horizon': horizon,
                    'predicted_at': datetime.utcnow().isoformat()
                }
            )
            response.raise_for_status()
            result = response.json()

            predictions = result.get('predictions', [])
            if predictions:
                logger.warning(
                    f"⚠️  Predicted {len(predictions)} potential event issues "
                    f"(horizon: {horizon})"
                )

            return result

        except Exception as e:
            logger.error(f"Failed to predict event issues: {e}")
            return {
                'horizon': horizon,
                'predictions': [],
                'error': str(e)
            }

    async def close(self):
        """Закрыть HTTP клиент"""
        await self.client.aclose()


# Convenience instance
_ai_event_manager_client: Optional[AIEventManagerClient] = None


def get_ai_event_manager_client(base_url: str = "http://localhost:8055") -> AIEventManagerClient:
    """
    Получить singleton instance AIEventManagerClient

    Usage:
        client = get_ai_event_manager_client()
        recommendations = await client.get_recommendations(scope='architecture')
    """
    global _ai_event_manager_client

    if _ai_event_manager_client is None:
        _ai_event_manager_client = AIEventManagerClient(base_url)

    return _ai_event_manager_client
