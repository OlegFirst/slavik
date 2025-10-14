#!/usr/bin/env python3
"""
Workflow Intelligence Client
Интеграция MIO Manager с Workflow Intelligence Engine
"""

import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WorkflowIntelligenceClient:
    """
    Клиент для взаимодействия с Workflow Intelligence Engine

    Использует Workflow Intelligence для:
    - Создания воркфлоу реакций на проблемы
    - Управления State Machine для процессов исправления
    - Обучения на успешных cases
    - AI-рекомендаций по следующим шагам
    """

    def __init__(self, workflow_intelligence_url: str = "http://localhost:8050"):
        self.base_url = workflow_intelligence_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def create_incident_workflow(
        self,
        incident_type: str,
        incident_data: Dict,
        severity: str
    ) -> Dict:
        """
        Создать workflow для реагирования на инцидент

        Args:
            incident_type: security | service_down | high_complexity | circular_dependency
            incident_data: Детали проблемы
            severity: low | medium | high | critical

        Returns:
            {
                'workflow_id': '...',
                'current_state': 'detected',
                'next_steps': ['analyze', 'create_task', 'delegate'],
                'ai_recommendations': [...]
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/workflows/create",
                json={
                    "workflow_type": f"incident_{incident_type}",
                    "initial_state": "detected",
                    "context": {
                        "incident_type": incident_type,
                        "incident_data": incident_data,
                        "severity": severity,
                        "detected_at": datetime.utcnow().isoformat(),
                        "source": "mio_manager"
                    }
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"✅ Created {incident_type} workflow: {result['workflow_id']}")
            return result

        except Exception as e:
            logger.error(f"❌ Failed to create incident workflow: {e}")
            return {
                "workflow_id": None,
                "error": str(e),
                "fallback": True
            }

    async def transition_workflow(
        self,
        workflow_id: str,
        to_state: str,
        action_data: Optional[Dict] = None
    ) -> Dict:
        """
        Переместить workflow в следующее состояние

        States для incident workflows:
        - detected → analyzing → task_created → delegated → in_progress → resolved → closed
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/workflows/{workflow_id}/transition",
                json={
                    "to_state": to_state,
                    "action_data": action_data or {},
                    "transitioned_at": datetime.utcnow().isoformat()
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"✅ Workflow {workflow_id}: {result['previous_state']} → {to_state}")
            return result

        except Exception as e:
            logger.error(f"❌ Failed to transition workflow {workflow_id}: {e}")
            return {"error": str(e)}

    async def get_ai_recommendations(
        self,
        workflow_id: str,
        current_context: Dict
    ) -> List[Dict]:
        """
        Получить AI рекомендации по следующим шагам

        Использует:
        - Case Library (похожие успешные cases)
        - AI Advisor (контекстные советы)
        - ML Predictor (вероятность успеха)
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/ai/recommendations",
                json={
                    "workflow_id": workflow_id,
                    "context": current_context
                }
            )
            response.raise_for_status()
            recommendations = response.json()

            logger.info(f"✅ Got {len(recommendations)} AI recommendations for {workflow_id}")
            return recommendations

        except Exception as e:
            logger.error(f"❌ Failed to get AI recommendations: {e}")
            return []

    async def save_successful_case(
        self,
        workflow_id: str,
        incident_type: str,
        resolution_data: Dict,
        outcome_metrics: Dict
    ) -> Dict:
        """
        Сохранить успешный case в Case Library

        Этот case будет использоваться для:
        - Обучения ML моделей
        - Рекомендаций в похожих ситуациях
        - Benchmarking
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/case-library/save",
                json={
                    "workflow_id": workflow_id,
                    "case_type": incident_type,
                    "resolution_data": resolution_data,
                    "outcome_metrics": outcome_metrics,
                    "saved_at": datetime.utcnow().isoformat()
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"✅ Saved successful case: {result['case_id']}")
            return result

        except Exception as e:
            logger.error(f"❌ Failed to save case: {e}")
            return {"error": str(e)}

    async def find_similar_cases(
        self,
        incident_type: str,
        incident_data: Dict,
        limit: int = 5
    ) -> List[Dict]:
        """
        Найти похожие успешные cases

        Использует:
        - Vector similarity search
        - Context matching
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/case-library/find-similar",
                json={
                    "incident_type": incident_type,
                    "incident_data": incident_data,
                    "limit": limit
                }
            )
            response.raise_for_status()
            cases = response.json()

            logger.info(f"✅ Found {len(cases)} similar cases")
            return cases

        except Exception as e:
            logger.error(f"❌ Failed to find similar cases: {e}")
            return []

    async def get_workflow_status(self, workflow_id: str) -> Dict:
        """Получить текущий статус workflow"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/workflows/{workflow_id}/status"
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"❌ Failed to get workflow status: {e}")
            return {"error": str(e)}

    async def predict_resolution_time(
        self,
        incident_type: str,
        incident_data: Dict
    ) -> Dict:
        """
        Предсказать время на исправление

        Использует ML модели Workflow Intelligence
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/ml/predict/resolution-time",
                json={
                    "incident_type": incident_type,
                    "incident_data": incident_data
                }
            )
            response.raise_for_status()
            prediction = response.json()

            logger.info(f"✅ Predicted resolution time: {prediction['estimated_minutes']} min")
            return prediction

        except Exception as e:
            logger.error(f"❌ Failed to predict resolution time: {e}")
            return {
                "estimated_minutes": None,
                "confidence": 0.0,
                "error": str(e)
            }

    async def check_governance_rules(
        self,
        workflow_id: str,
        planned_action: Dict
    ) -> Dict:
        """
        Проверить действие против Governance Rules

        Returns:
            {
                'allowed': True/False,
                'requires_approval': True/False,
                'safety_warnings': [...],
                'creative_zone': True/False
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/governance/check",
                json={
                    "workflow_id": workflow_id,
                    "planned_action": planned_action
                }
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"❌ Failed to check governance rules: {e}")
            return {
                "allowed": False,
                "error": str(e)
            }

    # ========================================================================
    # НОВЫЕ МЕТОДЫ ДЛЯ MIO MANAGER V2.0 (КРИТИЧНЫЕ)
    # ========================================================================

    async def escalate_problem(
        self,
        problem: Dict[str, Any],
        severity: str,
        context: Dict[str, Any],
        recommendations: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Эскалировать проблему Level 3 к мозгу

        Это главный метод для L3 эскалаций из ReactionWorkflow.

        Args:
            problem: Описание проблемы
            severity: low | medium | high | critical
            context: Контекст (метрики, состояние системы)
            recommendations: Рекомендации от MIO (опционально)

        Returns:
            {
                'escalation_id': 'ESC-20251007-001',
                'status': 'escalated',
                'workflow_id': 'wf-123',
                'estimated_response_time': '5-10 minutes',
                'priority': 'high',
                'assigned_to': 'brain_decision_engine'
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/escalations/create",
                json={
                    "problem": problem,
                    "severity": severity,
                    "context": context,
                    "recommendations": recommendations or [],
                    "escalated_by": "mio_manager",
                    "escalated_at": datetime.utcnow().isoformat()
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.info(
                f"🧠 Escalated to brain: {result.get('escalation_id')} "
                f"(severity={severity})"
            )

            return result

        except Exception as e:
            logger.error(f"❌ Failed to escalate problem: {e}")
            return {
                "escalation_id": None,
                "status": "failed",
                "error": str(e)
            }

    async def get_directive(
        self,
        escalation_id: str,
        timeout: int = 300
    ) -> Optional[Dict[str, Any]]:
        """
        Получить директиву от мозга по эскалации

        Используется в ReactionWorkflow после escalate_problem.
        Polling с timeout.

        Args:
            escalation_id: ID эскалации
            timeout: Timeout в секундах (default 5 минут)

        Returns:
            {
                'directive_id': 'DIR-123',
                'escalation_id': 'ESC-20251007-001',
                'action': 'scale_up',
                'parameters': {
                    'service': 'api-gateway',
                    'replicas': 3
                },
                'reasoning': 'Based on load prediction...',
                'priority': 'high',
                'execute_immediately': True
            }

            None if timeout или нет директивы
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/escalations/{escalation_id}/directive",
                params={"timeout": timeout}
            )
            response.raise_for_status()
            directive = response.json()

            if directive and directive.get('directive_id'):
                logger.info(
                    f"📋 Received directive {directive['directive_id']} "
                    f"for escalation {escalation_id}"
                )
                return directive
            else:
                logger.warning(f"⏳ No directive yet for {escalation_id}")
                return None

        except httpx.TimeoutException:
            logger.warning(f"⏰ Timeout waiting for directive: {escalation_id}")
            return None

        except Exception as e:
            logger.error(f"❌ Failed to get directive: {e}")
            return None

    async def publish_report(
        self,
        report_type: str,
        report_data: Dict[str, Any],
        insights: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Опубликовать отчет к мозгу

        Используется в ReportingWorkflow для отправки
        daily/weekly/monthly отчетов.

        Args:
            report_type: daily | weekly | monthly | incident
            report_data: Данные отчета
            insights: Инсайты и рекомендации

        Returns:
            {
                'report_id': 'RPT-20251007-001',
                'status': 'published',
                'received_by_brain': True,
                'brain_acknowledged': True
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/reports/publish",
                json={
                    "report_type": report_type,
                    "report_data": report_data,
                    "insights": insights or [],
                    "published_by": "mio_manager",
                    "published_at": datetime.utcnow().isoformat()
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.info(
                f"📊 Published {report_type} report to brain: "
                f"{result.get('report_id')}"
            )

            return result

        except Exception as e:
            logger.error(f"❌ Failed to publish report: {e}")
            return {
                "report_id": None,
                "status": "failed",
                "error": str(e)
            }

    async def report_task_progress(
        self,
        task_id: str,
        progress: float,
        status: str,
        details: Dict[str, Any] = None
    ) -> bool:
        """
        Отчитаться о прогрессе задачи

        Используется в ControlWorkflow для периодических
        обновлений о выполнении задачи.

        Args:
            task_id: ID задачи
            progress: Прогресс 0.0 - 1.0
            status: pending | in_progress | completed | failed
            details: Дополнительные детали

        Returns:
            True если успешно
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/tasks/{task_id}/progress",
                json={
                    "progress": progress,
                    "status": status,
                    "details": details or {},
                    "reported_by": "mio_manager",
                    "reported_at": datetime.utcnow().isoformat()
                }
            )
            response.raise_for_status()

            logger.debug(
                f"✅ Reported progress for {task_id}: "
                f"{progress*100:.0f}% ({status})"
            )

            return True

        except Exception as e:
            logger.error(f"❌ Failed to report task progress: {e}")
            return False

    async def subscribe_to_directives(
        self,
        callback_url: str,
        event_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Подписаться на директивы от мозга (webhook)

        Альтернатива polling в get_directive().

        Args:
            callback_url: URL для webhook (http://mio-manager/api/directives/webhook)
            event_types: Типы событий ['directive_issued', 'task_assigned']

        Returns:
            {
                'subscription_id': 'SUB-123',
                'status': 'active',
                'callback_url': '...'
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/subscriptions/create",
                json={
                    "subscriber": "mio_manager",
                    "callback_url": callback_url,
                    "event_types": event_types or [
                        "directive_issued",
                        "task_assigned",
                        "urgent_alert"
                    ],
                    "subscribed_at": datetime.utcnow().isoformat()
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.info(
                f"📡 Subscribed to directives: {result.get('subscription_id')}"
            )

            return result

        except Exception as e:
            logger.error(f"❌ Failed to subscribe to directives: {e}")
            return {
                "subscription_id": None,
                "status": "failed",
                "error": str(e)
            }

    async def health_check(self) -> Dict[str, Any]:
        """
        Проверить доступность workflow_intelligence

        Returns:
            {
                'status': 'healthy',
                'service': 'workflow_intelligence',
                'version': '2.0.0'
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
            logger.error(f"❌ workflow_intelligence health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    async def close(self):
        """Закрыть HTTP клиент"""
        await self.client.aclose()
