"""
AI Agent Router Client для MIO Manager

Интеграция AI Agent Router v2.0 с MIO Manager.
Делает agent-router центральной точкой входа для всех AI запросов.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

# Добавляем путь к agent-router
AGENT_ROUTER_PATH = Path(__file__).parent.parent.parent / "agent-router"
sys.path.insert(0, str(AGENT_ROUTER_PATH))

try:
    from router import AIAgentRouter, AgentCapability, AIAgent
    AGENT_ROUTER_AVAILABLE = True
except ImportError as e:
    AGENT_ROUTER_AVAILABLE = False
    logging.warning(f"AI Agent Router not available: {e}")

logger = logging.getLogger(__name__)


class AgentRouterClient:
    """
    Client для интеграции AI Agent Router с MIO Manager

    Использование:
        client = AgentRouterClient()
        await client.initialize()
        result = await client.route_ai_request(
            capability="bia",
            request_data={...}
        )
    """

    def __init__(
        self,
        redis_url: str = "redis://redis:6379/0",
        enable_circuit_breaker: bool = True,
        enable_metrics: bool = True,
        rate_limit: int = 1000
    ):
        """
        Initialize Agent Router Client

        Args:
            redis_url: Redis connection URL
            enable_circuit_breaker: Enable circuit breaker protection
            enable_metrics: Enable Prometheus metrics
            rate_limit: Global rate limit (requests per minute)
        """
        self.redis_url = redis_url
        self.enable_circuit_breaker = enable_circuit_breaker
        self.enable_metrics = enable_metrics
        self.rate_limit = rate_limit

        self.router: Optional[AIAgentRouter] = None
        self.initialized = False

        if not AGENT_ROUTER_AVAILABLE:
            logger.error("AI Agent Router module not available!")
            raise ImportError("Cannot import AI Agent Router")

    async def initialize(self):
        """Initialize the router"""
        if self.initialized:
            logger.warning("Agent Router Client already initialized")
            return

        try:
            self.router = AIAgentRouter(
                redis_url=self.redis_url,
                enable_circuit_breaker=self.enable_circuit_breaker,
                enable_metrics=self.enable_metrics,
                rate_limit=self.rate_limit
            )

            self.initialized = True
            logger.info("✅ Agent Router Client initialized successfully")

            # Initial health check
            health = await self.router.health_check_all_agents()
            healthy_count = sum(1 for h in health.values() if h.get("healthy"))
            logger.info(f"📊 Agent health: {healthy_count}/{len(health)} agents healthy")

        except Exception as e:
            logger.error(f"Failed to initialize Agent Router Client: {e}")
            raise

    async def route_ai_request(
        self,
        capability: str,
        request_data: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Route AI request to appropriate agent

        Args:
            capability: AI capability required (bia, pdca, document, compliance, etc.)
            request_data: Request payload
            context: Optional context (user_id, priority, etc.)

        Returns:
            Response from AI agent

        Raises:
            ValueError: If router not initialized or no agents available
            Exception: If request fails
        """
        if not self.initialized or not self.router:
            raise ValueError("Agent Router Client not initialized. Call initialize() first.")

        # Map string capability to enum
        capability_map = {
            "bia": AgentCapability.BIA_ANALYSIS,
            "pdca": AgentCapability.PDCA,
            "document": AgentCapability.DOCUMENT_PROCESSING,
            "compliance": AgentCapability.COMPLIANCE_CHECK,
            "workflow": AgentCapability.WORKFLOW_ORCHESTRATION,
            "github": AgentCapability.GITHUB_INTEGRATION,
            "decision": AgentCapability.DECISION_SUPPORT,
            "context": AgentCapability.CONTEXT_AWARENESS,
        }

        capability_enum = capability_map.get(capability.lower())
        if not capability_enum:
            raise ValueError(f"Unknown capability: {capability}. Available: {list(capability_map.keys())}")

        try:
            logger.info(f"🔄 Routing {capability} request to AI agent...")
            result = await self.router.route_request(
                capability=capability_enum,
                request_data=request_data,
                context=context or {}
            )
            logger.info(f"✅ {capability} request completed successfully")
            return result

        except Exception as e:
            logger.error(f"❌ Failed to route {capability} request: {e}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of all AI agents

        Returns:
            Health status of all agents
        """
        if not self.initialized or not self.router:
            return {"error": "Router not initialized"}

        try:
            health = await self.router.health_check_all_agents()
            return {
                "status": "healthy",
                "agents": health,
                "healthy_count": sum(1 for h in health.values() if h.get("healthy")),
                "total_count": len(health)
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"error": str(e)}

    async def get_analytics(self) -> Dict[str, Any]:
        """
        Get routing analytics

        Returns:
            Analytics data including agent stats, circuit breaker status, etc.
        """
        if not self.initialized or not self.router:
            return {"error": "Router not initialized"}

        try:
            return self.router.get_agent_analytics()
        except Exception as e:
            logger.error(f"Failed to get analytics: {e}")
            return {"error": str(e)}

    async def set_agent_rate_limit(self, agent_name: str, rate: int, per: float = 60.0):
        """
        Set rate limit for specific agent

        Args:
            agent_name: Name of the agent
            rate: Number of requests
            per: Time period in seconds
        """
        if not self.initialized or not self.router:
            raise ValueError("Router not initialized")

        await self.router.set_agent_rate_limit(agent_name, rate, per)
        logger.info(f"Set rate limit for {agent_name}: {rate} req/{per}s")

    async def reset_circuit_breaker(self, agent_name: str):
        """
        Manually reset circuit breaker for agent

        Args:
            agent_name: Name of the agent
        """
        if not self.initialized or not self.router:
            raise ValueError("Router not initialized")

        await self.router.reset_circuit_breaker(agent_name)
        logger.info(f"Circuit breaker reset for {agent_name}")

    async def reset_all_circuit_breakers(self):
        """Reset all circuit breakers"""
        if not self.initialized or not self.router:
            raise ValueError("Router not initialized")

        await self.router.reset_all_circuit_breakers()
        logger.info("All circuit breakers reset")

    def get_available_capabilities(self) -> List[str]:
        """
        Get list of available AI capabilities

        Returns:
            List of capability names
        """
        return [
            "bia",
            "pdca",
            "document",
            "compliance",
            "workflow",
            "github",
            "decision",
            "context"
        ]

    def get_router_status(self) -> Dict[str, Any]:
        """
        Get router status

        Returns:
            Router status including initialization state, configuration
        """
        return {
            "initialized": self.initialized,
            "circuit_breaker_enabled": self.enable_circuit_breaker,
            "metrics_enabled": self.enable_metrics,
            "rate_limit": self.rate_limit,
            "redis_url": self.redis_url,
            "available_capabilities": self.get_available_capabilities()
        }


# Singleton instance for easy import
_agent_router_client: Optional[AgentRouterClient] = None


async def get_agent_router_client(
    redis_url: str = "redis://redis:6379/0",
    auto_initialize: bool = True
) -> AgentRouterClient:
    """
    Get or create singleton Agent Router Client

    Args:
        redis_url: Redis connection URL
        auto_initialize: Automatically initialize router

    Returns:
        AgentRouterClient instance
    """
    global _agent_router_client

    if _agent_router_client is None:
        _agent_router_client = AgentRouterClient(redis_url=redis_url)

        if auto_initialize:
            await _agent_router_client.initialize()

    return _agent_router_client


# Convenience function for quick routing
async def route_ai_request(
    capability: str,
    request_data: Dict[str, Any],
    context: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Convenience function to route AI request

    Args:
        capability: AI capability (bia, pdca, document, etc.)
        request_data: Request payload
        context: Optional context

    Returns:
        Response from AI agent
    """
    client = await get_agent_router_client()
    return await client.route_ai_request(capability, request_data, context)
