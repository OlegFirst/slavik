"""
AI Agent Router - Intelligent service routing for BCM Platform
Implements Docker AI Agent pattern with GitHub App integration

ИНТЕГРАЦИИ:
- Circuit Breaker для защиты от cascade failures
- Prometheus metrics для мониторинга
- Service Registry для динамического обнаружения
- Rate Limiting для защиты от перегрузки
"""

import asyncio
import httpx
import json
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict
import redis.asyncio as redis
from datetime import datetime, timedelta

# Интеграция с существующими модулями
try:
    from .circuit_breaker import CircuitBreakerManager, CircuitBreakerOpenError
    CIRCUIT_BREAKER_AVAILABLE = True
except ImportError:
    CIRCUIT_BREAKER_AVAILABLE = False
    logging.warning("Circuit Breaker not available")

try:
    from .metrics import (
        record_request, record_agent_health, record_fallback,
        record_error, record_no_agents, update_agent_load,
        set_router_info, record_redis_operation
    )
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    logging.warning("Prometheus metrics not available")

logger = logging.getLogger(__name__)


class AgentCapability(str, Enum):
    """AI Agent capabilities"""
    PDCA = "pdca"
    BIA_ANALYSIS = "bia"
    DOCUMENT_PROCESSING = "document"
    COMPLIANCE_CHECK = "compliance"
    WORKFLOW_ORCHESTRATION = "workflow"
    GITHUB_INTEGRATION = "github"
    DECISION_SUPPORT = "decision"
    CONTEXT_AWARENESS = "context"


class AgentRole(str, Enum):
    """AI Agent roles"""
    ORCHESTRATOR = "orchestrator"      # Main brain
    PROCESSOR = "processor"           # Multi-service processor
    ASSISTANT = "assistant"           # Context-aware helper
    SPECIALIST = "specialist"         # Domain-specific expert
    BRIDGE = "bridge"                # External integration
    REGISTRY = "registry"            # Service discovery


@dataclass
class AIAgent:
    """AI Agent definition"""
    name: str
    role: AgentRole
    endpoint: str
    capabilities: List[AgentCapability]
    health_check: str
    priority: int = 1
    load_factor: float = 1.0
    last_health_check: Optional[datetime] = None
    is_healthy: bool = True
    response_times: List[float] = None  # Для advanced load balancing

    def __post_init__(self):
        if self.response_times is None:
            self.response_times = []


class RateLimiter:
    """Simple token bucket rate limiter"""

    def __init__(self, rate: int = 100, per: float = 1.0):
        """
        Args:
            rate: Количество запросов
            per: За период времени (секунды)
        """
        self.rate = rate
        self.per = per
        self.allowance = rate
        self.last_check = time.time()

    async def check(self) -> bool:
        """Проверить, можно ли выполнить запрос"""
        current = time.time()
        time_passed = current - self.last_check
        self.last_check = current

        # Добавляем токены за прошедшее время
        self.allowance += time_passed * (self.rate / self.per)

        if self.allowance > self.rate:
            self.allowance = self.rate

        if self.allowance < 1.0:
            return False
        else:
            self.allowance -= 1.0
            return True


class AIAgentRouter:
    """
    Intelligent AI Agent Router with Docker integration

    ИНТЕГРАЦИИ:
    - Circuit Breaker для защиты
    - Prometheus metrics
    - Rate Limiting
    - Advanced Load Balancing (response time based)
    """

    def __init__(self, redis_url: str = "redis://redis:6379/0",
                 enable_circuit_breaker: bool = True,
                 enable_metrics: bool = True,
                 rate_limit: int = 1000):
        self.redis_url = redis_url
        self.agents: Dict[str, AIAgent] = {}
        self.request_history: List[Dict] = []
        self.load_balancer_state: Dict[str, float] = {}

        # Rate Limiting
        self.rate_limiter = RateLimiter(rate=rate_limit, per=60.0)  # requests per minute
        self.agent_rate_limiters: Dict[str, RateLimiter] = {}

        # Circuit Breaker
        self.circuit_breaker_manager = None
        if enable_circuit_breaker and CIRCUIT_BREAKER_AVAILABLE:
            self.circuit_breaker_manager = CircuitBreakerManager()
            logger.info(" Circuit Breaker enabled")

        # Metrics
        self.metrics_enabled = enable_metrics and METRICS_AVAILABLE
        if self.metrics_enabled:
            logger.info(" Prometheus metrics enabled")

        # Statistics для advanced load balancing
        self.agent_stats: Dict[str, Dict] = defaultdict(lambda: {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'avg_response_time': 0.0,
            'last_response_times': []
        })

        # Initialize agent registry
        self._initialize_agents()

        # Set router info in metrics
        if self.metrics_enabled:
            set_router_info("2.0.0", len(self.agents))

    def _initialize_agents(self):
        """Initialize AI agent registry"""
        self.agents = {
            "ai_orchestrator": AIAgent(
                name="ai_orchestrator",
                role=AgentRole.ORCHESTRATOR,
                endpoint="http://ai_orchestrator:8000",
                capabilities=[
                    AgentCapability.PDCA,
                    AgentCapability.WORKFLOW_ORCHESTRATION,
                    AgentCapability.DECISION_SUPPORT
                ],
                health_check="/health",
                priority=1
            ),
            "unified_ai": AIAgent(
                name="unified_ai",
                role=AgentRole.PROCESSOR,
                endpoint="http://unified_ai:8090",
                capabilities=[
                    AgentCapability.BIA_ANALYSIS,
                    AgentCapability.DOCUMENT_PROCESSING,
                    AgentCapability.COMPLIANCE_CHECK
                ],
                health_check="/health",
                priority=2
            ),
            "pdca_assistant": AIAgent(
                name="pdca_assistant",
                role=AgentRole.ASSISTANT,
                endpoint="http://pdca_assistant:8010",
                capabilities=[
                    AgentCapability.PDCA,
                    AgentCapability.CONTEXT_AWARENESS
                ],
                health_check="/health",
                priority=3
            ),
            "github_app": AIAgent(
                name="github_app",
                role=AgentRole.BRIDGE,
                endpoint="http://github_app:8001",
                capabilities=[AgentCapability.GITHUB_INTEGRATION],
                health_check="/health",
                priority=4
            ),
            "document_ai": AIAgent(
                name="document_ai",
                role=AgentRole.SPECIALIST,
                endpoint="http://document_ai:8083",
                capabilities=[AgentCapability.DOCUMENT_PROCESSING],
                health_check="/health",
                priority=5
            )
        }

    async def route_request(self,
                          capability: AgentCapability,
                          request_data: Dict[str, Any],
                          context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Route request to appropriate AI agent

        ИНТЕГРАЦИИ:
        - Rate limiting check
        - Circuit breaker protection
        - Prometheus metrics
        - Advanced load balancing
        """
        start_time = time.time()

        # 1. Rate Limiting Check
        if not await self.rate_limiter.check():
            error_msg = "Rate limit exceeded"
            logger.warning(error_msg)
            if self.metrics_enabled:
                record_error(capability.value, "router", "rate_limit_exceeded")
            raise ValueError(error_msg)

        # 2. Find capable agents
        capable_agents = [
            agent for agent in self.agents.values()
            if capability in agent.capabilities and agent.is_healthy
        ]

        if not capable_agents:
            if self.metrics_enabled:
                record_no_agents(capability.value)
            raise ValueError(f"No healthy agents available for capability: {capability}")

        # 3. Select best agent (advanced load balancing: priority + response time)
        selected_agent = self._select_best_agent(capable_agents)

        # 4. Check agent-specific rate limit
        agent_limiter = self.agent_rate_limiters.get(selected_agent.name)
        if agent_limiter and not await agent_limiter.check():
            # Try another agent
            fallback_agents = [a for a in capable_agents if a != selected_agent]
            if fallback_agents:
                selected_agent = self._select_best_agent(fallback_agents)
            else:
                raise ValueError(f"Agent {selected_agent.name} rate limit exceeded and no fallback available")

        # 5. Route request (with Circuit Breaker if available)
        try:
            if self.circuit_breaker_manager:
                # Через Circuit Breaker
                breaker = await self.circuit_breaker_manager.get_breaker(selected_agent.name)
                response = await breaker.call(self._send_to_agent, selected_agent, request_data, context)
            else:
                # Напрямую
                response = await self._send_to_agent(selected_agent, request_data, context)

            # Calculate duration
            duration = time.time() - start_time

            # Update statistics
            self._update_agent_stats(selected_agent.name, duration, success=True)

            # Log success
            await self._log_request(capability, selected_agent.name, "success", response)

            # Metrics
            if self.metrics_enabled:
                record_request(capability.value, selected_agent.name, "success", duration)
                update_agent_load(selected_agent.name, self.load_balancer_state.get(selected_agent.name, 0))

            return response

        except Exception as e:
            duration = time.time() - start_time
            error_type = type(e).__name__

            logger.error(f"Agent {selected_agent.name} failed: {e}")

            # Update statistics
            self._update_agent_stats(selected_agent.name, duration, success=False)

            # Mark agent as potentially unhealthy
            selected_agent.is_healthy = False

            # Metrics
            if self.metrics_enabled:
                record_error(capability.value, selected_agent.name, error_type)

            # Try fallback agent
            fallback_agents = [a for a in capable_agents if a != selected_agent and a.is_healthy]
            if fallback_agents:
                fallback_agent = self._select_best_agent(fallback_agents)

                # Metrics for fallback
                if self.metrics_enabled:
                    record_fallback(capability.value, selected_agent.name, fallback_agent.name)

                try:
                    response = await self._send_to_agent(fallback_agent, request_data, context)
                    fallback_duration = time.time() - start_time
                    await self._log_request(capability, fallback_agent.name, "fallback", response)

                    if self.metrics_enabled:
                        record_request(capability.value, fallback_agent.name, "fallback", fallback_duration)

                    return response
                except Exception as fallback_error:
                    logger.error(f"Fallback agent {fallback_agent.name} also failed: {fallback_error}")

            # Log failure
            await self._log_request(capability, selected_agent.name, "failed", {"error": str(e)})
            raise

    def _select_best_agent(self, agents: List[AIAgent]) -> AIAgent:
        """
        Select best agent based on:
        1. Priority (lower is better)
        2. Average response time (lower is better)
        3. Current load (lower is better)
        """
        def agent_score(agent: AIAgent) -> tuple:
            stats = self.agent_stats[agent.name]
            avg_response = stats.get('avg_response_time', 0.0)
            current_load = self.load_balancer_state.get(agent.name, 0)

            # Трёхуровневая сортировка
            return (
                agent.priority,                    # 1. Приоритет
                avg_response if avg_response > 0 else 999.0,  # 2. Скорость ответа
                current_load                       # 3. Текущая нагрузка
            )

        return sorted(agents, key=agent_score)[0]

    def _update_agent_stats(self, agent_name: str, response_time: float, success: bool):
        """Update agent statistics for load balancing"""
        stats = self.agent_stats[agent_name]
        stats['total_requests'] += 1

        if success:
            stats['successful_requests'] += 1

            # Update response times (keep last 100)
            stats['last_response_times'].append(response_time)
            if len(stats['last_response_times']) > 100:
                stats['last_response_times'] = stats['last_response_times'][-100:]

            # Calculate average
            stats['avg_response_time'] = sum(stats['last_response_times']) / len(stats['last_response_times'])
        else:
            stats['failed_requests'] += 1

    async def _send_to_agent(self,
                           agent: AIAgent,
                           request_data: Dict[str, Any],
                           context: Optional[Dict] = None) -> Dict[str, Any]:
        """Send request to specific agent"""

        # Prepare request payload
        payload = {
            "data": request_data,
            "context": context or {},
            "timestamp": datetime.now().isoformat(),
            "routing_info": {
                "from": "ai_agent_router",
                "capability_requested": request_data.get("capability"),
                "agent_selected": agent.name
            }
        }

        # Send HTTP request
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{agent.endpoint}/ai/process",
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()

            # Update load tracking
            self.load_balancer_state[agent.name] = self.load_balancer_state.get(agent.name, 0) + 1

            return response.json()

    async def _log_request(self, capability: AgentCapability, agent_name: str,
                         status: str, response_data: Dict):
        """Log request for analytics"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "capability": capability,
            "agent": agent_name,
            "status": status,
            "response_size": len(str(response_data)),
            "processing_time": response_data.get("processing_time", 0)
        }

        self.request_history.append(log_entry)

        # Keep only last 1000 entries
        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-1000:]

        # Store in Redis for analytics
        try:
            redis_client = redis.from_url(self.redis_url)
            await redis_client.lpush("ai_agent_requests", json.dumps(log_entry))
            await redis_client.ltrim("ai_agent_requests", 0, 999)  # Keep last 1000
            await redis_client.close()
        except Exception as e:
            logger.warning(f"Failed to log to Redis: {e}")

    async def health_check_all_agents(self) -> Dict[str, Dict]:
        """Check health of all agents (with Prometheus metrics integration)"""
        results = {}

        async with httpx.AsyncClient() as client:
            for agent_name, agent in self.agents.items():
                try:
                    response = await client.get(
                        f"{agent.endpoint}{agent.health_check}",
                        timeout=5.0
                    )

                    agent.is_healthy = response.status_code == 200
                    agent.last_health_check = datetime.now()
                    response_time = response.elapsed.total_seconds()

                    results[agent_name] = {
                        "healthy": agent.is_healthy,
                        "status_code": response.status_code,
                        "response_time": response_time,
                        "last_check": agent.last_health_check.isoformat()
                    }

                    # Record metrics
                    if self.metrics_enabled:
                        record_agent_health(agent_name, agent.role.value, agent.is_healthy, response_time)

                except Exception as e:
                    agent.is_healthy = False
                    agent.last_health_check = datetime.now()

                    results[agent_name] = {
                        "healthy": False,
                        "error": str(e),
                        "last_check": agent.last_health_check.isoformat()
                    }

                    # Record unhealthy metrics
                    if self.metrics_enabled:
                        record_agent_health(agent_name, agent.role.value, False)

        return results

    def get_agent_analytics(self) -> Dict:
        """Get analytics for all agents (enhanced with statistics)"""
        return {
            "agents": {
                name: {
                    "role": agent.role.value,
                    "capabilities": [cap.value for cap in agent.capabilities],
                    "endpoint": agent.endpoint,
                    "healthy": agent.is_healthy,
                    "load_factor": self.load_balancer_state.get(name, 0),
                    "priority": agent.priority,
                    "stats": self.agent_stats[name],  # NEW: Statistics
                    "avg_response_time": self.agent_stats[name].get('avg_response_time', 0.0)
                }
                for name, agent in self.agents.items()
            },
            "recent_requests": len(self.request_history),
            "request_distribution": self._get_request_distribution(),
            "circuit_breakers": self._get_circuit_breaker_stats() if self.circuit_breaker_manager else {},
            "rate_limiter": {
                "current_allowance": self.rate_limiter.allowance,
                "rate": self.rate_limiter.rate,
                "per": self.rate_limiter.per
            }
        }

    def _get_circuit_breaker_stats(self) -> Dict:
        """Get circuit breaker statistics"""
        if self.circuit_breaker_manager:
            return self.circuit_breaker_manager.get_all_stats()
        return {}

    async def set_agent_rate_limit(self, agent_name: str, rate: int, per: float = 60.0):
        """Set rate limit for specific agent"""
        self.agent_rate_limiters[agent_name] = RateLimiter(rate=rate, per=per)
        logger.info(f"Set rate limit for {agent_name}: {rate} requests per {per}s")

    async def reset_circuit_breaker(self, agent_name: str):
        """Manually reset circuit breaker for agent"""
        if self.circuit_breaker_manager:
            await self.circuit_breaker_manager.reset_breaker(agent_name)
            logger.info(f"Circuit breaker reset for {agent_name}")

    async def reset_all_circuit_breakers(self):
        """Reset all circuit breakers"""
        if self.circuit_breaker_manager:
            await self.circuit_breaker_manager.reset_all()
            logger.info("All circuit breakers reset")

    def _get_request_distribution(self) -> Dict[str, int]:
        """Get request distribution by agent"""
        distribution = {}
        for req in self.request_history[-100:]:  # Last 100 requests
            agent = req["agent"]
            distribution[agent] = distribution.get(agent, 0) + 1
        return distribution

    # ============================================================================
    # Dynamic Service Discovery Integration
    # ============================================================================

    async def register_agent_from_discovery(
        self,
        name: str,
        role: str,
        endpoint: str,
        capabilities: List[str],
        priority: int = 5
    ) -> bool:
        """
        Dynamically register agent from service discovery

        Args:
            name: Agent name
            role: Agent role (orchestrator, processor, assistant, specialist, bridge)
            endpoint: Agent endpoint URL
            capabilities: List of capability strings
            priority: Agent priority (lower = higher priority)

        Returns:
            True if registered successfully
        """
        try:
            # Map role string to enum
            role_map = {
                "orchestrator": AgentRole.ORCHESTRATOR,
                "processor": AgentRole.PROCESSOR,
                "assistant": AgentRole.ASSISTANT,
                "specialist": AgentRole.SPECIALIST,
                "bridge": AgentRole.BRIDGE,
                "registry": AgentRole.REGISTRY
            }

            role_enum = role_map.get(role.lower())
            if not role_enum:
                logger.error(f"Unknown role: {role}")
                return False

            # Map capability strings to enums
            capability_map = {
                "pdca": AgentCapability.PDCA,
                "bia": AgentCapability.BIA_ANALYSIS,
                "document": AgentCapability.DOCUMENT_PROCESSING,
                "compliance": AgentCapability.COMPLIANCE_CHECK,
                "workflow": AgentCapability.WORKFLOW_ORCHESTRATION,
                "github": AgentCapability.GITHUB_INTEGRATION,
                "decision": AgentCapability.DECISION_SUPPORT,
                "context": AgentCapability.CONTEXT_AWARENESS
            }

            capability_enums = []
            for cap in capabilities:
                cap_enum = capability_map.get(cap.lower())
                if cap_enum:
                    capability_enums.append(cap_enum)
                else:
                    logger.warning(f"Unknown capability: {cap}")

            if not capability_enums:
                logger.error(f"No valid capabilities for agent {name}")
                return False

            # Create agent
            agent = AIAgent(
                name=name,
                role=role_enum,
                endpoint=endpoint,
                capabilities=capability_enums,
                health_check="/health",
                priority=priority
            )

            # Register
            self.agents[name] = agent
            logger.info(f" Dynamically registered agent: {name} ({role}) with {len(capability_enums)} capabilities")

            # Update metrics
            if self.metrics_enabled:
                set_router_info("2.0.0", len(self.agents))

            return True

        except Exception as e:
            logger.error(f"Failed to register agent {name}: {e}")
            return False

    async def unregister_agent(self, name: str) -> bool:
        """
        Unregister agent

        Args:
            name: Agent name

        Returns:
            True if unregistered successfully
        """
        if name in self.agents:
            del self.agents[name]
            logger.info(f"Unregistered agent: {name}")

            # Update metrics
            if self.metrics_enabled:
                set_router_info("2.0.0", len(self.agents))

            return True
        else:
            logger.warning(f"Agent {name} not found")
            return False

    async def sync_with_service_registry(self, service_registry):
        """
        Sync agents with Service Registry

        Args:
            service_registry: ServiceRegistry instance from /infrastructure/runtime/service-discovery

        This method queries the service registry and automatically registers/unregisters agents.
        """
        try:
            # Get all AI services from registry
            services = await service_registry.list_services()

            # Filter AI agent services (by convention, they have 'ai' in metadata)
            ai_services = [
                s for s in services
                if s.metadata.get("type") == "ai_agent" or "ai" in s.name.lower()
            ]

            current_agents = set(self.agents.keys())
            registry_agents = set(s.name for s in ai_services)

            # Add new agents
            for service in ai_services:
                if service.name not in current_agents:
                    await self.register_agent_from_discovery(
                        name=service.name,
                        role=service.metadata.get("role", "processor"),
                        endpoint=service.url or f"http://{service.name}:{service.port}",
                        capabilities=service.metadata.get("capabilities", []),
                        priority=service.metadata.get("priority", 5)
                    )

            # Remove agents not in registry
            for agent_name in current_agents - registry_agents:
                # Don't remove hardcoded agents
                if agent_name not in ["ai_orchestrator", "unified_ai", "pdca_assistant", "github_app", "document_ai"]:
                    await self.unregister_agent(agent_name)

            logger.info(f" Synced with service registry: {len(self.agents)} agents")

        except Exception as e:
            logger.error(f"Failed to sync with service registry: {e}")


# Global router instance
ai_router = AIAgentRouter()
