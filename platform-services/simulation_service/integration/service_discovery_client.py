"""
Service Discovery Client for Simulation Service

Provides Consul integration for:
- Service registration
- Health checks
- Heartbeat mechanism
- Service discovery
"""

import asyncio
import logging
from typing import Optional, Dict, Any
import consul.aio
from datetime import datetime

logger = logging.getLogger(__name__)


class ServiceDiscoveryClient:
    """
    Consul-based service discovery client

    Features:
    - Automatic registration on startup
    - Health check reporting
    - Heartbeat mechanism (TTL checks)
    - Service deregistration on shutdown
    """

    def __init__(
        self,
        service_name: str = "simulation-service",
        service_port: int = 8095,
        consul_host: str = "localhost",
        consul_port: int = 8500,
        health_check_interval: int = 10
    ):
        """
        Initialize Service Discovery client

        Args:
            service_name: Service name for registration
            service_port: Service port
            consul_host: Consul host
            consul_port: Consul port
            health_check_interval: Health check interval in seconds
        """
        self.service_name = service_name
        self.service_port = service_port
        self.consul_host = consul_host
        self.consul_port = consul_port
        self.health_check_interval = health_check_interval

        self.consul = consul.aio.Consul(host=consul_host, port=consul_port)
        self.service_id = f"{service_name}-{service_port}"
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._registered = False

    async def register(self) -> bool:
        """
        Register service with Consul

        Returns:
            True if registration successful
        """
        try:
            # Service metadata
            service_meta = {
                "version": "2.0.0",
                "type": "platform_service",
                "layer": "platform-services",
                "engines": "7",
                "api_endpoints": "31",
                "started_at": datetime.utcnow().isoformat()
            }

            # Health check configuration
            check = consul.Check.http(
                url=f"http://localhost:{self.service_port}/health",
                interval=f"{self.health_check_interval}s",
                timeout="5s",
                deregister="30s"  # Auto-deregister after 30s of failing checks
            )

            # Register service
            success = await self.consul.agent.service.register(
                name=self.service_name,
                service_id=self.service_id,
                address="localhost",
                port=self.service_port,
                tags=[
                    "simulation",
                    "bcm",
                    "ai-powered",
                    "v2.0.0"
                ],
                meta=service_meta,
                check=check
            )

            if success:
                self._registered = True
                logger.info(f"✅ Service registered: {self.service_id} on port {self.service_port}")

                # Start heartbeat
                await self._start_heartbeat()
                return True
            else:
                logger.error("❌ Failed to register service with Consul")
                return False

        except Exception as e:
            logger.error(f"❌ Error registering service: {e}", exc_info=True)
            return False

    async def deregister(self) -> bool:
        """
        Deregister service from Consul

        Returns:
            True if deregistration successful
        """
        try:
            # Stop heartbeat
            await self._stop_heartbeat()

            # Deregister service
            success = await self.consul.agent.service.deregister(self.service_id)

            if success:
                self._registered = False
                logger.info(f"✅ Service deregistered: {self.service_id}")
                return True
            else:
                logger.error("❌ Failed to deregister service from Consul")
                return False

        except Exception as e:
            logger.error(f"❌ Error deregistering service: {e}", exc_info=True)
            return False

    async def update_health(self, status: str, message: str = "") -> bool:
        """
        Update service health status

        Args:
            status: Health status ("passing", "warning", "critical")
            message: Optional message

        Returns:
            True if update successful
        """
        try:
            check_id = f"service:{self.service_id}"

            if status == "passing":
                success = await self.consul.agent.check.ttl_pass(check_id, notes=message)
            elif status == "warning":
                success = await self.consul.agent.check.ttl_warn(check_id, notes=message)
            elif status == "critical":
                success = await self.consul.agent.check.ttl_fail(check_id, notes=message)
            else:
                logger.error(f"Invalid health status: {status}")
                return False

            if success:
                logger.debug(f"Health status updated: {status}")
                return True
            else:
                logger.warning(f"Failed to update health status: {status}")
                return False

        except Exception as e:
            logger.error(f"Error updating health status: {e}")
            return False

    async def discover_service(self, service_name: str) -> Optional[Dict[str, Any]]:
        """
        Discover a service by name

        Args:
            service_name: Service name to discover

        Returns:
            Service information dict or None
        """
        try:
            index, services = await self.consul.health.service(
                service_name,
                passing=True  # Only return healthy services
            )

            if not services:
                logger.debug(f"Service not found: {service_name}")
                return None

            # Return first healthy service
            service = services[0]
            return {
                "name": service_name,
                "address": service["Service"]["Address"],
                "port": service["Service"]["Port"],
                "tags": service["Service"]["Tags"],
                "meta": service["Service"]["Meta"]
            }

        except Exception as e:
            logger.error(f"Error discovering service {service_name}: {e}")
            return None

    async def get_all_services(self) -> Dict[str, Any]:
        """
        Get all registered services

        Returns:
            Dictionary of services
        """
        try:
            index, services = await self.consul.catalog.services()
            return services

        except Exception as e:
            logger.error(f"Error getting all services: {e}")
            return {}

    async def _start_heartbeat(self) -> None:
        """Start heartbeat task"""
        if self._heartbeat_task is None or self._heartbeat_task.done():
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            logger.info("Heartbeat task started")

    async def _stop_heartbeat(self) -> None:
        """Stop heartbeat task"""
        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            logger.info("Heartbeat task stopped")

    async def _heartbeat_loop(self) -> None:
        """
        Heartbeat loop - periodically report healthy status

        Runs every health_check_interval seconds
        """
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)

                if self._registered:
                    await self.update_health("passing", "Service healthy")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
                # Try to report critical status
                try:
                    await self.update_health("critical", f"Heartbeat error: {str(e)}")
                except Exception:
                    pass

    async def health_check(self) -> Dict[str, Any]:
        """
        Check service discovery health

        Returns:
            Health status dictionary
        """
        try:
            # Check Consul connectivity
            await self.consul.agent.self()

            return {
                "status": "healthy",
                "registered": self._registered,
                "service_id": self.service_id,
                "consul_host": self.consul_host,
                "consul_port": self.consul_port
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "registered": self._registered,
                "error": str(e)
            }

    async def close(self) -> None:
        """Close client and cleanup"""
        await self.deregister()
        await self.consul.close()
