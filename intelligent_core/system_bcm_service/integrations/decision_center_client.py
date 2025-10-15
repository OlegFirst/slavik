"""
Decision Center Client - Integration for System BCM Coordinator

Requests approval from Decision Center before executing any recovery action.
"""

import httpx
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class DecisionOutcome(Enum):
    """Decision outcomes"""
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"
    ESCALATED = "escalated"


@dataclass
class Decision:
    """
    Decision response from Decision Center

    Attributes:
        decision_id: Unique decision ID
        request_id: Original request ID
        outcome: Decision outcome (approved/rejected/pending/escalated)
        justification: Why this decision was made
        decided_by: Who made the decision (system/human/ai)
        metadata: Additional metadata
    """
    decision_id: str
    request_id: str
    outcome: DecisionOutcome
    justification: str
    decided_by: str
    metadata: Dict[str, Any]


class DecisionCenterClient:
    """
    Client for Decision Center API

    Usage:
        client = DecisionCenterClient(base_url="http://localhost:8080")

        decision = await client.request_decision(
            service="database",
            action="restart",
            reason="High memory usage detected",
            priority=2,
            context={"recovery_attempts": 1}
        )

        if decision.outcome == DecisionOutcome.APPROVED:
            await execute_restart()
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        timeout: float = 30.0,
        retry_attempts: int = 3
    ):
        """
        Initialize Decision Center client

        Args:
            base_url: Decision Center API base URL
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.client = httpx.AsyncClient(timeout=timeout)

        logger.info(f"Decision Center client initialized: {base_url}")

    async def request_decision(
        self,
        service: str,
        action: str,
        reason: str,
        priority: int = 3,
        context: Optional[Dict[str, Any]] = None
    ) -> Decision:
        """
        Request decision from Decision Center

        Args:
            service: Service name (e.g., "database", "redis", "api-gateway")
            action: Action to perform (e.g., "restart", "scale_up", "failover")
            reason: Reason for action
            priority: Priority 1-5 (1=critical, 5=low)
            context: Additional context (recovery_attempts, downtime, metrics, etc.)

        Returns:
            Decision object

        Raises:
            Exception: If request fails after all retries

        Example:
            decision = await client.request_decision(
                service="redis",
                action="restart",
                reason="High memory usage detected",
                priority=2,
                context={
                    "recovery_attempts": 1,
                    "downtime_seconds": 120,
                    "memory_usage_percent": 95,
                    "recent_failures": []
                }
            )
        """
        url = f"{self.base_url}/api/v1/decisions"

        payload = {
            "service": service,
            "action": action,
            "reason": reason,
            "priority": priority,
            "context": context or {},
            "requester": "system_bcm_coordinator"
        }

        for attempt in range(1, self.retry_attempts + 1):
            try:
                logger.info(
                    f"Requesting decision: {service}.{action} "
                    f"(reason: {reason}, attempt {attempt}/{self.retry_attempts})"
                )

                response = await self.client.post(url, json=payload)
                response.raise_for_status()

                data = response.json()

                decision = Decision(
                    decision_id=data["decision_id"],
                    request_id=data["request_id"],
                    outcome=DecisionOutcome(data["outcome"]),
                    justification=data["justification"],
                    decided_by=data["decided_by"],
                    metadata=data.get("metadata", {})
                )

                logger.info(
                    f"Decision received: {decision.outcome.value} "
                    f"(decided_by: {decision.decided_by})"
                )
                logger.debug(f"Justification: {decision.justification}")

                return decision

            except httpx.HTTPStatusError as e:
                logger.error(
                    f"Decision request failed (HTTP {e.response.status_code}): {e}"
                )

                if attempt == self.retry_attempts:
                    # Last attempt failed, return safe rejection
                    logger.error("All retry attempts failed, returning safe rejection")
                    return self._create_safe_rejection(service, action, str(e))

                # Retry after delay
                import asyncio
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

            except Exception as e:
                logger.error(f"Decision request error: {e}", exc_info=True)

                if attempt == self.retry_attempts:
                    # Last attempt failed, return safe rejection
                    return self._create_safe_rejection(service, action, str(e))

                import asyncio
                await asyncio.sleep(2 ** attempt)

        # Fallback (should not reach here, but just in case)
        return self._create_safe_rejection(service, action, "Unknown error")

    def _create_safe_rejection(
        self,
        service: str,
        action: str,
        error: str
    ) -> Decision:
        """
        Create safe rejection decision when Decision Center is unreachable

        This is a fail-safe mechanism to prevent unsafe actions
        when governance is unavailable.

        Args:
            service: Service name
            action: Action
            error: Error message

        Returns:
            Rejected decision
        """
        logger.warning(
            f"Creating safe rejection for {service}.{action} "
            f"(Decision Center unreachable)"
        )

        return Decision(
            decision_id="fallback-rejection",
            request_id="fallback",
            outcome=DecisionOutcome.REJECTED,
            justification=(
                f"Decision Center unreachable - safe rejection. "
                f"Error: {error}. "
                f"Manual intervention required."
            ),
            decided_by="fallback",
            metadata={
                "fallback": True,
                "error": error,
                "safety_policy": "reject_when_governance_unavailable"
            }
        )

    async def get_escalations(self) -> list:
        """
        Get active escalations

        Returns:
            List of active escalations
        """
        url = f"{self.base_url}/api/v1/escalations"

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Failed to get escalations: {e}")
            return []

    async def get_service_policies(self, service: str) -> Dict[str, Any]:
        """
        Get policies for service

        Args:
            service: Service name

        Returns:
            Service policies
        """
        url = f"{self.base_url}/api/v1/policies/{service}"

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Failed to get policies for {service}: {e}")
            return {}

    async def get_decision_history(
        self,
        service: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get decision history for service

        Args:
            service: Service name
            days: Number of days to look back

        Returns:
            Decision history statistics
        """
        url = f"{self.base_url}/api/v1/audit/history/{service}"

        try:
            response = await self.client.get(url, params={"days": days})
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Failed to get history for {service}: {e}")
            return {}

    async def health_check(self) -> bool:
        """
        Check if Decision Center is healthy

        Returns:
            True if healthy, False otherwise
        """
        url = f"{self.base_url}/health"

        try:
            response = await self.client.get(url)
            return response.status_code == 200

        except Exception as e:
            logger.error(f"Decision Center health check failed: {e}")
            return False

    async def close(self):
        """Close client connection"""
        await self.client.aclose()


# Export
__all__ = ["DecisionCenterClient", "Decision", "DecisionOutcome"]
