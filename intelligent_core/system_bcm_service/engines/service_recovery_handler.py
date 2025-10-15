"""
Service Recovery Handler - Automated recovery with Decision Center governance

Handles service failures with Decision Center approval:
1. Detects service failure
2. Determines recovery action
3. Requests decision from Decision Center
4. Executes action if approved
5. Tracks recovery attempts
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.decision_center_client import (
    DecisionCenterClient,
    DecisionOutcome
)

logger = logging.getLogger(__name__)


class ServiceRecoveryHandler:
    """
    Service Recovery Handler with Decision Center governance

    Features:
    - Automatic service recovery with governance
    - Recovery attempt tracking
    - Downtime tracking
    - Failure pattern detection
    - Safe fallback when Decision Center unavailable
    """

    def __init__(
        self,
        decision_center_url: str = "http://localhost:8080",
        eventbus=None
    ):
        """
        Initialize Service Recovery Handler

        Args:
            decision_center_url: Decision Center API URL
            eventbus: EventBus instance for publishing events
        """
        # Decision Center client
        self.decision_center = DecisionCenterClient(base_url=decision_center_url)

        # EventBus
        self.eventbus = eventbus

        # Recovery attempt tracking
        self.recovery_attempts: Dict[str, int] = defaultdict(int)

        # Downtime tracking
        self.service_downtimes: Dict[str, datetime] = {}

        # Recent failures (for pattern detection)
        self.recent_failures: Dict[str, list] = defaultdict(list)

        # Recovery history
        self.recovery_history: list = []

        logger.info("Service Recovery Handler initialized with Decision Center governance")

    async def handle_service_failure(
        self,
        service_name: str,
        failure_type: str,
        metrics: Optional[Dict[str, Any]] = None,
        tier: str = "standard"
    ) -> Dict[str, Any]:
        """
        Handle service failure with Decision Center approval

        Args:
            service_name: Service name (e.g., "database", "redis")
            failure_type: Type of failure (e.g., "health_check_failed", "high_memory")
            metrics: Current service metrics
            tier: Service tier ("critical", "important", "optional")

        Returns:
            Recovery result

        Flow:
            1. Detect failure
            2. Determine action
            3. Request decision
            4. Execute if approved
            5. Track result
        """
        logger.warning(
            f"Service failure detected: {service_name} ({failure_type}, tier={tier})"
        )

        # Start downtime tracking
        if service_name not in self.service_downtimes:
            self.service_downtimes[service_name] = datetime.utcnow()

        # Increment recovery attempts
        self.recovery_attempts[service_name] += 1
        attempts = self.recovery_attempts[service_name]

        # Calculate downtime
        downtime_seconds = self._calculate_downtime(service_name)

        # Determine action
        action = self._determine_action(failure_type, metrics, attempts)

        # Calculate priority
        priority = self._calculate_priority(failure_type, tier, attempts)

        # Track failure for pattern detection
        self._track_failure(service_name, failure_type, metrics)

        # Build context
        context = {
            "recovery_attempts": attempts,
            "downtime_seconds": downtime_seconds,
            "failure_type": failure_type,
            "tier": tier,
            "metrics": metrics or {},
            "recent_failures": self.recent_failures[service_name][-10:]  # Last 10
        }

        # Request decision from Decision Center
        logger.info(f"Requesting decision for {service_name}.{action}...")

        decision = await self.decision_center.request_decision(
            service=service_name,
            action=action,
            reason=f"{failure_type} detected (attempt {attempts})",
            priority=priority,
            context=context
        )

        # Handle decision outcome
        result = {
            "service": service_name,
            "failure_type": failure_type,
            "action": action,
            "decision_id": decision.decision_id,
            "outcome": decision.outcome.value,
            "justification": decision.justification,
            "decided_by": decision.decided_by,
            "attempts": attempts,
            "downtime_seconds": downtime_seconds,
            "timestamp": datetime.utcnow().isoformat()
        }

        if decision.outcome == DecisionOutcome.APPROVED:
            logger.info(
                f"Action approved: {service_name}.{action} - {decision.justification}"
            )

            # Execute action
            execution_result = await self._execute_action(service_name, action, metrics)

            result["executed"] = True
            result["execution_result"] = execution_result

            # Check if recovery was successful
            if execution_result.get("success"):
                logger.info(f"Recovery successful: {service_name}")

                # Reset tracking on success
                self.recovery_attempts[service_name] = 0
                if service_name in self.service_downtimes:
                    del self.service_downtimes[service_name]

                result["recovery_successful"] = True

            else:
                logger.warning(f"Recovery failed: {service_name}")
                result["recovery_successful"] = False

        elif decision.outcome == DecisionOutcome.PENDING:
            logger.warning(
                f"Action pending manual approval: {service_name}.{action} - "
                f"{decision.justification}"
            )
            result["executed"] = False
            result["reason"] = "pending_manual_approval"

        elif decision.outcome == DecisionOutcome.ESCALATED:
            logger.warning(
                f"Action escalated: {service_name}.{action} - {decision.justification}"
            )
            result["executed"] = False
            result["reason"] = "escalated"

        elif decision.outcome == DecisionOutcome.REJECTED:
            logger.error(
                f"Action rejected: {service_name}.{action} - {decision.justification}"
            )
            result["executed"] = False
            result["reason"] = "rejected"

        # Track in history
        self.recovery_history.append(result)

        # Publish event
        if self.eventbus:
            await self._publish_event("service.recovery.attempted", result)

        return result

    def _determine_action(
        self,
        failure_type: str,
        metrics: Optional[Dict[str, Any]],
        attempts: int
    ) -> str:
        """
        Determine appropriate recovery action based on failure type

        Args:
            failure_type: Type of failure
            metrics: Current metrics
            attempts: Number of recovery attempts

        Returns:
            Action name
        """
        metrics = metrics or {}

        # Health check failed → restart
        if failure_type in ["health_check_failed", "service_unresponsive"]:
            return "restart"

        # High memory → restart to clear memory leak
        if failure_type == "high_memory":
            return "restart"

        # High CPU → scale up if first attempt, otherwise restart
        if failure_type == "high_cpu":
            if attempts == 1:
                return "scale_up"
            else:
                return "restart"

        # Low load → scale down
        if failure_type == "low_load":
            return "scale_down"

        # Instance down → failover
        if failure_type == "instance_down":
            return "failover"

        # Database connection issues → restart
        if failure_type in ["database_error", "connection_timeout"]:
            return "restart"

        # Performance degradation → investigate first
        if failure_type == "performance_degradation":
            if attempts == 1:
                return "investigate"
            else:
                return "restart"

        # Default: restart
        return "restart"

    def _calculate_priority(
        self,
        failure_type: str,
        tier: str,
        attempts: int
    ) -> int:
        """
        Calculate priority for failure

        Priority scale: 1 (critical) - 5 (low)

        Args:
            failure_type: Type of failure
            tier: Service tier
            attempts: Number of attempts

        Returns:
            Priority 1-5
        """
        # Start with base priority from tier
        tier_priority = {
            "critical": 1,
            "important": 2,
            "optional": 4
        }.get(tier, 3)

        # Adjust based on failure type
        critical_failures = ["instance_down", "database_error", "service_unresponsive"]
        if failure_type in critical_failures:
            tier_priority = min(tier_priority, 2)  # At least high

        # Increase priority if multiple attempts
        if attempts >= 3:
            tier_priority = min(tier_priority, 1)  # Critical after 3+ attempts

        return tier_priority

    def _track_failure(
        self,
        service_name: str,
        failure_type: str,
        metrics: Optional[Dict[str, Any]]
    ):
        """
        Track failure for pattern detection

        Args:
            service_name: Service name
            failure_type: Failure type
            metrics: Metrics
        """
        failure_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": failure_type,
            "metrics": metrics
        }

        self.recent_failures[service_name].append(failure_record)

        # Keep only last 50 failures
        if len(self.recent_failures[service_name]) > 50:
            self.recent_failures[service_name] = self.recent_failures[service_name][-50:]

    def _calculate_downtime(self, service_name: str) -> int:
        """
        Calculate downtime in seconds

        Args:
            service_name: Service name

        Returns:
            Downtime in seconds
        """
        if service_name not in self.service_downtimes:
            return 0

        downtime_start = self.service_downtimes[service_name]
        downtime_delta = datetime.utcnow() - downtime_start

        return int(downtime_delta.total_seconds())

    async def _execute_action(
        self,
        service_name: str,
        action: str,
        metrics: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Execute recovery action

        Args:
            service_name: Service name
            action: Action to execute
            metrics: Current metrics

        Returns:
            Execution result

        Note:
            This is a stub implementation for MVP.
            Production should integrate with actual service orchestration.
        """
        logger.info(f"Executing action: {service_name}.{action}")

        # Simulate action execution
        await asyncio.sleep(1)

        if action == "restart":
            return await self._restart_service(service_name)

        elif action == "failover":
            return await self._failover_service(service_name)

        elif action == "scale_up":
            return await self._scale_up_service(service_name)

        elif action == "scale_down":
            return await self._scale_down_service(service_name)

        elif action == "investigate":
            return {
                "success": True,
                "action": "investigate",
                "message": "Investigation triggered, metrics collected"
            }

        else:
            logger.error(f"Unknown action: {action}")
            return {"success": False, "error": f"Unknown action: {action}"}

    async def _restart_service(self, service_name: str) -> Dict[str, Any]:
        """
        Restart service

        Args:
            service_name: Service name

        Returns:
            Restart result

        Note:
            MVP stub - production should use actual orchestration
        """
        logger.info(f"Restarting service: {service_name}")

        # TODO: Integrate with Docker/Kubernetes API
        # docker restart {service_name}
        # kubectl rollout restart deployment/{service_name}

        return {
            "success": True,
            "action": "restart",
            "service": service_name,
            "message": f"Service {service_name} restart initiated",
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _failover_service(self, service_name: str) -> Dict[str, Any]:
        """Failover to backup instance"""
        logger.info(f"Initiating failover: {service_name}")

        # TODO: Implement failover logic
        return {
            "success": True,
            "action": "failover",
            "service": service_name,
            "message": f"Failover initiated for {service_name}"
        }

    async def _scale_up_service(self, service_name: str) -> Dict[str, Any]:
        """Scale up service"""
        logger.info(f"Scaling up service: {service_name}")

        # TODO: Implement scaling logic
        return {
            "success": True,
            "action": "scale_up",
            "service": service_name,
            "message": f"Service {service_name} scaled up"
        }

    async def _scale_down_service(self, service_name: str) -> Dict[str, Any]:
        """Scale down service"""
        logger.info(f"Scaling down service: {service_name}")

        # TODO: Implement scaling logic
        return {
            "success": True,
            "action": "scale_down",
            "service": service_name,
            "message": f"Service {service_name} scaled down"
        }

    async def _publish_event(self, event_type: str, data: Dict[str, Any]):
        """Publish event to EventBus"""
        if not self.eventbus:
            return

        try:
            from infrastructure.eventbus import Event
            event = Event(
                type=f"platform.{event_type}",
                data=data,
                source="service_recovery_handler"
            )
            await self.eventbus.publish(event)
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")

    def get_recovery_stats(self) -> Dict[str, Any]:
        """
        Get recovery statistics

        Returns:
            Recovery statistics
        """
        total_attempts = sum(self.recovery_attempts.values())

        successful_recoveries = sum(
            1 for r in self.recovery_history
            if r.get("recovery_successful", False)
        )

        return {
            "total_attempts": total_attempts,
            "successful_recoveries": successful_recoveries,
            "services_with_active_recovery": len(self.recovery_attempts),
            "services_with_downtime": len(self.service_downtimes),
            "recovery_history_size": len(self.recovery_history),
            "recovery_attempts_by_service": dict(self.recovery_attempts),
            "success_rate": (
                successful_recoveries / len(self.recovery_history)
                if self.recovery_history
                else 0.0
            )
        }

    async def close(self):
        """Close client connections"""
        await self.decision_center.close()


# Export
__all__ = ["ServiceRecoveryHandler"]
