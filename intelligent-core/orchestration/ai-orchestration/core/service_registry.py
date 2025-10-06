"""
Service Registry - Service discovery and registration
Tracks all services, their status, dependencies, and metadata
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class Service:
    """Service definition"""
    name: str
    orchestrator: str
    status: str = "unknown"  # unknown, starting, running, stopping, stopped, failed
    registered_at: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    health_status: Optional[str] = None
    port: Optional[int] = None
    url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'orchestrator': self.orchestrator,
            'status': self.status,
            'registered_at': self.registered_at.isoformat(),
            'last_seen': self.last_seen.isoformat(),
            'metadata': self.metadata,
            'dependencies': self.dependencies,
            'health_status': self.health_status,
            'port': self.port,
            'url': self.url
        }


class ServiceRegistry:
    """
    Service discovery and registration

    Maintains in-memory registry of all services
    Can persist to Redis for distributed access
    """

    def __init__(self):
        self.services: Dict[str, Service] = {}
        self.redis_client = None
        logger.info("ServiceRegistry initialized")

    async def connect_redis(self, redis_client) -> None:
        """
        Connect to Redis for persistence

        Args:
            redis_client: Redis client instance
        """
        self.redis_client = redis_client
        logger.info("ServiceRegistry connected to Redis")

        # Load existing services from Redis
        await self._load_from_redis()

    async def register(self, service_name: str, orchestrator: str,
                      metadata: Optional[Dict[str, Any]] = None,
                      dependencies: Optional[List[str]] = None) -> Service:
        """
        Register a service

        Args:
            service_name: Name of the service
            orchestrator: Orchestrator managing this service
            metadata: Additional service metadata
            dependencies: List of service dependencies

        Returns:
            Registered Service object
        """
        if service_name in self.services:
            # Update existing
            service = self.services[service_name]
            service.last_seen = datetime.utcnow()
            if metadata:
                service.metadata.update(metadata)
            if dependencies:
                service.dependencies = dependencies
            logger.debug(f"Updated service registration: {service_name}")
        else:
            # Create new
            service = Service(
                name=service_name,
                orchestrator=orchestrator,
                status="registered",
                metadata=metadata or {},
                dependencies=dependencies or []
            )
            self.services[service_name] = service
            logger.info(f"Registered new service: {service_name} (orchestrator: {orchestrator})")

        # Persist to Redis
        await self._persist_to_redis(service)

        return service

    async def unregister(self, service_name: str) -> bool:
        """
        Unregister a service

        Args:
            service_name: Name of the service

        Returns:
            True if unregistered successfully
        """
        if service_name in self.services:
            del self.services[service_name]
            logger.info(f"Unregistered service: {service_name}")

            # Remove from Redis
            if self.redis_client:
                try:
                    await self.redis_client.hdel('service_registry', service_name)
                except Exception as e:
                    logger.error(f"Failed to remove {service_name} from Redis: {e}")

            return True
        else:
            logger.warning(f"Service {service_name} not found in registry")
            return False

    async def get_service(self, service_name: str) -> Optional[Service]:
        """
        Get service by name

        Args:
            service_name: Name of the service

        Returns:
            Service object or None
        """
        return self.services.get(service_name)

    async def list_services(self, orchestrator: Optional[str] = None,
                           status: Optional[str] = None) -> List[Service]:
        """
        List all services with optional filters

        Args:
            orchestrator: Filter by orchestrator
            status: Filter by status

        Returns:
            List of Service objects
        """
        services = list(self.services.values())

        if orchestrator:
            services = [s for s in services if s.orchestrator == orchestrator]

        if status:
            services = [s for s in services if s.status == status]

        return services

    async def update_status(self, service_name: str, status: str) -> bool:
        """
        Update service status

        Args:
            service_name: Name of the service
            status: New status

        Returns:
            True if updated successfully
        """
        service = self.services.get(service_name)
        if service:
            service.status = status
            service.last_seen = datetime.utcnow()
            await self._persist_to_redis(service)
            logger.debug(f"Updated {service_name} status to {status}")
            return True
        else:
            logger.warning(f"Cannot update status for unknown service: {service_name}")
            return False

    async def update_health(self, service_name: str, health_status: str) -> bool:
        """
        Update service health status

        Args:
            service_name: Name of the service
            health_status: Health status (healthy, unhealthy, degraded)

        Returns:
            True if updated successfully
        """
        service = self.services.get(service_name)
        if service:
            service.health_status = health_status
            service.last_seen = datetime.utcnow()
            await self._persist_to_redis(service)
            logger.debug(f"Updated {service_name} health to {health_status}")
            return True
        return False

    async def get_dependencies(self, service_name: str) -> List[str]:
        """
        Get service dependencies

        Args:
            service_name: Name of the service

        Returns:
            List of dependency service names
        """
        service = self.services.get(service_name)
        if service:
            return service.dependencies
        return []

    async def get_dependents(self, service_name: str) -> List[str]:
        """
        Get services that depend on this service

        Args:
            service_name: Name of the service

        Returns:
            List of dependent service names
        """
        dependents = []
        for service in self.services.values():
            if service_name in service.dependencies:
                dependents.append(service.name)
        return dependents

    async def is_dependencies_ready(self, service_name: str) -> bool:
        """
        Check if all dependencies are ready (status=running, health=healthy)

        Args:
            service_name: Name of the service

        Returns:
            True if all dependencies ready
        """
        dependencies = await self.get_dependencies(service_name)

        for dep_name in dependencies:
            dep_service = await self.get_service(dep_name)
            if not dep_service:
                logger.warning(f"Dependency {dep_name} not found in registry")
                return False

            if dep_service.status != "running":
                logger.debug(f"Dependency {dep_name} not running (status: {dep_service.status})")
                return False

            if dep_service.health_status != "healthy":
                logger.debug(f"Dependency {dep_name} not healthy (health: {dep_service.health_status})")
                return False

        return True

    async def get_registry_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics

        Returns:
            Dictionary with stats
        """
        total = len(self.services)
        by_status = {}
        by_orchestrator = {}

        for service in self.services.values():
            by_status[service.status] = by_status.get(service.status, 0) + 1
            by_orchestrator[service.orchestrator] = by_orchestrator.get(service.orchestrator, 0) + 1

        return {
            'total_services': total,
            'by_status': by_status,
            'by_orchestrator': by_orchestrator,
            'services': [s.name for s in self.services.values()]
        }

    async def _persist_to_redis(self, service: Service) -> None:
        """Persist service to Redis"""
        if self.redis_client:
            try:
                service_data = json.dumps(service.to_dict())
                await self.redis_client.hset('service_registry', service.name, service_data)
            except Exception as e:
                logger.error(f"Failed to persist {service.name} to Redis: {e}")

    async def _load_from_redis(self) -> None:
        """Load services from Redis"""
        if self.redis_client:
            try:
                services_data = await self.redis_client.hgetall('service_registry')
                for service_name, service_json in services_data.items():
                    service_dict = json.loads(service_json)
                    service = Service(
                        name=service_dict['name'],
                        orchestrator=service_dict['orchestrator'],
                        status=service_dict['status'],
                        registered_at=datetime.fromisoformat(service_dict['registered_at']),
                        last_seen=datetime.fromisoformat(service_dict['last_seen']),
                        metadata=service_dict.get('metadata', {}),
                        dependencies=service_dict.get('dependencies', []),
                        health_status=service_dict.get('health_status'),
                        port=service_dict.get('port'),
                        url=service_dict.get('url')
                    )
                    self.services[service_name] = service

                logger.info(f"Loaded {len(self.services)} services from Redis")
            except Exception as e:
                logger.error(f"Failed to load services from Redis: {e}")