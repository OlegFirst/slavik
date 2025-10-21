#!/usr/bin/env python3
"""
AI Workflow Optimizer Client
Интеграция MIO Manager с AI Workflow Optimizer (ML-модели)
"""

import httpx
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class WorkflowOptimizerClient:
    """
    Клиент для ML-оптимизации и предсказаний

    Использует AI Workflow Optimizer для:
    - Предсказания времени выполнения
    - Обнаружения anomalies
    - Оптимизации ресурсов
    - Анализа bottlenecks
    """

    def __init__(self, optimizer_url: str = "http://localhost:8051"):
        self.base_url = optimizer_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def predict_execution_time(
        self,
        process_type: str,
        process_data: Dict
    ) -> Dict:
        """
        Предсказать время выполнения процесса

        Returns:
            {
                'predicted_minutes': 45.2,
                'confidence': 0.87,
                'factors': {
                    'complexity': 'high',
                    'resource_count': 3
                }
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/predict/execution-time",
                json={
                    "process_type": process_type,
                    "process_data": process_data
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.info(
                f" Predicted execution time: {result['predicted_minutes']}min "
                f"(confidence: {result['confidence']*100:.1f}%)"
            )
            return result

        except Exception as e:
            logger.error(f" Failed to predict execution time: {e}")
            return {
                "predicted_minutes": None,
                "confidence": 0.0,
                "error": str(e)
            }

    async def detect_anomalies(
        self,
        process_id: str,
        metrics: Dict
    ) -> Dict:
        """
        Обнаружить anomalies в метриках процесса

        Returns:
            {
                'is_anomaly': True/False,
                'anomaly_score': 0.85,
                'anomalous_features': ['execution_time', 'failure_rate'],
                'risk_level': 'high',
                'recommendations': [...]
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/detect/anomalies",
                json={
                    "process_id": process_id,
                    "metrics": metrics
                }
            )
            response.raise_for_status()
            result = response.json()

            if result.get('is_anomaly'):
                logger.warning(
                    f"️  Anomaly detected for {process_id}: "
                    f"score={result['anomaly_score']:.2f}, "
                    f"risk={result['risk_level']}"
                )
            else:
                logger.info(f" No anomalies detected for {process_id}")

            return result

        except Exception as e:
            logger.error(f" Failed to detect anomalies: {e}")
            return {
                "is_anomaly": False,
                "error": str(e)
            }

    async def analyze_bottlenecks(
        self,
        process_id: str,
        execution_data: Dict
    ) -> Dict:
        """
        Анализ bottlenecks в процессе

        Returns:
            {
                'bottlenecks': [
                    {
                        'step': 'dependency_analysis',
                        'severity': 'high',
                        'impact_minutes': 15.3,
                        'frequency': 0.8
                    }
                ],
                'recommendations': [...]
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/analyze/bottlenecks",
                json={
                    "process_id": process_id,
                    "execution_data": execution_data
                }
            )
            response.raise_for_status()
            result = response.json()

            if result.get('bottlenecks'):
                logger.warning(
                    f"️  Found {len(result['bottlenecks'])} bottlenecks in {process_id}"
                )
            else:
                logger.info(f" No bottlenecks found in {process_id}")

            return result

        except Exception as e:
            logger.error(f" Failed to analyze bottlenecks: {e}")
            return {
                "bottlenecks": [],
                "error": str(e)
            }

    async def optimize_resources(
        self,
        process_id: str,
        current_allocation: Dict,
        optimization_goals: List[str]
    ) -> Dict:
        """
        Оптимизация распределения ресурсов

        Args:
            optimization_goals: ['reduce_time', 'reduce_cost', 'improve_quality']

        Returns:
            {
                'current_allocation': {...},
                'recommended_allocation': {...},
                'expected_improvement': {
                    'time_reduction_percent': 25.0,
                    'cost_reduction_percent': 15.0
                }
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/optimize/resources",
                json={
                    "process_id": process_id,
                    "current_allocation": current_allocation,
                    "optimization_goals": optimization_goals
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.info(
                f" Optimized resources for {process_id}: "
                f"time reduction={result['expected_improvement'].get('time_reduction_percent', 0):.1f}%"
            )
            return result

        except Exception as e:
            logger.error(f" Failed to optimize resources: {e}")
            return {
                "current_allocation": current_allocation,
                "recommended_allocation": current_allocation,
                "error": str(e)
            }

    async def get_optimization_recommendations(
        self,
        process_id: str,
        historical_data: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Получить рекомендации по оптимизации

        Returns:
            [
                {
                    'recommendation': 'Reduce dependency analysis frequency',
                    'expected_impact': 'Save 10 minutes per execution',
                    'confidence': 0.85,
                    'priority': 'high'
                }
            ]
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/recommendations/optimize",
                json={
                    "process_id": process_id,
                    "historical_data": historical_data
                }
            )
            response.raise_for_status()
            recommendations = response.json()

            logger.info(f" Got {len(recommendations)} optimization recommendations")
            return recommendations

        except Exception as e:
            logger.error(f" Failed to get recommendations: {e}")
            return []

    async def predict_success_probability(
        self,
        process_type: str,
        process_params: Dict
    ) -> Dict:
        """
        Предсказать вероятность успеха

        Returns:
            {
                'success_probability': 0.92,
                'confidence': 0.88,
                'risk_factors': [
                    {'factor': 'high_complexity', 'impact': -0.15}
                ]
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/predict/success",
                json={
                    "process_type": process_type,
                    "process_params": process_params
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.info(
                f" Predicted success probability: {result['success_probability']*100:.1f}%"
            )
            return result

        except Exception as e:
            logger.error(f" Failed to predict success probability: {e}")
            return {
                "success_probability": 0.5,
                "confidence": 0.0,
                "error": str(e)
            }

    async def record_execution(
        self,
        process_id: str,
        execution_data: Dict
    ) -> Dict:
        """
        Записать выполнение процесса для обучения ML моделей

        Args:
            execution_data: {
                'execution_time_minutes': 45.2,
                'success': True,
                'resource_count': 3,
                'bottlenecks': [...],
                'metadata': {...}
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/executions/record",
                json={
                    "process_id": process_id,
                    "execution_data": execution_data
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f" Recorded execution for {process_id}")
            return result

        except Exception as e:
            logger.error(f" Failed to record execution: {e}")
            return {"error": str(e)}

    # ========================================================================
    # НОВЫЕ МЕТОДЫ ДЛЯ MIO MANAGER V2.0 (ЕЖЕДНЕВНЫЙ АНАЛИЗ)
    # ========================================================================

    async def analyze_system_performance(
        self,
        system_metrics: Dict,
        timeframe: str = '24h'
    ) -> Dict:
        """
        Глубокий анализ производительности системы

        Для ежедневного цикла SmartScheduler (03:00 AM).

        Args:
            system_metrics: Метрики всей системы
            timeframe: Период анализа (24h, 7d, 30d)

        Returns:
            {
                'overall_health_score': 0.87,
                'bottlenecks': [
                    {
                        'service': 'api-gateway',
                        'issue': 'High latency',
                        'impact': 'medium',
                        'recommendation': 'Enable caching',
                        'estimated_improvement': '30%'
                    }
                ],
                'optimization_opportunities': [
                    {
                        'area': 'memory_usage',
                        'current': '85%',
                        'target': '60%',
                        'actions': ['Scale down X', 'Optimize Y'],
                        'priority': 'medium'
                    }
                ],
                'cost_savings': {
                    'potential_monthly_usd': 1200,
                    'actions': [...]
                },
                'performance_trends': {
                    'improving': ['latency', 'throughput'],
                    'degrading': ['error_rate'],
                    'stable': ['cpu_usage']
                },
                'recommendations': [
                    {
                        'recommendation': 'Scale down orchestrator',
                        'reason': 'Low utilization (15%)',
                        'impact': 'High',
                        'effort': 'Low'
                    }
                ]
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/analyze/system-performance",
                json={
                    'system_metrics': system_metrics,
                    'timeframe': timeframe,
                    'analysis_depth': 'deep'
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.info(
                f" System Performance Analysis: "
                f"health_score={result.get('overall_health_score', 0):.2f}, "
                f"bottlenecks={len(result.get('bottlenecks', []))}"
            )

            return result

        except Exception as e:
            logger.error(f" Failed to analyze system performance: {e}")
            return {
                'overall_health_score': 0.0,
                'bottlenecks': [],
                'optimization_opportunities': [],
                'error': str(e)
            }

    async def get_recommendations(
        self,
        service: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Dict]:
        """
        Получить рекомендации по оптимизации

        Args:
            service: Конкретный сервис (опционально)
            category: Категория (performance, cost, reliability)

        Returns:
            [
                {
                    'recommendation_id': 'REC-001',
                    'service': 'api-gateway',
                    'category': 'performance',
                    'recommendation': 'Enable response caching',
                    'impact': 'high',
                    'effort': 'low',
                    'estimated_improvement': '40% latency reduction',
                    'priority': 8
                }
            ]
        """
        try:
            params = {}
            if service:
                params['service'] = service
            if category:
                params['category'] = category

            response = await self.client.get(
                f"{self.base_url}/api/recommendations",
                params=params
            )
            response.raise_for_status()
            recommendations = response.json()

            logger.info(f" Got {len(recommendations)} optimization recommendations")

            return recommendations

        except Exception as e:
            logger.error(f" Failed to get recommendations: {e}")
            return []

    async def predict_resource_needs(
        self,
        horizon: str = '7d'
    ) -> Dict:
        """
        Предсказать потребности в ресурсах

        Args:
            horizon: Горизонт предсказания (1d, 7d, 30d)

        Returns:
            {
                'horizon': '7d',
                'predictions': {
                    'cpu': {
                        'current_average': 45.2,
                        'predicted_average': 62.3,
                        'predicted_peak': 89.5,
                        'recommendation': 'No action needed'
                    },
                    'memory': {
                        'current_average': 68.1,
                        'predicted_average': 75.4,
                        'predicted_peak': 92.3,
                        'recommendation': 'Consider adding 1 node'
                    }
                },
                'scaling_recommendations': [
                    {
                        'service': 'workflow-intelligence',
                        'action': 'scale_up',
                        'when': '2025-10-10',
                        'reason': 'Predicted load increase'
                    }
                ]
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/predict/resource-needs",
                json={'horizon': horizon}
            )
            response.raise_for_status()
            result = response.json()

            logger.info(
                f" Resource needs predicted for {horizon}: "
                f"{len(result.get('scaling_recommendations', []))} actions suggested"
            )

            return result

        except Exception as e:
            logger.error(f" Failed to predict resource needs: {e}")
            return {
                'horizon': horizon,
                'predictions': {},
                'scaling_recommendations': [],
                'error': str(e)
            }

    async def health_check(self) -> Dict:
        """
        Проверить доступность Workflow Optimizer

        Returns:
            {
                'status': 'healthy',
                'service': 'workflow_optimizer',
                'ml_models_loaded': 5,
                'version': '1.0.0'
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
            logger.error(f" Workflow Optimizer health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

    async def close(self):
        """Закрыть HTTP клиент"""
        await self.client.aclose()
