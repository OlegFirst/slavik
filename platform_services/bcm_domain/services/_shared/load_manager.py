"""
Load Manager

Monitors service load and provides intelligent load management.
Enables graceful degradation and load shedding.
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


class LoadLevel(Enum):
    """Current load level"""
    IDLE = "idle"          # < 20% capacity
    NORMAL = "normal"      # 20-60% capacity
    MEDIUM = "medium"      # 60-80% capacity
    HIGH = "high"          # 80-95% capacity
    CRITICAL = "critical"  # > 95% capacity


@dataclass
class LoadPolicy:
    """
    Load management policy.

    Defines thresholds and behaviors for different load levels.
    """
    # Thresholds (percentage of capacity)
    idle_threshold: float = 0.2
    normal_threshold: float = 0.6
    medium_threshold: float = 0.8
    high_threshold: float = 0.95

    # Queue sizes
    max_queue_size: int = 1000
    max_deferred_events: int = 500

    # Timeouts
    request_timeout_seconds: int = 30
    queue_timeout_seconds: int = 300

    # Degradation
    enable_auto_degradation: bool = True
    degradation_threshold: float = 0.9  # Auto-degrade at 90% load
    recovery_threshold: float = 0.6     # Recover at 60% load

    # Load shedding
    enable_load_shedding: bool = True
    shed_threshold: float = 0.95       # Start shedding at 95%


@dataclass
class LoadMetrics:
    """Current load metrics"""
    current_load: float                # 0.0 to 1.0
    active_requests: int
    queued_events: int
    deferred_events: int
    rejected_events: int
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    avg_request_time_ms: float = 0.0
    p95_request_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


class LoadManager:
    """
    Load management for self-aware services.

    Features:
    - Real-time load monitoring
    - Capacity estimation
    - Automatic degradation
    - Load shedding
    - Queue management
    - Predictive load forecasting

    Usage:
        load_manager = LoadManager("bia")
        await load_manager.start()

        # Check if can handle event
        if await load_manager.can_accept():
            await load_manager.track_request_start()
            # ... handle event
            await load_manager.track_request_end()
    """

    def __init__(
        self,
        service_name: str,
        policy: Optional[LoadPolicy] = None,
        max_concurrent_requests: int = 100
    ):
        """
        Initialize load manager.

        Args:
            service_name: Service identifier
            policy: Load management policy (uses default if None)
            max_concurrent_requests: Maximum concurrent requests
        """
        self.service_name = service_name
        self.policy = policy or LoadPolicy()
        self.max_concurrent_requests = max_concurrent_requests

        # State
        self._active_requests = 0
        self._queued_events: deque = deque(maxlen=self.policy.max_queue_size)
        self._deferred_events: deque = deque(maxlen=self.policy.max_deferred_events)
        self._rejected_count = 0

        # Metrics
        self._request_times: deque = deque(maxlen=1000)
        self._load_history: deque = deque(maxlen=100)  # Last 100 measurements
        self._current_load = 0.0

        # Task
        self._monitor_task: Optional[asyncio.Task] = None
        self._running = False

        # Callbacks
        self._degradation_callback: Optional[callable] = None
        self._recovery_callback: Optional[callable] = None

        logger.info(f"LoadManager initialized for {service_name} (max {max_concurrent_requests} concurrent)")

    async def start(self):
        """Start load monitoring"""
        if self._running:
            return

        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info(f"Load monitoring started for {self.service_name}")

    async def stop(self):
        """Stop load monitoring"""
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info(f"Load monitoring stopped for {self.service_name}")

    def set_degradation_callback(self, callback: callable):
        """Set callback for when degradation should occur"""
        self._degradation_callback = callback

    def set_recovery_callback(self, callback: callable):
        """Set callback for when recovery should occur"""
        self._recovery_callback = callback

    async def can_accept(self, priority: str = "normal") -> bool:
        """
        Check if service can accept new request.

        Args:
            priority: Request priority (critical, high, normal, low)

        Returns:
            True if can accept request
        """
        # Critical requests always accepted (unless at hard limit)
        if priority == "critical":
            return self._active_requests < self.max_concurrent_requests * 1.2

        # Check capacity
        load_level = await self.get_load_level()

        if load_level == LoadLevel.CRITICAL:
            # Only critical requests
            return priority == "critical"
        elif load_level == LoadLevel.HIGH:
            # Critical and high priority only
            return priority in ["critical", "high"]
        elif load_level == LoadLevel.MEDIUM:
            # All except background
            return priority != "background"

        return True

    async def track_request_start(self):
        """Track start of request"""
        self._active_requests += 1
        await self._update_load()

    async def track_request_end(self, duration_ms: Optional[float] = None):
        """
        Track end of request.

        Args:
            duration_ms: Request duration in milliseconds
        """
        self._active_requests = max(0, self._active_requests - 1)

        if duration_ms:
            self._request_times.append(duration_ms)

        await self._update_load()

    async def queue_event(self, event: Dict[str, Any]) -> bool:
        """
        Queue event for later processing.

        Args:
            event: Event to queue

        Returns:
            True if queued, False if queue full
        """
        if len(self._queued_events) >= self.policy.max_queue_size:
            logger.warning(f"Queue full for {self.service_name} - rejecting event")
            self._rejected_count += 1
            return False

        self._queued_events.append({
            **event,
            "queued_at": datetime.utcnow()
        })
        return True

    async def defer_event(self, event: Dict[str, Any]) -> bool:
        """
        Defer event for later processing.

        Args:
            event: Event to defer

        Returns:
            True if deferred, False if limit reached
        """
        if len(self._deferred_events) >= self.policy.max_deferred_events:
            logger.warning(f"Deferred events limit reached for {self.service_name}")
            self._rejected_count += 1
            return False

        self._deferred_events.append({
            **event,
            "deferred_at": datetime.utcnow()
        })
        return True

    async def get_queued_event(self) -> Optional[Dict[str, Any]]:
        """Get next queued event"""
        if self._queued_events:
            return self._queued_events.popleft()
        return None

    async def get_deferred_event(self) -> Optional[Dict[str, Any]]:
        """Get next deferred event"""
        if self._deferred_events:
            return self._deferred_events.popleft()
        return None

    async def get_load_level(self) -> LoadLevel:
        """
        Get current load level.

        Returns:
            Current LoadLevel
        """
        load = await self._calculate_load()

        if load < self.policy.idle_threshold:
            return LoadLevel.IDLE
        elif load < self.policy.normal_threshold:
            return LoadLevel.NORMAL
        elif load < self.policy.medium_threshold:
            return LoadLevel.MEDIUM
        elif load < self.policy.high_threshold:
            return LoadLevel.HIGH
        else:
            return LoadLevel.CRITICAL

    def get_load_level_sync(self) -> str:
        """Get load level synchronously (for non-async contexts)"""
        load = self._current_load

        if load < self.policy.idle_threshold:
            return "idle"
        elif load < self.policy.normal_threshold:
            return "normal"
        elif load < self.policy.medium_threshold:
            return "medium"
        elif load < self.policy.high_threshold:
            return "high"
        else:
            return "critical"

    async def get_metrics(self) -> LoadMetrics:
        """Get current load metrics"""
        load = await self._calculate_load()

        return LoadMetrics(
            current_load=load,
            active_requests=self._active_requests,
            queued_events=len(self._queued_events),
            deferred_events=len(self._deferred_events),
            rejected_events=self._rejected_count,
            avg_request_time_ms=self._calculate_avg_request_time(),
            p95_request_time_ms=self._calculate_p95_request_time()
        )

    async def predict_load(self, seconds_ahead: int = 60) -> float:
        """
        Predict load in the future.

        Uses simple linear regression on recent load history.

        Args:
            seconds_ahead: How far ahead to predict

        Returns:
            Predicted load (0.0 to 1.0)
        """
        if len(self._load_history) < 5:
            return self._current_load

        # Simple moving average prediction
        recent = list(self._load_history)[-10:]
        avg_load = sum(recent) / len(recent)

        # Trend calculation
        if len(recent) >= 2:
            trend = (recent[-1] - recent[0]) / len(recent)
            predicted = avg_load + (trend * seconds_ahead / 10)
            return max(0.0, min(1.0, predicted))

        return avg_load

    # Private methods

    async def _monitor_loop(self):
        """Main monitoring loop"""
        while self._running:
            try:
                await asyncio.sleep(5)  # Check every 5 seconds
                await self._check_thresholds()
                await self._process_queued_events()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in load monitor loop: {e}", exc_info=True)

    async def _update_load(self):
        """Update current load calculation"""
        self._current_load = await self._calculate_load()
        self._load_history.append(self._current_load)

    async def _calculate_load(self) -> float:
        """
        Calculate current load as percentage of capacity.

        Considers:
        - Active requests vs max concurrent
        - Queue size
        - Request processing times
        """
        # Base load from active requests
        base_load = self._active_requests / self.max_concurrent_requests

        # Queue pressure
        queue_pressure = len(self._queued_events) / self.policy.max_queue_size * 0.3

        # Deferred events pressure
        deferred_pressure = len(self._deferred_events) / self.policy.max_deferred_events * 0.2

        # Total load
        total_load = min(1.0, base_load + queue_pressure + deferred_pressure)

        return total_load

    async def _check_thresholds(self):
        """Check if load thresholds are crossed and trigger actions"""
        load = await self._calculate_load()

        # Check for auto-degradation
        if self.policy.enable_auto_degradation:
            if load >= self.policy.degradation_threshold:
                if self._degradation_callback:
                    logger.warning(f"Load {load:.2%} >= degradation threshold {self.policy.degradation_threshold:.2%}")
                    await self._degradation_callback("High load")
            elif load <= self.policy.recovery_threshold:
                if self._recovery_callback:
                    logger.info(f"Load {load:.2%} <= recovery threshold {self.policy.recovery_threshold:.2%}")
                    await self._recovery_callback()

        # Check for load shedding
        if self.policy.enable_load_shedding and load >= self.policy.shed_threshold:
            await self._shed_load()

    async def _shed_load(self):
        """Shed low-priority load"""
        # Remove oldest low-priority events from queue
        shed_count = 0
        new_queue = deque(maxlen=self.policy.max_queue_size)

        for event in self._queued_events:
            priority = event.get("priority", "normal")
            if priority in ["critical", "high"]:
                new_queue.append(event)
            else:
                shed_count += 1
                self._rejected_count += 1

        self._queued_events = new_queue
        if shed_count > 0:
            logger.warning(f"Shed {shed_count} low-priority events due to load")

    async def _process_queued_events(self):
        """Process queued events if capacity available"""
        load = await self._calculate_load()

        # Only process queue if load is reasonable
        if load < self.policy.medium_threshold and self._queued_events:
            # Can process some queued events
            # This would be handled by the service's event processor
            pass

        # Clean up old deferred events
        await self._cleanup_old_deferred()

    async def _cleanup_old_deferred(self):
        """Remove deferred events that are too old"""
        cutoff = datetime.utcnow() - timedelta(seconds=self.policy.queue_timeout_seconds)
        new_deferred = deque(maxlen=self.policy.max_deferred_events)

        removed = 0
        for event in self._deferred_events:
            deferred_at = event.get("deferred_at")
            if deferred_at and deferred_at > cutoff:
                new_deferred.append(event)
            else:
                removed += 1

        self._deferred_events = new_deferred
        if removed > 0:
            logger.info(f"Cleaned up {removed} old deferred events")

    def _calculate_avg_request_time(self) -> float:
        """Calculate average request time"""
        if not self._request_times:
            return 0.0
        return sum(self._request_times) / len(self._request_times)

    def _calculate_p95_request_time(self) -> float:
        """Calculate 95th percentile request time"""
        if not self._request_times:
            return 0.0

        sorted_times = sorted(self._request_times)
        p95_index = int(len(sorted_times) * 0.95)
        return sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1]
