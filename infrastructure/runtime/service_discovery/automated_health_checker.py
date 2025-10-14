"""
Automated Health Checker

Continuous health checking system that works with Service Registry and EventBus.
Automatically detects and reports service health issues.

Integrated with Central Brain Tests for complete service monitoring.
"""

import asyncio
import logging
import socket
from typing import Dict, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass

from infrastructure.runtime.service_discovery.service_registry import ServiceRegistry, Service
from infrastructure.runtime.service_discovery.eventbus_integration import (
    publish_service_health,
    publish_service_stopped
)

logger = logging.getLogger(__name__)


@dataclass
class HealthCheckConfig:
    """Health check configuration"""
    interval_seconds: int = 30  # Check every 30 seconds
    timeout_seconds: int = 5  # Timeout for health checks
    max_failures: int = 3  # Max consecutive failures before marking unhealthy
    check_port: bool = True  # Check if port is listening
    check_endpoint: bool = True  # Check HTTP health endpoint


class AutomatedHealthChecker:
    """
    Automated health checking system

    Continuously monitors all registered services and:
    1. Checks if port is listening
    2. Checks HTTP health endpoint (if configured)
    3. Publishes health status to EventBus
    4. Updates Service Registry
    5. Alerts when services become unhealthy
    """

    def __init__(self, service_registry: ServiceRegistry, eventbus,
                 config: Optional[HealthCheckConfig] = None):
        """
        Initialize health checker

        Args:
            service_registry: ServiceRegistry instance
            eventbus: EventBus instance
            config: Health check configuration
        """
        self.registry = service_registry
        self.eventbus = eventbus
        self.config = config or HealthCheckConfig()

        # Track consecutive failures
        self.failure_count: Dict[str, int] = {}

        # Background task
        self._checker_task: Optional[asyncio.Task] = None

        # Callbacks
        self.on_service_unhealthy = None
        self.on_service_recovered = None

    async def start(self) -> None:
        """Start automated health checking"""
        logger.info(
            f"Starting Automated Health Checker "
            f"(interval: {self.config.interval_seconds}s)"
        )

        self._checker_task = asyncio.create_task(self._health_check_loop())

        logger.info("Automated Health Checker started")

    async def stop(self) -> None:
        """Stop automated health checking"""
        logger.info("Stopping Automated Health Checker")

        if self._checker_task:
            self._checker_task.cancel()
            try:
                await self._checker_task
            except asyncio.CancelledError:
                pass

        logger.info("Automated Health Checker stopped")

    async def _health_check_loop(self) -> None:
        """Background task for continuous health checking"""
        while True:
            try:
                await asyncio.sleep(self.config.interval_seconds)

                # Check all services
                await self._check_all_services()

            except asyncio.CancelledError:
                logger.info("Health check loop cancelled")
                break

            except Exception as e:
                logger.error(f"Error in health check loop: {e}", exc_info=True)
                # Continue checking even if error occurs
                await asyncio.sleep(5)

    async def _check_all_services(self) -> None:
        """Check health of all registered services"""
        services = await self.registry.list_services()

        logger.debug(f"Checking health of {len(services)} services")

        for service in services:
            # Skip if service is stopped
            if service.status in ('stopped', 'stopping'):
                continue

            await self._check_service_health(service)

    async def _check_service_health(self, service: Service) -> None:
        """
        Check health of a single service

        Args:
            service: Service to check
        """
        is_healthy = True
        failure_reasons = []

        # 1. Check if port is listening (if port is configured)
        if self.config.check_port and service.port:
            if not self._check_port_listening(service.port):
                is_healthy = False
                failure_reasons.append(f"Port {service.port} not listening")

        # 2. Check HTTP health endpoint (if configured)
        if self.config.check_endpoint and service.url:
            endpoint_healthy, error = await self._check_http_endpoint(service.url)
            if not endpoint_healthy:
                is_healthy = False
                failure_reasons.append(f"Health endpoint failed: {error}")

        # 3. Update failure count
        if not is_healthy:
            self.failure_count[service.name] = self.failure_count.get(service.name, 0) + 1
        else:
            # Reset failure count on success
            if service.name in self.failure_count:
                # Service recovered!
                if self.failure_count[service.name] >= self.config.max_failures:
                    logger.info(f"✅ Service RECOVERED: {service.name}")
                    await self._handle_service_recovered(service)

                self.failure_count[service.name] = 0

        # 4. Determine health status
        consecutive_failures = self.failure_count.get(service.name, 0)

        if consecutive_failures >= self.config.max_failures:
            # Service is unhealthy
            new_health = 'unhealthy'
        elif consecutive_failures > 0:
            # Service is degraded
            new_health = 'degraded'
        else:
            # Service is healthy
            new_health = 'healthy'

        # 5. Update health if changed
        if service.health_status != new_health:
            old_health = service.health_status
            await self.registry.update_health(service.name, new_health)

            logger.info(
                f"🏥 Health status changed: {service.name} "
                f"{old_health} -> {new_health}"
            )

            # Publish health event
            await publish_service_health(
                self.eventbus,
                service.name,
                new_health
            )

            # Handle unhealthy service
            if new_health == 'unhealthy':
                await self._handle_service_unhealthy(
                    service,
                    failure_reasons
                )

    def _check_port_listening(self, port: int, host: str = 'localhost') -> bool:
        """
        Check if port is listening

        Args:
            port: Port number
            host: Hostname

        Returns:
            True if port is listening
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.config.timeout_seconds)

        try:
            result = sock.connect_ex((host, port))
            return result == 0
        except socket.error:
            return False
        finally:
            sock.close()

    async def _check_http_endpoint(self, url: str) -> tuple[bool, Optional[str]]:
        """
        Check HTTP health endpoint

        Args:
            url: Health endpoint URL

        Returns:
            (is_healthy, error_message)
        """
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
                async with session.get(url, timeout=timeout) as response:
                    if response.status == 200:
                        return (True, None)
                    else:
                        return (False, f"HTTP {response.status}")

        except ImportError:
            # Fallback: use subprocess curl
            import subprocess

            try:
                result = subprocess.run(
                    ['curl', '-f', '-s', '-m', str(self.config.timeout_seconds), url],
                    capture_output=True,
                    timeout=self.config.timeout_seconds + 1
                )

                if result.returncode == 0:
                    return (True, None)
                else:
                    return (False, f"curl failed with code {result.returncode}")

            except (subprocess.SubprocessError, FileNotFoundError):
                return (False, "Cannot check endpoint (aiohttp and curl unavailable)")

        except asyncio.TimeoutError:
            return (False, "Timeout")

        except Exception as e:
            return (False, str(e))

    async def _handle_service_unhealthy(self, service: Service,
                                       failure_reasons: List[str]) -> None:
        """
        Handle unhealthy service

        Args:
            service: Unhealthy service
            failure_reasons: List of failure reasons
        """
        logger.error(
            f"❌ Service UNHEALTHY: {service.name}\n"
            f"   Consecutive failures: {self.failure_count.get(service.name, 0)}\n"
            f"   Reasons: {', '.join(failure_reasons)}"
        )

        # Update service status
        await self.registry.update_status(service.name, 'failed')

        # Call callback if set
        if self.on_service_unhealthy:
            await self.on_service_unhealthy(service, failure_reasons)

        # Publish alert to EventBus
        await self.eventbus.publish({
            'type': 'platform.service_discovery.service_unhealthy',
            'data': {
                'service_name': service.name,
                'health_status': 'unhealthy',
                'failure_reasons': failure_reasons,
                'consecutive_failures': self.failure_count.get(service.name, 0),
                'timestamp': datetime.utcnow().isoformat()
            }
        })

    async def _handle_service_recovered(self, service: Service) -> None:
        """
        Handle service recovery

        Args:
            service: Recovered service
        """
        logger.info(f"✅ Service RECOVERED: {service.name}")

        # Update service status
        await self.registry.update_status(service.name, 'running')

        # Call callback if set
        if self.on_service_recovered:
            await self.on_service_recovered(service)

        # Publish recovery event
        await self.eventbus.publish({
            'type': 'platform.service_discovery.service_recovered',
            'data': {
                'service_name': service.name,
                'timestamp': datetime.utcnow().isoformat()
            }
        })

    async def check_service_now(self, service_name: str) -> Dict[str, any]:
        """
        Immediately check a specific service (bypass scheduled checks)

        Args:
            service_name: Name of service to check

        Returns:
            Health check result
        """
        service = await self.registry.get_service(service_name)

        if not service:
            return {
                'service_name': service_name,
                'exists': False,
                'error': 'Service not found in registry'
            }

        # Perform health check
        is_healthy = True
        checks = {}

        # Check port
        if service.port:
            port_listening = self._check_port_listening(service.port)
            checks['port'] = {
                'listening': port_listening,
                'port': service.port
            }
            if not port_listening:
                is_healthy = False

        # Check endpoint
        if service.url:
            endpoint_healthy, error = await self._check_http_endpoint(service.url)
            checks['endpoint'] = {
                'healthy': endpoint_healthy,
                'url': service.url,
                'error': error
            }
            if not endpoint_healthy:
                is_healthy = False

        return {
            'service_name': service_name,
            'exists': True,
            'healthy': is_healthy,
            'health_status': service.health_status,
            'checks': checks,
            'consecutive_failures': self.failure_count.get(service_name, 0),
            'timestamp': datetime.utcnow().isoformat()
        }

    async def get_health_summary(self) -> Dict[str, any]:
        """
        Get summary of all service health

        Returns:
            Health summary
        """
        services = await self.registry.list_services()

        total = len(services)
        healthy = sum(1 for s in services if s.health_status == 'healthy')
        degraded = sum(1 for s in services if s.health_status == 'degraded')
        unhealthy = sum(1 for s in services if s.health_status == 'unhealthy')
        unknown = sum(1 for s in services if s.health_status is None)

        return {
            'total_services': total,
            'healthy': healthy,
            'degraded': degraded,
            'unhealthy': unhealthy,
            'unknown': unknown,
            'health_percentage': (healthy / total * 100) if total > 0 else 0,
            'services': [
                {
                    'name': s.name,
                    'health_status': s.health_status,
                    'status': s.status,
                    'port': s.port
                }
                for s in services
            ],
            'timestamp': datetime.utcnow().isoformat()
        }
