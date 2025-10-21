"""
Direct Orchestrator Integration for Database Intelligence

Прямая интеграция с AI Orchestrator без EventBus (но EventBus тоже остается).

Dual approach:
1. EventBus - для async alerts, pub/sub
2. Direct API - для sync commands, orchestration
"""

import logging
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class OrchestratorCommand:
    """Command from Orchestrator"""
    command_id: str
    command_type: str  # optimize_query, kill_query, vacuum_table, create_index
    parameters: Dict[str, Any]
    priority: str  # critical, high, normal, low
    requested_by: str  # orchestrator, ai-foundation, manual
    timestamp: datetime


@dataclass
class CommandResult:
    """Result of executed command"""
    command_id: str
    status: str  # success, failed, skipped
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class OrchestratorClient:
    """
    Direct client for AI Orchestrator

    Provides:
    - Service registration
    - Heartbeat mechanism
    - Command receiving
    - Status reporting
    - Metrics push
    """

    def __init__(self, orchestrator_url: str = "http://localhost:8002"):
        self.orchestrator_url = orchestrator_url
        self.service_id = "db-intelligence"
        self.registered = False

    # =========================================================================
    # SERVICE LIFECYCLE
    # =========================================================================

    async def register(self) -> bool:
        """
        Register DB Intelligence service with Orchestrator

        Orchestrator gets full service metadata
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.orchestrator_url}/infrastructure/services/register",
                    json={
                        "service_id": self.service_id,
                        "service_name": "Database Intelligence",
                        "service_type": "infrastructure",
                        "version": "1.0.0",
                        "port": 8050,
                        "critical": True,  # Critical infrastructure
                        "capabilities": [
                            "query_monitoring",
                            "performance_analysis",
                            "security_monitoring",
                            "optimization_suggestions",
                            "admin_operations",
                            "health_monitoring"
                        ],
                        "endpoints": {
                            "health": "/health",
                            "metrics": "/metrics",
                            "slow_queries": "/slow-queries",
                            "suggestions": "/suggestions",
                            "analyze": "/analyze",
                            "tables": "/tables",
                            "prometheus": "/metrics/prometheus"
                        },
                        "dependencies": [
                            "postgresql",
                            "redis",
                            "rabbitmq"
                        ],
                        "managed_resources": [
                            "database_connections",
                            "query_performance",
                            "security_policies",
                            "optimization_indexes"
                        ],
                        "metadata": {
                            "description": "AI-powered database monitoring and optimization",
                            "auto_optimize": True,
                            "security_monitoring": True,
                            "learning_enabled": True
                        }
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    self.registered = True
                    logger.info(f" Registered with Orchestrator at {self.orchestrator_url}")
                    return True
                else:
                    logger.error(f"Registration failed: {response.status_code} - {response.text}")
                    return False

        except Exception as e:
            logger.error(f"Failed to register with Orchestrator: {e}")
            return False

    async def heartbeat(self, health_data: Dict[str, Any]) -> bool:
        """
        Send heartbeat with current health status

        Orchestrator uses this to monitor service health
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.orchestrator_url}/infrastructure/services/{self.service_id}/heartbeat",
                    json={
                        "timestamp": datetime.now().isoformat(),
                        "status": health_data.get("status", "unknown"),
                        "health": health_data,
                        "uptime_seconds": health_data.get("uptime_seconds", 0)
                    },
                    timeout=5.0
                )

                return response.status_code == 200

        except Exception as e:
            logger.debug(f"Heartbeat failed: {e}")
            return False

    async def deregister(self) -> bool:
        """
        Deregister service on shutdown

        Graceful shutdown notification
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.orchestrator_url}/infrastructure/services/{self.service_id}/deregister",
                    json={
                        "reason": "graceful_shutdown",
                        "timestamp": datetime.now().isoformat()
                    },
                    timeout=5.0
                )

                if response.status_code == 200:
                    logger.info(" Deregistered from Orchestrator")
                    return True

        except Exception as e:
            logger.error(f"Deregistration failed: {e}")

        return False

    # =========================================================================
    # COMMAND HANDLING
    # =========================================================================

    async def poll_commands(self) -> List[OrchestratorCommand]:
        """
        Poll Orchestrator for pending commands

        Orchestrator queues commands for DB Intelligence
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.orchestrator_url}/infrastructure/services/{self.service_id}/commands",
                    params={"limit": 10},
                    timeout=5.0
                )

                if response.status_code == 200:
                    commands_data = response.json().get("commands", [])
                    return [
                        OrchestratorCommand(
                            command_id=cmd["command_id"],
                            command_type=cmd["command_type"],
                            parameters=cmd["parameters"],
                            priority=cmd.get("priority", "normal"),
                            requested_by=cmd.get("requested_by", "orchestrator"),
                            timestamp=datetime.fromisoformat(cmd["timestamp"])
                        )
                        for cmd in commands_data
                    ]

        except Exception as e:
            logger.error(f"Failed to poll commands: {e}")

        return []

    async def report_command_result(self, result: CommandResult) -> bool:
        """
        Report command execution result back to Orchestrator

        Orchestrator tracks command outcomes for learning
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.orchestrator_url}/infrastructure/services/{self.service_id}/commands/{result.command_id}/result",
                    json=asdict(result),
                    timeout=10.0
                )

                return response.status_code == 200

        except Exception as e:
            logger.error(f"Failed to report command result: {e}")
            return False

    # =========================================================================
    # ALERTS & NOTIFICATIONS
    # =========================================================================

    async def send_critical_alert(
        self,
        alert_type: str,
        message: str,
        details: Dict[str, Any],
        requires_action: bool = True
    ) -> bool:
        """
        Send critical alert directly to Orchestrator

        Bypasses EventBus for immediate attention
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.orchestrator_url}/infrastructure/alerts/critical",
                    json={
                        "source": self.service_id,
                        "alert_type": alert_type,
                        "severity": "critical",
                        "message": message,
                        "details": details,
                        "requires_action": requires_action,
                        "timestamp": datetime.now().isoformat()
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    logger.info(f" Critical alert sent: {alert_type}")
                    return True

        except Exception as e:
            logger.error(f"Failed to send critical alert: {e}")

        return False

    async def send_recommendation(
        self,
        recommendation_type: str,
        suggestion: str,
        confidence: float,
        impact: str,
        details: Dict[str, Any]
    ) -> Optional[str]:
        """
        Send optimization recommendation to Orchestrator

        Orchestrator decides whether to apply or escalate

        Returns: recommendation_id if accepted
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.orchestrator_url}/infrastructure/recommendations",
                    json={
                        "source": self.service_id,
                        "recommendation_type": recommendation_type,
                        "suggestion": suggestion,
                        "confidence": confidence,
                        "impact": impact,
                        "details": details,
                        "timestamp": datetime.now().isoformat()
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return data.get("recommendation_id")

        except Exception as e:
            logger.error(f"Failed to send recommendation: {e}")

        return None

    # =========================================================================
    # METRICS PUSH
    # =========================================================================

    async def push_metrics(self, metrics: Dict[str, Any]) -> bool:
        """
        Push aggregated metrics to Orchestrator

        Orchestrator aggregates metrics from all infrastructure services
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.orchestrator_url}/infrastructure/metrics/{self.service_id}",
                    json={
                        "timestamp": datetime.now().isoformat(),
                        "metrics": metrics
                    },
                    timeout=5.0
                )

                return response.status_code == 200

        except Exception as e:
            logger.debug(f"Metrics push failed: {e}")
            return False

    # =========================================================================
    # RESOURCE REQUESTS
    # =========================================================================

    async def request_resource(
        self,
        resource_type: str,
        reason: str,
        details: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Request resource from Orchestrator

        Examples:
        - Request index creation approval
        - Request VACUUM scheduling
        - Request query kill permission
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.orchestrator_url}/infrastructure/resources/request",
                    json={
                        "requester": self.service_id,
                        "resource_type": resource_type,
                        "reason": reason,
                        "details": details,
                        "timestamp": datetime.now().isoformat()
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    return response.json()

        except Exception as e:
            logger.error(f"Resource request failed: {e}")

        return None

    # =========================================================================
    # COORDINATION
    # =========================================================================

    async def coordinate_with_service(
        self,
        target_service: str,
        action: str,
        parameters: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Request Orchestrator to coordinate with another service

        Example: Coordinate with AI Foundation for query analysis
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.orchestrator_url}/infrastructure/coordinate",
                    json={
                        "requester": self.service_id,
                        "target_service": target_service,
                        "action": action,
                        "parameters": parameters,
                        "timestamp": datetime.now().isoformat()
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    return response.json()

        except Exception as e:
            logger.error(f"Coordination failed: {e}")

        return None


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_orchestrator_client: Optional[OrchestratorClient] = None


def get_orchestrator_client() -> OrchestratorClient:
    """Get global Orchestrator client instance"""
    global _orchestrator_client
    if _orchestrator_client is None:
        import os
        _orchestrator_client = OrchestratorClient(
            orchestrator_url=os.getenv("ORCHESTRATOR_URL", "http://localhost:8002")
        )
    return _orchestrator_client


async def initialize_orchestrator_integration():
    """Initialize Orchestrator integration"""
    client = get_orchestrator_client()
    success = await client.register()
    return success


async def shutdown_orchestrator_integration():
    """Shutdown Orchestrator integration"""
    client = get_orchestrator_client()
    await client.deregister()
