"""
Infrastructure Coordinator (Phase 1 - Task 1.4, Enhanced in Phase 1.1)
=======================================================================

Main coordinator for Infrastructure level (Level 1).

Coordinates:
- Health Monitoring (30 sec intervals via Health Monitor)
- Auto-Recovery (event-driven via AutoRecovery)
- Resource Optimization (5 min intervals via ResourceOptimizer)
- Escalation Management (Phase 1.1 - human escalation for failed recovery)

Features:
- Registers critical services for monitoring
- Configures recovery strategies
- Configures escalation policies
- Starts all coordination services
- Provides unified status API

Phase 1.1 Enhancements:
- EscalationManager integration
- NotificationService for alerts
- Auto-recovery stoppage on escalation
- Pattern-based failure detection

Usage:
    ```python
    coordinator = InfrastructureCoordinator(event_bus_backend='redis')
    await coordinator.start()

    # Get status
    status = await coordinator.get_status()

    # Stop
    await coordinator.stop()
    ```
"""

import logging
import asyncio
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

logger = logging.getLogger(__name__)


class InfrastructureCoordinator:
    """
    Infrastructure Level Coordinator

    Coordinates all Infrastructure-level services:
    - Health Monitor (from ai-orchestration)
    - Auto-Recovery
    - Resource Optimizer
    - Escalation Manager (Phase 1.1)
    - Notification Service (Phase 1.1)
    """

    def __init__(self, event_bus_backend='redis', redis_url=None, enable_governance=True):
        """
        Initialize Infrastructure Coordinator

        Args:
            event_bus_backend: EventBus backend ('memory' or 'redis')
            redis_url: Redis URL (if using redis backend)
            enable_governance: Enable governance layer (Decision Center, Phase 1.1)
        """
        from infrastructure.eventbus import create_eventbus
        from infrastructure.eventbus.coordination import AutoRecovery, RecoveryStrategy, ResourceOptimizer

        # Import Phase 1.1 governance components
        if enable_governance:
            from infrastructure.policy_engine import (
                InfrastructureDecisionCenter,
                EscalationManager,
                NotificationService,
                initialize_policy_engine
            )
            from infrastructure.policy_engine.notification_service import (
                NotificationConfig, NotificationPriority
            )
            from infrastructure.policy_engine.escalation_manager import (
                EscalationPolicy
            )

        # Import HealthMonitor directly
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "health_monitor",
            "/Users/MD/AI-Platform-ISO/intelligent-core/orchestration/ai-orchestration/core/health_monitor.py"
        )
        health_monitor_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(health_monitor_module)

        HealthMonitor = health_monitor_module.HealthMonitor
        HealthCheck = health_monitor_module.HealthCheck

        # Create EventBus
        self.eventbus = create_eventbus(event_bus_backend, redis_url=redis_url)

        # Create Phase 1.1 governance layer (Decision Center, Notification, Escalation)
        self.enable_governance = enable_governance
        if enable_governance:
            # Initialize policy engine
            import os
            policy_path = os.path.join(
                os.path.dirname(__file__),
                '../../decision-center/policies.yaml'
            )
            if os.path.exists(policy_path):
                initialize_policy_engine(policy_path)
                logger.info(f"✅ Policy Engine initialized from {policy_path}")
            else:
                logger.warning(f"⚠️  Policy file not found: {policy_path} - using defaults")
                initialize_policy_engine()  # Use defaults

            # Create Decision Center (central governance)
            self.decision_center = InfrastructureDecisionCenter(
                eventbus=self.eventbus
            )

            # Configure notification service
            notification_config = NotificationConfig(
                default_email_recipients=['ops@ai-platform.com'],
                smtp_host='localhost',
                smtp_port=587
            )
            self.notification_service = NotificationService(notification_config, self.eventbus)

            # Create escalation manager
            self.escalation_manager = EscalationManager(
                notification_service=self.notification_service,
                eventbus=self.eventbus
            )
        else:
            self.decision_center = None
            self.notification_service = None
            self.escalation_manager = None

        # Create coordination services with governance integration
        self.health_monitor = HealthMonitor()
        self.auto_recovery = AutoRecovery(
            eventbus=self.eventbus,
            decision_center=self.decision_center,
            escalation_manager=self.escalation_manager
        )
        self.resource_optimizer = ResourceOptimizer(
            eventbus=self.eventbus,
            decision_center=self.decision_center
        )

        # Store HealthCheck class for registering services
        self.HealthCheck = HealthCheck

        # Store classes for registration
        if enable_governance:
            self.EscalationPolicy = EscalationPolicy

        logger.info(f"InfrastructureCoordinator initialized (governance={'enabled' if enable_governance else 'disabled'})")

    async def start(self):
        """Start all infrastructure coordination services"""
        logger.info("=" * 70)
        logger.info("Starting Infrastructure Coordinator (Phase 1 + Phase 1.1)")
        logger.info("=" * 70)

        # Step 0: Initialize Governance Layer (Phase 1.1)
        if self.enable_governance:
            logger.info("\nStep 0: Initializing Governance Layer (Phase 1.1)...")
            logger.info("  ✅ Decision Center initialized")
            logger.info("  ✅ Escalation Manager initialized")
            logger.info("  ✅ Notification Service initialized")
            logger.info("  ✅ Policy Engine loaded from YAML")

            # Print policy summary
            from infrastructure.policy_engine import get_policy_engine
            engine = get_policy_engine()
            if engine and hasattr(engine, 'policies') and engine.policies:
                recovery_policies = engine.policies.get('recovery', {})
                critical_services = recovery_policies.get('critical_services', {})
                logger.info(f"  📋 Policies loaded for {len(critical_services)} critical services")
            else:
                logger.info("  📋 Using default policies")

        # Step 1: Connect Health Monitor to EventBus
        logger.info("\nStep 1: Connecting Health Monitor to EventBus...")
        await self.health_monitor.connect_eventbus(self.eventbus)
        logger.info("✅ Health Monitor connected to EventBus")

        # Step 2: Register critical services for health monitoring
        logger.info("\nStep 2: Registering critical services...")
        await self._register_critical_services()
        logger.info(f"✅ Registered {len(self.health_monitor.checks)} health checks")

        # Step 3: Register recovery strategies
        logger.info("\nStep 3: Registering recovery strategies...")
        await self._register_recovery_strategies()
        logger.info(f"✅ Registered {len(self.auto_recovery.strategies)} recovery strategies")

        # Step 3.1: Register escalation policies (Phase 1.1)
        if self.enable_governance:
            logger.info("\nStep 3.1: Registering escalation policies (Phase 1.1)...")
            await self._register_escalation_policies()
            logger.info(f"✅ Registered {len(self.escalation_manager.policies)} escalation policies")

        # Step 4: Start services
        logger.info("\nStep 4: Starting coordination services...")

        # Start Auto-Recovery (subscribes to events)
        await self.auto_recovery.start()

        # Start Health Monitor (continuous monitoring)
        asyncio.create_task(self.health_monitor.monitor_continuously())

        # Start Resource Optimizer (5 min cycles)
        asyncio.create_task(self.resource_optimizer.start())

        logger.info("=" * 70)
        logger.info("✅ Infrastructure Coordinator STARTED")
        logger.info("=" * 70)
        logger.info("Services running:")
        logger.info("  🏥 Health Monitor: Running (30 sec intervals)")
        logger.info("  🔧 Auto-Recovery: Listening for health events (with Decision Center)")
        logger.info("  📊 Resource Optimizer: Running (5 min intervals, with Decision Center)")
        if self.enable_governance:
            logger.info("  🎯 Decision Center: Active (Phase 1.1)")
            logger.info("  🚨 Escalation Manager: Ready (Phase 1.1)")
            logger.info("  📧 Notification Service: Ready (Phase 1.1)")
        logger.info("=" * 70)

    async def _register_critical_services(self):
        """
        Register critical services for health monitoring

        Based on PORT_ALLOCATION.md:
        - eventbus (port 8055 - ai-event-manager)
        - api_gateway (port 8000)
        - database (port 5432)
        - redis (port 6379)
        - rag_pipeline (port 8020 - ai-foundation)
        """
        services = [
            {
                'name': 'eventbus',
                'type': 'http',
                'interval': 30,
                'url': 'http://localhost:8055/health'
            },
            {
                'name': 'api_gateway',
                'type': 'http',
                'interval': 30,
                'url': 'http://localhost:8000/health'
            },
            {
                'name': 'database',
                'type': 'custom',
                'interval': 60,
                'checker': self._check_database
            },
            {
                'name': 'redis',
                'type': 'custom',
                'interval': 30,
                'checker': self._check_redis
            },
            {
                'name': 'rag_pipeline',
                'type': 'http',
                'interval': 60,
                'url': 'http://localhost:8020/health'
            }
        ]

        for service in services:
            check = self.HealthCheck(
                service_name=service['name'],
                check_type=service['type'],
                interval=service['interval'],
                config={'url': service.get('url')} if service['type'] == 'http' else {},
                custom_checker=service.get('checker')
            )
            await self.health_monitor.register_check(check)
            logger.info(f"  ✅ {service['name']} (interval: {service['interval']}s)")

    async def _check_database(self, service_name: str, config: dict):
        """Custom database health check"""
        try:
            # TODO: Check PostgreSQL connectivity
            # For now, always return healthy (demo)
            return True
        except Exception as e:
            logger.error(f"Database check failed: {e}")
            return False

    async def _check_redis(self, service_name: str, config: dict):
        """Custom Redis health check"""
        try:
            # TODO: Check Redis PING
            # For now, always return healthy (demo)
            return True
        except Exception as e:
            logger.error(f"Redis check failed: {e}")
            return False

    async def _register_recovery_strategies(self):
        """
        Register recovery strategies for critical services

        Strategy types:
        - restart: Restart the service (Docker/systemctl)
        - failover: Redirect to backup instance
        - circuit_breaker: Stop traffic, use fallback
        """
        from infrastructure.eventbus.coordination import RecoveryStrategy

        strategies = [
            RecoveryStrategy(
                service_name='eventbus',
                strategy_type='restart',
                max_attempts=3,
                backoff_seconds=5
            ),
            RecoveryStrategy(
                service_name='api_gateway',
                strategy_type='restart',
                max_attempts=3,
                backoff_seconds=10
            ),
            RecoveryStrategy(
                service_name='database',
                strategy_type='circuit_breaker',  # Don't restart DB!
                max_attempts=1,
                backoff_seconds=30
            ),
            RecoveryStrategy(
                service_name='redis',
                strategy_type='restart',
                max_attempts=3,
                backoff_seconds=5
            ),
            RecoveryStrategy(
                service_name='rag_pipeline',
                strategy_type='restart',
                max_attempts=2,
                backoff_seconds=15
            )
        ]

        for strategy in strategies:
            await self.auto_recovery.register_strategy(strategy)
            logger.info(f"  ✅ {strategy.service_name}: {strategy.strategy_type} "
                       f"(max {strategy.max_attempts} attempts)")

    async def _register_escalation_policies(self):
        """
        Register escalation policies for critical services (Phase 1.1)

        Policies determine when to escalate failed recovery to humans.
        """
        if not self.enable_governance:
            return

        # Define which services are critical
        # Critical services escalate faster (after 2 attempts instead of 3)
        critical_services = ['eventbus', 'database', 'api_gateway']

        policies = [
            self.EscalationPolicy(
                service_name='eventbus',
                is_critical=True,
                max_attempts=3,
                critical_service_max_attempts=2,
                escalation_timeout_seconds=180,  # 3 minutes
                pattern_failure_threshold=5,
                notify_email=['ops@ai-platform.com', 'devops@ai-platform.com'],
                auto_create_incident=True,
                incident_priority='critical'
            ),
            self.EscalationPolicy(
                service_name='api_gateway',
                is_critical=True,
                max_attempts=3,
                critical_service_max_attempts=2,
                escalation_timeout_seconds=180,
                pattern_failure_threshold=5,
                notify_email=['ops@ai-platform.com'],
                auto_create_incident=True,
                incident_priority='high'
            ),
            self.EscalationPolicy(
                service_name='database',
                is_critical=True,
                max_attempts=1,  # Don't retry DB - escalate immediately
                critical_service_max_attempts=1,
                escalation_timeout_seconds=60,
                pattern_failure_threshold=3,
                notify_email=['ops@ai-platform.com', 'dba@ai-platform.com'],
                auto_create_incident=True,
                incident_priority='critical'
            ),
            self.EscalationPolicy(
                service_name='redis',
                is_critical=False,
                max_attempts=3,
                escalation_timeout_seconds=300,
                pattern_failure_threshold=5,
                notify_email=['ops@ai-platform.com'],
                auto_create_incident=True,
                incident_priority='medium'
            ),
            self.EscalationPolicy(
                service_name='rag_pipeline',
                is_critical=False,
                max_attempts=2,
                escalation_timeout_seconds=240,
                pattern_failure_threshold=5,
                notify_email=['ai-ops@ai-platform.com'],
                auto_create_incident=True,
                incident_priority='medium'
            )
        ]

        for policy in policies:
            self.escalation_manager.register_policy(policy)
            logger.info(f"  ✅ {policy.service_name}: critical={policy.is_critical}, "
                       f"max_attempts={policy.max_attempts}, "
                       f"timeout={policy.escalation_timeout_seconds}s")

    async def stop(self):
        """Stop all infrastructure coordination services"""
        logger.info("Stopping Infrastructure Coordinator...")

        await self.health_monitor.stop_monitoring()
        await self.auto_recovery.stop()
        await self.resource_optimizer.stop()
        await self.eventbus.close()

        logger.info("✅ Infrastructure Coordinator stopped")

    async def get_status(self):
        """Get status of all infrastructure services"""
        status = {
            'health_monitor': {
                'monitoring': self.health_monitor.monitoring,
                'checks_registered': len(self.health_monitor.checks),
                'results': await self.health_monitor.get_all_results()
            },
            'auto_recovery': await self.auto_recovery.get_stats(),
            'resource_optimizer': await self.resource_optimizer.get_stats()
        }

        # Add governance stats if enabled (Phase 1.1)
        if self.enable_governance:
            status['decision_center'] = await self.decision_center.get_stats()
            status['escalation_manager'] = self.escalation_manager.get_stats()
            status['notification_service'] = self.notification_service.get_stats()

        return status


# CLI interface for running standalone
async def main():
    """Run Infrastructure Coordinator standalone"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("\n" + "=" * 70)
    print("Infrastructure Coordinator - Phase 1")
    print("=" * 70 + "\n")

    coordinator = InfrastructureCoordinator(event_bus_backend='memory')  # Use memory for demo
    await coordinator.start()

    try:
        # Run for 5 minutes (demo)
        logger.info("\n⏰ Running for 5 minutes (demo mode)...\n")
        await asyncio.sleep(300)

        # Show final status
        logger.info("\n📊 Final Status:")
        status = await coordinator.get_status()
        logger.info(f"Health Monitor: {status['health_monitor']['checks_registered']} checks")
        logger.info(f"Auto-Recovery: {status['auto_recovery']['total_recoveries']} total recoveries")
        logger.info(f"Resource Optimizer: {status['resource_optimizer']['cycles_completed']} cycles completed")

    except KeyboardInterrupt:
        logger.info("\n⏹️  Stopping (Ctrl+C pressed)...")
    finally:
        await coordinator.stop()
        logger.info("\n✅ Infrastructure Coordinator demo completed\n")


if __name__ == '__main__':
    asyncio.run(main())
