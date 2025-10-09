"""
Balancer Service - Main Entry Point

Инициализирует и запускает все балансировщики Phase 2:
- System Balancer (МОЗГ ГЛОБАЛЬНЫЙ)
- Resource Tracker (ГЛАЗА)
- Three-Dimensional Balancer (3D BALANCE)

Версия: 2.4.0 (MVP - Minimum Viable Product)
"""

import asyncio
import sys
import os
import signal
import logging
from pathlib import Path
from typing import Optional

# Add intelligent-core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "intelligent-core"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "infrastructure"))

import structlog
from prometheus_client import start_http_server, Counter, Gauge

# Import EventBus
from infrastructure.eventbus import create_eventbus

# Import balancers
from intelligent_core.ai_foundation.balancer import (
    SystemBalancer,
    ImpactEvidenceTracker,
    PredictiveROIOptimizer,
    ThreeDimensionalBalancer
)

# Logging setup
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

# Prometheus metrics
BALANCER_SERVICE_UP = Gauge('balancer_service_up', 'Balancer service is running')
BALANCER_ERRORS = Counter('balancer_errors_total', 'Total balancer errors', ['component'])
BALANCER_EVENTS_PROCESSED = Counter('balancer_events_processed_total', 'Events processed', ['component'])


class BalancerService:
    """
    Balancer Service - orchestrates all Phase 2 balancers

    Components:
    1. System Balancer - global balancing with reward/penalty
    2. Impact Evidence Tracker - rational dimension
    3. Predictive ROI Optimizer - intuitive + pragmatic dimensions
    4. Three-Dimensional Balancer - balance between all three
    """

    def __init__(self):
        self.logger = logger.bind(service="balancer-service")
        self.eventbus: Optional[any] = None
        self.running = False

        # Balancers
        self.system_balancer: Optional[SystemBalancer] = None
        self.evidence_tracker: Optional[ImpactEvidenceTracker] = None
        self.roi_optimizer: Optional[PredictiveROIOptimizer] = None
        self.balancer_3d: Optional[ThreeDimensionalBalancer] = None

        # Tasks
        self.tasks = []

        self.logger.info("BalancerService initialized")

    async def initialize(self):
        """Initialize all components"""
        self.logger.info("Initializing BalancerService...")

        try:
            # 1. Create EventBus connection
            self.logger.info("Creating EventBus connection...")
            self.eventbus = create_eventbus('redis')
            await self.eventbus.connect()
            self.logger.info("EventBus connected", backend='redis')

            # 2. Initialize Impact Evidence Tracker (RATIONAL)
            self.logger.info("Initializing Impact Evidence Tracker (RATIONAL)...")
            self.evidence_tracker = ImpactEvidenceTracker()
            self.logger.info("Impact Evidence Tracker initialized")

            # 3. Initialize Predictive ROI Optimizer (INTUITIVE + PRAGMATIC)
            self.logger.info("Initializing Predictive ROI Optimizer (INTUITIVE + PRAGMATIC)...")
            self.roi_optimizer = PredictiveROIOptimizer(
                evidence_tracker=self.evidence_tracker
            )
            self.logger.info("Predictive ROI Optimizer initialized")

            # 4. Initialize Three-Dimensional Balancer
            self.logger.info("Initializing Three-Dimensional Balancer...")
            self.balancer_3d = ThreeDimensionalBalancer(
                evidence_tracker=self.evidence_tracker,
                roi_optimizer=self.roi_optimizer
            )
            self.logger.info("Three-Dimensional Balancer initialized")

            # 5. Initialize System Balancer (GLOBAL BRAIN)
            self.logger.info("Initializing System Balancer (GLOBAL BRAIN)...")
            self.system_balancer = SystemBalancer(
                eventbus=self.eventbus,
                balancer_3d=self.balancer_3d
            )
            self.logger.info("System Balancer initialized")

            # 6. Subscribe to EventBus events
            await self._subscribe_to_events()

            self.logger.info("BalancerService initialization complete")
            BALANCER_SERVICE_UP.set(1)

        except Exception as e:
            self.logger.error("Failed to initialize BalancerService", error=str(e), exc_info=True)
            BALANCER_ERRORS.labels(component='initialization').inc()
            raise

    async def _subscribe_to_events(self):
        """Subscribe to EventBus events"""
        self.logger.info("Subscribing to EventBus events...")

        # Subscribe to imbalance events from Survival Instinct
        await self.eventbus.subscribe(
            'platform.bcm.imbalance_detected',
            self._handle_imbalance_event
        )
        self.logger.info("Subscribed to platform.bcm.imbalance_detected")

        # Subscribe to resource events from Resource Tracker
        await self.eventbus.subscribe(
            'platform.resources.snapshot',
            self._handle_resource_snapshot
        )
        self.logger.info("Subscribed to platform.resources.snapshot")

        await self.eventbus.subscribe(
            'platform.resources.deficit',
            self._handle_resource_deficit
        )
        self.logger.info("Subscribed to platform.resources.deficit")

    async def _handle_imbalance_event(self, event: dict):
        """Handle imbalance event from Survival Instinct"""
        try:
            self.logger.info(
                "Received imbalance event",
                module=event.get('source'),
                kpi_name=event['data'].get('kpi_name'),
                level=event['data'].get('level')
            )

            # Record baseline for evidence tracker
            module_name = event.get('source', 'unknown').split('.')[0]
            self.evidence_tracker.record_baseline(
                module_name=module_name,
                health_score=event['data'].get('health_score', 50.0),
                cpu_usage=event['data'].get('cpu_usage', 0.0),
                memory_usage=event['data'].get('memory_usage', 0.0)
            )

            # Let System Balancer handle it
            if self.system_balancer:
                # System Balancer will process this in its monitoring loop
                pass

            BALANCER_EVENTS_PROCESSED.labels(component='imbalance').inc()

        except Exception as e:
            self.logger.error("Error handling imbalance event", error=str(e), exc_info=True)
            BALANCER_ERRORS.labels(component='imbalance_handler').inc()

    async def _handle_resource_snapshot(self, event: dict):
        """Handle resource snapshot from Resource Tracker"""
        try:
            self.logger.debug(
                "Received resource snapshot",
                cpu=event['data'].get('cpu_percent'),
                memory=event['data'].get('memory_percent')
            )

            # Store for System Balancer to use
            # System Balancer will access this via EventBus

            BALANCER_EVENTS_PROCESSED.labels(component='resource_snapshot').inc()

        except Exception as e:
            self.logger.error("Error handling resource snapshot", error=str(e), exc_info=True)
            BALANCER_ERRORS.labels(component='resource_handler').inc()

    async def _handle_resource_deficit(self, event: dict):
        """Handle resource deficit event"""
        try:
            self.logger.warning(
                "Resource deficit detected",
                deficit_type=event['data'].get('deficit_type'),
                severity=event['data'].get('severity')
            )

            # Trigger immediate balancing if critical
            if self.system_balancer and event['data'].get('severity') == 'critical':
                # System Balancer will handle in next cycle
                pass

            BALANCER_EVENTS_PROCESSED.labels(component='resource_deficit').inc()

        except Exception as e:
            self.logger.error("Error handling resource deficit", error=str(e), exc_info=True)
            BALANCER_ERRORS.labels(component='deficit_handler').inc()

    async def start(self):
        """Start the service"""
        self.logger.info("Starting BalancerService...")
        self.running = True

        try:
            # Start System Balancer monitoring loop
            if self.system_balancer:
                task = asyncio.create_task(self.system_balancer.start())
                self.tasks.append(task)
                self.logger.info("System Balancer started")

            self.logger.info("BalancerService started successfully")

            # Keep service running
            while self.running:
                await asyncio.sleep(1)

        except Exception as e:
            self.logger.error("Error in BalancerService", error=str(e), exc_info=True)
            BALANCER_ERRORS.labels(component='service').inc()
            raise

    async def stop(self):
        """Stop the service"""
        self.logger.info("Stopping BalancerService...")
        self.running = False

        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        # Disconnect EventBus
        if self.eventbus:
            await self.eventbus.disconnect()

        BALANCER_SERVICE_UP.set(0)
        self.logger.info("BalancerService stopped")


async def main():
    """Main entry point"""
    # Start Prometheus metrics server
    start_http_server(9091)
    logger.info("Prometheus metrics server started on :9091")

    # Create service
    service = BalancerService()

    # Setup signal handlers
    loop = asyncio.get_event_loop()

    def signal_handler(signum, frame):
        logger.info("Received signal, shutting down...", signal=signum)
        asyncio.create_task(service.stop())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Initialize and start
        await service.initialize()
        await service.start()

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error("Fatal error", error=str(e), exc_info=True)
        sys.exit(1)
    finally:
        await service.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete")
