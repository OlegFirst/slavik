"""
Service Router for API Gateway
Production-grade routing with service discovery and intelligent path matching
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime

from config import settings
from routing.health_checker import HealthChecker, get_health_checker
from routing.load_balancer import (
    LoadBalancer,
    LoadBalancingAlgorithm,
    ServiceInstance,
    get_load_balancer
)

logger = logging.getLogger(__name__)


@dataclass
class RouteConfig:
    """
    Configuration for a service route

    Attributes:
        name: Service name (unique identifier)
        path_prefix: URL path prefix (e.g., "/coordination")
        backend_urls: List of backend URLs (for load balancing)
        weight: Default weight for load balancing
        priority: Route matching priority (higher = checked first)
        strip_prefix: Whether to strip path prefix when forwarding
        timeout: Request timeout in seconds (override default)
    """
    name: str
    path_prefix: str
    backend_urls: List[str]
    weight: int = 1
    priority: int = 0
    strip_prefix: bool = False
    timeout: Optional[float] = None


class ServiceRouter:
    """
    Production-grade service router with intelligent path matching

    Features:
    - Service discovery from config
    - Dynamic route registration
    - Prefix-based path matching
    - Integration with LoadBalancer
    - Integration with HealthChecker
    - Priority-based routing
    - Path rewriting support
    - Wildcard and regex support
    - Thread-safe operations

    Usage:
        router = ServiceRouter()
        await router.initialize()

        # Route request (async)
        backend_url = await router.route_request("/coordination/tasks/123")
        # Returns: "http://localhost:8004" (or healthy instance)

        # Get service info
        service = router.get_service_by_name("coordination-center")
        print(service["url"], service["healthy"])
    """

    def __init__(self):
        """Initialize service router"""
        # Route registry
        self._routes: Dict[str, RouteConfig] = {}  # name -> config

        # Path prefix mapping (for fast lookup)
        self._path_map: Dict[str, str] = {}  # path_prefix -> service_name

        # Integration with health checker and load balancer
        self._health_checker: Optional[HealthChecker] = None
        self._load_balancers: Dict[str, LoadBalancer] = {}  # service_name -> LoadBalancer

        # Compiled regex patterns for advanced matching
        self._regex_routes: List[Tuple[re.Pattern, str]] = []  # (pattern, service_name)

        # Thread safety
        self._lock = asyncio.Lock()

        # Metrics
        self._total_routes: int = 0
        self._route_hits: Dict[str, int] = {}  # service_name -> hit_count
        self._route_misses: int = 0

        logger.info("ServiceRouter initialized")

    async def initialize(self) -> None:
        """
        Initialize router with services from config

        Loads backend services from settings and registers them
        """
        logger.info("Initializing ServiceRouter...")

        # Get health checker singleton
        self._health_checker = get_health_checker()

        # Register services from config
        if settings.backend_services:
            for path_prefix, backend_url in settings.backend_services.items():
                # Extract service name from path prefix
                service_name = path_prefix.strip("/").replace("/", "-")

                # Register route
                await self.register_route(
                    name=service_name,
                    path_prefix=path_prefix,
                    backend_urls=[backend_url],
                    weight=1
                )

        logger.info(
            f"ServiceRouter initialized with {len(self._routes)} routes: "
            f"{list(self._routes.keys())}"
        )

    async def register_route(
        self,
        name: str,
        path_prefix: str,
        backend_urls: List[str],
        weight: int = 1,
        priority: int = 0,
        strip_prefix: bool = False,
        timeout: Optional[float] = None
    ) -> None:
        """
        Register service route

        Args:
            name: Service name (unique identifier)
            path_prefix: URL path prefix (e.g., "/coordination")
            backend_urls: List of backend URLs
            weight: Default weight for load balancing
            priority: Route matching priority (higher = checked first)
            strip_prefix: Whether to strip path prefix when forwarding
            timeout: Request timeout override
        """
        async with self._lock:
            # Create route config
            route_config = RouteConfig(
                name=name,
                path_prefix=path_prefix,
                backend_urls=backend_urls,
                weight=weight,
                priority=priority,
                strip_prefix=strip_prefix,
                timeout=timeout
            )

            # Register route
            self._routes[name] = route_config

            # Update path mapping
            self._path_map[path_prefix] = name

            # Initialize route hit counter
            self._route_hits[name] = 0

            # Create load balancer for this service (if multiple backends)
            if len(backend_urls) > 1:
                lb = LoadBalancer(algorithm=LoadBalancingAlgorithm.ROUND_ROBIN)
                for url in backend_urls:
                    await lb.add_instance(url, weight=weight)
                self._load_balancers[name] = lb
            else:
                # Single backend - still use load balancer for consistency
                lb = LoadBalancer(algorithm=LoadBalancingAlgorithm.ROUND_ROBIN)
                await lb.add_instance(backend_urls[0], weight=weight)
                self._load_balancers[name] = lb

            # Register with health checker
            if self._health_checker:
                for url in backend_urls:
                    # Use URL as service name for health checker
                    health_service_name = f"{name}:{url}"
                    self._health_checker.register_service(health_service_name, url)

            # Update regex routes if needed (for wildcard/regex matching)
            if "*" in path_prefix or "(" in path_prefix:
                pattern = self._compile_path_pattern(path_prefix)
                self._regex_routes.append((pattern, name))
                # Sort by priority
                self._regex_routes.sort(
                    key=lambda x: self._routes[x[1]].priority,
                    reverse=True
                )

            logger.info(
                f"Registered route: {name} -> {path_prefix} "
                f"(backends: {len(backend_urls)}, priority: {priority})"
            )

    async def unregister_route(self, name: str) -> None:
        """
        Unregister service route

        Args:
            name: Service name
        """
        async with self._lock:
            if name not in self._routes:
                logger.warning(f"Route {name} not found")
                return

            route = self._routes[name]

            # Remove from path map
            if route.path_prefix in self._path_map:
                del self._path_map[route.path_prefix]

            # Remove from regex routes
            self._regex_routes = [
                (pattern, svc_name)
                for pattern, svc_name in self._regex_routes
                if svc_name != name
            ]

            # Remove from load balancers
            if name in self._load_balancers:
                del self._load_balancers[name]

            # Unregister from health checker
            if self._health_checker:
                for url in route.backend_urls:
                    health_service_name = f"{name}:{url}"
                    self._health_checker.unregister_service(health_service_name)

            # Remove route
            del self._routes[name]

            logger.info(f"Unregistered route: {name}")

    async def route_request(self, path: str) -> Optional[str]:
        """
        Route request to backend service based on path

        This is the main routing logic that matches incoming request paths
        to backend service URLs.

        Args:
            path: Request path (e.g., "/coordination/tasks/123")

        Returns:
            Backend service URL or None if no match found

        Algorithm:
        1. Try exact prefix match (fastest)
        2. Try longest prefix match
        3. Try regex pattern match
        4. Check service health via HealthChecker
        5. Select instance via LoadBalancer
        """
        # Normalize path
        path = path if path.startswith("/") else f"/{path}"

        # Track metrics
        self._total_routes += 1

        # Step 1: Try exact prefix match (fastest)
        for prefix, service_name in self._path_map.items():
            if path.startswith(prefix):
                backend_url = await self._select_backend_instance(service_name)

                if backend_url:
                    self._route_hits[service_name] = self._route_hits.get(service_name, 0) + 1
                    logger.debug(f"Route matched: {path} -> {service_name} ({backend_url})")
                    return backend_url

        # Step 2: Try longest prefix match (for complex paths)
        longest_match = None
        longest_length = 0

        for prefix, service_name in self._path_map.items():
            if path.startswith(prefix) and len(prefix) > longest_length:
                longest_match = service_name
                longest_length = len(prefix)

        if longest_match:
            backend_url = await self._select_backend_instance(longest_match)

            if backend_url:
                self._route_hits[longest_match] = self._route_hits.get(longest_match, 0) + 1
                logger.debug(f"Route matched (longest): {path} -> {longest_match} ({backend_url})")
                return backend_url

        # Step 3: Try regex pattern match
        for pattern, service_name in self._regex_routes:
            if pattern.match(path):
                backend_url = await self._select_backend_instance(service_name)

                if backend_url:
                    self._route_hits[service_name] = self._route_hits.get(service_name, 0) + 1
                    logger.debug(f"Route matched (regex): {path} -> {service_name} ({backend_url})")
                    return backend_url

        # No match found
        self._route_misses += 1
        logger.warning(f"No route found for path: {path}")
        return None

    async def _select_backend_instance(self, service_name: str) -> Optional[str]:
        """
        Select backend instance for service using load balancer

        Args:
            service_name: Service name

        Returns:
            Backend URL or None if no healthy instance available
        """
        if service_name not in self._load_balancers:
            logger.error(f"No load balancer for service: {service_name}")
            return None

        lb = self._load_balancers[service_name]

        # Update health status from health checker
        if self._health_checker:
            route = self._routes.get(service_name)
            if route:
                for url in route.backend_urls:
                    health_service_name = f"{service_name}:{url}"
                    is_healthy = self._health_checker.is_service_healthy(health_service_name)

                    # Update load balancer health status
                    await lb.update_health(url, is_healthy)

        # Select instance
        try:
            instance = await lb.select_instance()

            if instance:
                return instance.url
            else:
                logger.warning(f"No healthy instance available for service: {service_name}")
                return None

        except Exception as e:
            logger.error(f"Error selecting instance for {service_name}: {e}")
            return None

    def _compile_path_pattern(self, path_prefix: str) -> re.Pattern:
        """
        Compile path prefix to regex pattern

        Supports:
        - Wildcards: /api/* -> /api/.*
        - Variables: /api/{id} -> /api/[^/]+

        Args:
            path_prefix: Path prefix with wildcards/variables

        Returns:
            Compiled regex pattern
        """
        # Escape special characters except * and {}
        pattern = re.escape(path_prefix)

        # Replace wildcards
        pattern = pattern.replace(r"\*", ".*")

        # Replace variables {name} with [^/]+
        pattern = re.sub(r"\\\{[^}]+\\\}", "[^/]+", pattern)

        # Anchor pattern
        pattern = f"^{pattern}"

        return re.compile(pattern)

    def get_service_by_name(self, name: str) -> Optional[Dict]:
        """
        Get service information by name

        Args:
            name: Service name

        Returns:
            Dict with service info or None if not found
        """
        if name not in self._routes:
            return None

        route = self._routes[name]

        # Get health status
        healthy_backends = []
        unhealthy_backends = []

        if self._health_checker:
            for url in route.backend_urls:
                health_service_name = f"{name}:{url}"
                is_healthy = self._health_checker.is_service_healthy(health_service_name)

                if is_healthy:
                    healthy_backends.append(url)
                else:
                    unhealthy_backends.append(url)
        else:
            healthy_backends = route.backend_urls

        return {
            "name": name,
            "path_prefix": route.path_prefix,
            "backend_urls": route.backend_urls,
            "healthy_backends": healthy_backends,
            "unhealthy_backends": unhealthy_backends,
            "weight": route.weight,
            "priority": route.priority,
            "strip_prefix": route.strip_prefix,
            "timeout": route.timeout,
            "hits": self._route_hits.get(name, 0),
        }

    def get_all_services(self) -> Dict[str, Dict]:
        """
        Get information for all registered services

        Returns:
            Dict mapping service name to service info
        """
        return {
            name: {
                "name": name,
                "path_prefix": route.path_prefix,
                "url": route.backend_urls[0] if route.backend_urls else None,
                "backend_count": len(route.backend_urls),
                "weight": route.weight,
                "priority": route.priority,
                "hits": self._route_hits.get(name, 0),
            }
            for name, route in self._routes.items()
        }

    def get_route_for_path(self, path: str) -> Optional[str]:
        """
        Get service name for given path (without selecting instance)

        Args:
            path: Request path

        Returns:
            Service name or None if no match
        """
        # Normalize path
        path = path if path.startswith("/") else f"/{path}"

        # Try exact prefix match
        for prefix, service_name in self._path_map.items():
            if path.startswith(prefix):
                return service_name

        # Try regex patterns
        for pattern, service_name in self._regex_routes:
            if pattern.match(path):
                return service_name

        return None

    async def get_metrics(self) -> Dict:
        """
        Get router metrics

        Returns:
            Dict with router metrics
        """
        async with self._lock:
            total_routes = len(self._routes)
            total_backends = sum(
                len(route.backend_urls)
                for route in self._routes.values()
            )

            # Get health summary
            healthy_services = 0
            unhealthy_services = 0

            if self._health_checker:
                for name in self._routes.keys():
                    # Check if at least one backend is healthy
                    has_healthy = False
                    for url in self._routes[name].backend_urls:
                        health_service_name = f"{name}:{url}"
                        if self._health_checker.is_service_healthy(health_service_name):
                            has_healthy = True
                            break

                    if has_healthy:
                        healthy_services += 1
                    else:
                        unhealthy_services += 1

            # Calculate hit rate
            total_hits = sum(self._route_hits.values())
            hit_rate = 0.0
            if self._total_routes > 0:
                hit_rate = (total_hits / self._total_routes) * 100

            return {
                "total_routes": total_routes,
                "total_backends": total_backends,
                "healthy_services": healthy_services,
                "unhealthy_services": unhealthy_services,
                "total_requests": self._total_routes,
                "successful_routes": total_hits,
                "route_misses": self._route_misses,
                "hit_rate_percent": round(hit_rate, 2),
                "top_routes": sorted(
                    self._route_hits.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10],
            }

    async def health_check(self) -> Dict:
        """
        Perform health check on router and all services

        Returns:
            Dict with health check results
        """
        all_healthy = True
        services_status = {}

        for name, route in self._routes.items():
            service_health = {
                "healthy": False,
                "healthy_backends": 0,
                "total_backends": len(route.backend_urls),
            }

            if self._health_checker:
                for url in route.backend_urls:
                    health_service_name = f"{name}:{url}"
                    if self._health_checker.is_service_healthy(health_service_name):
                        service_health["healthy_backends"] += 1

                service_health["healthy"] = service_health["healthy_backends"] > 0
            else:
                service_health["healthy"] = True
                service_health["healthy_backends"] = len(route.backend_urls)

            if not service_health["healthy"]:
                all_healthy = False

            services_status[name] = service_health

        return {
            "status": "healthy" if all_healthy else "degraded",
            "total_services": len(self._routes),
            "healthy_services": sum(
                1 for s in services_status.values() if s["healthy"]
            ),
            "services": services_status,
        }


# Global service router instance (singleton)
_service_router: Optional[ServiceRouter] = None


def get_service_router() -> ServiceRouter:
    """
    Get global service router instance (singleton pattern)

    Returns:
        Global ServiceRouter instance
    """
    global _service_router

    if _service_router is None:
        _service_router = ServiceRouter()
        logger.info("Created global ServiceRouter")

    return _service_router
