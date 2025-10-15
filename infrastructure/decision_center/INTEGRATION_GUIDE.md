# Decision Center Integration Guide

This guide shows how to integrate Decision Center with Infrastructure Coordinator.

## Overview

Infrastructure Coordinator **must** request approval from Decision Center **before** executing any action (restart, scale, failover, config change, etc.).

**Flow:**
1. Infrastructure Coordinator detects issue
2. Prepares action (e.g., "restart database")
3. **Requests decision from Decision Center**
4. Waits for decision response
5. Executes action only if **approved**

## Integration Steps

### Step 1: Add Decision Center Client

Create a client class in Infrastructure Coordinator:

```python
# intelligent_core/infrastructure_coordinator/decision_center_client.py

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
    """Decision response"""
    decision_id: str
    request_id: str
    outcome: DecisionOutcome
    justification: str
    decided_by: str
    metadata: Dict[str, Any]


class DecisionCenterClient:
    """
    Client for Decision Center API
    """

    def __init__(self, base_url: str = "http://localhost:8080"):
        """
        Initialize client

        Args:
            base_url: Decision Center API base URL
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
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
            service: Service name
            action: Action to perform
            reason: Reason for action
            priority: Priority 1-5 (1=critical)
            context: Additional context

        Returns:
            Decision object

        Raises:
            Exception: If request fails
        """
        url = f"{self.base_url}/api/v1/decisions"

        payload = {
            "service": service,
            "action": action,
            "reason": reason,
            "priority": priority,
            "context": context or {},
            "requester": "infrastructure_coordinator"
        }

        try:
            logger.info(
                f"Requesting decision: {service}.{action} "
                f"(reason: {reason})"
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

            return decision

        except httpx.HTTPStatusError as e:
            logger.error(f"Decision request failed: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"Decision request error: {e}", exc_info=True)
            raise

    async def close(self):
        """Close client"""
        await self.client.aclose()
```

### Step 2: Update Infrastructure Coordinator

Integrate Decision Center client into coordinator:

```python
# intelligent_core/infrastructure_coordinator/coordinator.py

from .decision_center_client import DecisionCenterClient, DecisionOutcome

class InfrastructureCoordinator:
    """
    Infrastructure Coordinator with Decision Center integration
    """

    def __init__(self):
        # ... existing initialization ...

        # Add Decision Center client
        self.decision_center = DecisionCenterClient(
            base_url="http://decision-center:8080"
        )

        # Recovery attempt tracking
        self.recovery_attempts: Dict[str, int] = {}

    async def handle_service_failure(
        self,
        service_name: str,
        failure_type: str,
        metrics: Dict[str, Any]
    ):
        """
        Handle service failure with Decision Center approval

        Args:
            service_name: Service name
            failure_type: Type of failure
            metrics: Current metrics
        """
        logger.warning(
            f"Service failure detected: {service_name} ({failure_type})"
        )

        # Increment recovery attempts
        attempts = self.recovery_attempts.get(service_name, 0)
        self.recovery_attempts[service_name] = attempts + 1

        # Determine action
        action = self._determine_action(failure_type, metrics)

        # Calculate downtime
        downtime_seconds = self._calculate_downtime(service_name)

        # Build context
        context = {
            "recovery_attempts": attempts,
            "downtime_seconds": downtime_seconds,
            "failure_type": failure_type,
            "metrics": metrics,
            "recent_failures": self._get_recent_failures(service_name)
        }

        # Request decision from Decision Center
        decision = await self.decision_center.request_decision(
            service=service_name,
            action=action,
            reason=f"{failure_type} detected",
            priority=self._calculate_priority(failure_type),
            context=context
        )

        # Handle decision outcome
        if decision.outcome == DecisionOutcome.APPROVED:
            logger.info(
                f"Action approved: {service_name}.{action} - "
                f"{decision.justification}"
            )
            await self._execute_action(service_name, action)

        elif decision.outcome == DecisionOutcome.PENDING:
            logger.warning(
                f"Action pending manual approval: {service_name}.{action} - "
                f"{decision.justification}"
            )
            # Wait for approval or timeout
            await self._wait_for_approval(decision.decision_id)

        elif decision.outcome == DecisionOutcome.ESCALATED:
            logger.warning(
                f"Action escalated: {service_name}.{action} - "
                f"{decision.justification}"
            )
            # Escalated to operator, monitor and wait

        elif decision.outcome == DecisionOutcome.REJECTED:
            logger.error(
                f"Action rejected: {service_name}.{action} - "
                f"{decision.justification}"
            )
            # Don't execute, log rejection

    async def _execute_action(self, service_name: str, action: str):
        """
        Execute approved action

        Args:
            service_name: Service name
            action: Action to execute
        """
        logger.info(f"Executing action: {service_name}.{action}")

        if action == "restart":
            await self._restart_service(service_name)

        elif action == "failover":
            await self._failover_service(service_name)

        elif action == "scale_up":
            await self._scale_up_service(service_name)

        elif action == "scale_down":
            await self._scale_down_service(service_name)

        elif action == "configuration_change":
            await self._change_configuration(service_name)

        else:
            logger.error(f"Unknown action: {action}")

    def _determine_action(
        self,
        failure_type: str,
        metrics: Dict[str, Any]
    ) -> str:
        """
        Determine appropriate action based on failure type

        Args:
            failure_type: Type of failure
            metrics: Current metrics

        Returns:
            Action name
        """
        if failure_type == "health_check_failed":
            return "restart"

        elif failure_type == "high_memory":
            return "restart"

        elif failure_type == "high_cpu":
            return "scale_up"

        elif failure_type == "low_load":
            return "scale_down"

        elif failure_type == "instance_down":
            return "failover"

        else:
            return "restart"  # default

    def _calculate_priority(self, failure_type: str) -> int:
        """
        Calculate priority for failure type

        Args:
            failure_type: Type of failure

        Returns:
            Priority 1-5 (1=critical)
        """
        critical_failures = ["instance_down", "database_error"]
        high_priority_failures = ["health_check_failed", "high_memory"]

        if failure_type in critical_failures:
            return 1  # Critical
        elif failure_type in high_priority_failures:
            return 2  # High
        else:
            return 3  # Medium
```

### Step 3: Update Recovery Logic

Ensure all recovery actions go through Decision Center:

```python
async def restart_service(self, service_name: str):
    """
    Restart service (with Decision Center approval)

    Args:
        service_name: Service name
    """
    # Request decision
    decision = await self.decision_center.request_decision(
        service=service_name,
        action="restart",
        reason="Manual restart requested",
        priority=3,
        context={
            "recovery_attempts": self.recovery_attempts.get(service_name, 0),
            "downtime_seconds": 0
        }
    )

    # Execute if approved
    if decision.outcome == DecisionOutcome.APPROVED:
        logger.info(f"Restarting {service_name}...")
        # Execute restart
        await self._execute_restart(service_name)
        logger.info(f"Restart complete: {service_name}")
    else:
        logger.warning(
            f"Restart rejected/pending: {decision.justification}"
        )
```

### Step 4: Add Configuration

Add Decision Center configuration:

```yaml
# config/infrastructure_coordinator.yaml

decision_center:
  enabled: true
  base_url: "http://decision-center:8080"
  timeout_seconds: 30
  retry_attempts: 3
  retry_delay_seconds: 5

# Service definitions
services:
  database:
    name: "database"
    critical: true
    max_auto_attempts: 2
    # ... other config ...

  redis:
    name: "redis"
    critical: false
    max_auto_attempts: 3
    # ... other config ...
```

### Step 5: Handle Pending Decisions

Implement logic to wait for manual approval:

```python
async def _wait_for_approval(
    self,
    decision_id: str,
    timeout_seconds: int = 1800
):
    """
    Wait for manual approval of pending decision

    Args:
        decision_id: Decision ID
        timeout_seconds: Timeout (default 30 minutes)
    """
    import asyncio

    start_time = asyncio.get_event_loop().time()

    while True:
        # Check if timeout
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed > timeout_seconds:
            logger.error(
                f"Approval timeout for decision {decision_id}"
            )
            break

        # Poll for decision status (simplified)
        # TODO: Implement proper polling or webhook
        await asyncio.sleep(10)

        # In production: poll GET /api/v1/decisions/{decision_id}
        # or use webhook callback
```

## Testing Integration

### Unit Tests

```python
# tests/test_infrastructure_coordinator.py

import pytest
from unittest.mock import AsyncMock, MagicMock
from infrastructure_coordinator.coordinator import InfrastructureCoordinator
from infrastructure_coordinator.decision_center_client import Decision, DecisionOutcome

@pytest.mark.asyncio
async def test_handle_failure_approved():
    """Test handling failure with approved decision"""
    # Setup
    coordinator = InfrastructureCoordinator()
    coordinator.decision_center.request_decision = AsyncMock(
        return_value=Decision(
            decision_id="test-id",
            request_id="req-id",
            outcome=DecisionOutcome.APPROVED,
            justification="Auto-approved",
            decided_by="system",
            metadata={}
        )
    )
    coordinator._execute_action = AsyncMock()

    # Execute
    await coordinator.handle_service_failure(
        service_name="redis",
        failure_type="health_check_failed",
        metrics={"memory_percent": 95}
    )

    # Assert
    coordinator._execute_action.assert_called_once()


@pytest.mark.asyncio
async def test_handle_failure_rejected():
    """Test handling failure with rejected decision"""
    # Setup
    coordinator = InfrastructureCoordinator()
    coordinator.decision_center.request_decision = AsyncMock(
        return_value=Decision(
            decision_id="test-id",
            request_id="req-id",
            outcome=DecisionOutcome.REJECTED,
            justification="Max attempts exceeded",
            decided_by="system",
            metadata={}
        )
    )
    coordinator._execute_action = AsyncMock()

    # Execute
    await coordinator.handle_service_failure(
        service_name="redis",
        failure_type="health_check_failed",
        metrics={}
    )

    # Assert
    coordinator._execute_action.assert_not_called()
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_integration_with_decision_center():
    """Test full integration with Decision Center"""
    # Start Decision Center in test mode
    # ... setup ...

    # Create coordinator
    coordinator = InfrastructureCoordinator()

    # Request decision
    decision = await coordinator.decision_center.request_decision(
        service="test-service",
        action="restart",
        reason="Test",
        priority=3,
        context={"recovery_attempts": 1}
    )

    # Assert
    assert decision.outcome in [
        DecisionOutcome.APPROVED,
        DecisionOutcome.REJECTED
    ]
```

## Deployment

### Docker Compose

```yaml
# docker-compose.yml

version: '3.8'

services:
  decision-center:
    build: ./infrastructure/decision_center
    ports:
      - "8080:8080"
    volumes:
      - ./infrastructure/decision_center/policies.yaml:/app/policies.yaml
      - ./logs/decision_center:/var/log/decision_center
    environment:
      - DECISION_CENTER_LOG_DIR=/var/log/decision_center
      - DECISION_CENTER_RETENTION_DAYS=90
    networks:
      - platform

  infrastructure-coordinator:
    build: ./intelligent_core/infrastructure_coordinator
    environment:
      - DECISION_CENTER_URL=http://decision-center:8080
    depends_on:
      - decision-center
    networks:
      - platform

networks:
  platform:
    driver: bridge
```

### Kubernetes

```yaml
# decision-center-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: decision-center
spec:
  replicas: 2
  selector:
    matchLabels:
      app: decision-center
  template:
    metadata:
      labels:
        app: decision-center
    spec:
      containers:
      - name: decision-center
        image: decision-center:latest
        ports:
        - containerPort: 8080
        volumeMounts:
        - name: policies
          mountPath: /app/policies.yaml
          subPath: policies.yaml
        - name: logs
          mountPath: /var/log/decision_center
      volumes:
      - name: policies
        configMap:
          name: decision-center-policies
      - name: logs
        persistentVolumeClaim:
          claimName: decision-center-logs

---
apiVersion: v1
kind: Service
metadata:
  name: decision-center
spec:
  selector:
    app: decision-center
  ports:
  - port: 8080
    targetPort: 8080
```

## Monitoring

### Grafana Dashboard

Monitor Decision Center metrics:

```
# Prometheus queries for Grafana

# Total decisions
sum(rate(decision_center_decisions_total[5m])) by (outcome)

# Decision latency
histogram_quantile(0.95,
  sum(rate(decision_center_decision_latency_seconds_bucket[5m])) by (le)
)

# Escalations
sum(decision_center_active_escalations) by (escalation_level)

# Rejection rate
sum(rate(decision_center_decisions_total{outcome="rejected"}[5m])) /
sum(rate(decision_center_decisions_total[5m]))
```

## Troubleshooting

### Decision Center Unreachable

```python
# Add retry logic
from tenacity import retry, stop_after_attempt, wait_exponential

class DecisionCenterClient:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def request_decision(self, ...):
        # ... existing code ...
```

### High Rejection Rate

1. Check policies: `GET /api/v1/policies/{service}`
2. Review audit logs: `GET /api/v1/audit/history/{service}`
3. Adjust `max_auto_attempts` in policies.yaml

### Escalations Piling Up

1. Check active escalations: `GET /api/v1/escalations`
2. Respond to escalations via UI or API
3. Review escalation triggers in policies

## Best Practices

1. **Always request decision before action**
2. **Track recovery_attempts** for each service
3. **Include rich context** (metrics, history, downtime)
4. **Handle all outcomes** (approved, rejected, pending, escalated)
5. **Monitor decision metrics** in Grafana
6. **Test policy changes** before deploying
7. **Set up alerts** for high rejection rates

## Next Steps

1. Implement webhook callbacks for pending decisions
2. Add UI for operators to respond to escalations
3. Integrate real AI models (Phase 2)
4. Add predictive analytics for proactive decisions
