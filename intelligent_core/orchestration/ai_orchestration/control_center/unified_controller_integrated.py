"""
Unified Controller - Master orchestration controller (Enhanced with Platform Integration)
=========================================================================================

Coordinates all specialized orchestrators with Graceful Choreography:
- Platform Integration (Intelligent EventBus, Saga Engine, Self-Aware, CQRS)
- PlatformOrchestrator (infrastructure)
- AIOrchestrator (intelligence & automation)
- ScenarioOrchestrator (BCM training)

Provides single entry point for entire orchestration system.
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime

# Platform Integration - THE NEW WAY
from infrastructure.platform_integration import init_platform, get_platform, shutdown_platform

# Use absolute imports with platform_orch to avoid circular import with stdlib platform module
import sys
from pathlib import Path

# Add parent directory to path to enable absolute imports
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from platform_orch import PlatformOrchestrator
from ai import AIOrchestrator
from scenario import ScenarioOrchestrator

logger = logging.getLogger(__name__)


class UnifiedController:
    """
    Master orchestration controller with Platform Integration

    Single entry point that coordinates:
    1. Platform Integration (Graceful Choreography)
    2. All specialized orchestrators

    Manages startup sequence, ensures dependencies, provides system status.
    """

    def __init__(self):
        """Initialize all orchestrators"""
        logger.info("Initializing UnifiedController (with Platform Integration)...")

        # Platform Integration (will be initialized in start_all)
        self.platform_integration = None

        # Initialize orchestrators (they will use platform_integration)
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
        Start all orchestrators with Platform Integration

        Startup order:
        0. Platform Integration (Intelligent EventBus, Saga, Self-Aware, CQRS)
        1. Platform Orchestrator (foundation services, infrastructure)
        2. AI & Scenario (parallel - both depend on Platform)

        Returns:
            Startup result with timing and status
        """
        if self.running:
            logger.warning("System already running")
            return {'status': 'already_running'}

        logger.info("=" * 70)
        logger.info("STARTING BCM UNIFIED ORCHESTRATION SYSTEM")
        logger.info("(Enhanced with Graceful Choreography)")
        logger.info("=" * 70)

        start_time = datetime.utcnow()
        self.running = True

        try:
            # Step 0: Initialize Platform Integration
            logger.info("Step 0/3: Initializing Platform Integration...")
            logger.info("  → Intelligent EventBus")
            logger.info("  → Saga Pattern Engine")
            logger.info("  → Self-Aware Services")
            logger.info("  → CQRS Infrastructure")

            # Get database and redis URLs from environment
            database_url = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./orchestration.db')
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

            self.platform_integration = await init_platform(
                database_url=database_url,
                redis_url=redis_url,
                enable_intelligent_routing=True,
                enable_saga_engine=True,
                enable_self_aware=True,
                enable_cqrs=True  # Enable CQRS for orchestration
            )

            platform_status = self.platform_integration.get_status()
            logger.info(f"   Platform Integration ready: {platform_status}")

            # Register orchestration sagas
            await self._register_orchestration_sagas()

            # Step 1: Start Platform Orchestrator (MUST complete first)
            logger.info("\nStep 1/3: Starting Platform Orchestrator...")

            # Pass platform_integration to PlatformOrchestrator
            if hasattr(self.platform, 'set_platform_integration'):
                self.platform.set_platform_integration(self.platform_integration)

            await self.platform.start()
            logger.info("   Platform ready")

            # Step 2: Start AI & Scenario in parallel
            logger.info("\nStep 2/3: Starting AI & Scenario Orchestrators...")

            # Pass platform_integration to orchestrators
            if hasattr(self.ai, 'set_platform_integration'):
                self.ai.set_platform_integration(self.platform_integration)

            if hasattr(self.scenario, 'set_platform_integration'):
                self.scenario.set_platform_integration(self.platform_integration)

            ai_task = asyncio.create_task(self.ai.start())
            scenario_task = asyncio.create_task(self.scenario.start())

            results = await asyncio.gather(ai_task, scenario_task, return_exceptions=True)

            # Check for failures
            ai_status = 'running'
            if isinstance(results[0], Exception):
                logger.error(f"   AI Orchestrator failed: {results[0]}")
                ai_status = 'failed'
            else:
                logger.info("   AI Orchestrator ready")

            scenario_status = 'running'
            if isinstance(results[1], Exception):
                logger.error(f"   Scenario Orchestrator failed: {results[1]}")
                scenario_status = 'failed'
            else:
                logger.info("   Scenario Orchestrator ready")

            # Step 3: Post-startup integration
            logger.info("\nStep 3/3: Finalizing integration...")
            await self._post_startup_integration()
            logger.info("   Integration complete")

            # Mark startup complete
            self.startup_completed = True
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            self.startup_time = elapsed

            logger.info("\n" + "=" * 70)
            logger.info(f" SYSTEM STARTED SUCCESSFULLY in {elapsed:.2f}s")
            logger.info("=" * 70)
            logger.info(" Graceful Choreography Active")
            logger.info(f"    Intelligent EventBus: {self.platform_integration.intelligent_router is not None}")
            logger.info(f"    Saga Engine: {self.platform_integration.saga_orchestrator is not None}")
            logger.info(f"    Self-Aware: Enabled")
            logger.info(f"    CQRS: {self.platform_integration.cqrs_command_handler is not None}")
            logger.info("=" * 70 + "\n")

            return {
                'status': 'started',
                'startup_time_seconds': elapsed,
                'platform_integration': platform_status,
                'orchestrators': {
                    'platform': 'running',
                    'ai': ai_status,
                    'scenario': scenario_status
                },
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f" System startup failed: {e}", exc_info=True)
            self.running = False
            self.startup_completed = False

            # Attempt cleanup
            await self._emergency_shutdown()

            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    async def _register_orchestration_sagas(self):
        """Register orchestration-specific sagas"""
        if not self.platform_integration or not self.platform_integration.saga_orchestrator:
            logger.warning("Saga engine not available, skipping saga registration")
            return

        logger.info("  → Registering orchestration sagas...")

        try:
            # Import saga definitions
            from intelligent_core.orchestration.saga_engine.example_sagas import (
                create_bcm_program_saga,
                create_incident_response_saga
            )

            # Register sagas
            self.platform_integration.saga_orchestrator.register_saga(create_bcm_program_saga())
            self.platform_integration.saga_orchestrator.register_saga(create_incident_response_saga())

            # Get registered count
            if hasattr(self.platform_integration.saga_orchestrator, '_sagas'):
                saga_count = len(self.platform_integration.saga_orchestrator._sagas)
                logger.info(f"   Registered {saga_count} orchestration sagas")

        except ImportError as e:
            logger.warning(f"  ️  Could not import saga definitions: {e}")
        except Exception as e:
            logger.error(f"   Error registering sagas: {e}")

    async def _post_startup_integration(self):
        """Post-startup integration tasks"""
        # Subscribe orchestrators to relevant events via Intelligent EventBus
        if self.platform_integration and self.platform_integration.intelligent_router:
            router = self.platform_integration.intelligent_router

            # Subscribe AI Orchestrator to decision events
            try:
                if hasattr(self.ai, 'handle_event'):
                    await router.register_subscriber(
                        subscriber_id="ai_orchestrator",
                        event_pattern="decision.*",
                        handler=self.ai.handle_event,
                        capabilities={
                            "domains": ["ai", "orchestration", "decision"],
                            "max_concurrent": 20,
                            "avg_processing_time_ms": 100,
                            "sla_ms": 500,
                            "semantic_tags": ["ai", "orchestration", "decision", "automation"]
                        }
                    )
                    logger.info("     AI Orchestrator subscribed to decision events")
            except Exception as e:
                logger.warning(f"    ️  Could not subscribe AI Orchestrator: {e}")

            # Subscribe Scenario Orchestrator to training events
            try:
                if hasattr(self.scenario, 'handle_event'):
                    await router.register_subscriber(
                        subscriber_id="scenario_orchestrator",
                        event_pattern="scenario.*",
                        handler=self.scenario.handle_event,
                        capabilities={
                            "domains": ["scenario", "training", "simulation"],
                            "max_concurrent": 10,
                            "avg_processing_time_ms": 200,
                            "sla_ms": 1000,
                            "semantic_tags": ["scenario", "training", "simulation", "bcm"]
                        }
                    )
                    logger.info("     Scenario Orchestrator subscribed to scenario events")
            except Exception as e:
                logger.warning(f"    ️  Could not subscribe Scenario Orchestrator: {e}")

    async def stop_all(self) -> Dict[str, Any]:
        """
        Stop all orchestrators in reverse order

        Shutdown order:
        1. Scenario & AI (parallel)
        2. Platform (infrastructure)
        3. Platform Integration (Graceful Choreography)

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
            logger.info("Step 1/3: Stopping Scenario & AI Orchestrators...")

            await asyncio.gather(
                self.scenario.stop(),
                self.ai.stop(),
                return_exceptions=True
            )
            logger.info("   AI & Scenario stopped")

            # Step 2: Stop Platform
            logger.info("Step 2/3: Stopping Platform Orchestrator...")
            await self.platform.stop()
            logger.info("   Platform stopped")

            # Step 3: Shutdown Platform Integration
            logger.info("Step 3/3: Shutting down Platform Integration...")
            await shutdown_platform()
            logger.info("   Platform Integration shutdown")

            elapsed = (datetime.utcnow() - stop_time).total_seconds()

            logger.info("=" * 70)
            logger.info(f" SYSTEM STOPPED in {elapsed:.2f}s")
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
                'stop_result': stop_result
            }

        # Wait a bit
        await asyncio.sleep(2)

        # Start
        start_result = await self.start_all()
        if start_result['status'] != 'started':
            return {
                'status': 'restart_failed',
                'error': 'Failed to start system',
                'start_result': start_result
            }

        return {
            'status': 'restarted',
            'stop_result': stop_result,
            'start_result': start_result,
            'timestamp': datetime.utcnow().isoformat()
        }

    async def restart_orchestrator(self, orchestrator_name: str) -> Dict[str, Any]:
        """
        Restart specific orchestrator

        Args:
            orchestrator_name: 'platform', 'ai', or 'scenario'

        Returns:
            Restart result
        """
        orchestrator_map = {
            'platform': self.platform,
            'ai': self.ai,
            'scenario': self.scenario
        }

        orchestrator = orchestrator_map.get(orchestrator_name)
        if not orchestrator:
            return {
                'status': 'error',
                'error': f'Unknown orchestrator: {orchestrator_name}'
            }

        logger.info(f"Restarting {orchestrator_name} orchestrator...")

        try:
            # Stop
            await orchestrator.stop()
            logger.info(f"   {orchestrator_name} stopped")

            # Wait
            await asyncio.sleep(1)

            # Start
            await orchestrator.start()
            logger.info(f"   {orchestrator_name} started")

            return {
                'status': 'restarted',
                'orchestrator': orchestrator_name,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to restart {orchestrator_name}: {e}")
            return {
                'status': 'error',
                'orchestrator': orchestrator_name,
                'error': str(e)
            }

    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status

        Returns:
            Complete system status
        """
        status = {
            'running': self.running,
            'startup_completed': self.startup_completed,
            'startup_time_seconds': self.startup_time,
            'uptime_seconds': (datetime.utcnow() - datetime.fromisoformat(
                datetime.utcnow().isoformat()
            )).total_seconds() if self.startup_completed else 0,
            'timestamp': datetime.utcnow().isoformat()
        }

        # Platform Integration status
        if self.platform_integration:
            status['platform_integration'] = self.platform_integration.get_status()

            # Add intelligent router metrics
            if self.platform_integration.intelligent_router:
                status['intelligent_router_metrics'] = self.platform_integration.intelligent_router.get_metrics()

        # Orchestrator statuses
        status['orchestrators'] = {}

        for name in ['platform', 'ai', 'scenario']:
            orchestrator = getattr(self, name)
            if hasattr(orchestrator, 'get_status'):
                status['orchestrators'][name] = await orchestrator.get_status()
            else:
                status['orchestrators'][name] = {'available': orchestrator is not None}

        return status

    async def get_platform_status(self) -> Dict[str, Any]:
        """Get Platform Orchestrator status"""
        if hasattr(self.platform, 'get_status'):
            return await self.platform.get_status()
        return {'error': 'Platform orchestrator does not support get_status()'}

    async def get_ai_status(self) -> Dict[str, Any]:
        """Get AI Orchestrator status"""
        if hasattr(self.ai, 'get_status'):
            return await self.ai.get_status()
        return {'error': 'AI orchestrator does not support get_status()'}

    async def get_scenario_status(self) -> Dict[str, Any]:
        """Get Scenario Orchestrator status"""
        if hasattr(self.scenario, 'get_status'):
            return await self.scenario.get_status()
        return {'error': 'Scenario orchestrator does not support get_status()'}

    async def _emergency_shutdown(self):
        """Emergency shutdown on failure"""
        logger.warning("Performing emergency shutdown...")

        try:
            # Try to stop orchestrators
            await asyncio.gather(
                self.scenario.stop(),
                self.ai.stop(),
                self.platform.stop(),
                return_exceptions=True
            )

            # Try to shutdown platform integration
            if self.platform_integration:
                await shutdown_platform()

        except Exception as e:
            logger.error(f"Error during emergency shutdown: {e}")

        logger.info("Emergency shutdown complete")
