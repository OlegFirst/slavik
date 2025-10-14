"""
Escalation Manager - Escalates Complex Problems to Brain

Управляет эскалацией сложных проблем к Workflow Intelligence (мозгу)
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class EscalationRequest:
    """Запрос на эскалацию к мозгу"""
    escalation_id: str
    problem: Dict[str, Any]
    severity: str
    context: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    escalated_at: str
    reason: str
    status: str = "pending"  # pending, sent, received, resolved


class EscalationManager:
    """
    Менеджер эскалаций к мозгу

    Отвечает за:
    - Формирование запроса к мозгу
    - Отправку эскалации
    - Отслеживание статуса
    - Получение решения от мозга
    """

    def __init__(self):
        """Инициализация"""
        self.escalations = {}  # escalation_id -> EscalationRequest
        self.escalation_counter = 0

    async def escalate_to_brain(
        self,
        problem: Dict[str, Any],
        severity: str,
        context: Dict[str, Any],
        recommendations: Optional[List[Dict]] = None,
        reason: str = "complex_problem"
    ) -> EscalationRequest:
        """
        Эскалирует проблему к мозгу

        Args:
            problem: Описание проблемы
            severity: Серьёзность (critical, high, medium, low)
            context: Контекст (метрики, логи, etc.)
            recommendations: Варианты решений (опционально)
            reason: Причина эскалации

        Returns:
            EscalationRequest
        """
        # Генерируем ID
        self.escalation_counter += 1
        escalation_id = f"ESC-{datetime.utcnow().strftime('%Y%m%d')}-{self.escalation_counter:04d}"

        # Создаём запрос
        escalation = EscalationRequest(
            escalation_id=escalation_id,
            problem=problem,
            severity=severity,
            context=context,
            recommendations=recommendations or [],
            escalated_at=datetime.utcnow().isoformat(),
            reason=reason,
            status="pending"
        )

        # Сохраняем
        self.escalations[escalation_id] = escalation

        logger.info(
            f"Created escalation {escalation_id}: "
            f"{problem.get('type', 'unknown')} ({severity}) - {reason}"
        )

        # Отправляем мозгу
        await self._send_to_brain(escalation)

        return escalation

    async def _send_to_brain(self, escalation: EscalationRequest):
        """
        Отправляет эскалацию мозгу

        TODO: Реальная отправка через workflow_intelligence_client
        """
        try:
            logger.info(f"Sending escalation {escalation.escalation_id} to Brain")

            # Формируем сообщение
            message = {
                "escalation_id": escalation.escalation_id,
                "problem": escalation.problem,
                "severity": escalation.severity,
                "context": escalation.context,
                "recommendations": escalation.recommendations,
                "escalated_at": escalation.escalated_at,
                "reason": escalation.reason,
                "asking_for": "decision",
                "from": "mio_manager"
            }

            # TODO: Реальная отправка
            # await workflow_intelligence_client.report_problem(message)

            # Обновляем статус
            escalation.status = "sent"

            logger.info(f"Escalation {escalation.escalation_id} sent to Brain")

        except Exception as e:
            logger.error(f"Error sending escalation {escalation.escalation_id}: {e}")
            escalation.status = "error"

    async def receive_directive(
        self,
        escalation_id: str,
        directive: Dict[str, Any]
    ) -> bool:
        """
        Получает решение от мозга

        Args:
            escalation_id: ID эскалации
            directive: Указание от мозга

        Returns:
            True if received successfully
        """
        if escalation_id not in self.escalations:
            logger.error(f"Unknown escalation ID: {escalation_id}")
            return False

        escalation = self.escalations[escalation_id]

        logger.info(
            f"Received directive from Brain for {escalation_id}: "
            f"{directive.get('action', 'unknown')}"
        )

        # Сохраняем решение в context
        escalation.context["directive"] = directive
        escalation.context["directive_received_at"] = datetime.utcnow().isoformat()
        escalation.status = "received"

        return True

    async def mark_resolved(
        self,
        escalation_id: str,
        result: Dict[str, Any]
    ):
        """
        Отмечает эскалацию как решённую

        Args:
            escalation_id: ID эскалации
            result: Результат выполнения
        """
        if escalation_id not in self.escalations:
            logger.error(f"Unknown escalation ID: {escalation_id}")
            return

        escalation = self.escalations[escalation_id]

        logger.info(f"Escalation {escalation_id} resolved: {result.get('status', 'unknown')}")

        # Сохраняем результат
        escalation.context["result"] = result
        escalation.context["resolved_at"] = datetime.utcnow().isoformat()
        escalation.status = "resolved"

        # TODO: Отправляем результат мозгу (feedback loop)
        await self._report_result_to_brain(escalation, result)

    async def _report_result_to_brain(
        self,
        escalation: EscalationRequest,
        result: Dict[str, Any]
    ):
        """Отправляет результат мозгу (для learning)"""
        try:
            logger.info(f"Reporting result to Brain for {escalation.escalation_id}")

            message = {
                "escalation_id": escalation.escalation_id,
                "problem": escalation.problem,
                "directive": escalation.context.get("directive"),
                "result": result,
                "resolved_at": escalation.context.get("resolved_at")
            }

            # TODO: Реальная отправка
            # await workflow_intelligence_client.report_result(message)

            logger.info(f"Result reported for {escalation.escalation_id}")

        except Exception as e:
            logger.error(f"Error reporting result for {escalation.escalation_id}: {e}")

    def get_pending_escalations(self) -> List[EscalationRequest]:
        """Возвращает ожидающие эскалации"""
        return [
            e for e in self.escalations.values()
            if e.status in ["pending", "sent"]
        ]

    def get_escalation(self, escalation_id: str) -> Optional[EscalationRequest]:
        """Возвращает эскалацию по ID"""
        return self.escalations.get(escalation_id)

    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику эскалаций"""
        total = len(self.escalations)
        if total == 0:
            return {
                "total": 0,
                "by_status": {},
                "by_severity": {},
                "avg_resolution_time": 0
            }

        by_status = {}
        by_severity = {}
        resolution_times = []

        for escalation in self.escalations.values():
            # By status
            by_status[escalation.status] = by_status.get(escalation.status, 0) + 1

            # By severity
            by_severity[escalation.severity] = by_severity.get(escalation.severity, 0) + 1

            # Resolution time
            if escalation.status == "resolved":
                escalated_at = datetime.fromisoformat(escalation.escalated_at)
                resolved_at = datetime.fromisoformat(escalation.context["resolved_at"])
                resolution_time = (resolved_at - escalated_at).total_seconds()
                resolution_times.append(resolution_time)

        avg_resolution_time = (
            sum(resolution_times) / len(resolution_times)
            if resolution_times
            else 0
        )

        return {
            "total": total,
            "by_status": by_status,
            "by_severity": by_severity,
            "avg_resolution_time": avg_resolution_time
        }
