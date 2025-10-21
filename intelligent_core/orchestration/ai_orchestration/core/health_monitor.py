"""
Health Monitor - Health checking system for all services
Supports Docker health checks, HTTP endpoints, and custom checks

Phase 1 Integration: Publishes health events to EventBus
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import asyncio
import httpx

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status values"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Health check result"""
    service_name: str
    status: HealthStatus
    checked_at: datetime = field(default_factory=datetime.utcnow)
    response_time_ms: Optional[float] = None
    message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def is_healthy(self) -> bool:
        """Check if status is healthy"""
        return self.status == HealthStatus.HEALTHY


@dataclass
class HealthCheck:
    """Health check configuration"""
    service_name: str
    check_type: str  # docker, http, custom
    interval: int = 30  # seconds
    timeout: int = 10  # seconds
    retries: int = 3
    config: Dict[str, Any] = field(default_factory=dict)
    custom_checker: Optional[Callable] = None


class HealthMonitor:
    """
    Health monitoring for all services

    Supports multiple check types:
    - Docker: Check container status
    - HTTP: Check HTTP endpoint
    - Custom: Custom check function

    Phase 1: Publishes health status changes to EventBus
    """

    def __init__(self):
        self.checks: Dict[str, HealthCheck] = {}
        self.results: Dict[str, HealthCheckResult] = {}
        self.monitoring = False
        self.docker_client = None
        self.http_client = httpx.AsyncClient(timeout=10.0)
        self.eventbus = None  # EventBus integration (Phase 1)
        logger.info("HealthMonitor initialized")

    async def connect_docker(self, docker_client) -> None:
        """
        Connect to Docker for container health checks

        Args:
            docker_client: Docker client instance
        """
        self.docker_client = docker_client
        logger.info("HealthMonitor connected to Docker")

    async def connect_eventbus(self, eventbus) -> None:
        """
        Connect to EventBus for publishing health events (Phase 1)

        Args:
            eventbus: EventBus instance (from infrastructure.eventbus)
        """
        self.eventbus = eventbus
        logger.info("HealthMonitor connected to EventBus - will publish health events")

    async def register_check(self, check: HealthCheck) -> None:
        """
        Register a health check

        Args:
            check: HealthCheck configuration
        """
        self.checks[check.service_name] = check
        logger.info(f"Registered health check for {check.service_name} (type: {check.check_type})")

    async def unregister_check(self, service_name: str) -> bool:
        """
        Unregister a health check

        Args:
            service_name: Name of the service

        Returns:
            True if unregistered successfully
        """
        if service_name in self.checks:
            del self.checks[service_name]
            if service_name in self.results:
                del self.results[service_name]
            logger.info(f"Unregistered health check for {service_name}")
            return True
        return False

    async def check_service(self, service_name: str) -> HealthCheckResult:
        """
        Run health check for a service

        Args:
            service_name: Name of the service

        Returns:
            HealthCheckResult
        """
        check = self.checks.get(service_name)
        if not check:
            logger.warning(f"No health check registered for {service_name}")
            return HealthCheckResult(
                service_name=service_name,
                status=HealthStatus.UNKNOWN,
                message="No health check registered"
            )

        # Run check based on type
        if check.check_type == "docker":
            result = await self._check_docker(check)
        elif check.check_type == "http":
            result = await self._check_http(check)
        elif check.check_type == "custom" and check.custom_checker:
            result = await self._check_custom(check)
        else:
            result = HealthCheckResult(
                service_name=service_name,
                status=HealthStatus.UNKNOWN,
                message=f"Unknown check type: {check.check_type}"
            )

        # Store result
        self.results[service_name] = result

        return result

    async def _check_docker(self, check: HealthCheck) -> HealthCheckResult:
        """Check Docker container health"""
        if not self.docker_client:
            return HealthCheckResult(
                service_name=check.service_name,
                status=HealthStatus.UNKNOWN,
                message="Docker client not connected"
            )

        try:
            start_time = datetime.utcnow()
            container_name = check.config.get('container_name', f"iso-22301-{check.service_name}-1")

            # Get container status
            try:
                container = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.docker_client.containers.get,
                    container_name
                )
                status = container.status
                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

                if status == "running":
                    # Check container health if available
                    health = container.attrs.get('State', {}).get('Health', {})
                    if health:
                        health_status = health.get('Status', 'none')
                        if health_status == 'healthy':
                            return HealthCheckResult(
                                service_name=check.service_name,
                                status=HealthStatus.HEALTHY,
                                response_time_ms=response_time,
                                message="Container running and healthy",
                                details={'container_health': health_status}
                            )
                        elif health_status == 'unhealthy':
                            return HealthCheckResult(
                                service_name=check.service_name,
                                status=HealthStatus.UNHEALTHY,
                                response_time_ms=response_time,
                                message="Container unhealthy",
                                details={'container_health': health_status}
                            )
                        else:  # starting
                            return HealthCheckResult(
                                service_name=check.service_name,
                                status=HealthStatus.DEGRADED,
                                response_time_ms=response_time,
                                message="Container starting",
                                details={'container_health': health_status}
                            )
                    else:
                        # No health check defined, just check if running
                        return HealthCheckResult(
                            service_name=check.service_name,
                            status=HealthStatus.HEALTHY,
                            response_time_ms=response_time,
                            message="Container running"
                        )
                else:
                    return HealthCheckResult(
                        service_name=check.service_name,
                        status=HealthStatus.UNHEALTHY,
                        response_time_ms=response_time,
                        message=f"Container status: {status}",
                        details={'container_status': status}
                    )

            except Exception as e:
                return HealthCheckResult(
                    service_name=check.service_name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Container not found: {e}"
                )

        except Exception as e:
            logger.error(f"Docker health check failed for {check.service_name}: {e}")
            return HealthCheckResult(
                service_name=check.service_name,
                status=HealthStatus.UNKNOWN,
                message=f"Check failed: {str(e)}"
            )

    async def _check_http(self, check: HealthCheck) -> HealthCheckResult:
        """Check HTTP endpoint health"""
        url = check.config.get('url')
        if not url:
            return HealthCheckResult(
                service_name=check.service_name,
                status=HealthStatus.UNKNOWN,
                message="No URL configured"
            )

        expected_status = check.config.get('expected_status', 200)
        method = check.config.get('method', 'GET').upper()

        for attempt in range(check.retries):
            try:
                start_time = datetime.utcnow()

                if method == 'GET':
                    response = await self.http_client.get(url)
                elif method == 'POST':
                    response = await self.http_client.post(url, json=check.config.get('payload', {}))
                else:
                    response = await self.http_client.request(method, url)

                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

                if response.status_code == expected_status:
                    return HealthCheckResult(
                        service_name=check.service_name,
                        status=HealthStatus.HEALTHY,
                        response_time_ms=response_time,
                        message=f"HTTP {response.status_code}",
                        details={'status_code': response.status_code}
                    )
                else:
                    return HealthCheckResult(
                        service_name=check.service_name,
                        status=HealthStatus.DEGRADED,
                        response_time_ms=response_time,
                        message=f"Unexpected status: {response.status_code}",
                        details={'status_code': response.status_code, 'expected': expected_status}
                    )

            except httpx.TimeoutException:
                if attempt == check.retries - 1:
                    return HealthCheckResult(
                        service_name=check.service_name,
                        status=HealthStatus.UNHEALTHY,
                        message="HTTP timeout"
                    )
                await asyncio.sleep(1)

            except Exception as e:
                if attempt == check.retries - 1:
                    return HealthCheckResult(
                        service_name=check.service_name,
                        status=HealthStatus.UNHEALTHY,
                        message=f"HTTP check failed: {str(e)}"
                    )
                await asyncio.sleep(1)

    async def _check_custom(self, check: HealthCheck) -> HealthCheckResult:
        """Run custom health check"""
        if not check.custom_checker:
            return HealthCheckResult(
                service_name=check.service_name,
                status=HealthStatus.UNKNOWN,
                message="No custom checker function"
            )

        try:
            start_time = datetime.utcnow()
            result = await check.custom_checker(check.service_name, check.config)
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            if isinstance(result, bool):
                # Simple bool return
                return HealthCheckResult(
                    service_name=check.service_name,
                    status=HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY,
                    response_time_ms=response_time,
                    message="Custom check completed"
                )
            elif isinstance(result, HealthCheckResult):
                # Full result return
                return result
            else:
                return HealthCheckResult(
                    service_name=check.service_name,
                    status=HealthStatus.UNKNOWN,
                    message="Invalid custom checker return type"
                )

        except Exception as e:
            logger.error(f"Custom health check failed for {check.service_name}: {e}")
            return HealthCheckResult(
                service_name=check.service_name,
                status=HealthStatus.UNKNOWN,
                message=f"Custom check error: {str(e)}"
            )

    async def monitor_continuously(self) -> None:
        """
        Start continuous monitoring

        Runs health checks on all registered services at their configured intervals
        Phase 1: Publishes health status changes to EventBus
        """
        self.monitoring = True
        logger.info("Starting continuous health monitoring")

        # Track next check time for each service
        next_checks: Dict[str, datetime] = {}

        # Phase 1: Track previous status for change detection
        previous_status: Dict[str, HealthStatus] = {}

        while self.monitoring:
            current_time = datetime.utcnow()

            for service_name, check in self.checks.items():
                # Check if it's time to run this check
                if service_name not in next_checks or current_time >= next_checks[service_name]:
                    # Run check
                    result = await self.check_service(service_name)

                    # Phase 1: Publish event if status changed
                    prev_status = previous_status.get(service_name)
                    if prev_status != result.status:
                        await self._publish_health_event(service_name, result, prev_status)
                        previous_status[service_name] = result.status

                    # Log if unhealthy
                    if result.status == HealthStatus.UNHEALTHY:
                        logger.warning(f"Service {service_name} unhealthy: {result.message}")
                    elif result.status == HealthStatus.DEGRADED:
                        logger.info(f"Service {service_name} degraded: {result.message}")

                    # Schedule next check
                    next_checks[service_name] = current_time + timedelta(seconds=check.interval)

            # Sleep for a short period before next iteration
            await asyncio.sleep(5)

        logger.info("Stopped continuous health monitoring")

    async def stop_monitoring(self) -> None:
        """Stop continuous monitoring"""
        self.monitoring = False
        logger.info("Stopping health monitoring")

    async def _publish_health_event(
        self,
        service_name: str,
        result: HealthCheckResult,
        previous_status: Optional[HealthStatus]
    ) -> None:
        """
        Publish health status change event to EventBus (Phase 1)

        Args:
            service_name: Name of the service
            result: Current health check result
            previous_status: Previous health status (None if first check)
        """
        if not self.eventbus:
            return  # EventBus not connected, skip publishing

        try:
            # Import here to avoid circular dependencies
            from infrastructure.eventbus import Event

            # Create event based on current status
            event_type = f'infrastructure.health.{result.status.value}'

            event = Event.create(
                event_type=event_type,  # Parameter name is 'event_type'
                data={
                    'service_name': service_name,
                    'status': result.status.value,
                    'previous_status': previous_status.value if previous_status else None,
                    'response_time_ms': result.response_time_ms,
                    'message': result.message,
                    'details': result.details,
                    'checked_at': result.checked_at.isoformat()
                },
                source='health_monitor',
                tenant_id='system'  # System-level infrastructure event
            )

            await self.eventbus.publish(event)
            logger.info(f" Published health event: {service_name} → {result.status.value}")

        except Exception as e:
            logger.error(f"Failed to publish health event for {service_name}: {e}")

    async def get_all_results(self) -> Dict[str, HealthCheckResult]:
        """
        Get all health check results

        Returns:
            Dictionary of service_name -> HealthCheckResult
        """
        return self.results.copy()

    async def get_unhealthy_services(self) -> List[str]:
        """
        Get list of unhealthy services

        Returns:
            List of service names
        """
        return [
            service_name
            for service_name, result in self.results.items()
            if result.status == HealthStatus.UNHEALTHY
        ]

    async def close(self) -> None:
        """Close HTTP client"""
        await self.http_client.aclose()