"""
Health Checker for API Gateway
Production-grade health monitoring with background checks and failure tracking
"""

import asyncio
import logging
import time
from typing import Dict, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field

import httpx

from config import settings

logger = logging.getLogger(__name__)


@dataclass
class HealthStatus:
    """
    Health status for a service instance

    Attributes:
        url: Service URL
        healthy: Whether service is currently healthy
        last_check: Timestamp of last health check
        last_success: Timestamp of last successful check
        consecutive_failures: Number of consecutive failures
        total_checks: Total number of health checks performed
        total_failures: Total number of failed checks
        response_time_ms: Last response time in milliseconds
        error_message: Last error message (if unhealthy)
    """
    url: str
    healthy: bool = True
    last_check: Optional[datetime] = None
    last_success: Optional[datetime] = None
    consecutive_failures: int = 0
    total_checks: int = 0
    total_failures: int = 0
    response_time_ms: float = 0.0
    error_message: Optional[str] = None


class HealthChecker:
    """
    Production-grade health checker for backend services

    Features:
    - Background health check loop (configurable interval)
    - HTTP GET to /health endpoints
    - Track response time
    - Mark unhealthy after N failures
    - Auto-recovery detection
    - Thread-safe operations
    - Comprehensive metrics

    Usage:
        health_checker = HealthChecker(
            check_interval=30,
            unhealthy_threshold=3
        )

        # Register services
        health_checker.register_service("service1", "http://localhost:8001")
        health_checker.register_service("service2", "http://localhost:8002")

        # Start background monitoring
        await health_checker.start_monitoring()

        # Get health status
        status = health_checker.get_health_status("service1")
        if status.healthy:
            # Service is healthy
            pass
    """

    def __init__(
        self,
        check_interval: int = None,
        unhealthy_threshold: int = None,
        timeout: float = None
    ):
        """
        Initialize health checker

        Args:
            check_interval: Interval between health checks in seconds (default: from config)
            unhealthy_threshold: Failures before marking unhealthy (default: from config)
            timeout: Health check timeout in seconds (default: from config)
        """
        self.check_interval = check_interval or settings.health_check_interval
        self.unhealthy_threshold = unhealthy_threshold or settings.unhealthy_threshold
        self.timeout = timeout or settings.health_check_timeout

        # Service registry
        self._services: Dict[str, str] = {}  # name -> base_url

        # Health status tracking
        self._health_status: Dict[str, HealthStatus] = {}

        # Background monitoring
        self._monitoring_task: Optional[asyncio.Task] = None
        self._monitoring_active: bool = False
        self._stop_event = asyncio.Event()

        # HTTP client for health checks
        self._http_client: Optional[httpx.AsyncClient] = None

        # Thread safety
        self._lock = asyncio.Lock()

        logger.info(
            f"HealthChecker initialized: interval={self.check_interval}s, "
            f"threshold={self.unhealthy_threshold}, timeout={self.timeout}s"
        )

    async def _ensure_http_client(self) -> httpx.AsyncClient:
        """Ensure HTTP client is initialized"""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                follow_redirects=False,
            )
        return self._http_client

    async def close(self) -> None:
        """Close health checker and cleanup resources"""
        # Stop monitoring
        self.stop_monitoring()

        # Wait for monitoring task to complete
        if self._monitoring_task:
            try:
                await asyncio.wait_for(self._monitoring_task, timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("Health monitoring task did not stop gracefully")
                self._monitoring_task.cancel()

        # Close HTTP client
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

        logger.info("HealthChecker closed")

    def register_service(self, name: str, base_url: str) -> None:
        """
        Register service for health monitoring

        Args:
            name: Service name (unique identifier)
            base_url: Base URL of service (e.g., "http://localhost:8001")
        """
        self._services[name] = base_url

        # Initialize health status
        if name not in self._health_status:
            self._health_status[name] = HealthStatus(url=base_url)

        logger.info(f"Registered service for health monitoring: {name} -> {base_url}")

    def unregister_service(self, name: str) -> None:
        """
        Unregister service from health monitoring

        Args:
            name: Service name
        """
        if name in self._services:
            del self._services[name]
            logger.info(f"Unregistered service: {name}")

        if name in self._health_status:
            del self._health_status[name]

    async def check_service_health(self, name: str) -> HealthStatus:
        """
        Perform health check on specific service

        Args:
            name: Service name

        Returns:
            HealthStatus object with check results
        """
        if name not in self._services:
            logger.error(f"Service {name} not registered")
            return HealthStatus(url="", healthy=False, error_message="Service not registered")

        base_url = self._services[name]
        health_url = f"{base_url}/health"

        async with self._lock:
            status = self._health_status.get(name, HealthStatus(url=base_url))
            status.total_checks += 1
            status.last_check = datetime.utcnow()

        start_time = time.time()

        try:
            client = await self._ensure_http_client()

            # Perform health check
            response = await client.get(health_url)

            # Calculate response time
            response_time_ms = (time.time() - start_time) * 1000

            # Check if response is successful
            is_healthy = response.status_code == 200

            async with self._lock:
                status.response_time_ms = response_time_ms

                if is_healthy:
                    # Service is healthy
                    was_unhealthy = not status.healthy

                    status.healthy = True
                    status.consecutive_failures = 0
                    status.last_success = datetime.utcnow()
                    status.error_message = None

                    if was_unhealthy:
                        logger.info(
                            f"Service {name} recovered (response_time: {response_time_ms:.2f}ms)"
                        )
                    else:
                        logger.debug(
                            f"Health check passed for {name} (response_time: {response_time_ms:.2f}ms)"
                        )
                else:
                    # Non-200 status code
                    status.consecutive_failures += 1
                    status.total_failures += 1
                    status.error_message = f"HTTP {response.status_code}"

                    # Mark unhealthy if threshold exceeded
                    if status.consecutive_failures >= self.unhealthy_threshold:
                        if status.healthy:
                            logger.warning(
                                f"Service {name} marked unhealthy after "
                                f"{status.consecutive_failures} failures"
                            )
                        status.healthy = False
                    else:
                        logger.debug(
                            f"Health check failed for {name}: HTTP {response.status_code} "
                            f"({status.consecutive_failures}/{self.unhealthy_threshold})"
                        )

        except httpx.TimeoutException:
            # Timeout
            response_time_ms = (time.time() - start_time) * 1000

            async with self._lock:
                status.consecutive_failures += 1
                status.total_failures += 1
                status.response_time_ms = response_time_ms
                status.error_message = "Health check timeout"

                if status.consecutive_failures >= self.unhealthy_threshold:
                    if status.healthy:
                        logger.warning(
                            f"Service {name} marked unhealthy: timeout after "
                            f"{status.consecutive_failures} failures"
                        )
                    status.healthy = False

        except httpx.RequestError as e:
            # Connection error
            response_time_ms = (time.time() - start_time) * 1000

            async with self._lock:
                status.consecutive_failures += 1
                status.total_failures += 1
                status.response_time_ms = response_time_ms
                status.error_message = f"Connection error: {str(e)}"

                if status.consecutive_failures >= self.unhealthy_threshold:
                    if status.healthy:
                        logger.warning(
                            f"Service {name} marked unhealthy: {str(e)} "
                            f"({status.consecutive_failures} failures)"
                        )
                    status.healthy = False

        except Exception as e:
            # Unexpected error
            logger.error(f"Unexpected error checking health of {name}: {e}")

            async with self._lock:
                status.consecutive_failures += 1
                status.total_failures += 1
                status.error_message = f"Unexpected error: {str(e)}"

                if status.consecutive_failures >= self.unhealthy_threshold:
                    status.healthy = False

        # Update stored status
        async with self._lock:
            self._health_status[name] = status

        return status

    async def check_all_services(self) -> Dict[str, HealthStatus]:
        """
        Perform health check on all registered services

        Returns:
            Dict mapping service name to HealthStatus
        """
        if not self._services:
            logger.debug("No services registered for health check")
            return {}

        # Check all services concurrently
        tasks = [
            self.check_service_health(name)
            for name in self._services.keys()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Build results dict
        health_results = {}
        for name, result in zip(self._services.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"Health check failed for {name}: {result}")
                health_results[name] = HealthStatus(
                    url=self._services[name],
                    healthy=False,
                    error_message=str(result)
                )
            else:
                health_results[name] = result

        return health_results

    async def start_monitoring(self) -> None:
        """Start background health monitoring loop"""
        if self._monitoring_active:
            logger.warning("Health monitoring already active")
            return

        self._monitoring_active = True
        self._stop_event.clear()

        # Create monitoring task
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())

        logger.info(
            f"Started health monitoring (interval: {self.check_interval}s, "
            f"services: {len(self._services)})"
        )

    def stop_monitoring(self) -> None:
        """Stop background health monitoring loop"""
        if not self._monitoring_active:
            return

        self._monitoring_active = False
        self._stop_event.set()

        logger.info("Stopped health monitoring")

    async def _monitoring_loop(self) -> None:
        """
        Background monitoring loop

        Performs health checks at regular intervals
        """
        logger.info("Health monitoring loop started")

        while self._monitoring_active:
            try:
                # Perform health checks
                await self.check_all_services()

                # Wait for next check interval (or stop event)
                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(),
                        timeout=self.check_interval
                    )
                    # Stop event was set, exit loop
                    break
                except asyncio.TimeoutError:
                    # Timeout is normal, continue to next iteration
                    pass

            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                # Continue monitoring even on errors
                await asyncio.sleep(5)

        logger.info("Health monitoring loop stopped")

    def get_health_status(self, name: str) -> Optional[HealthStatus]:
        """
        Get health status for specific service

        Args:
            name: Service name

        Returns:
            HealthStatus or None if service not found
        """
        return self._health_status.get(name)

    def get_all_health_status(self) -> Dict[str, Dict]:
        """
        Get health status for all services

        Returns:
            Dict mapping service name to health status dict
        """
        return {
            name: {
                "url": status.url,
                "healthy": status.healthy,
                "last_check": status.last_check.isoformat() if status.last_check else None,
                "last_success": status.last_success.isoformat() if status.last_success else None,
                "consecutive_failures": status.consecutive_failures,
                "total_checks": status.total_checks,
                "total_failures": status.total_failures,
                "response_time_ms": round(status.response_time_ms, 2),
                "error_message": status.error_message,
            }
            for name, status in self._health_status.items()
        }

    def is_service_healthy(self, name: str) -> bool:
        """
        Check if service is healthy

        Args:
            name: Service name

        Returns:
            True if healthy, False otherwise
        """
        status = self._health_status.get(name)
        return status.healthy if status else False

    def get_healthy_services(self) -> Set[str]:
        """
        Get set of healthy service names

        Returns:
            Set of service names that are healthy
        """
        return {
            name for name, status in self._health_status.items()
            if status.healthy
        }

    def get_unhealthy_services(self) -> Set[str]:
        """
        Get set of unhealthy service names

        Returns:
            Set of service names that are unhealthy
        """
        return {
            name for name, status in self._health_status.items()
            if not status.healthy
        }

    async def get_metrics(self) -> Dict:
        """
        Get health checker metrics

        Returns:
            Dict with health checker metrics
        """
        async with self._lock:
            total_services = len(self._services)
            healthy_count = len(self.get_healthy_services())
            unhealthy_count = len(self.get_unhealthy_services())

            total_checks = sum(
                status.total_checks
                for status in self._health_status.values()
            )
            total_failures = sum(
                status.total_failures
                for status in self._health_status.values()
            )

            avg_response_time = 0.0
            if self._health_status:
                avg_response_time = sum(
                    status.response_time_ms
                    for status in self._health_status.values()
                ) / len(self._health_status)

            success_rate = 0.0
            if total_checks > 0:
                success_rate = ((total_checks - total_failures) / total_checks) * 100

            return {
                "monitoring_active": self._monitoring_active,
                "check_interval_seconds": self.check_interval,
                "unhealthy_threshold": self.unhealthy_threshold,
                "total_services": total_services,
                "healthy_services": healthy_count,
                "unhealthy_services": unhealthy_count,
                "total_checks": total_checks,
                "total_failures": total_failures,
                "success_rate_percent": round(success_rate, 2),
                "avg_response_time_ms": round(avg_response_time, 2),
            }


# Global health checker instance (singleton)
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """
    Get global health checker instance (singleton pattern)

    Returns:
        Global HealthChecker instance
    """
    global _health_checker

    if _health_checker is None:
        _health_checker = HealthChecker()
        logger.info("Created global HealthChecker")

    return _health_checker
