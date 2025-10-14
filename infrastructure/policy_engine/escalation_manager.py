"""
Escalation Manager (Phase 1.1)
================================

Manages escalations when auto-recovery fails or reaches critical thresholds.

Features:
- Escalation decision logic
- Human notification
- Auto-recovery stoppage
- Incident ticket creation
- Manual approval workflows
- Escalation history tracking

Integration:
- Decision Center (escalation policies)
- Notification Service (alerts)
- EventBus (escalation events)
- Audit Logger (escalation audit trail)

Events Published:
- infrastructure.escalation.created
- infrastructure.escalation.notified
- infrastructure.escalation.resolved
- infrastructure.recovery.stopped (after escalation)
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class EscalationReason(Enum):
    """Reasons for escalation"""
    MAX_ATTEMPTS_REACHED = "max_attempts_reached"
    CRITICAL_SERVICE_FAILURE = "critical_service_failure"
    TIMEOUT_EXCEEDED = "timeout_exceeded"
    PATTERN_DETECTED = "pattern_detected"
    MANUAL_TRIGGER = "manual_trigger"


class EscalationStatus(Enum):
    """Escalation status"""
    PENDING = "pending"
    NOTIFIED = "notified"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"


@dataclass
class EscalationPolicy:
    """Escalation policy configuration"""
    service_name: str

    # Escalation thresholds
    max_attempts: int = 3
    critical_service_max_attempts: int = 2  # Critical services escalate faster
    escalation_timeout_seconds: int = 300  # 5 minutes
    pattern_failure_threshold: int = 5  # 5 failures in pattern window
    pattern_window_seconds: int = 3600  # 1 hour

    # Critical service designation
    is_critical: bool = False

    # Notification settings
    notify_email: List[str] = field(default_factory=list)
    notify_slack: bool = True

    # Incident creation
    auto_create_incident: bool = True
    incident_priority: str = "high"

    # Manual approval
    require_manual_approval: bool = False


@dataclass
class Escalation:
    """Escalation record"""
    id: str
    service_name: str
    reason: EscalationReason
    status: EscalationStatus
    created_at: datetime

    # Context
    recovery_attempts: int
    recovery_duration_seconds: float
    failure_history: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Actions taken
    notifications_sent: List[str] = field(default_factory=list)
    incident_id: Optional[str] = None
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

    # Auto-recovery control
    recovery_stopped: bool = False


class EscalationManager:
    """
    Escalation Manager

    Decides when to escalate failed auto-recovery to humans.

    Example:
        ```python
        from infrastructure.decision-center.notification_service import NotificationService, NotificationConfig

        config = NotificationConfig()
        notification_service = NotificationService(config, eventbus)

        manager = EscalationManager(notification_service, eventbus)

        # Register policy
        manager.register_policy(EscalationPolicy(
            service_name='api_gateway',
            is_critical=True,
            max_attempts=3,
            critical_service_max_attempts=2
        ))

        # Check if should escalate
        should_escalate, reason = manager.should_escalate(
            service_name='api_gateway',
            current_attempts=2,
            recovery_start_time=datetime.utcnow() - timedelta(minutes=2),
            is_still_unhealthy=True
        )

        if should_escalate:
            escalation = await manager.escalate(
                service_name='api_gateway',
                reason=reason,
                recovery_attempts=2,
                recovery_duration=120,
                metadata={'details': 'Service unresponsive'}
            )
        ```
    """

    def __init__(self, notification_service, eventbus=None, audit_logger=None):
        """
        Initialize Escalation Manager

        Args:
            notification_service: NotificationService instance
            eventbus: Optional EventBus instance
            audit_logger: Optional audit logger
        """
        self.notification_service = notification_service
        self.eventbus = eventbus
        self.audit_logger = audit_logger

        self.policies: Dict[str, EscalationPolicy] = {}
        self.escalations: Dict[str, Escalation] = {}  # escalation_id -> Escalation
        self.service_escalations: Dict[str, List[str]] = {}  # service_name -> [escalation_ids]
        self.failure_history: Dict[str, List[datetime]] = {}  # service_name -> [failure_times]

        # Auto-recovery blocklist (services currently escalated)
        self.recovery_blocked: Dict[str, str] = {}  # service_name -> escalation_id

        logger.info("EscalationManager initialized")

    def register_policy(self, policy: EscalationPolicy):
        """
        Register escalation policy for a service

        Args:
            policy: EscalationPolicy instance
        """
        self.policies[policy.service_name] = policy
        self.service_escalations[policy.service_name] = []
        self.failure_history[policy.service_name] = []
        logger.info(f"Registered escalation policy for {policy.service_name} "
                   f"(critical={policy.is_critical})")

    def should_escalate(
        self,
        service_name: str,
        current_attempts: int,
        recovery_start_time: datetime,
        is_still_unhealthy: bool
    ) -> tuple[bool, Optional[EscalationReason]]:
        """
        Check if escalation is needed

        Args:
            service_name: Service name
            current_attempts: Current recovery attempt count
            recovery_start_time: When recovery started
            is_still_unhealthy: Whether service is still unhealthy

        Returns:
            Tuple of (should_escalate: bool, reason: Optional[EscalationReason])

        Escalation Triggers:
        1. Attempts >= max_attempts from policy
        2. Service is critical AND still unhealthy after 2 attempts
        3. Total recovery duration > escalation_timeout
        4. Same service failed 5+ times in last hour (pattern detection)
        """
        policy = self.policies.get(service_name)
        if not policy:
            logger.warning(f"No escalation policy for {service_name} - no escalation")
            return False, None

        # 1. Max attempts reached
        if current_attempts >= policy.max_attempts:
            logger.warning(f"Escalation trigger: {service_name} reached max attempts ({current_attempts})")
            return True, EscalationReason.MAX_ATTEMPTS_REACHED

        # 2. Critical service still unhealthy after critical_service_max_attempts
        if policy.is_critical and is_still_unhealthy and current_attempts >= policy.critical_service_max_attempts:
            logger.warning(f"Escalation trigger: Critical service {service_name} failed after "
                         f"{current_attempts} attempts")
            return True, EscalationReason.CRITICAL_SERVICE_FAILURE

        # 3. Recovery timeout exceeded
        recovery_duration = (datetime.utcnow() - recovery_start_time).total_seconds()
        if recovery_duration > policy.escalation_timeout_seconds:
            logger.warning(f"Escalation trigger: {service_name} recovery timeout "
                         f"({recovery_duration:.0f}s > {policy.escalation_timeout_seconds}s)")
            return True, EscalationReason.TIMEOUT_EXCEEDED

        # 4. Pattern detection - multiple failures in time window
        recent_failures = self._get_recent_failures(service_name, policy.pattern_window_seconds)
        if len(recent_failures) >= policy.pattern_failure_threshold:
            logger.warning(f"Escalation trigger: {service_name} pattern detected "
                         f"({len(recent_failures)} failures in {policy.pattern_window_seconds}s)")
            return True, EscalationReason.PATTERN_DETECTED

        return False, None

    def _get_recent_failures(self, service_name: str, window_seconds: int) -> List[datetime]:
        """Get failures within time window"""
        if service_name not in self.failure_history:
            return []

        cutoff = datetime.utcnow() - timedelta(seconds=window_seconds)
        return [
            failure_time
            for failure_time in self.failure_history[service_name]
            if failure_time > cutoff
        ]

    def record_failure(self, service_name: str):
        """
        Record a failure for pattern detection

        Args:
            service_name: Service name
        """
        if service_name not in self.failure_history:
            self.failure_history[service_name] = []

        self.failure_history[service_name].append(datetime.utcnow())

        # Keep only last 24 hours of history
        cutoff = datetime.utcnow() - timedelta(hours=24)
        self.failure_history[service_name] = [
            t for t in self.failure_history[service_name] if t > cutoff
        ]

    async def escalate(
        self,
        service_name: str,
        reason: EscalationReason,
        recovery_attempts: int,
        recovery_duration: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Escalation:
        """
        Create escalation and notify operators

        Args:
            service_name: Service name
            reason: Escalation reason
            recovery_attempts: Number of recovery attempts made
            recovery_duration: Total recovery duration in seconds
            metadata: Additional metadata

        Returns:
            Escalation: Created escalation record
        """
        policy = self.policies.get(service_name)
        if not policy:
            raise ValueError(f"No escalation policy for {service_name}")

        # Create escalation
        escalation = Escalation(
            id=str(uuid.uuid4()),
            service_name=service_name,
            reason=reason,
            status=EscalationStatus.PENDING,
            created_at=datetime.utcnow(),
            recovery_attempts=recovery_attempts,
            recovery_duration_seconds=recovery_duration,
            failure_history=self._get_recent_failures(service_name, 3600),
            metadata=metadata or {}
        )

        # Store escalation
        self.escalations[escalation.id] = escalation
        self.service_escalations[service_name].append(escalation.id)

        logger.warning(f"🚨 ESCALATION CREATED: {service_name} - {reason.value}")

        # Publish escalation.created event
        await self._publish_event('infrastructure.escalation.created', escalation)

        # Stop auto-recovery for this service
        await self.stop_auto_recovery(service_name, escalation.id)

        # Notify operators
        await self.notify_operators(escalation)

        # Create incident ticket if enabled
        if policy.auto_create_incident:
            await self.create_incident_ticket(escalation)

        return escalation

    async def notify_operators(self, escalation: Escalation) -> bool:
        """
        Send notifications to operators

        Args:
            escalation: Escalation record

        Returns:
            bool: True if at least one notification succeeded
        """
        policy = self.policies.get(escalation.service_name)
        if not policy:
            logger.error(f"No policy for {escalation.service_name} - cannot notify")
            return False

        # Build notification message
        title = f"🚨 ESCALATION: {escalation.service_name} - {escalation.reason.value}"

        message = f"""
Service: {escalation.service_name}
Reason: {escalation.reason.value}
Recovery Attempts: {escalation.recovery_attempts}
Recovery Duration: {escalation.recovery_duration_seconds:.1f}s
Recent Failures: {len(escalation.failure_history)}

AUTOMATIC RECOVERY HAS BEEN STOPPED.
Manual intervention required.

Escalation ID: {escalation.id}
Created: {escalation.created_at.isoformat()}
        """.strip()

        # Determine notification priority
        from infrastructure.policy_engine.notification_service import NotificationPriority

        priority = NotificationPriority.CRITICAL if policy.is_critical else NotificationPriority.HIGH

        # Send notification
        notification = await self.notification_service.send_notification(
            title=title,
            message=message,
            priority=priority,
            metadata={
                'escalation_id': escalation.id,
                'service_name': escalation.service_name,
                'reason': escalation.reason.value,
                'recovery_attempts': escalation.recovery_attempts,
                'is_critical': policy.is_critical
            },
            recipients=policy.notify_email if policy.notify_email else None
        )

        # Update escalation
        escalation.notifications_sent = [ch.value for ch in notification.sent_channels]
        escalation.status = EscalationStatus.NOTIFIED

        # Publish escalation.notified event
        await self._publish_event('infrastructure.escalation.notified', escalation)

        logger.info(f"Operators notified for escalation {escalation.id}")

        return notification.sent

    async def create_incident_ticket(self, escalation: Escalation) -> Optional[str]:
        """
        Create incident ticket in ticketing system

        Args:
            escalation: Escalation record

        Returns:
            Optional[str]: Incident ticket ID

        TODO: Integrate with actual ticketing system (Jira, ServiceNow, etc.)
        """
        policy = self.policies.get(escalation.service_name)
        if not policy:
            return None

        # For now, just create a mock ticket ID
        incident_id = f"INC-{escalation.id[:8]}"

        escalation.incident_id = incident_id

        logger.info(f"Incident ticket created: {incident_id} for escalation {escalation.id}")

        # TODO: Actually create ticket in external system
        # await jira_client.create_issue(...)

        return incident_id

    async def stop_auto_recovery(self, service_name: str, escalation_id: str):
        """
        Stop auto-recovery for a service

        Args:
            service_name: Service name
            escalation_id: Escalation ID that triggered the stop
        """
        self.recovery_blocked[service_name] = escalation_id

        escalation = self.escalations.get(escalation_id)
        if escalation:
            escalation.recovery_stopped = True

        # Publish recovery.stopped event
        await self._publish_event('infrastructure.recovery.stopped', escalation)

        logger.warning(f"🛑 Auto-recovery STOPPED for {service_name} (escalation: {escalation_id})")

    def is_recovery_allowed(self, service_name: str) -> bool:
        """
        Check if auto-recovery is allowed for a service

        Args:
            service_name: Service name

        Returns:
            bool: True if recovery is allowed
        """
        is_blocked = service_name in self.recovery_blocked
        if is_blocked:
            logger.warning(f"Auto-recovery blocked for {service_name} - escalation in progress")
        return not is_blocked

    async def require_manual_approval(self, escalation_id: str, timeout_seconds: int = 3600) -> bool:
        """
        Wait for manual approval before proceeding

        Args:
            escalation_id: Escalation ID
            timeout_seconds: Maximum wait time

        Returns:
            bool: True if approved, False if timeout

        TODO: Integrate with approval workflow system
        """
        escalation = self.escalations.get(escalation_id)
        if not escalation:
            logger.error(f"Escalation {escalation_id} not found")
            return False

        logger.info(f"Waiting for manual approval for escalation {escalation_id} "
                   f"(timeout: {timeout_seconds}s)")

        # For now, just wait for timeout
        # TODO: Implement actual approval mechanism (webhook, API endpoint, etc.)
        await asyncio.sleep(timeout_seconds)

        logger.warning(f"Manual approval timeout for escalation {escalation_id}")
        return False

    async def resolve_escalation(
        self,
        escalation_id: str,
        resolved_by: str,
        resolution_notes: Optional[str] = None,
        resume_auto_recovery: bool = True
    ):
        """
        Mark escalation as resolved

        Args:
            escalation_id: Escalation ID
            resolved_by: Who resolved it
            resolution_notes: Optional resolution notes
            resume_auto_recovery: Whether to resume auto-recovery
        """
        escalation = self.escalations.get(escalation_id)
        if not escalation:
            logger.error(f"Escalation {escalation_id} not found")
            return

        escalation.status = EscalationStatus.RESOLVED
        escalation.acknowledged_by = resolved_by
        escalation.resolved_at = datetime.utcnow()
        escalation.resolution_notes = resolution_notes

        # Resume auto-recovery if requested
        if resume_auto_recovery and escalation.service_name in self.recovery_blocked:
            del self.recovery_blocked[escalation.service_name]
            logger.info(f"Auto-recovery RESUMED for {escalation.service_name}")

        # Publish escalation.resolved event
        await self._publish_event('infrastructure.escalation.resolved', escalation)

        logger.info(f"Escalation {escalation_id} resolved by {resolved_by}")

    def get_escalation_history(
        self,
        service_name: Optional[str] = None,
        status: Optional[EscalationStatus] = None,
        limit: int = 100
    ) -> List[Escalation]:
        """
        Get escalation history

        Args:
            service_name: Optional filter by service
            status: Optional filter by status
            limit: Maximum number of escalations

        Returns:
            List of escalations
        """
        escalations = list(self.escalations.values())

        if service_name:
            escalation_ids = self.service_escalations.get(service_name, [])
            escalations = [e for e in escalations if e.id in escalation_ids]

        if status:
            escalations = [e for e in escalations if e.status == status]

        # Sort by created_at descending
        escalations.sort(key=lambda e: e.created_at, reverse=True)

        return escalations[:limit]

    def get_active_escalations(self) -> List[Escalation]:
        """
        Get all active (non-resolved) escalations

        Returns:
            List of active escalations
        """
        return [
            e for e in self.escalations.values()
            if e.status not in [EscalationStatus.RESOLVED, EscalationStatus.CANCELLED]
        ]

    async def _publish_event(self, event_type: str, escalation: Optional[Escalation]):
        """Publish event to EventBus"""
        if not self.eventbus:
            return

        from infrastructure.eventbus.core.events import Event, EventPriority

        data = {}
        if escalation:
            data = {
                'escalation_id': escalation.id,
                'service_name': escalation.service_name,
                'reason': escalation.reason.value,
                'status': escalation.status.value,
                'recovery_attempts': escalation.recovery_attempts,
                'recovery_stopped': escalation.recovery_stopped,
                'created_at': escalation.created_at.isoformat()
            }

        event = Event.create(
            event_type=event_type,
            data=data,
            source='escalation_manager',
            tenant_id='system',
            priority=EventPriority.CRITICAL
        )

        await self.eventbus.publish(event)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get escalation statistics

        Returns:
            Dict with escalation stats
        """
        total = len(self.escalations)
        active = len(self.get_active_escalations())

        by_reason = {}
        for reason in EscalationReason:
            count = len([e for e in self.escalations.values() if e.reason == reason])
            by_reason[reason.value] = count

        by_status = {}
        for status in EscalationStatus:
            count = len([e for e in self.escalations.values() if e.status == status])
            by_status[status.value] = count

        return {
            'total_escalations': total,
            'active_escalations': active,
            'services_blocked': len(self.recovery_blocked),
            'by_reason': by_reason,
            'by_status': by_status,
            'blocked_services': list(self.recovery_blocked.keys())
        }
