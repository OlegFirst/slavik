"""
Health Check Daemon для AI Agent Router

Background task для периодической проверки здоровья агентов.
"""

import asyncio
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class HealthCheckDaemon:
    """
    Daemon для автоматических health checks

    Периодически проверяет здоровье всех агентов и обновляет их статус.
    """

    def __init__(
        self,
        router,
        check_interval: int = 30,
        auto_start: bool = False
    ):
        """
        Initialize Health Check Daemon

        Args:
            router: AIAgentRouter instance
            check_interval: Interval between checks in seconds
            auto_start: Start daemon automatically
        """
        self.router = router
        self.check_interval = check_interval
        self.running = False
        self.task: Optional[asyncio.Task] = None
        self.last_check: Optional[datetime] = None
        self.check_count = 0
        self.failed_checks = 0

        if auto_start:
            asyncio.create_task(self.start())

    async def start(self):
        """Start health check daemon"""
        if self.running:
            logger.warning("Health check daemon already running")
            return

        self.running = True
        self.task = asyncio.create_task(self._run())
        logger.info(f" Health check daemon started (interval: {self.check_interval}s)")

    async def stop(self):
        """Stop health check daemon"""
        if not self.running:
            logger.warning("Health check daemon not running")
            return

        self.running = False

        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

        logger.info(" Health check daemon stopped")

    async def _run(self):
        """Main daemon loop"""
        logger.info(f" Health check daemon loop started")

        while self.running:
            try:
                # Perform health check
                await self._perform_check()

                # Wait for next interval
                await asyncio.sleep(self.check_interval)

            except asyncio.CancelledError:
                logger.info("Health check daemon cancelled")
                break

            except Exception as e:
                self.failed_checks += 1
                logger.error(f"Health check failed: {e}")

                # Shorter retry interval on failure
                await asyncio.sleep(min(self.check_interval, 10))

    async def _perform_check(self):
        """Perform single health check"""
        try:
            logger.debug("Performing health check...")

            # Check all agents
            health_results = await self.router.health_check_all_agents()

            # Count healthy/unhealthy
            healthy_count = sum(1 for h in health_results.values() if h.get("healthy"))
            total_count = len(health_results)

            # Update stats
            self.last_check = datetime.now()
            self.check_count += 1

            # Log summary
            if healthy_count == total_count:
                logger.debug(f" All {total_count} agents healthy")
            else:
                unhealthy = [name for name, h in health_results.items() if not h.get("healthy")]
                logger.warning(f"️ Health check: {healthy_count}/{total_count} healthy. Unhealthy: {unhealthy}")

            # Auto-recovery: попытка восстановить unhealthy агентов
            for agent_name, health in health_results.items():
                if not health.get("healthy"):
                    await self._attempt_recovery(agent_name, health)

        except Exception as e:
            logger.error(f"Health check error: {e}")
            raise

    async def _attempt_recovery(self, agent_name: str, health: dict):
        """
        Attempt to recover unhealthy agent

        Args:
            agent_name: Name of unhealthy agent
            health: Health check result
        """
        logger.info(f" Attempting recovery for {agent_name}...")

        # Check if circuit breaker is open
        if self.router.circuit_breaker_manager:
            breaker = await self.router.circuit_breaker_manager.get_breaker(agent_name)
            breaker_stats = breaker.get_stats()

            if breaker_stats["state"] == "OPEN":
                logger.info(f"Circuit breaker for {agent_name} is OPEN, waiting for auto-recovery...")
                return

        # Возможные стратегии recovery:
        # 1. Просто ждем следующей проверки (агент может восстановиться сам)
        # 2. Можно попробовать ping endpoint
        # 3. Можно уведомить админа
        # 4. Можно попробовать restart (если есть оркестратор)

        logger.debug(f"Agent {agent_name} recovery strategy: wait for next health check")

    def get_stats(self) -> dict:
        """Get daemon statistics"""
        return {
            "running": self.running,
            "check_interval": self.check_interval,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "total_checks": self.check_count,
            "failed_checks": self.failed_checks,
            "success_rate": (
                (self.check_count - self.failed_checks) / self.check_count
                if self.check_count > 0 else 0
            )
        }


# Singleton instance
_health_daemon: Optional[HealthCheckDaemon] = None


async def get_health_daemon(router, check_interval: int = 30) -> HealthCheckDaemon:
    """
    Get or create singleton Health Check Daemon

    Args:
        router: AIAgentRouter instance
        check_interval: Check interval in seconds

    Returns:
        HealthCheckDaemon instance
    """
    global _health_daemon

    if _health_daemon is None:
        _health_daemon = HealthCheckDaemon(
            router=router,
            check_interval=check_interval
        )
        await _health_daemon.start()

    return _health_daemon


async def start_health_daemon(router, check_interval: int = 30):
    """
    Convenience function to start health daemon

    Args:
        router: AIAgentRouter instance
        check_interval: Check interval in seconds
    """
    daemon = await get_health_daemon(router, check_interval)
    if not daemon.running:
        await daemon.start()
