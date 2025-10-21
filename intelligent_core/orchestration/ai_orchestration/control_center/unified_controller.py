"""
Unified Controller - Master orchestration controller

Coordinates all specialized orchestrators:
- PlatformOrchestrator (infrastructure)
- AIOrchestrator (intelligence & automation)
- ScenarioOrchestrator (BCM training)

Provides single entry point for entire orchestration system.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from platform_orch import PlatformOrchestrator
from ai import AIOrchestrator
from scenario import ScenarioOrchestrator

logger = logging.getLogger(__name__)


class UnifiedController:
    """
    Master orchestration controller

    Single entry point that coordinates all specialized orchestrators.
    Manages startup sequence, ensures dependencies, provides system status.
    """

    def __init__(self):
        """Initialize all orchestrators"""
        logger.info("Initializing UnifiedController...")

        # Initialize orchestrators
        self.platform = PlatformOrchestrator()
        self.ai = AIOrchestrator()
        self.scenario = ScenarioOrchestrator()

        # Control state
        self.running = False
        self.startup_completed = False
        self.startup_time = None

        logger.info("UnifiedController initialized")

    async def start_all(self) -> Dict[str, Any]:
        """
        Start all orchestrators in correct sequence

        Startup order:
        1. Platform (foundation services, infrastructure)
        2. AI & Scenario (parallel - both depend on Platform)

        Returns:
            Startup result with timing and status
        """
        if self.running:
            logger.warning("System already running")
            return {'status': 'already_running'}

        logger.info("=" * 70)
        logger.info("STARTING BCM UNIFIED ORCHESTRATION SYSTEM")
        logger.info("=" * 70)

        start_time = datetime.utcnow()
        self.running = True

        try:
            # Step 1: Start Platform Orchestrator (MUST complete first)
            logger.info("Step 1/2: Starting Platform Orchestrator...")
            await self.platform.start()
            logger.info(" Platform ready")

            # Step 2: Start AI & Scenario in parallel
            logger.info("Step 2/2: Starting AI & Scenario Orchestrators...")

            ai_task = asyncio.create_task(self.ai.start())
            scenario_task = asyncio.create_task(self.scenario.start())

            results = await asyncio.gather(ai_task, scenario_task, return_exceptions=True)

            # Check for failures
            if isinstance(results[0], Exception):
                logger.error(f"AI Orchestrator failed: {results[0]}")
            else:
                logger.info(" AI Orchestrator ready")

            if isinstance(results[1], Exception):
                logger.error(f"Scenario Orchestrator failed: {results[1]}")
            else:
                logger.info(" Scenario Orchestrator ready")

            # Mark startup complete
            self.startup_completed = True
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            self.startup_time = elapsed

            logger.info("=" * 70)
            logger.info(f"SYSTEM STARTED SUCCESSFULLY in {elapsed:.2f}s")
            logger.info("=" * 70)

            return {
                'status': 'started',
                'startup_time_seconds': elapsed,
                'orchestrators': {
                    'platform': 'running',
                    'ai': 'running' if not isinstance(results[0], Exception) else 'failed',
                    'scenario': 'running' if not isinstance(results[1], Exception) else 'failed'
                },
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"System startup failed: {e}")
            self.running = False
            self.startup_completed = False

            # Attempt cleanup
            await self._emergency_shutdown()

            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    async def stop_all(self) -> Dict[str, Any]:
        """
        Stop all orchestrators in reverse order

        Shutdown order:
        1. Scenario & AI (parallel)
        2. Platform (infrastructure last)

        Returns:
            Shutdown result
        """
        if not self.running:
            logger.warning("System not running")
            return {'status': 'not_running'}

        logger.info("=" * 70)
        logger.info("STOPPING BCM UNIFIED ORCHESTRATION SYSTEM")
        logger.info("=" * 70)

        stop_time = datetime.utcnow()
        self.running = False

        try:
            # Step 1: Stop Scenario & AI in parallel
            logger.info("Step 1/2: Stopping Scenario & AI Orchestrators...")

            await asyncio.gather(
                self.scenario.stop(),
                self.ai.stop(),
                return_exceptions=True
            )
            logger.info(" AI & Scenario stopped")

            # Step 2: Stop Platform
            logger.info("Step 2/2: Stopping Platform Orchestrator...")
            await self.platform.stop()
            logger.info(" Platform stopped")

            elapsed = (datetime.utcnow() - stop_time).total_seconds()

            logger.info("=" * 70)
            logger.info(f"SYSTEM STOPPED in {elapsed:.2f}s")
            logger.info("=" * 70)

            return {
                'status': 'stopped',
                'shutdown_time_seconds': elapsed,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    async def restart_all(self) -> Dict[str, Any]:
        """
        Restart entire system

        Returns:
            Restart result
        """
        logger.info("Restarting system...")

        # Stop
        stop_result = await self.stop_all()
        if stop_result['status'] not in ['stopped', 'not_running']:
            return {
                'status': 'restart_failed',
                'error': 'Failed to stop system',
                'details': stop_result
            }

        # Wait a moment
        await asyncio.sleep(2)

        # Start
        start_result = await self.start_all()

        return {
            'status': 'restarted' if start_result['status'] == 'started' else 'restart_failed',
            'stop_result': stop_result,
            'start_result': start_result,
            'timestamp': datetime.utcnow().isoformat()
        }

    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get overall system status

        Returns:
            Comprehensive status from all orchestrators
        """
        # Get status from each orchestrator
        platform_status = await self.platform.get_status()
        ai_status = await self.ai.get_status()
        scenario_status = await self.scenario.get_status()

        return {
            'system': {
                'running': self.running,
                'startup_completed': self.startup_completed,
                'startup_time_seconds': self.startup_time,
                'uptime_seconds': (datetime.utcnow() - datetime.fromtimestamp(self.startup_time)).total_seconds() if self.startup_time else 0
            },
            'orchestrators': {
                'platform': platform_status,
                'ai': ai_status,
                'scenario': scenario_status
            },
            'health': {
                'platform': 'healthy' if platform_status.get('running') else 'unhealthy',
                'ai': 'healthy' if ai_status.get('running') else 'unhealthy',
                'scenario': 'healthy' if scenario_status.get('running') else 'unhealthy',
                'overall': 'healthy' if all([
                    platform_status.get('running'),
                    ai_status.get('running'),
                    scenario_status.get('running')
                ]) else 'degraded'
            },
            'timestamp': datetime.utcnow().isoformat()
        }

    async def get_platform_status(self) -> Dict[str, Any]:
        """Get Platform Orchestrator status"""
        return await self.platform.get_status()

    async def get_ai_status(self) -> Dict[str, Any]:
        """Get AI Orchestrator status"""
        return await self.ai.get_status()

    async def get_scenario_status(self) -> Dict[str, Any]:
        """Get Scenario Orchestrator status"""
        return await self.scenario.get_status()

    async def restart_orchestrator(self, orchestrator: str) -> Dict[str, Any]:
        """
        Restart specific orchestrator

        Args:
            orchestrator: One of 'platform', 'ai', 'scenario'

        Returns:
            Restart result
        """
        if orchestrator == 'platform':
            logger.info("Restarting Platform Orchestrator...")
            await self.platform.stop()
            await asyncio.sleep(1)
            await self.platform.start()
            return {'status': 'restarted', 'orchestrator': 'platform'}

        elif orchestrator == 'ai':
            logger.info("Restarting AI Orchestrator...")
            await self.ai.stop()
            await asyncio.sleep(1)
            await self.ai.start()
            return {'status': 'restarted', 'orchestrator': 'ai'}

        elif orchestrator == 'scenario':
            logger.info("Restarting Scenario Orchestrator...")
            await self.scenario.stop()
            await asyncio.sleep(1)
            await self.scenario.start()
            return {'status': 'restarted', 'orchestrator': 'scenario'}

        else:
            return {
                'status': 'error',
                'error': f'Unknown orchestrator: {orchestrator}',
                'valid_options': ['platform', 'ai', 'scenario']
            }

    async def _emergency_shutdown(self) -> None:
        """Emergency shutdown on startup failure"""
        logger.warning("Performing emergency shutdown...")

        try:
            await asyncio.gather(
                self.scenario.stop(),
                self.ai.stop(),
                self.platform.stop(),
                return_exceptions=True
            )
        except Exception as e:
            logger.error(f"Error during emergency shutdown: {e}")

    def get_orchestrator(self, name: str) -> Optional[Any]:
        """
        Get orchestrator instance by name

        Args:
            name: Orchestrator name ('platform', 'ai', 'scenario')

        Returns:
            Orchestrator instance or None
        """
        orchestrators = {
            'platform': self.platform,
            'ai': self.ai,
            'scenario': self.scenario
        }

        return orchestrators.get(name)