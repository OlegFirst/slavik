"""
System BCM Client - Python Library for Easy Integration

Используй этот клиент для интеграции с System BCM Service из любого Python сервиса.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx


logger = logging.getLogger(__name__)


class SystemBCMClient:
    """
    Client for System BCM Service

    Usage:
        client = SystemBCMClient("http://system-bcm-service:8050")

        # Check health
        health = await client.health()

        # Trigger cycle
        result = await client.trigger_cycle()

        # Trigger recovery
        await client.trigger_recovery("api-gateway", "connection_error")

        # Get status
        status = await client.get_status()
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8050",
        timeout: int = 30,
        api_key: Optional[str] = None
    ):
        """
        Initialize System BCM Client

        Args:
            base_url: System BCM Service URL
            timeout: Request timeout in seconds
            api_key: API key for authentication (if required)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.api_key = api_key

        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers=self._get_headers()
        )

        logger.info(f"SystemBCMClient initialized: {self.base_url}")

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SystemBCMClient/1.0.0"
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        return headers

    async def health(self) -> Dict[str, Any]:
        """
        Check System BCM Service health

        Returns:
            Health status dict
        """
        try:
            response = await self._client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise

    async def get_status(self) -> Dict[str, Any]:
        """
        Get detailed System BCM status

        Returns:
            Detailed status including last cycle results
        """
        try:
            response = await self._client.get(f"{self.base_url}/status")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Get status failed: {e}")
            raise

    async def trigger_cycle(self) -> Dict[str, Any]:
        """
        Manually trigger a BCM cycle

        Returns:
            Cycle execution results
        """
        try:
            logger.info("Triggering BCM cycle...")
            response = await self._client.post(f"{self.base_url}/cycle/trigger")
            response.raise_for_status()
            result = response.json()
            logger.info(f"Cycle completed: {result.get('status')}")
            return result
        except Exception as e:
            logger.error(f"Trigger cycle failed: {e}")
            raise

    async def trigger_recovery(
        self,
        service: str,
        incident_type: str
    ) -> Dict[str, Any]:
        """
        Manually trigger recovery for a service

        Args:
            service: Service name (e.g., "api-gateway")
            incident_type: Type of incident (e.g., "failure", "degradation")

        Returns:
            Recovery trigger response
        """
        try:
            logger.info(f"Triggering recovery for {service} ({incident_type})...")
            response = await self._client.post(
                f"{self.base_url}/recovery/trigger",
                params={"service": service, "incident_type": incident_type}
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"Recovery triggered: {result.get('status')}")
            return result
        except Exception as e:
            logger.error(f"Trigger recovery failed: {e}")
            raise

    async def get_metrics(self) -> str:
        """
        Get Prometheus metrics

        Returns:
            Metrics in Prometheus format
        """
        try:
            response = await self._client.get(f"{self.base_url}/metrics")
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Get metrics failed: {e}")
            raise

    async def is_healthy(self) -> bool:
        """
        Quick health check (boolean)

        Returns:
            True if healthy, False otherwise
        """
        try:
            health = await self.health()
            return health.get("status") == "healthy" and health.get("running") == True
        except:
            return False

    async def wait_for_healthy(self, timeout: int = 60, interval: int = 2):
        """
        Wait for service to become healthy

        Args:
            timeout: Max wait time in seconds
            interval: Check interval in seconds

        Raises:
            TimeoutError if service doesn't become healthy in time
        """
        start = datetime.utcnow()

        while (datetime.utcnow() - start).total_seconds() < timeout:
            if await self.is_healthy():
                logger.info("System BCM Service is healthy!")
                return

            logger.debug(f"Waiting for System BCM Service to become healthy...")
            await asyncio.sleep(interval)

        raise TimeoutError(f"System BCM Service did not become healthy within {timeout}s")

    async def get_last_cycle_result(self) -> Optional[Dict[str, Any]]:
        """
        Get results from last BCM cycle

        Returns:
            Last cycle results or None if no cycles run yet
        """
        try:
            status = await self.get_status()
            return status.get("last_cycle_result")
        except Exception as e:
            logger.error(f"Get last cycle result failed: {e}")
            return None

    async def get_cycle_count(self) -> int:
        """
        Get total number of BCM cycles executed

        Returns:
            Cycle count
        """
        try:
            status = await self.get_status()
            return status.get("cycle_count", 0)
        except Exception as e:
            logger.error(f"Get cycle count failed: {e}")
            return 0

    async def get_improvements_applied(self) -> int:
        """
        Get total number of improvements applied

        Returns:
            Total improvements count
        """
        try:
            status = await self.get_status()
            return status.get("total_improvements_applied", 0)
        except Exception as e:
            logger.error(f"Get improvements count failed: {e}")
            return 0

    async def close(self):
        """Close the client"""
        await self._client.aclose()
        logger.info("SystemBCMClient closed")

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()


# ===========================================================================
# EventBus Integration Helpers
# ===========================================================================

class SystemBCMEventPublisher:
    """
    Helper for publishing platform events to System BCM

    Usage:
        publisher = SystemBCMEventPublisher(eventbus)

        # On health degradation
        await publisher.health_degraded("api-gateway", "response_time", 500, 200)

        # On service failure
        await publisher.service_failed("rag-service", "connection_error", "Cannot connect to Qdrant")

        # On resource contention
        await publisher.resource_contention("cpu", 95, 80)
    """

    def __init__(self, eventbus):
        """
        Initialize publisher

        Args:
            eventbus: EventBus instance from infrastructure.eventbus
        """
        self.eventbus = eventbus

    async def health_degraded(
        self,
        service: str,
        metric: str,
        value: float,
        threshold: float,
        severity: str = "warning"
    ):
        """
        Publish health degradation event

        Args:
            service: Service name
            metric: Metric name (e.g., "response_time", "error_rate")
            value: Current value
            threshold: Threshold value
            severity: Severity level (warning, error, critical)
        """
        from infrastructure.eventbus import Event

        await self.eventbus.publish(Event(
            type="platform.health.degraded",
            data={
                "service": service,
                "severity": severity,
                "metric": metric,
                "value": value,
                "threshold": threshold,
                "timestamp": datetime.utcnow().isoformat()
            },
            source=service
        ))

    async def service_failed(
        self,
        service: str,
        incident_type: str,
        error: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Publish service failure event

        Args:
            service: Service name
            incident_type: Type of failure (e.g., "connection_error", "timeout", "crash")
            error: Error message
            details: Additional details
        """
        from infrastructure.eventbus import Event

        await self.eventbus.publish(Event(
            type="platform.service.failed",
            data={
                "service": service,
                "type": incident_type,
                "error": error,
                "details": details or {},
                "timestamp": datetime.utcnow().isoformat()
            },
            source=service
        ))

    async def resource_contention(
        self,
        resource_type: str,
        utilization: float,
        threshold: float,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Publish resource contention event

        Args:
            resource_type: Type of resource (cpu, memory, network, disk_io)
            utilization: Current utilization (percentage)
            threshold: Threshold (percentage)
            details: Additional details
        """
        from infrastructure.eventbus import Event

        await self.eventbus.publish(Event(
            type="platform.resources.contention",
            data={
                "resource_type": resource_type,
                "utilization": utilization,
                "threshold": threshold,
                "details": details or {},
                "timestamp": datetime.utcnow().isoformat()
            },
            source="resource_monitor"
        ))

    async def recovery_completed(
        self,
        service: str,
        procedure_id: str,
        recovery_time: float,
        status: str = "success"
    ):
        """
        Publish recovery completed event

        Args:
            service: Service name
            procedure_id: Recovery procedure ID
            recovery_time: Recovery time in seconds
            status: Recovery status (success, failed, partial)
        """
        from infrastructure.eventbus import Event

        await self.eventbus.publish(Event(
            type="platform.recovery.completed",
            data={
                "service": service,
                "procedure_id": procedure_id,
                "recovery_time_seconds": recovery_time,
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            },
            source=service
        ))


# ===========================================================================
# Monitoring Integration Helpers
# ===========================================================================

class SystemBCMMetricsCollector:
    """
    Helper for collecting System BCM metrics from any service

    Usage:
        collector = SystemBCMMetricsCollector()

        # Register metrics
        collector.register_service_metric("api-gateway", "availability", 99.95)
        collector.register_rto_metric("api-gateway", target=60, actual=45)

        # Export to Prometheus
        metrics = collector.export_prometheus()
    """

    def __init__(self):
        self.metrics: Dict[str, float] = {}

    def register_service_metric(self, service: str, metric: str, value: float):
        """Register a service metric"""
        key = f"platform_service_{metric}{{service=\"{service}\"}}"
        self.metrics[key] = value

    def register_rto_metric(self, service: str, target: float, actual: float):
        """Register RTO metric"""
        self.register_service_metric(service, "rto_target_seconds", target)
        self.register_service_metric(service, "rto_actual_seconds", actual)

    def register_rpo_metric(self, service: str, target: float, actual: float):
        """Register RPO metric"""
        self.register_service_metric(service, "rpo_target_seconds", target)
        self.register_service_metric(service, "rpo_actual_seconds", actual)

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        for key, value in self.metrics.items():
            lines.append(f"{key} {value}")
        return "\n".join(lines)


# ===========================================================================
# Usage Examples
# ===========================================================================

async def example_usage():
    """Example usage of System BCM Client"""

    # Create client
    async with SystemBCMClient("http://localhost:8050") as client:

        # Check health
        health = await client.health()
        print(f"Health: {health}")

        # Get status
        status = await client.get_status()
        print(f"Cycle count: {status['cycle_count']}")
        print(f"Improvements: {status['total_improvements_applied']}")

        # Trigger cycle
        result = await client.trigger_cycle()
        print(f"Cycle result: {result['status']}")

        # Trigger recovery
        await client.trigger_recovery("api-gateway", "timeout")

        # Get metrics
        metrics = await client.get_metrics()
        print(f"Metrics:\n{metrics}")


async def example_eventbus_integration():
    """Example EventBus integration"""
    from infrastructure.eventbus import create_eventbus

    # Create EventBus
    eventbus = create_eventbus('redis')

    # Create publisher
    publisher = SystemBCMEventPublisher(eventbus)

    # Publish health degradation
    await publisher.health_degraded(
        service="api-gateway",
        metric="response_time_p95",
        value=500,
        threshold=200,
        severity="warning"
    )

    # Publish service failure
    await publisher.service_failed(
        service="rag-service",
        incident_type="connection_error",
        error="Cannot connect to Qdrant",
        details={"qdrant_url": "http://qdrant:6333"}
    )

    # Publish resource contention
    await publisher.resource_contention(
        resource_type="cpu",
        utilization=95,
        threshold=80
    )


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
