"""
Полный пример интеграции AI Agent Router v2.0

Демонстрирует все возможности:
- Инициализация с circuit breaker, metrics, rate limiting
- Интеграция с MIO Manager
- Dynamic service discovery
- Health check daemon
- Metrics server
"""

import asyncio
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import agent router components
from router import AIAgentRouter, AgentCapability
from health_daemon import HealthCheckDaemon


async def example_basic_usage():
    """Example 1: Basic usage"""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 1: Basic Usage")
    logger.info("=" * 60)

    # Initialize router
    router = AIAgentRouter(
        redis_url="redis://redis:6379/0",
        enable_circuit_breaker=True,
        enable_metrics=True,
        rate_limit=1000
    )

    logger.info("✅ Router initialized")

    # Check agent health
    health = await router.health_check_all_agents()
    logger.info(f"📊 Agent health: {health}")

    # Get analytics
    analytics = router.get_agent_analytics()
    logger.info(f"📈 Analytics: {len(analytics['agents'])} agents registered")

    return router


async def example_routing_request(router):
    """Example 2: Route AI request"""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 2: Routing AI Request")
    logger.info("=" * 60)

    try:
        # Route BIA analysis request
        result = await router.route_request(
            capability=AgentCapability.BIA_ANALYSIS,
            request_data={
                "organization": "Example Corp",
                "scope": "IT Department"
            },
            context={
                "user_id": "demo_user",
                "priority": "high"
            }
        )

        logger.info(f"✅ Request routed successfully: {result}")

    except Exception as e:
        logger.error(f"❌ Routing failed: {e}")


async def example_rate_limiting(router):
    """Example 3: Rate limiting"""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 3: Rate Limiting")
    logger.info("=" * 60)

    # Set rate limit for specific agent
    await router.set_agent_rate_limit("unified_ai", rate=50, per=60.0)
    logger.info("✅ Set rate limit for unified_ai: 50 req/min")

    # Get rate limiter status
    analytics = router.get_agent_analytics()
    logger.info(f"📊 Rate limiter: {analytics['rate_limiter']}")


async def example_circuit_breaker(router):
    """Example 4: Circuit breaker"""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 4: Circuit Breaker")
    logger.info("=" * 60)

    if router.circuit_breaker_manager:
        # Get circuit breaker stats
        cb_stats = router.circuit_breaker_manager.get_all_stats()
        logger.info(f"📊 Circuit breakers: {list(cb_stats.keys())}")

        # Manual reset (if needed)
        # await router.reset_circuit_breaker("ai_orchestrator")
        logger.info("✅ Circuit breakers operational")
    else:
        logger.warning("⚠️ Circuit breaker not available")


async def example_dynamic_registration(router):
    """Example 5: Dynamic agent registration"""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 5: Dynamic Agent Registration")
    logger.info("=" * 60)

    # Register new agent dynamically
    success = await router.register_agent_from_discovery(
        name="custom_ai_agent",
        role="specialist",
        endpoint="http://custom-ai:8100",
        capabilities=["document", "compliance"],
        priority=6
    )

    if success:
        logger.info("✅ Dynamically registered custom agent")
        logger.info(f"📊 Total agents: {len(router.agents)}")
    else:
        logger.error("❌ Failed to register agent")


async def example_health_daemon(router):
    """Example 6: Health check daemon"""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 6: Health Check Daemon")
    logger.info("=" * 60)

    # Start health check daemon
    daemon = HealthCheckDaemon(router, check_interval=30)
    await daemon.start()

    logger.info("✅ Health check daemon started")

    # Wait for a few checks
    logger.info("⏳ Waiting for 3 health checks...")
    await asyncio.sleep(65)  # 2 checks @ 30s interval

    # Get daemon stats
    stats = daemon.get_stats()
    logger.info(f"📊 Daemon stats: {stats}")

    # Stop daemon
    await daemon.stop()
    logger.info("✅ Health check daemon stopped")


async def example_mio_integration():
    """Example 7: MIO Manager integration"""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 7: MIO Manager Integration")
    logger.info("=" * 60)

    try:
        # Import MIO Manager client
        sys.path.insert(0, str(Path(__file__).parent.parent / "mio-manager" / "integrations"))
        from agent_router_client import AgentRouterClient

        # Initialize client
        client = AgentRouterClient(
            redis_url="redis://redis:6379/0",
            enable_circuit_breaker=True,
            enable_metrics=True,
            rate_limit=1000
        )

        await client.initialize()
        logger.info("✅ MIO Manager client initialized")

        # Route request through client
        result = await client.route_ai_request(
            capability="bia",
            request_data={"organization": "MIO Test Corp"},
            context={"user_id": "mio_user"}
        )

        logger.info(f"✅ Request routed via MIO Manager: {result}")

        # Get client status
        status = client.get_router_status()
        logger.info(f"📊 Router status: {status}")

    except Exception as e:
        logger.error(f"❌ MIO integration failed: {e}")


async def example_metrics_server():
    """Example 8: Start metrics server"""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 8: Metrics Server")
    logger.info("=" * 60)

    logger.info("To start metrics server, run:")
    logger.info("  python metrics_server.py")
    logger.info("\nMetrics will be available at:")
    logger.info("  http://localhost:9090/metrics  (for Prometheus)")
    logger.info("  http://localhost:9090/health   (health check)")


async def main():
    """Run all examples"""
    logger.info("\n" + "🚀" * 30)
    logger.info("AI Agent Router v2.0 - Integration Examples")
    logger.info("🚀" * 30)

    try:
        # Example 1: Basic usage
        router = await example_basic_usage()

        # Example 2: Routing request
        await example_routing_request(router)

        # Example 3: Rate limiting
        await example_rate_limiting(router)

        # Example 4: Circuit breaker
        await example_circuit_breaker(router)

        # Example 5: Dynamic registration
        await example_dynamic_registration(router)

        # Example 6: Health daemon (commented out - takes time)
        # await example_health_daemon(router)

        # Example 7: MIO integration
        await example_mio_integration()

        # Example 8: Metrics server info
        await example_metrics_server()

        logger.info("\n" + "✅" * 30)
        logger.info("All examples completed successfully!")
        logger.info("✅" * 30)

    except Exception as e:
        logger.error(f"\n❌ Example failed: {e}", exc_info=True)


if __name__ == "__main__":
    # Run examples
    asyncio.run(main())
