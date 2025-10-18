"""
Health Monitor

Self-monitoring component for service health tracking.
Provides real-time health status, metrics, and alerts.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import deque
import time

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Service health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Individual health check result"""
    name: str
    status: HealthStatus
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthMetrics:
    """Service health metrics"""
    uptime_seconds: float
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    active_requests: int = 0
    error_rate: float = 0.0
    avg_response_time_ms: float = 0.0
    recent_errors: List[str] = field(default_factory=list)


class HealthMonitor:
    """
    Health monitoring for self-aware services.

    Features:
    - Continuous health checks
    - Dependency monitoring (DB, Redis, EventBus, etc.)
    - Automatic degradation detection
    - Health metrics collection
    - Alert generation

    Usage:
        monitor = HealthMonitor("bia")
        await monitor.start()

        # Register dependency checks
        monitor.register_check("database", check_db_health)
        monitor.register_check("redis", check_redis_health)

        # Get current status
        status = await monitor.get_status()
    """

    def __init__(
        self,
        service_name: str,
        check_interval: int = 30,
        degraded_threshold: int = 2,
        down_threshold: int = 3
    ):
        """
        Initialize health monitor.

        Args:
            service_name: Service identifier
            check_interval: Health check interval in seconds
            degraded_threshold: Failed checks before degraded
            down_threshold: Failed checks before down
        """
        self.service_name = service_name
        self.check_interval = check_interval
        self.degraded_threshold = degraded_threshold
        self.down_threshold = down_threshold

        # State
        self._status = HealthStatus.UNKNOWN
        self._degraded_reason: Optional[str] = None
        self._start_time = datetime.utcnow()
        self._checks: Dict[str, callable] = {}
        self._check_results: Dict[str, deque] = {}  # Last N results per check
        self._max_history = 10

        # Metrics
        self._metrics = HealthMetrics(uptime_seconds=0)
        self._request_times: deque = deque(maxlen=100)
        self._error_count: deque = deque(maxlen=100)

        # Task
        self._monitor_task: Optional[asyncio.Task] = None
        self._running = False

        logger.info(f"HealthMonitor initialized for {service_name}")

    def register_check(self, name: str, check_func: callable):
        """
        Register a health check function.

        Args:
            name: Check identifier
            check_func: Async function that returns HealthCheck
        """
        self._checks[name] = check_func
        self._check_results[name] = deque(maxlen=self._max_history)
        logger.debug(f"Registered health check: {name}")

    async def start(self):
        """Start health monitoring"""
        if self._running:
            return

        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info(f"Health monitoring started for {self.service_name}")

    async def stop(self):
        """Stop health monitoring"""
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info(f"Health monitoring stopped for {self.service_name}")

    async def get_status(self) -> HealthCheck:
        """
        Get current health status.

        Returns:
            HealthCheck with overall status
        """
        # Run all checks
        check_results = await self._run_all_checks()

        # Determine overall status
        overall_status = self._calculate_overall_status(check_results)

        # Update metrics
        self._metrics.uptime_seconds = (datetime.utcnow() - self._start_time).total_seconds()

        return HealthCheck(
            name="overall",
            status=overall_status,
            message=self._degraded_reason or "Service healthy",
            timestamp=datetime.utcnow(),
            metadata={
                "checks": {name: result.status.value for name, result in check_results.items()},
                "metrics": self._get_metrics_dict()
            }
        )

    def get_status_sync(self) -> Dict[str, Any]:
        """Get status synchronously (for non-async contexts)"""
        return {
            "status": self._status.value,
            "uptime_seconds": (datetime.utcnow() - self._start_time).total_seconds(),
            "degraded_reason": self._degraded_reason
        }

    async def set_healthy(self):
        """Manually set service to healthy"""
        self._status = HealthStatus.HEALTHY
        self._degraded_reason = None
        logger.info(f"{self.service_name} marked as HEALTHY")

    async def set_degraded(self, reason: str):
        """Manually set service to degraded"""
        self._status = HealthStatus.DEGRADED
        self._degraded_reason = reason
        logger.warning(f"{self.service_name} marked as DEGRADED: {reason}")

    async def set_down(self, reason: str):
        """Manually set service to down"""
        self._status = HealthStatus.DOWN
        self._degraded_reason = reason
        logger.error(f"{self.service_name} marked as DOWN: {reason}")

    def record_request(self, duration_ms: float, error: bool = False):
        """
        Record request for metrics.

        Args:
            duration_ms: Request duration in milliseconds
            error: Whether request resulted in error
        """
        self._request_times.append(duration_ms)
        if error:
            self._error_count.append(1)
        else:
            self._error_count.append(0)

        # Update metrics
        self._update_metrics()

    def get_metrics(self) -> HealthMetrics:
        """Get current health metrics"""
        self._update_metrics()
        return self._metrics

    # Private methods

    async def _monitor_loop(self):
        """Main monitoring loop"""
        while self._running:
            try:
                await asyncio.sleep(self.check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitor loop: {e}", exc_info=True)

    async def _perform_health_checks(self):
        """Perform all registered health checks"""
        check_results = await self._run_all_checks()

        # Store results
        for name, result in check_results.items():
            self._check_results[name].append(result)

        # Update overall status
        self._status = self._calculate_overall_status(check_results)

        # Log if status changed
        if self._status != HealthStatus.HEALTHY:
            logger.warning(f"{self.service_name} health: {self._status.value}")

    async def _run_all_checks(self) -> Dict[str, HealthCheck]:
        """Run all registered health checks"""
        results = {}

        for name, check_func in self._checks.items():
            try:
                start = time.time()
                result = await check_func()
                duration = (time.time() - start) * 1000

                if isinstance(result, HealthCheck):
                    result.duration_ms = duration
                    results[name] = result
                else:
                    # Convert bool to HealthCheck
                    results[name] = HealthCheck(
                        name=name,
                        status=HealthStatus.HEALTHY if result else HealthStatus.DOWN,
                        duration_ms=duration
                    )
            except Exception as e:
                logger.error(f"Health check {name} failed: {e}", exc_info=True)
                results[name] = HealthCheck(
                    name=name,
                    status=HealthStatus.DOWN,
                    message=str(e)
                )

        return results

    def _calculate_overall_status(self, check_results: Dict[str, HealthCheck]) -> HealthStatus:
        """Calculate overall status from individual checks"""
        if not check_results:
            return HealthStatus.UNKNOWN

        # Count failures
        down_count = sum(1 for r in check_results.values() if r.status == HealthStatus.DOWN)
        degraded_count = sum(1 for r in check_results.values() if r.status == HealthStatus.DEGRADED)

        total_checks = len(check_results)

        # Determine status
        if down_count >= self.down_threshold:
            return HealthStatus.DOWN
        elif down_count > 0 or degraded_count >= self.degraded_threshold:
            return HealthStatus.DEGRADED
        elif degraded_count > 0:
            return HealthStatus.DEGRADED

        return HealthStatus.HEALTHY

    def _update_metrics(self):
        """Update health metrics from recorded data"""
        if self._request_times:
            self._metrics.avg_response_time_ms = sum(self._request_times) / len(self._request_times)

        if self._error_count:
            self._metrics.error_rate = sum(self._error_count) / len(self._error_count)

        self._metrics.uptime_seconds = (datetime.utcnow() - self._start_time).total_seconds()

    def _get_metrics_dict(self) -> Dict[str, Any]:
        """Get metrics as dictionary"""
        return {
            "uptime_seconds": self._metrics.uptime_seconds,
            "cpu_usage": self._metrics.cpu_usage,
            "memory_usage": self._metrics.memory_usage,
            "active_requests": self._metrics.active_requests,
            "error_rate": self._metrics.error_rate,
            "avg_response_time_ms": self._metrics.avg_response_time_ms,
            "recent_errors": self._metrics.recent_errors[:10]
        }


# Default health checks

async def check_database_health(db_session) -> HealthCheck:
    """Check database connection health"""
    try:
        # Simple query to check connection
        await db_session.execute("SELECT 1")
        return HealthCheck(
            name="database",
            status=HealthStatus.HEALTHY,
            message="Database connection healthy"
        )
    except Exception as e:
        return HealthCheck(
            name="database",
            status=HealthStatus.DOWN,
            message=f"Database error: {str(e)}"
        )


async def check_redis_health(redis_client) -> HealthCheck:
    """Check Redis connection health"""
    try:
        pong = await redis_client.ping()
        if pong:
            return HealthCheck(
                name="redis",
                status=HealthStatus.HEALTHY,
                message="Redis connection healthy"
            )
        else:
            return HealthCheck(
                name="redis",
                status=HealthStatus.DOWN,
                message="Redis ping failed"
            )
    except Exception as e:
        return HealthCheck(
            name="redis",
            status=HealthStatus.DEGRADED,
            message=f"Redis error: {str(e)}"
        )


async def check_eventbus_health(eventbus_client) -> HealthCheck:
    """Check EventBus connection health"""
    try:
        is_connected = eventbus_client.is_connected() if hasattr(eventbus_client, 'is_connected') else True
        if is_connected:
            return HealthCheck(
                name="eventbus",
                status=HealthStatus.HEALTHY,
                message="EventBus connection healthy"
            )
        else:
            return HealthCheck(
                name="eventbus",
                status=HealthStatus.DOWN,
                message="EventBus not connected"
            )
    except Exception as e:
        return HealthCheck(
            name="eventbus",
            status=HealthStatus.DEGRADED,
            message=f"EventBus error: {str(e)}"
        )
