"""
Predictive Service Client
==========================

Интеграция MIO Manager с Predictive Service для:
- Предсказания нагрузки (load spikes)
- Детекция аномалий
- Прогноз использования ресурсов
- Превентивные действия

Критично для:
- L2 Quick Response (превентивное масштабирование)
- Observation (детекция будущих проблем)
- Reporting (прогнозы в отчетах)
"""

import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class PredictiveClient:
    """
    Клиент для взаимодействия с Predictive Service

    Predictive Service предоставляет:
    - ML предсказания нагрузки
    - Anomaly detection
    - Resource forecasting
    - Proactive recommendations
    """

    def __init__(self, base_url: str = "http://localhost:8052"):
        """
        Args:
            base_url: URL Predictive Service (по умолчанию http://localhost:8052)
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"PredictiveClient initialized: {base_url}")

    async def predict_load_spike(
        self,
        service: str,
        horizon: str = '1h',
        current_metrics: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Предсказать скачок нагрузки

        Args:
            service: Имя сервиса (api-gateway, workflow-intelligence, etc.)
            horizon: Горизонт предсказания (1h, 6h, 24h)
            current_metrics: Текущие метрики для контекста

        Returns:
            {
                'spike_predicted': True/False,
                'spike_probability': 0.85,
                'predicted_load': 1500,  # requests/sec
                'current_load': 800,
                'increase_percentage': 87.5,
                'horizon': '1h',
                'confidence': 0.82,
                'recommendation': 'Scale up preventively'
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/predict/load-spike",
                json={
                    'service': service,
                    'horizon': horizon,
                    'current_metrics': current_metrics or {},
                    'requested_at': datetime.utcnow().isoformat()
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.info(
                f"Load prediction for {service}: "
                f"spike={result.get('spike_predicted')}, "
                f"probability={result.get('spike_probability', 0):.2f}"
            )

            return result

        except httpx.HTTPStatusError as e:
            logger.error(f"Predictive Service error {e.response.status_code}: {e}")
            return self._fallback_prediction()

        except Exception as e:
            logger.error(f"Failed to get load prediction: {e}")
            return self._fallback_prediction()

    async def detect_anomalies(
        self,
        metrics: Dict[str, Any],
        baseline: Optional[Dict[str, Any]] = None,
        sensitivity: str = 'medium'
    ) -> List[Dict[str, Any]]:
        """
        Детектировать аномалии в метриках

        Args:
            metrics: Текущие метрики
            baseline: Базовая линия (исторические данные)
            sensitivity: Чувствительность (low, medium, high)

        Returns:
            [
                {
                    'metric': 'cpu_usage',
                    'current_value': 95.5,
                    'expected_value': 45.2,
                    'deviation': 50.3,
                    'severity': 'high',
                    'anomaly_type': 'spike',
                    'confidence': 0.94
                }
            ]
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/detect/anomalies",
                json={
                    'metrics': metrics,
                    'baseline': baseline or {},
                    'sensitivity': sensitivity,
                    'detected_at': datetime.utcnow().isoformat()
                }
            )
            response.raise_for_status()
            result = response.json()

            anomalies = result.get('anomalies', [])

            if anomalies:
                logger.warning(f"Detected {len(anomalies)} anomalies")

            return anomalies

        except Exception as e:
            logger.error(f"Failed to detect anomalies: {e}")
            return []

    async def forecast_resource_usage(
        self,
        service: str,
        resource_type: str,
        horizon: str = '24h'
    ) -> Dict[str, Any]:
        """
        Прогноз использования ресурсов

        Args:
            service: Имя сервиса
            resource_type: Тип ресурса (cpu, memory, disk, network)
            horizon: Горизонт прогноза (6h, 24h, 7d)

        Returns:
            {
                'service': 'workflow-intelligence',
                'resource': 'memory',
                'current_usage': 2.1,  # GB
                'predicted_usage': 3.8,  # GB
                'predicted_at': '2025-10-08T12:00:00Z',
                'forecast': [
                    {'time': '06:00', 'value': 2.3},
                    {'time': '12:00', 'value': 3.8},
                    {'time': '18:00', 'value': 3.2}
                ],
                'recommendation': 'No action needed',
                'confidence': 0.87
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/forecast/resources",
                json={
                    'service': service,
                    'resource_type': resource_type,
                    'horizon': horizon,
                    'requested_at': datetime.utcnow().isoformat()
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.info(
                f"Resource forecast for {service}/{resource_type}: "
                f"current={result.get('current_usage')}, "
                f"predicted={result.get('predicted_usage')}"
            )

            return result

        except Exception as e:
            logger.error(f"Failed to get resource forecast: {e}")
            return {
                'service': service,
                'resource': resource_type,
                'error': str(e)
            }

    async def get_proactive_recommendations(
        self,
        system_metrics: Dict[str, Any],
        timeframe: str = '1h'
    ) -> List[Dict[str, Any]]:
        """
        Получить проактивные рекомендации

        Args:
            system_metrics: Метрики всей системы
            timeframe: Временной период анализа

        Returns:
            [
                {
                    'recommendation': 'Scale up api-gateway',
                    'reason': 'Predicted load spike in 45 minutes',
                    'priority': 'high',
                    'confidence': 0.89,
                    'estimated_impact': 'Prevent 95% of potential issues',
                    'suggested_action': {
                        'action': 'scale_up',
                        'service': 'api-gateway',
                        'replicas': 3
                    }
                }
            ]
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/recommendations/proactive",
                json={
                    'system_metrics': system_metrics,
                    'timeframe': timeframe,
                    'requested_at': datetime.utcnow().isoformat()
                }
            )
            response.raise_for_status()
            result = response.json()

            recommendations = result.get('recommendations', [])

            if recommendations:
                logger.info(f"Received {len(recommendations)} proactive recommendations")

            return recommendations

        except Exception as e:
            logger.error(f"Failed to get proactive recommendations: {e}")
            return []

    async def analyze_trend(
        self,
        metric_name: str,
        metric_values: List[float],
        timestamps: List[str]
    ) -> Dict[str, Any]:
        """
        Анализ тренда метрики

        Args:
            metric_name: Название метрики
            metric_values: Значения метрики
            timestamps: Временные метки

        Returns:
            {
                'metric': 'cpu_usage',
                'trend': 'increasing',  # increasing, decreasing, stable, volatile
                'trend_strength': 0.75,
                'predicted_next': 82.3,
                'will_exceed_threshold': True,
                'threshold': 80.0,
                'time_to_threshold': '2h 15m',
                'recommendation': 'Monitor closely'
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/analyze/trend",
                json={
                    'metric_name': metric_name,
                    'metric_values': metric_values,
                    'timestamps': timestamps,
                    'analyzed_at': datetime.utcnow().isoformat()
                }
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Failed to analyze trend: {e}")
            return {'error': str(e)}

    async def predict_incident_probability(
        self,
        current_state: Dict[str, Any],
        incident_type: str
    ) -> Dict[str, Any]:
        """
        Предсказать вероятность инцидента

        Args:
            current_state: Текущее состояние системы
            incident_type: Тип инцидента (outage, performance_degradation, security_breach)

        Returns:
            {
                'incident_type': 'outage',
                'probability': 0.23,
                'risk_level': 'medium',
                'contributing_factors': [
                    'High memory usage',
                    'Increasing error rate'
                ],
                'prevention_actions': [
                    'Scale up memory',
                    'Investigate error sources'
                ],
                'confidence': 0.81
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/predict/incident",
                json={
                    'current_state': current_state,
                    'incident_type': incident_type,
                    'predicted_at': datetime.utcnow().isoformat()
                }
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Failed to predict incident probability: {e}")
            return {
                'incident_type': incident_type,
                'probability': 0.0,
                'error': str(e)
            }

    async def health_check(self) -> Dict[str, Any]:
        """
        Проверить доступность Predictive Service

        Returns:
            {
                'status': 'healthy',
                'service': 'predictive',
                'version': '1.0.0',
                'ml_models_loaded': 5,
                'uptime_seconds': 86400
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
            logger.error(f"Predictive Service health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

    def _fallback_prediction(self) -> Dict[str, Any]:
        """Fallback предсказание если сервис недоступен"""
        return {
            'spike_predicted': False,
            'spike_probability': 0.0,
            'confidence': 0.0,
            'error': 'Predictive Service unavailable',
            'fallback': True
        }

    async def close(self):
        """Закрыть HTTP клиент"""
        await self.client.aclose()


# Convenience instance
_predictive_client: Optional[PredictiveClient] = None


def get_predictive_client(base_url: str = "http://localhost:8052") -> PredictiveClient:
    """
    Получить singleton instance PredictiveClient

    Usage:
        client = get_predictive_client()
        prediction = await client.predict_load_spike('api-gateway')
    """
    global _predictive_client

    if _predictive_client is None:
        _predictive_client = PredictiveClient(base_url)

    return _predictive_client
