"""
Escalation Manager - Handles escalation to human operators
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..models.decision import Decision, DecisionRequest, DecisionType, DecisionOutcome
from ..models.escalation import EscalationLevel, EscalationRequest

logger = logging.getLogger(__name__)


class EscalationManager:
    """
    Управляет эскалацией решений к операторам

    Responsibilities:
    - Determine escalation level (L1-L4)
    - Calculate urgency (1-5)
    - Create escalation requests
    - Send notifications (email/Slack/SMS)
    - Track response times
    - Store escalation history
    """

    def __init__(
        self,
        notification_handler: Optional['NotificationHandler'] = None,
        storage: Optional['EscalationStorage'] = None
    ):
        """
        Initialize Escalation Manager

        Args:
            notification_handler: Handler for sending notifications (optional for MVP)
            storage: Storage for escalation history (optional for MVP)
        """
        self.notification_handler = notification_handler
        self.storage = storage

        # In-memory escalation tracking (MVP)
        self.active_escalations: Dict[str, EscalationRequest] = {}

        logger.info("Escalation Manager initialized")

    async def escalate(
        self,
        request: DecisionRequest,
        reason: str,
        policies: Optional[Dict[str, Any]] = None
    ) -> Decision:
        """
        Эскалирует решение к оператору

        Args:
            request: Original decision request
            reason: Reason for escalation
            policies: Service policies

        Returns:
            Escalated decision

        Flow:
        1. Determine escalation level (L1-L4)
        2. Calculate urgency (1-5)
        3. Create escalation request
        4. Send notifications
        5. Return ESCALATED decision
        """
        logger.info(
            f"Escalating {request.service}.{request.action}: {reason}"
        )

        # 1. Determine escalation level
        escalation_level = self._determine_escalation_level(request, policies)

        # 2. Calculate urgency
        urgency = self._calculate_urgency(request, policies)

        # 3. Create escalation request
        escalation = EscalationRequest.create(
            original_request=request,
            escalation_level=escalation_level,
            reason=reason,
            urgency=urgency,
            assigned_to=self._get_assigned_operator(escalation_level)
        )

        # Store in active escalations
        self.active_escalations[escalation.escalation_id] = escalation

        # Store in persistent storage if available
        if self.storage:
            await self.storage.store_escalation(escalation)

        # 4. Send notifications
        await self._notify_escalation(escalation)

        # 5. Create ESCALATED decision
        decision = Decision.create(
            request=request,
            decision_type=DecisionType.ESCALATED,
            outcome=DecisionOutcome.ESCALATED,
            justification=f"Escalated to {escalation_level.value}: {reason}",
            decided_by="system",
            metadata={
                "escalation_id": escalation.escalation_id,
                "escalation_level": escalation_level.value,
                "urgency": urgency,
                "assigned_to": escalation.assigned_to
            }
        )

        logger.info(
            f"Escalation created: {escalation.escalation_id} "
            f"(level={escalation_level.value}, urgency={urgency})"
        )

        return decision

    async def respond_to_escalation(
        self,
        escalation_id: str,
        approved: bool,
        operator: str,
        resolution: str
    ) -> Decision:
        """
        Обрабатывает ответ оператора на эскалацию

        Args:
            escalation_id: Escalation ID
            approved: Whether approved
            operator: Operator name
            resolution: Resolution text

        Returns:
            Final decision

        Raises:
            ValueError: If escalation not found
        """
        # Find escalation
        escalation = self.active_escalations.get(escalation_id)

        if not escalation:
            logger.error(f"Escalation not found: {escalation_id}")
            raise ValueError(f"Escalation not found: {escalation_id}")

        # Mark as resolved
        escalation.responded_at = datetime.utcnow()
        escalation.resolution = resolution

        # Update storage
        if self.storage:
            await self.storage.update_escalation(escalation)

        # Create final decision
        outcome = DecisionOutcome.APPROVED if approved else DecisionOutcome.REJECTED

        decision = Decision.create(
            request=escalation.original_request,
            decision_type=DecisionType.ESCALATED,
            outcome=outcome,
            justification=f"Human decision by {operator}: {resolution}",
            decided_by=operator,
            metadata={
                "escalation_id": escalation_id,
                "response_time_seconds": escalation.response_time_seconds()
            }
        )

        logger.info(
            f"Escalation resolved: {escalation_id} "
            f"(approved={approved}, response_time={escalation.response_time_seconds()}s)"
        )

        # Remove from active escalations
        del self.active_escalations[escalation_id]

        return decision

    def _determine_escalation_level(
        self,
        request: DecisionRequest,
        policies: Optional[Dict[str, Any]]
    ) -> EscalationLevel:
        """
        Определяет уровень эскалации

        Escalation levels:
        - L1 (Operator): Standard operations, routine issues
        - L2 (Engineer): Technical issues, repeated failures
        - L3 (Architect): Critical services, architectural changes
        - L4 (Management): Business impact, SLA violations

        Args:
            request: Decision request
            policies: Service policies

        Returns:
            Escalation level
        """
        policies = policies or {}

        # L4 Management: Critical services with business impact
        if policies.get("escalate_immediately", False):
            logger.debug("L4 Management: Critical service with immediate escalation")
            return EscalationLevel.L4_MANAGEMENT

        # L4 Management: RTO violation imminent
        rto = policies.get("rto", 300)
        downtime = request.context.get("downtime_seconds", 0)
        if downtime > rto * 0.9:  # 90% of RTO
            logger.debug(f"L4 Management: RTO violation imminent ({downtime}s > 90% of {rto}s)")
            return EscalationLevel.L4_MANAGEMENT

        # L3 Architect: Critical services
        if policies.get("critical", False):
            logger.debug("L3 Architect: Critical service")
            return EscalationLevel.L3_ARCHITECT

        # L3 Architect: Configuration changes
        if request.action == "configuration_change":
            logger.debug("L3 Architect: Configuration change")
            return EscalationLevel.L3_ARCHITECT

        # L2 Engineer: Repeated failures (pattern)
        attempts = request.context.get("recovery_attempts", 0)
        if attempts >= 3:
            logger.debug(f"L2 Engineer: Repeated failures ({attempts} attempts)")
            return EscalationLevel.L2_ENGINEER

        # L2 Engineer: High priority
        if request.priority <= 2:
            logger.debug(f"L2 Engineer: High priority ({request.priority})")
            return EscalationLevel.L2_ENGINEER

        # L1 Operator: Standard operations
        logger.debug("L1 Operator: Standard operation")
        return EscalationLevel.L1_OPERATOR

    def _calculate_urgency(
        self,
        request: DecisionRequest,
        policies: Optional[Dict[str, Any]]
    ) -> int:
        """
        Рассчитывает urgency (1-5, 1 = most urgent)

        Urgency factors:
        - Request priority
        - RTO/RPO proximity
        - Service criticality
        - Business hours

        Args:
            request: Decision request
            policies: Service policies

        Returns:
            Urgency 1-5
        """
        policies = policies or {}
        urgency = 3  # Default: medium

        # Priority-based urgency
        if request.priority == 1:
            urgency = 1  # Critical
        elif request.priority == 2:
            urgency = 2  # High
        elif request.priority >= 4:
            urgency = 4  # Low

        # Increase urgency if RTO violation imminent
        rto = policies.get("rto", 300)
        downtime = request.context.get("downtime_seconds", 0)

        if downtime > rto * 0.9:
            urgency = min(urgency, 1)  # Most urgent
        elif downtime > rto * 0.7:
            urgency = min(urgency, 2)  # Very urgent

        # Increase urgency for critical services
        if policies.get("critical", False):
            urgency = min(urgency, 2)

        # Business hours check (optional)
        is_business_hours = self._is_business_hours()
        if not is_business_hours and urgency > 2:
            # Lower urgency outside business hours
            urgency = min(urgency + 1, 5)

        logger.debug(
            f"Calculated urgency: {urgency} "
            f"(priority={request.priority}, downtime={downtime}s, rto={rto}s)"
        )

        return urgency

    def _get_assigned_operator(self, escalation_level: EscalationLevel) -> str:
        """
        Определяет кому назначить эскалацию

        Args:
            escalation_level: Escalation level

        Returns:
            Operator name/email

        Note:
            MVP implementation returns generic role.
            Production should integrate with on-call rotation system.
        """
        # MVP: Return generic role
        role_map = {
            EscalationLevel.L1_OPERATOR: "on-call-operator",
            EscalationLevel.L2_ENGINEER: "on-call-engineer",
            EscalationLevel.L3_ARCHITECT: "lead-architect",
            EscalationLevel.L4_MANAGEMENT: "engineering-manager"
        }

        assigned = role_map.get(escalation_level, "on-call-operator")

        logger.debug(f"Assigned to: {assigned} (level={escalation_level.value})")

        return assigned

    def _is_business_hours(self) -> bool:
        """
        Проверяет business hours (Mon-Fri 9:00-18:00 UTC)

        Returns:
            True if business hours
        """
        now = datetime.utcnow()

        # Weekend check
        if now.weekday() >= 5:  # Saturday=5, Sunday=6
            return False

        # Hour check (9:00-18:00)
        if now.hour < 9 or now.hour >= 18:
            return False

        return True

    async def _notify_escalation(self, escalation: EscalationRequest):
        """
        Отправляет уведомления об эскалации

        Args:
            escalation: Escalation request

        Notifications:
        - Email to assigned operator
        - Slack message to ops channel
        - SMS for urgency 1-2
        """
        if not self.notification_handler:
            logger.warning("No notification handler configured - skipping notifications")
            return

        try:
            # Build notification message
            message = self._build_notification_message(escalation)

            # Send email
            await self.notification_handler.send_email(
                to=escalation.assigned_to,
                subject=f"[Escalation L{escalation.escalation_level.value[-1]}] {escalation.original_request.service}",
                body=message
            )

            # Send Slack notification
            await self.notification_handler.send_slack(
                channel="#ops-escalations",
                message=message
            )

            # Send SMS for high urgency
            if escalation.urgency <= 2:
                await self.notification_handler.send_sms(
                    to=escalation.assigned_to,
                    message=f"URGENT: Escalation {escalation.escalation_id[:8]}"
                )

            logger.info(f"Notifications sent for escalation {escalation.escalation_id}")

        except Exception as e:
            logger.error(f"Failed to send notifications: {e}", exc_info=True)
            # Don't fail escalation if notifications fail

    def _build_notification_message(self, escalation: EscalationRequest) -> str:
        """
        Строит сообщение уведомления

        Args:
            escalation: Escalation request

        Returns:
            Formatted notification message
        """
        request = escalation.original_request

        urgency_labels = {
            1: "🔴 CRITICAL",
            2: "🟠 HIGH",
            3: "🟡 MEDIUM",
            4: "🟢 LOW",
            5: "⚪ INFO"
        }

        urgency_label = urgency_labels.get(escalation.urgency, "❓ UNKNOWN")

        message = f"""
Escalation Required - {urgency_label}

Escalation ID: {escalation.escalation_id}
Level: {escalation.escalation_level.value}
Assigned To: {escalation.assigned_to}

Service: {request.service}
Action: {request.action}
Reason: {escalation.reason}

Priority: {request.priority}
Requester: {request.requester}

Context:
- Recovery Attempts: {request.context.get('recovery_attempts', 0)}
- Downtime: {request.context.get('downtime_seconds', 0)}s
- Recent Failures: {len(request.context.get('recent_failures', []))}

Created At: {escalation.created_at.isoformat()}

Please respond via Decision Center UI or API.
        """

        return message.strip()

    def get_active_escalations(self) -> List[EscalationRequest]:
        """
        Возвращает список активных эскалаций

        Returns:
            List of active escalation requests
        """
        return list(self.active_escalations.values())

    def get_escalation(self, escalation_id: str) -> Optional[EscalationRequest]:
        """
        Получает эскалацию по ID

        Args:
            escalation_id: Escalation ID

        Returns:
            Escalation request or None
        """
        return self.active_escalations.get(escalation_id)
