"""
AI Agent Router - Intelligent service routing for BCM Platform
Implements Docker AI Agent pattern with GitHub App integration
"""

import asyncio
import httpx
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import redis.asyncio as redis
from datetime import datetime, timedelta

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


class AIAgentRouter:
    """Intelligent AI Agent Router with Docker integration"""

    def __init__(self, redis_url: str = "redis://redis:6379/0"):
        self.redis_url = redis_url
        self.agents: Dict[str, AIAgent] = {}
        self.request_history: List[Dict] = []
        self.load_balancer_state: Dict[str, float] = {}

        # Initialize agent registry
        self._initialize_agents()

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
        """Route request to appropriate AI agent"""

        # Find capable agents
        capable_agents = [
            agent for agent in self.agents.values()
            if capability in agent.capabilities and agent.is_healthy
        ]

        if not capable_agents:
            raise ValueError(f"No healthy agents available for capability: {capability}")

        # Select best agent (priority + load balancing)
        selected_agent = self._select_best_agent(capable_agents)

        # Route request
        try:
            response = await self._send_to_agent(selected_agent, request_data, context)

            # Log success
            await self._log_request(capability, selected_agent.name, "success", response)

            return response

        except Exception as e:
            logger.error(f"Agent {selected_agent.name} failed: {e}")

            # Mark agent as potentially unhealthy
            selected_agent.is_healthy = False

            # Try fallback agent
            fallback_agents = [a for a in capable_agents if a != selected_agent and a.is_healthy]
            if fallback_agents:
                fallback_agent = self._select_best_agent(fallback_agents)
                response = await self._send_to_agent(fallback_agent, request_data, context)
                await self._log_request(capability, fallback_agent.name, "fallback", response)
                return response

            # Log failure
            await self._log_request(capability, selected_agent.name, "failed", {"error": str(e)})
            raise

    def _select_best_agent(self, agents: List[AIAgent]) -> AIAgent:
        """Select best agent based on priority and load"""
        # Sort by priority first, then by load
        return sorted(agents,
                     key=lambda a: (a.priority, self.load_balancer_state.get(a.name, 0)))[0]

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
        """Check health of all agents"""
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

                    results[agent_name] = {
                        "healthy": agent.is_healthy,
                        "status_code": response.status_code,
                        "response_time": response.elapsed.total_seconds(),
                        "last_check": agent.last_health_check.isoformat()
                    }

                except Exception as e:
                    agent.is_healthy = False
                    agent.last_health_check = datetime.now()

                    results[agent_name] = {
                        "healthy": False,
                        "error": str(e),
                        "last_check": agent.last_health_check.isoformat()
                    }

        return results

    def get_agent_analytics(self) -> Dict:
        """Get analytics for all agents"""
        return {
            "agents": {
                name: {
                    "role": agent.role.value,
                    "capabilities": [cap.value for cap in agent.capabilities],
                    "endpoint": agent.endpoint,
                    "healthy": agent.is_healthy,
                    "load_factor": self.load_balancer_state.get(name, 0),
                    "priority": agent.priority
                }
                for name, agent in self.agents.items()
            },
            "recent_requests": len(self.request_history),
            "request_distribution": self._get_request_distribution()
        }

    def _get_request_distribution(self) -> Dict[str, int]:
        """Get request distribution by agent"""
        distribution = {}
        for req in self.request_history[-100:]:  # Last 100 requests
            agent = req["agent"]
            distribution[agent] = distribution.get(agent, 0) + 1
        return distribution


# Global router instance
ai_router = AIAgentRouter()
