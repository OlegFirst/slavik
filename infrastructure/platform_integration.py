"""
Platform Integration - Graceful Choreography
=============================================

This module integrates all architectural patterns across the entire platform:

1. Intelligent EventBus - AI-powered event routing
2. Saga Pattern Engine - Distributed transactions
3. Self-Aware Services - Graceful degradation
4. CQRS Infrastructure - Scalable read/write

Usage:
    from infrastructure.platform_integration import init_platform, get_platform

    # Initialize everything
    await init_platform(
        database_url="postgresql://...",
        redis_url="redis://localhost:6379",
        enable_intelligent_routing=True,
        enable_saga_engine=True,
        enable_self_aware=True,
        enable_cqrs=True
    )

    # Get platform instance
    platform = get_platform()

    # Use components
    await platform.eventbus.publish(event)
    await platform.saga.execute_saga("bcm_program_creation", context)
    ...
"""

import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class PlatformConfig:
    """Platform integration configuration"""
    database_url: str
    redis_url: str

    # Feature flags
    enable_intelligent_routing: bool = True
    enable_saga_engine: bool = True
    enable_self_aware: bool = True
    enable_cqrs: bool = True

    # EventBus config
    eventbus_backend: str = "redis"  # memory, redis, rabbitmq
    enable_ai_analysis: bool = True
    enable_semantic_matching: bool = True

    # Saga config
    saga_state_store: str = "redis"  # memory, redis, postgresql

    # CQRS config
    cqrs_cache_ttl: int = 300  # 5 minutes default

    # Performance
    max_concurrent_events: int = 100
    enable_metrics: bool = True


class PlatformIntegration:
    """
    Platform-wide integration manager

    Coordinates all architectural patterns across the entire platform.
    Provides unified access to:
    - Intelligent EventBus
    - Saga Engine
    - Self-Aware Services infrastructure
    - CQRS components
    """

    def __init__(self, config: PlatformConfig):
        self.config = config
        self._initialized = False

        # Component instances
        self.eventbus = None
        self.intelligent_router = None
        self.saga_orchestrator = None
        self.cqrs_command_handler = None
        self.cqrs_query_handler = None

        logger.info("PlatformIntegration created with config: %s", config)

    async def initialize(self):
        """Initialize all platform components"""
        if self._initialized:
            logger.warning("Platform already initialized")
            return

        logger.info("🚀 Initializing Platform Integration...")

        tasks = []

        # 1. Initialize EventBus
        if self.config.enable_intelligent_routing:
            tasks.append(self._init_intelligent_eventbus())
        else:
            tasks.append(self._init_basic_eventbus())

        # 2. Initialize Saga Engine
        if self.config.enable_saga_engine:
            tasks.append(self._init_saga_engine())

        # 3. Initialize CQRS
        if self.config.enable_cqrs:
            tasks.append(self._init_cqrs())

        # Run all initializations in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check for errors
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Initialization task {i} failed: {result}")
                raise result

        self._initialized = True
        logger.info("✅ Platform Integration initialized successfully")

    async def _init_intelligent_eventbus(self):
        """Initialize Intelligent EventBus with AI routing"""
        logger.info("  📡 Initializing Intelligent EventBus...")

        try:
            from infrastructure.eventbus import create_eventbus, IntelligentEventRouter, INTELLIGENT_ROUTER_AVAILABLE

            if not INTELLIGENT_ROUTER_AVAILABLE:
                logger.warning("  ⚠️  Intelligent Router not available, falling back to basic EventBus")
                return await self._init_basic_eventbus()

            # Create base eventbus
            self.eventbus = create_eventbus(self.config.eventbus_backend)

            # Wrap with intelligent router
            self.intelligent_router = IntelligentEventRouter(
                base_eventbus=self.eventbus,
                enable_ai_analysis=self.config.enable_ai_analysis,
                enable_semantic_matching=self.config.enable_semantic_matching
            )

            await self.intelligent_router.initialize()

            logger.info("  ✅ Intelligent EventBus initialized")

        except Exception as e:
            logger.error(f"  ❌ Failed to initialize Intelligent EventBus: {e}")
            logger.info("  ⚠️  Falling back to basic EventBus")
            return await self._init_basic_eventbus()

    async def _init_basic_eventbus(self):
        """Initialize basic EventBus (fallback)"""
        logger.info("  📡 Initializing Basic EventBus...")

        from infrastructure.eventbus import create_eventbus

        self.eventbus = create_eventbus(self.config.eventbus_backend)

        logger.info("  ✅ Basic EventBus initialized")

    async def _init_saga_engine(self):
        """Initialize Saga Pattern Engine"""
        logger.info("  🔄 Initializing Saga Engine...")

        try:
            from intelligent_core.orchestration.saga_engine import (
                SagaOrchestrator,
                InMemorySagaStateStore,
                RedisSagaStateStore,
                PostgresSagaStateStore
            )

            # Create state store based on config
            if self.config.saga_state_store == "postgresql":
                state_store = PostgresSagaStateStore(self.config.database_url)
            elif self.config.saga_state_store == "redis":
                # Parse redis URL
                import redis.asyncio as redis
                redis_client = await redis.from_url(self.config.redis_url)
                state_store = RedisSagaStateStore(redis_client)
            else:  # memory
                state_store = InMemorySagaStateStore()

            # Initialize state store (if needed)
            if hasattr(state_store, 'initialize'):
                await state_store.initialize()

            # Create orchestrator
            self.saga_orchestrator = SagaOrchestrator(
                state_store=state_store,
                service_invoker=self._default_service_invoker,
                event_publisher=self._publish_event
            )

            logger.info("  ✅ Saga Engine initialized with %s state store", self.config.saga_state_store)

        except ImportError as e:
            logger.warning(f"  ⚠️  Saga Engine not available: {e}")
            self.saga_orchestrator = None
        except Exception as e:
            logger.error(f"  ❌ Failed to initialize Saga Engine: {e}")
            self.saga_orchestrator = None

    async def _init_cqrs(self):
        """Initialize CQRS Infrastructure"""
        logger.info("  ⚡ Initializing CQRS Infrastructure...")

        try:
            from platform_services.bcm_domain._cqrs import (
                init_cqrs,
                get_command_handler,
                get_query_handler
            )

            # Initialize CQRS
            await init_cqrs(
                database_url=self.config.database_url,
                eventbus_client=self.eventbus,
                redis_url=self.config.redis_url
            )

            # Get handlers
            self.cqrs_command_handler = get_command_handler()
            self.cqrs_query_handler = get_query_handler()

            logger.info("  ✅ CQRS Infrastructure initialized")

        except ImportError as e:
            logger.warning(f"  ⚠️  CQRS not available: {e}")
            self.cqrs_command_handler = None
            self.cqrs_query_handler = None
        except Exception as e:
            logger.error(f"  ❌ Failed to initialize CQRS: {e}")
            self.cqrs_command_handler = None
            self.cqrs_query_handler = None

    async def _default_service_invoker(self, service_name: str, action: str, params: Dict[str, Any]) -> Any:
        """
        Default service invoker for Saga Engine

        This should be customized based on your service discovery mechanism
        """
        logger.info(f"Invoking service: {service_name}.{action} with params: {params}")

        # TODO: Implement actual service invocation
        # This is a placeholder that should be replaced with:
        # - HTTP calls to microservices
        # - gRPC calls
        # - Direct function calls
        # - Queue-based invocation

        return {"status": "success", "invoked": f"{service_name}.{action}"}

    async def _publish_event(self, event_type: str, data: Dict[str, Any], **kwargs):
        """Publish event via EventBus"""
        if self.intelligent_router:
            from infrastructure.eventbus import Event
            event = Event.create(
                event_type=event_type,
                data=data,
                source="saga_engine",
                **kwargs
            )
            await self.intelligent_router.route_event(event)
        elif self.eventbus:
            from infrastructure.eventbus import Event
            event = Event.create(
                event_type=event_type,
                data=data,
                source="saga_engine",
                **kwargs
            )
            await self.eventbus.publish(event)

    async def shutdown(self):
        """Shutdown all platform components"""
        logger.info("🛑 Shutting down Platform Integration...")

        tasks = []

        # Shutdown EventBus
        if self.eventbus and hasattr(self.eventbus, 'close'):
            tasks.append(self.eventbus.close())

        # Shutdown Saga state store
        if self.saga_orchestrator and hasattr(self.saga_orchestrator.state_store, 'close'):
            tasks.append(self.saga_orchestrator.state_store.close())

        # Shutdown CQRS
        try:
            from platform_services.bcm_domain._cqrs import shutdown_cqrs
            tasks.append(shutdown_cqrs())
        except ImportError:
            pass

        # Run all shutdowns in parallel
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        self._initialized = False
        logger.info("✅ Platform Integration shutdown complete")

    def get_status(self) -> Dict[str, Any]:
        """Get platform integration status"""
        return {
            "initialized": self._initialized,
            "components": {
                "eventbus": "basic" if self.eventbus and not self.intelligent_router else ("intelligent" if self.intelligent_router else "disabled"),
                "saga_engine": "enabled" if self.saga_orchestrator else "disabled",
                "cqrs": "enabled" if self.cqrs_command_handler else "disabled",
            },
            "config": {
                "intelligent_routing": self.config.enable_intelligent_routing,
                "saga_engine": self.config.enable_saga_engine,
                "self_aware": self.config.enable_self_aware,
                "cqrs": self.config.enable_cqrs,
            }
        }


# Global platform instance
_platform: Optional[PlatformIntegration] = None


async def init_platform(
    database_url: str,
    redis_url: str,
    **kwargs
) -> PlatformIntegration:
    """
    Initialize platform integration

    Args:
        database_url: PostgreSQL connection string
        redis_url: Redis connection string
        **kwargs: Additional configuration options

    Returns:
        Initialized PlatformIntegration instance

    Example:
        platform = await init_platform(
            database_url="postgresql://localhost/bcm",
            redis_url="redis://localhost:6379",
            enable_intelligent_routing=True,
            enable_saga_engine=True,
            enable_cqrs=True
        )
    """
    global _platform

    config = PlatformConfig(
        database_url=database_url,
        redis_url=redis_url,
        **kwargs
    )

    _platform = PlatformIntegration(config)
    await _platform.initialize()

    return _platform


def get_platform() -> Optional[PlatformIntegration]:
    """
    Get global platform integration instance

    Returns:
        PlatformIntegration instance or None if not initialized
    """
    return _platform


async def shutdown_platform():
    """Shutdown platform integration"""
    global _platform

    if _platform:
        await _platform.shutdown()
        _platform = None
