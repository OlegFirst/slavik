"""
Base Orchestrator - Abstract class for all orchestrators
Provides common functionality: event publishing, service registry, health monitoring
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
import asyncio

from .service_registry import ServiceRegistry
from .health_monitor import HealthMonitor
from .event_coordinator import EventCoordinator
from .docker_manager import DockerManager

logger = logging.getLogger(__name__)


class BaseOrchestrator(ABC):
    """
    Base class for all orchestrators (Platform, AI, Scenario, Workflow)

    Provides:
    - Service registry access
    - EventBus integration
    - Health monitoring
    - Docker management
    """

    def __init__(self):
        self.service_registry = ServiceRegistry()
        self.event_coordinator = EventCoordinator()
        self.health_monitor = HealthMonitor()
        self.docker_manager = DockerManager()
        self.running = False
        self.name = self.__class__.__name__

        logger.info(f"{self.name} initialized")

    @abstractmethod
    async def start(self) -> None:
        """
        Start the orchestrator
        Must be implemented by subclasses
        """
        pass

    @abstractmethod
    async def stop(self) -> None:
        """
        Stop the orchestrator
        Must be implemented by subclasses
        """
        pass

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """
        Get orchestrator status
        Must be implemented by subclasses

        Returns:
            Dict with status information
        """
        pass

    async def publish_event(self, event_type: str, data: Dict[str, Any],
                           tenant_id: Optional[str] = None) -> None:
        """
        Publish event to EventBus

        Args:
            event_type: Event type (e.g., "platform.ready")
            data: Event data
            tenant_id: Tenant identifier (optional)
        """
        try:
            await self.event_coordinator.publish({
                'type': event_type,
                'data': data,
                'tenant_id': tenant_id,
                'source': self.name
            })
            logger.debug(f"{self.name} published event: {event_type}")
        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")

    async def register_service(self, service_name: str,
                               metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Register service in registry

        Args:
            service_name: Name of the service
            metadata: Additional service metadata
        """
        try:
            await self.service_registry.register(
                service_name=service_name,
                orchestrator=self.name,
                metadata=metadata or {}
            )
            logger.info(f"{self.name} registered service: {service_name}")
        except Exception as e:
            logger.error(f"Failed to register service {service_name}: {e}")

    async def subscribe_to_events(self, event_pattern: str,
                                  handler: callable) -> None:
        """
        Subscribe to events matching pattern

        Args:
            event_pattern: Event pattern (e.g., "bcm.*", "platform.*")
            handler: Event handler function
        """
        try:
            await self.event_coordinator.subscribe(event_pattern, handler)
            logger.info(f"{self.name} subscribed to: {event_pattern}")
        except Exception as e:
            logger.error(f"Failed to subscribe to {event_pattern}: {e}")

    async def monitor_service_health(self, service_name: str) -> bool:
        """
        Check if service is healthy

        Args:
            service_name: Name of the service

        Returns:
            True if healthy, False otherwise
        """
        try:
            status = await self.health_monitor.check_service(service_name)
            return status.healthy
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            return False

    async def start_docker_service(self, service_name: str,
                                   timeout: int = 300) -> bool:
        """
        Start Docker service

        Args:
            service_name: Name of the service
            timeout: Timeout in seconds

        Returns:
            True if started successfully
        """
        try:
            success = await self.docker_manager.start_service(service_name)
            if success:
                # Wait for healthy
                for _ in range(timeout // 10):
                    if await self.monitor_service_health(service_name):
                        logger.info(f"Service {service_name} started and healthy")
                        return True
                    await asyncio.sleep(10)

                logger.warning(f"Service {service_name} started but not healthy after {timeout}s")
                return False
            else:
                logger.error(f"Failed to start service {service_name}")
                return False
        except Exception as e:
            logger.error(f"Error starting service {service_name}: {e}")
            return False

    async def stop_docker_service(self, service_name: str) -> bool:
        """
        Stop Docker service

        Args:
            service_name: Name of the service

        Returns:
            True if stopped successfully
        """
        try:
            success = await self.docker_manager.stop_service(service_name)
            if success:
                logger.info(f"Service {service_name} stopped")
            return success
        except Exception as e:
            logger.error(f"Error stopping service {service_name}: {e}")
            return False

    async def restart_docker_service(self, service_name: str) -> bool:
        """
        Restart Docker service

        Args:
            service_name: Name of the service

        Returns:
            True if restarted successfully
        """
        try:
            success = await self.docker_manager.restart_service(service_name)
            if success:
                logger.info(f"Service {service_name} restarted")
                # Wait for healthy
                await asyncio.sleep(10)
                healthy = await self.monitor_service_health(service_name)
                return healthy
            return False
        except Exception as e:
            logger.error(f"Error restarting service {service_name}: {e}")
            return False

    def __repr__(self) -> str:
        return f"<{self.name} running={self.running}>"