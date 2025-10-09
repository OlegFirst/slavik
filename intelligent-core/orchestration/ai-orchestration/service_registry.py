"""
Service Registry
================

Dynamic service discovery and health-aware routing for AI Orchestrator.

Responsibilities:
- Service registration and discovery
- Health checking
- Load balancing
- Retry logic with exponential backoff
- Circuit breaker pattern
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import aiohttp


logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceInfo:
    """
    Service registration information.

    Attributes:
        name: Service name
        url: Base URL
        health_endpoint: Health check endpoint
        status: Current health status
        last_check: Last health check timestamp
        failure_count: Consecutive failure count
        metadata: Additional service metadata
    """
    name: str
    url: str
    health_endpoint: str
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_check: Optional[datetime] = None
    failure_count: int = 0
    response_times: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def avg_response_time(self) -> float:
        """Calculate average response time."""
        if not self.response_times:
            return 0.0
        return sum(self.response_times[-10:]) / min(len(self.response_times), 10)

    def is_available(self) -> bool:
        """Check if service is available for requests."""
        return self.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]


class ServiceRegistry:
    """
    Dynamic service discovery and health-aware routing.

    Features:
    - Service registration and discovery
    - Automatic health checking
    - Retry logic with exponential backoff
    - Circuit breaker pattern
    - Load balancing across multiple instances

    Example:
        ```python
        registry = ServiceRegistry()
        await registry.initialize()

        # Register services
        await registry.register_service(
            'bia',
            'http://localhost:8012',
            '/health'
        )

        # Call service with automatic retry
        result = await registry.call_service(
            'bia',
            'POST',
            '/api/v1/processes',
            {'name': 'IT Systems'}
        )
        ```
    """

    def __init__(
        self,
        health_check_interval: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        circuit_breaker_threshold: int = 5
    ):
        """
        Initialize service registry.

        Args:
            health_check_interval: Seconds between health checks
            max_retries: Maximum retry attempts
            retry_delay: Initial retry delay (exponential backoff)
            circuit_breaker_threshold: Failures before circuit opens
        """
        self.services: Dict[str, ServiceInfo] = {}
        self.health_check_interval = health_check_interval
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.circuit_breaker_threshold = circuit_breaker_threshold

        self._health_check_task: Optional[asyncio.Task] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self._initialized = False

        logger.info("ServiceRegistry created")

    async def initialize(self) -> None:
        """Initialize the service registry."""
        if self._initialized:
            logger.warning("ServiceRegistry already initialized")
            return

        # Create HTTP session
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )

        # Start health check loop
        self._health_check_task = asyncio.create_task(self._health_check_loop())

        self._initialized = True
        logger.info("ServiceRegistry initialized")

    async def shutdown(self) -> None:
        """Shutdown the service registry."""
        logger.info("Shutting down ServiceRegistry...")

        # Cancel health checks
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        # Close HTTP session
        if self._session:
            await self._session.close()

        logger.info("ServiceRegistry shutdown complete")

    async def register_service(
        self,
        name: str,
        url: str,
        health_endpoint: str = '/health',
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Register a service.

        Args:
            name: Service name (e.g., 'bia', 'risk')
            url: Base URL (e.g., 'http://localhost:8012')
            health_endpoint: Health check endpoint (default: '/health')
            metadata: Additional service metadata
        """
        service_info = ServiceInfo(
            name=name,
            url=url,
            health_endpoint=health_endpoint,
            metadata=metadata or {}
        )

        self.services[name] = service_info

        # Immediate health check
        await self._check_service_health(service_info)

        logger.info(f"Registered service '{name}' at {url} (status: {service_info.status.value})")

    async def get_service(self, name: str) -> Optional[ServiceInfo]:
        """
        Get service info if available.

        Args:
            name: Service name

        Returns:
            ServiceInfo if service is available, None otherwise
        """
        service = self.services.get(name)

        if not service:
            logger.warning(f"Service '{name}' not registered")
            return None

        if not service.is_available():
            logger.warning(f"Service '{name}' is not available (status: {service.status.value})")
            return None

        return service

    async def call_service(
        self,
        service_name: str,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Call a service with automatic retry and circuit breaker.

        Args:
            service_name: Name of the service
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., '/api/v1/processes')
            data: Request body (for POST/PUT)
            params: Query parameters
            headers: HTTP headers

        Returns:
            dict: Response data

        Raises:
            ValueError: If service not found or unavailable
            RuntimeError: If all retry attempts fail
        """
        service = await self.get_service(service_name)

        if not service:
            raise ValueError(f"Service '{service_name}' not available")

        # Build full URL
        url = f"{service.url}{endpoint}"

        # Default headers
        if headers is None:
            headers = {}
        headers.setdefault('Content-Type', 'application/json')

        # Retry loop with exponential backoff
        last_error = None
        for attempt in range(self.max_retries):
            try:
                start_time = datetime.utcnow()

                async with self._session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=headers
                ) as response:
                    response_time = (datetime.utcnow() - start_time).total_seconds()

                    # Record response time
                    service.response_times.append(response_time)

                    # Reset failure count on success
                    service.failure_count = 0

                    # Check response status
                    if response.status >= 200 and response.status < 300:
                        result = await response.json()
                        logger.info(
                            f"Service call succeeded: {service_name} {method} {endpoint} "
                            f"(status={response.status}, time={response_time:.2f}s)"
                        )
                        return result
                    else:
                        error_text = await response.text()
                        logger.warning(
                            f"Service returned error: {service_name} {method} {endpoint} "
                            f"(status={response.status}, error={error_text})"
                        )
                        last_error = f"HTTP {response.status}: {error_text}"

            except asyncio.TimeoutError as e:
                last_error = f"Timeout calling {service_name}"
                logger.warning(f"Attempt {attempt + 1}/{self.max_retries} failed: {last_error}")
                service.failure_count += 1

            except aiohttp.ClientError as e:
                last_error = f"Connection error: {str(e)}"
                logger.warning(f"Attempt {attempt + 1}/{self.max_retries} failed: {last_error}")
                service.failure_count += 1

            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                logger.error(f"Attempt {attempt + 1}/{self.max_retries} failed: {last_error}", exc_info=True)
                service.failure_count += 1

            # Exponential backoff before retry
            if attempt < self.max_retries - 1:
                delay = self.retry_delay * (2 ** attempt)
                logger.info(f"Retrying in {delay}s...")
                await asyncio.sleep(delay)

        # All retries failed - update service status
        if service.failure_count >= self.circuit_breaker_threshold:
            service.status = ServiceStatus.UNHEALTHY
            logger.error(f"Circuit breaker opened for service '{service_name}'")

        raise RuntimeError(
            f"Service call failed after {self.max_retries} attempts: {last_error}"
        )

    async def _health_check_loop(self) -> None:
        """Background task to check service health."""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)

                # Check all services
                for service in self.services.values():
                    await self._check_service_health(service)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}", exc_info=True)

    async def _check_service_health(self, service: ServiceInfo) -> None:
        """
        Check health of a single service.

        Args:
            service: Service to check
        """
        try:
            url = f"{service.url}{service.health_endpoint}"

            async with self._session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                service.last_check = datetime.utcnow()

                if response.status == 200:
                    old_status = service.status
                    service.status = ServiceStatus.HEALTHY
                    service.failure_count = 0

                    if old_status != ServiceStatus.HEALTHY:
                        logger.info(f"Service '{service.name}' is now HEALTHY")
                else:
                    service.status = ServiceStatus.DEGRADED
                    logger.warning(f"Service '{service.name}' returned status {response.status}")

        except Exception as e:
            service.last_check = datetime.utcnow()
            service.failure_count += 1

            if service.failure_count >= self.circuit_breaker_threshold:
                old_status = service.status
                service.status = ServiceStatus.UNHEALTHY

                if old_status != ServiceStatus.UNHEALTHY:
                    logger.error(f"Service '{service.name}' is UNHEALTHY: {e}")
            else:
                service.status = ServiceStatus.DEGRADED
                logger.debug(f"Service '{service.name}' health check failed: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        return {
            'total_services': len(self.services),
            'healthy_services': sum(1 for s in self.services.values() if s.status == ServiceStatus.HEALTHY),
            'degraded_services': sum(1 for s in self.services.values() if s.status == ServiceStatus.DEGRADED),
            'unhealthy_services': sum(1 for s in self.services.values() if s.status == ServiceStatus.UNHEALTHY),
            'services': {
                name: {
                    'status': service.status.value,
                    'last_check': service.last_check.isoformat() if service.last_check else None,
                    'failure_count': service.failure_count,
                    'avg_response_time': service.avg_response_time
                }
                for name, service in self.services.items()
            }
        }
