"""
Temporal Workflows для AI Agent Router

Автоматизация операций:
- Health monitoring
- Circuit breaker recovery
- Service discovery sync
- Metrics export
"""

import asyncio
import logging
from datetime import timedelta
from typing import Optional, Dict, Any

from temporalio import workflow, activity
from temporalio.common import RetryPolicy

logger = logging.getLogger(__name__)


# ============================================================================
# Activities (Действия)
# ============================================================================

@activity.defn
async def check_all_agents(router_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Activity: Проверить здоровье всех агентов

    Args:
        router_config: Конфигурация router для инициализации

    Returns:
        Health status всех агентов
    """
    try:
        # Import router
        from router import AIAgentRouter

        # Initialize router
        router = AIAgentRouter(**router_config)

        # Check health
        health = await router.health_check_all_agents()

        # Calculate stats
        healthy_count = sum(1 for h in health.values() if h.get("healthy"))
        total_count = len(health)

        logger.info(f"Health check: {healthy_count}/{total_count} agents healthy")

        return {
            "healthy_count": healthy_count,
            "total_count": total_count,
            "agents": health
        }

    except Exception as e:
        logger.error(f"Health check activity failed: {e}")
        raise


@activity.defn
async def check_agent_health(router_config: Dict, agent_name: str) -> bool:
    """
    Activity: Проверить здоровье конкретного агента

    Args:
        router_config: Router configuration
        agent_name: Name of agent to check

    Returns:
        True if agent is healthy
    """
    try:
        from router import AIAgentRouter

        router = AIAgentRouter(**router_config)
        health = await router.health_check_all_agents()

        return health.get(agent_name, {}).get("healthy", False)

    except Exception as e:
        logger.error(f"Failed to check {agent_name} health: {e}")
        return False


@activity.defn
async def reset_circuit_breaker(router_config: Dict, agent_name: str) -> bool:
    """
    Activity: Reset circuit breaker для агента

    Args:
        router_config: Router configuration
        agent_name: Agent name

    Returns:
        True if reset successfully
    """
    try:
        from router import AIAgentRouter

        router = AIAgentRouter(**router_config)
        await router.reset_circuit_breaker(agent_name)

        logger.info(f"Circuit breaker reset for {agent_name}")
        return True

    except Exception as e:
        logger.error(f"Failed to reset circuit breaker for {agent_name}: {e}")
        return False


@activity.defn
async def sync_with_service_registry(router_config: Dict, registry_config: Dict) -> Dict:
    """
    Activity: Синхронизация с Service Registry

    Args:
        router_config: Router configuration
        registry_config: Service Registry configuration

    Returns:
        Sync results
    """
    try:
        from router import AIAgentRouter
        import sys
        from pathlib import Path

        # Import service registry
        registry_path = Path("/Users/MD/AI-Platform-ISO/infrastructure/runtime/service-discovery")
        sys.path.insert(0, str(registry_path))
        from service_registry import ServiceRegistry

        # Initialize
        router = AIAgentRouter(**router_config)
        registry = ServiceRegistry()

        # Sync
        await router.sync_with_service_registry(registry)

        logger.info(f"Synced with service registry: {len(router.agents)} agents")

        return {
            "success": True,
            "total_agents": len(router.agents),
            "agent_names": list(router.agents.keys())
        }

    except Exception as e:
        logger.error(f"Service discovery sync failed: {e}")
        return {"success": False, "error": str(e)}


@activity.defn
async def export_metrics(router_config: Dict) -> Dict:
    """
    Activity: Экспорт метрик

    Args:
        router_config: Router configuration

    Returns:
        Metrics export result
    """
    try:
        from router import AIAgentRouter

        router = AIAgentRouter(**router_config)
        analytics = router.get_agent_analytics()

        logger.info(f"Metrics exported: {len(analytics['agents'])} agents")

        return {
            "success": True,
            "agents_count": len(analytics["agents"]),
            "recent_requests": analytics["recent_requests"]
        }

    except Exception as e:
        logger.error(f"Metrics export failed: {e}")
        return {"success": False, "error": str(e)}


@activity.defn
async def send_alert(message: str, severity: str = "warning") -> bool:
    """
    Activity: Отправить alert

    Args:
        message: Alert message
        severity: Severity level (info, warning, error, critical)

    Returns:
        True if sent successfully
    """
    try:
        # TODO: Интеграция с notification service
        logger.warning(f"ALERT [{severity.upper()}]: {message}")
        return True

    except Exception as e:
        logger.error(f"Failed to send alert: {e}")
        return False


# ============================================================================
# Workflows
# ============================================================================

@workflow.defn
class AgentHealthMonitoringWorkflow:
    """
    Долгосрочный workflow для мониторинга здоровья агентов

    Что делает:
    - Каждые 30 секунд проверяет всех агентов
    - При critical problems отправляет alerts
    - Логирует статистику
    """

    @workflow.run
    async def run(
        self,
        router_config: Dict[str, Any],
        check_interval: int = 30,
        alert_threshold: float = 0.5  # Alert if < 50% agents healthy
    ) -> None:
        """
        Run health monitoring workflow

        Args:
            router_config: Router configuration
            check_interval: Check interval in seconds
            alert_threshold: Alert if healthy ratio < threshold
        """
        workflow.logger.info(f"Starting health monitoring workflow (interval: {check_interval}s)")

        check_count = 0

        while True:
            try:
                # Health check
                health_result = await workflow.execute_activity(
                    check_all_agents,
                    router_config,
                    start_to_close_timeout=timedelta(seconds=60),
                    retry_policy=RetryPolicy(
                        initial_interval=timedelta(seconds=1),
                        maximum_interval=timedelta(seconds=10),
                        maximum_attempts=3
                    )
                )

                check_count += 1

                # Calculate health ratio
                healthy_ratio = (
                    health_result["healthy_count"] / health_result["total_count"]
                    if health_result["total_count"] > 0 else 0
                )

                workflow.logger.info(
                    f"Health check #{check_count}: "
                    f"{health_result['healthy_count']}/{health_result['total_count']} "
                    f"({healthy_ratio:.1%})"
                )

                # Alert if below threshold
                if healthy_ratio < alert_threshold:
                    await workflow.execute_activity(
                        send_alert,
                        f"Agent health below threshold: {healthy_ratio:.1%} "
                        f"({health_result['healthy_count']}/{health_result['total_count']})",
                        "critical",
                        start_to_close_timeout=timedelta(seconds=10)
                    )

                # Sleep until next check
                await asyncio.sleep(check_interval)

            except Exception as e:
                workflow.logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(min(check_interval, 10))  # Shorter retry


@workflow.defn
class CircuitBreakerRecoveryWorkflow:
    """
    Автоматический recovery circuit breaker

    Что делает:
    - Мониторит OPEN circuit breakers
    - Периодически проверяет агента
    - При восстановлении → reset circuit breaker
    """

    @workflow.run
    async def run(
        self,
        router_config: Dict,
        agent_name: str,
        max_attempts: int = 20,
        initial_backoff: int = 30
    ) -> Dict[str, Any]:
        """
        Run circuit breaker recovery workflow

        Args:
            router_config: Router configuration
            agent_name: Agent to recover
            max_attempts: Maximum recovery attempts
            initial_backoff: Initial backoff in seconds

        Returns:
            Recovery result
        """
        workflow.logger.info(f"Starting circuit breaker recovery for {agent_name}")

        backoff = initial_backoff

        for attempt in range(1, max_attempts + 1):
            workflow.logger.info(
                f"Recovery attempt {attempt}/{max_attempts} for {agent_name} "
                f"(backoff: {backoff}s)"
            )

            # Check if agent recovered
            is_healthy = await workflow.execute_activity(
                check_agent_health,
                router_config,
                agent_name,
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RetryPolicy(maximum_attempts=2)
            )

            if is_healthy:
                # Agent recovered! Reset circuit breaker
                workflow.logger.info(f"Agent {agent_name} recovered! Resetting circuit breaker...")

                reset_success = await workflow.execute_activity(
                    reset_circuit_breaker,
                    router_config,
                    agent_name,
                    start_to_close_timeout=timedelta(seconds=10)
                )

                if reset_success:
                    workflow.logger.info(f" Circuit breaker reset for {agent_name}")
                    return {
                        "success": True,
                        "attempts": attempt,
                        "message": f"Recovered after {attempt} attempts"
                    }

            # Exponential backoff (max 300s)
            backoff = min(backoff * 2, 300)
            await asyncio.sleep(backoff)

        # Max attempts reached
        workflow.logger.warning(f" Max recovery attempts reached for {agent_name}")

        # Send alert
        await workflow.execute_activity(
            send_alert,
            f"Failed to recover agent {agent_name} after {max_attempts} attempts",
            "critical",
            start_to_close_timeout=timedelta(seconds=10)
        )

        return {
            "success": False,
            "attempts": max_attempts,
            "message": "Max attempts reached"
        }


@workflow.defn
class ServiceDiscoverySyncWorkflow:
    """
    Периодическая синхронизация с Service Registry

    Что делает:
    - Каждые 5 минут синхронизируется с registry
    - Обнаруживает новые агенты
    - Удаляет отключенные агенты
    """

    @workflow.run
    async def run(
        self,
        router_config: Dict,
        registry_config: Dict,
        sync_interval: int = 300  # 5 minutes
    ) -> None:
        """
        Run service discovery sync workflow

        Args:
            router_config: Router configuration
            registry_config: Service Registry configuration
            sync_interval: Sync interval in seconds
        """
        workflow.logger.info(f"Starting service discovery sync (interval: {sync_interval}s)")

        sync_count = 0

        while True:
            try:
                # Sync with registry
                result = await workflow.execute_activity(
                    sync_with_service_registry,
                    router_config,
                    registry_config,
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=RetryPolicy(
                        initial_interval=timedelta(seconds=5),
                        maximum_attempts=3
                    )
                )

                sync_count += 1

                if result["success"]:
                    workflow.logger.info(
                        f"Sync #{sync_count} complete: "
                        f"{result['total_agents']} agents registered"
                    )
                else:
                    workflow.logger.error(f"Sync #{sync_count} failed: {result.get('error')}")

                # Sleep
                await asyncio.sleep(sync_interval)

            except Exception as e:
                workflow.logger.error(f"Service discovery sync error: {e}")
                await asyncio.sleep(min(sync_interval, 60))


@workflow.defn
class MetricsExportWorkflow:
    """
    Периодический экспорт метрик

    Что делает:
    - Каждую минуту экспортирует метрики
    - Aggregates statistics
    - Push to Prometheus Pushgateway (опционально)
    """

    @workflow.run
    async def run(
        self,
        router_config: Dict,
        export_interval: int = 60  # 1 minute
    ) -> None:
        """
        Run metrics export workflow

        Args:
            router_config: Router configuration
            export_interval: Export interval in seconds
        """
        workflow.logger.info(f"Starting metrics export (interval: {export_interval}s)")

        export_count = 0

        while True:
            try:
                # Export metrics
                result = await workflow.execute_activity(
                    export_metrics,
                    router_config,
                    start_to_close_timeout=timedelta(seconds=10),
                    retry_policy=RetryPolicy(maximum_attempts=2)
                )

                export_count += 1

                if result["success"]:
                    workflow.logger.debug(
                        f"Metrics export #{export_count}: "
                        f"{result['agents_count']} agents, "
                        f"{result['recent_requests']} recent requests"
                    )
                else:
                    workflow.logger.error(f"Metrics export #{export_count} failed")

                # Sleep
                await asyncio.sleep(export_interval)

            except Exception as e:
                workflow.logger.error(f"Metrics export error: {e}")
                await asyncio.sleep(min(export_interval, 30))


# ============================================================================
# Convenience Functions
# ============================================================================

async def start_all_workflows(
    temporal_client,
    router_config: Dict,
    registry_config: Optional[Dict] = None
):
    """
    Start all agent router workflows

    Args:
        temporal_client: Temporal client
        router_config: Router configuration
        registry_config: Service Registry configuration (optional)
    """
    # 1. Health monitoring
    await temporal_client.start_workflow(
        AgentHealthMonitoringWorkflow.run,
        router_config,
        id="agent-router-health-monitoring",
        task_queue="agent-router-workflows"
    )
    logger.info(" Started AgentHealthMonitoringWorkflow")

    # 2. Service discovery sync (if registry provided)
    if registry_config:
        await temporal_client.start_workflow(
            ServiceDiscoverySyncWorkflow.run,
            router_config,
            registry_config,
            id="agent-router-service-discovery",
            task_queue="agent-router-workflows"
        )
        logger.info(" Started ServiceDiscoverySyncWorkflow")

    # 3. Metrics export
    await temporal_client.start_workflow(
        MetricsExportWorkflow.run,
        router_config,
        id="agent-router-metrics-export",
        task_queue="agent-router-workflows"
    )
    logger.info(" Started MetricsExportWorkflow")

    logger.info(" All agent router workflows started!")
