"""
EventBus Helper for AI Office Infrastructure Services

Universal helper module for EventBus integration.
Use this in all AI Office services for consistent service discovery.

Usage:
    from _shared.eventbus_helper import EventBusHelper

    helper = EventBusHelper(
        service_name="analytics-specialist",
        port=8056,
        capabilities=["metrics_discovery", "dependency_mapping"]
    )

    @app.on_event("startup")
    async def startup():
        await helper.startup()

    @app.on_event("shutdown")
    async def shutdown():
        await helper.shutdown()
"""

import logging
import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Add infrastructure to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# EventBus imports
try:
    from infrastructure.eventbus import create_eventbus
    EVENTBUS_AVAILABLE = True
except ImportError:
    EVENTBUS_AVAILABLE = False

logger = logging.getLogger(__name__)


class EventBusHelper:
    """
    Universal EventBus integration helper for AI Office services

    Provides:
    - Automatic service registration on startup
    - Periodic heartbeat publishing
    - Graceful shutdown with deregistration
    - Health status publishing
    """

    def __init__(
        self,
        service_name: str,
        port: int,
        orchestrator: str = "ai-office",
        capabilities: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
        service_type: str = "service",
        version: str = "1.0.0"
    ):
        """
        Args:
            service_name: Name of the service (e.g., "analytics-specialist")
            port: Service port number
            orchestrator: Orchestrator category (default: "ai-office")
            capabilities: List of service capabilities
            dependencies: List of service dependencies
            service_type: Type of service (e.g., "specialist", "agent", "coordinator")
            version: Service version
        """
        self.service_name = service_name
        self.port = port
        self.orchestrator = orchestrator
        self.capabilities = capabilities or []
        self.dependencies = dependencies or ["eventbus"]
        self.service_type = service_type
        self.version = version

        self.eventbus = None
        self.heartbeat_task = None

        logger.info(f"EventBusHelper initialized for {service_name}")

    async def startup(self) -> bool:
        """
        Initialize EventBus and publish service started event

        Returns:
            True if successful, False otherwise
        """
        if not EVENTBUS_AVAILABLE:
            logger.warning("️  EventBus not available - service discovery disabled")
            return False

        try:
            # Create EventBus connection
            logger.info("Connecting to EventBus...")
            self.eventbus = create_eventbus('redis')
            await self.eventbus.connect()
            logger.info(" EventBus connected")

            # Publish service started
            await self._publish_service_started()

            # Start heartbeat task
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            logger.info(" Heartbeat task started")

            return True

        except Exception as e:
            logger.error(f"EventBus initialization failed: {e}")
            logger.warning("️  Running without EventBus integration")
            self.eventbus = None
            return False

    async def shutdown(self):
        """
        Gracefully shutdown EventBus integration
        """
        logger.info(f" {self.service_name} shutting down...")

        # Stop heartbeat
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass

        # Publish service stopped
        if self.eventbus:
            try:
                await self.eventbus.publish(
                    'platform.service.stopped',
                    {
                        'service_name': self.service_name,
                        'timestamp': datetime.now().isoformat(),
                        'reason': 'graceful_shutdown'
                    }
                )
                logger.info(" Published service stopped event")
            except Exception as e:
                logger.error(f"Failed to publish shutdown event: {e}")

            # Disconnect EventBus
            try:
                await self.eventbus.disconnect()
                logger.info(" EventBus disconnected")
            except Exception as e:
                logger.error(f"EventBus disconnect error: {e}")

        logger.info(" Shutdown complete")

    async def publish_health(self, health_status: str = "healthy", metrics: Optional[Dict] = None):
        """
        Publish health status to EventBus

        Args:
            health_status: "healthy" or "unhealthy"
            metrics: Optional dict of service-specific metrics
        """
        if not self.eventbus:
            return

        try:
            await self.eventbus.publish(
                'platform.service.health',
                {
                    'service_name': self.service_name,
                    'health_status': health_status,
                    'timestamp': datetime.now().isoformat(),
                    'metrics': metrics or {}
                }
            )
            logger.debug(f" Published health: {health_status}")
        except Exception as e:
            logger.error(f"Failed to publish health: {e}")

    def is_connected(self) -> bool:
        """Check if EventBus is connected"""
        return self.eventbus is not None

    # Private methods

    async def _publish_service_started(self):
        """Publish service started event"""
        if not self.eventbus:
            return

        try:
            await self.eventbus.publish(
                'platform.service.started',
                {
                    'service_name': self.service_name,
                    'orchestrator': self.orchestrator,
                    'port': self.port,
                    'timestamp': datetime.now().isoformat(),
                    'metadata': {
                        'version': self.version,
                        'capabilities': self.capabilities,
                        'type': self.service_type
                    },
                    'dependencies': self.dependencies
                }
            )
            logger.info(f" Published service started event: {self.service_name}")
        except Exception as e:
            logger.error(f"Failed to publish service started event: {e}")

    async def _heartbeat_loop(self):
        """Publish heartbeat events periodically"""
        if not self.eventbus:
            return

        while True:
            try:
                await self.eventbus.publish(
                    'platform.service.heartbeat',
                    {
                        'service_name': self.service_name,
                        'timestamp': datetime.now().isoformat(),
                        'status': 'active'
                    }
                )
                logger.debug(f" Heartbeat sent: {self.service_name}")
                await asyncio.sleep(30)  # Every 30 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
                await asyncio.sleep(5)


# Convenience decorator for FastAPI apps
def with_eventbus(service_name: str, port: int, **kwargs):
    """
    Decorator to add EventBus integration to FastAPI app

    Usage:
        @with_eventbus("analytics-specialist", 8056, capabilities=["metrics"])
        def create_app():
            app = FastAPI()
            return app
    """
    def decorator(create_app_func):
        def wrapper():
            app = create_app_func()
            helper = EventBusHelper(service_name, port, **kwargs)

            @app.on_event("startup")
            async def startup_with_eventbus():
                await helper.startup()

            @app.on_event("shutdown")
            async def shutdown_with_eventbus():
                await helper.shutdown()

            # Attach helper to app for access in endpoints
            app.state.eventbus_helper = helper

            return app
        return wrapper
    return decorator
