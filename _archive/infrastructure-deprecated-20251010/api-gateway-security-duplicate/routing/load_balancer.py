"""
Load Balancer for API Gateway
Production-grade load balancing with multiple algorithms and health awareness
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import random

logger = logging.getLogger(__name__)


class LoadBalancingAlgorithm(Enum):
    """Supported load balancing algorithms"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    RANDOM = "random"


@dataclass
class ServiceInstance:
    """
    Represents a backend service instance

    Attributes:
        url: Service URL (e.g., "http://localhost:8001")
        weight: Load balancing weight (higher = more traffic)
        healthy: Whether instance is healthy
        active_connections: Current number of active connections
        total_requests: Total requests served
        last_selected: Timestamp of last selection
        response_time_ms: Average response time in milliseconds
    """
    url: str
    weight: int = 1
    healthy: bool = True
    active_connections: int = 0
    total_requests: int = 0
    last_selected: Optional[datetime] = None
    response_time_ms: float = 0.0

    def __hash__(self):
        return hash(self.url)


class LoadBalancer:
    """
    Production-grade load balancer with multiple algorithms

    Features:
    - Round-robin distribution
    - Least connections algorithm
    - Weighted distribution
    - Health-aware selection
    - Connection tracking
    - Thread-safe operations
    - Performance metrics

    Usage:
        lb = LoadBalancer(algorithm=LoadBalancingAlgorithm.ROUND_ROBIN)
        lb.add_instance("http://service1:8001", weight=2)
        lb.add_instance("http://service2:8002", weight=1)

        # Select instance for request
        instance = lb.select_instance()
        if instance:
            # Make request
            await make_request(instance.url)
            lb.release_instance(instance)
    """

    def __init__(
        self,
        algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN,
        enable_health_check: bool = True
    ):
        """
        Initialize load balancer

        Args:
            algorithm: Load balancing algorithm to use
            enable_health_check: Whether to filter unhealthy instances
        """
        self.algorithm = algorithm
        self.enable_health_check = enable_health_check

        # Instance storage
        self._instances: Dict[str, ServiceInstance] = {}

        # Round-robin state
        self._round_robin_index: int = 0

        # Thread safety
        self._lock = asyncio.Lock()

        # Metrics
        self._total_selections: int = 0
        self._failed_selections: int = 0

        logger.info(
            f"LoadBalancer initialized with algorithm: {algorithm.value}, "
            f"health_check: {enable_health_check}"
        )

    async def add_instance(
        self,
        url: str,
        weight: int = 1,
        healthy: bool = True
    ) -> None:
        """
        Add service instance to load balancer

        Args:
            url: Service URL
            weight: Load balancing weight (default: 1)
            healthy: Initial health status (default: True)
        """
        async with self._lock:
            if url in self._instances:
                logger.debug(f"Instance {url} already exists, updating weight")
                self._instances[url].weight = weight
                self._instances[url].healthy = healthy
            else:
                instance = ServiceInstance(
                    url=url,
                    weight=weight,
                    healthy=healthy
                )
                self._instances[url] = instance
                logger.info(f"Added instance: {url} (weight: {weight})")

    async def remove_instance(self, url: str) -> None:
        """
        Remove service instance from load balancer

        Args:
            url: Service URL to remove
        """
        async with self._lock:
            if url in self._instances:
                del self._instances[url]
                logger.info(f"Removed instance: {url}")
            else:
                logger.warning(f"Instance {url} not found")

    async def update_health(self, url: str, healthy: bool) -> None:
        """
        Update health status of service instance

        Args:
            url: Service URL
            healthy: New health status
        """
        async with self._lock:
            if url in self._instances:
                old_status = self._instances[url].healthy
                self._instances[url].healthy = healthy

                if old_status != healthy:
                    status_str = "healthy" if healthy else "unhealthy"
                    logger.info(f"Instance {url} marked as {status_str}")
            else:
                logger.warning(f"Cannot update health: instance {url} not found")

    async def update_response_time(self, url: str, response_time_ms: float) -> None:
        """
        Update average response time for instance

        Args:
            url: Service URL
            response_time_ms: Response time in milliseconds
        """
        async with self._lock:
            if url in self._instances:
                instance = self._instances[url]
                # Calculate exponential moving average
                if instance.response_time_ms == 0:
                    instance.response_time_ms = response_time_ms
                else:
                    # Alpha = 0.3 for EMA (30% new value, 70% old value)
                    alpha = 0.3
                    instance.response_time_ms = (
                        alpha * response_time_ms +
                        (1 - alpha) * instance.response_time_ms
                    )

    async def select_instance(self) -> Optional[ServiceInstance]:
        """
        Select service instance based on configured algorithm

        Returns:
            Selected ServiceInstance or None if no healthy instances available
        """
        async with self._lock:
            self._total_selections += 1

            # Get available instances
            available = self._get_available_instances()

            if not available:
                self._failed_selections += 1
                logger.warning("No healthy instances available for selection")
                return None

            # Select based on algorithm
            instance = None

            if self.algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
                instance = self._select_round_robin(available)

            elif self.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
                instance = self._select_least_connections(available)

            elif self.algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
                instance = self._select_weighted_round_robin(available)

            elif self.algorithm == LoadBalancingAlgorithm.RANDOM:
                instance = self._select_random(available)

            else:
                logger.error(f"Unknown algorithm: {self.algorithm}")
                instance = available[0]

            # Update instance state
            if instance:
                instance.active_connections += 1
                instance.total_requests += 1
                instance.last_selected = datetime.utcnow()

                logger.debug(
                    f"Selected instance: {instance.url} "
                    f"(algorithm: {self.algorithm.value}, "
                    f"active_connections: {instance.active_connections})"
                )

            return instance

    async def release_instance(self, instance: ServiceInstance) -> None:
        """
        Release instance after request completion

        Args:
            instance: ServiceInstance to release
        """
        async with self._lock:
            if instance.url in self._instances:
                self._instances[instance.url].active_connections = max(
                    0,
                    self._instances[instance.url].active_connections - 1
                )
                logger.debug(
                    f"Released instance: {instance.url} "
                    f"(active_connections: {self._instances[instance.url].active_connections})"
                )

    def _get_available_instances(self) -> List[ServiceInstance]:
        """
        Get list of available (healthy) instances

        Returns:
            List of healthy ServiceInstance objects
        """
        if self.enable_health_check:
            return [
                inst for inst in self._instances.values()
                if inst.healthy
            ]
        else:
            return list(self._instances.values())

    def _select_round_robin(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """
        Select instance using round-robin algorithm

        Args:
            instances: List of available instances

        Returns:
            Selected ServiceInstance
        """
        instance = instances[self._round_robin_index % len(instances)]
        self._round_robin_index = (self._round_robin_index + 1) % len(instances)
        return instance

    def _select_least_connections(
        self,
        instances: List[ServiceInstance]
    ) -> ServiceInstance:
        """
        Select instance with least active connections

        Args:
            instances: List of available instances

        Returns:
            ServiceInstance with least connections
        """
        return min(instances, key=lambda inst: inst.active_connections)

    def _select_weighted_round_robin(
        self,
        instances: List[ServiceInstance]
    ) -> ServiceInstance:
        """
        Select instance using weighted round-robin

        Higher weight = more requests. Weight of 2 gets 2x more requests than weight of 1.

        Args:
            instances: List of available instances

        Returns:
            Selected ServiceInstance
        """
        # Build weighted list (repeat instances based on weight)
        weighted_instances = []
        for instance in instances:
            weighted_instances.extend([instance] * instance.weight)

        if not weighted_instances:
            return instances[0]

        instance = weighted_instances[self._round_robin_index % len(weighted_instances)]
        self._round_robin_index = (self._round_robin_index + 1) % len(weighted_instances)
        return instance

    def _select_random(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """
        Select random instance

        Args:
            instances: List of available instances

        Returns:
            Randomly selected ServiceInstance
        """
        return random.choice(instances)

    async def get_instance_stats(self, url: str) -> Optional[Dict]:
        """
        Get statistics for specific instance

        Args:
            url: Service URL

        Returns:
            Dict with instance statistics or None if not found
        """
        async with self._lock:
            if url not in self._instances:
                return None

            instance = self._instances[url]
            return {
                "url": instance.url,
                "weight": instance.weight,
                "healthy": instance.healthy,
                "active_connections": instance.active_connections,
                "total_requests": instance.total_requests,
                "response_time_ms": round(instance.response_time_ms, 2),
                "last_selected": instance.last_selected.isoformat() if instance.last_selected else None,
            }

    async def get_all_instances(self) -> List[Dict]:
        """
        Get statistics for all instances

        Returns:
            List of instance statistics
        """
        async with self._lock:
            return [
                {
                    "url": inst.url,
                    "weight": inst.weight,
                    "healthy": inst.healthy,
                    "active_connections": inst.active_connections,
                    "total_requests": inst.total_requests,
                    "response_time_ms": round(inst.response_time_ms, 2),
                    "last_selected": inst.last_selected.isoformat() if inst.last_selected else None,
                }
                for inst in self._instances.values()
            ]

    async def get_metrics(self) -> Dict:
        """
        Get load balancer metrics

        Returns:
            Dict with load balancer metrics
        """
        async with self._lock:
            total_instances = len(self._instances)
            healthy_instances = sum(1 for inst in self._instances.values() if inst.healthy)
            total_connections = sum(inst.active_connections for inst in self._instances.values())
            total_requests = sum(inst.total_requests for inst in self._instances.values())

            success_rate = 0.0
            if self._total_selections > 0:
                success_rate = (
                    (self._total_selections - self._failed_selections) /
                    self._total_selections * 100
                )

            return {
                "algorithm": self.algorithm.value,
                "total_instances": total_instances,
                "healthy_instances": healthy_instances,
                "unhealthy_instances": total_instances - healthy_instances,
                "total_connections": total_connections,
                "total_requests": total_requests,
                "total_selections": self._total_selections,
                "failed_selections": self._failed_selections,
                "success_rate_percent": round(success_rate, 2),
            }

    async def reset_metrics(self) -> None:
        """Reset load balancer metrics"""
        async with self._lock:
            self._total_selections = 0
            self._failed_selections = 0

            for instance in self._instances.values():
                instance.total_requests = 0
                instance.active_connections = 0
                instance.response_time_ms = 0.0

            logger.info("Load balancer metrics reset")


# Global load balancer instance (singleton)
_load_balancer: Optional[LoadBalancer] = None


def get_load_balancer(
    algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN
) -> LoadBalancer:
    """
    Get global load balancer instance (singleton pattern)

    Args:
        algorithm: Load balancing algorithm (only used on first call)

    Returns:
        Global LoadBalancer instance
    """
    global _load_balancer

    if _load_balancer is None:
        _load_balancer = LoadBalancer(algorithm=algorithm)
        logger.info(f"Created global LoadBalancer with algorithm: {algorithm.value}")

    return _load_balancer
