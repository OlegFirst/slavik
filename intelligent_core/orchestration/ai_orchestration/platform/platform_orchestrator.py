"""
Platform Orchestrator - Main platform infrastructure orchestrator

Manages:
- Service lifecycle (start/stop/restart)
- Dependency-based startup
- Health monitoring
- Platform-wide events
- Database initialization

Source: Consolidated from /services/platform-orchestrator/main.py
"""

import asyncio
import logging
from typing import Dict, Optional, List, Any
from datetime import datetime

from core import BaseOrchestrator
from .service_groups import ServiceGroup, SERVICE_GROUPS, get_startup_order, get_parallel_groups

logger = logging.getLogger(__name__)


class PlatformOrchestrator(BaseOrchestrator):
    """
    Platform infrastructure orchestrator

    Responsibilities:
    - Start/stop all platform services in correct order
    - Monitor service health continuously
    - Handle service failures and auto-restart
    - Publish platform lifecycle events
    - Track platform status in database
    """

    def __init__(self):
        super().__init__()
        self.redis_client = None
        self.pg_pool = None
        self.groups = SERVICE_GROUPS.copy()
        self.startup_completed = False
        self.monitoring_task = None

        logger.info("PlatformOrchestrator initialized")

    async def connect_services(self) -> None:
        """
        Connect to Redis and PostgreSQL

        Required for:
        - EventBus (Redis)
        - Platform status tracking (PostgreSQL)
        """
        logger.info("Connecting to platform services...")

        # Connect Redis (via event_coordinator)
        try:
            import redis.asyncio as redis
            redis_url = "redis://redis:6379"  # TODO: from config
            self.redis_client = await redis.from_url(redis_url)

            # Connect event coordinator
            await self.event_coordinator.connect(
                redis_client=self.redis_client,
                eventbus_url="http://eventbus:8001"
            )

            # Connect service registry to Redis
            await self.service_registry.connect_redis(self.redis_client)

            logger.info("Connected to Redis")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            logger.info("Will operate without Redis persistence")

        # Connect PostgreSQL
        try:
            import asyncpg
            pg_url = "postgresql://bcm_user:bcm_password@postgres:5432/bcm_platform"  # TODO: from config
            self.pg_pool = await asyncpg.create_pool(pg_url, min_size=2, max_size=10)
            logger.info("Connected to PostgreSQL")
        except Exception as e:
            logger.warning(f"PostgreSQL connection failed: {e}")
            logger.info("Will operate without database tracking")

    async def initialize_database(self) -> None:
        """
        Initialize platform status tracking tables

        Creates:
        - platform_status - service status tracking
        - platform_events - platform event log
        """
        if not self.pg_pool:
            logger.warning("PostgreSQL not available - skipping database initialization")
            return

        logger.info("Initializing platform database schema...")

        async with self.pg_pool.acquire() as conn:
            # Create platform_status table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS platform_status (
                    id SERIAL PRIMARY KEY,
                    service_name VARCHAR(100) NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB,
                    UNIQUE(service_name)
                )
            """)

            # Create platform_events table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS platform_events (
                    id SERIAL PRIMARY KEY,
                    event_type VARCHAR(100) NOT NULL,
                    event_data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            logger.info("Database schema initialized")

    async def start(self) -> None:
        """
        Start the platform

        Startup sequence:
        1. Connect to Redis & PostgreSQL
        2. Initialize database
        3. Start foundation services
        4. Start infrastructure services
        5. Start business & intelligence services (parallel)
        6. Start application services
        7. Publish platform.ready event
        8. Start continuous monitoring
        """
        if self.running:
            logger.warning("Platform already running")
            return

        logger.info("=" * 60)
        logger.info("STARTING BCM PLATFORM")
        logger.info("=" * 60)

        start_time = datetime.utcnow()
        self.running = True

        try:
            # Step 1: Connect services
            await self.connect_services()

            # Step 2: Initialize database
            await self.initialize_database()

            # Step 3: Get startup order
            parallel_groups = get_parallel_groups()
            logger.info(f"Startup plan: {len(parallel_groups)} levels")
            for i, level_groups in enumerate(parallel_groups):
                logger.info(f"  Level {i+1}: {', '.join(level_groups)}")

            # Step 4: Start groups level by level
            for level_num, level_groups in enumerate(parallel_groups):
                logger.info(f"Starting level {level_num + 1}: {', '.join(level_groups)}")

                # Start groups in parallel if multiple at same level
                if len(level_groups) == 1:
                    # Single group - start sequentially
                    success = await self.start_group(level_groups[0])
                    if not success:
                        group = self.groups[level_groups[0]]
                        if group.critical:
                            raise Exception(f"Critical group {level_groups[0]} failed to start")
                else:
                    # Multiple groups - start in parallel
                    tasks = [self.start_group(group_name) for group_name in level_groups]
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    # Check for critical failures
                    for group_name, result in zip(level_groups, results):
                        if isinstance(result, Exception) or not result:
                            group = self.groups[group_name]
                            if group.critical:
                                raise Exception(f"Critical group {group_name} failed: {result}")
                            else:
                                logger.warning(f"Non-critical group {group_name} failed: {result}")

            # Step 5: Mark startup as completed
            self.startup_completed = True
            elapsed = (datetime.utcnow() - start_time).total_seconds()

            logger.info("=" * 60)
            logger.info(f"PLATFORM STARTED SUCCESSFULLY in {elapsed:.1f}s")
            logger.info("=" * 60)

            # Step 6: Publish platform.ready event
            await self.publish_event(
                event_type='platform.ready',
                data={
                    'startup_time_seconds': elapsed,
                    'groups': list(self.groups.keys()),
                    'services_count': sum(len(g.services) for g in self.groups.values())
                }
            )

            # Step 7: Start continuous monitoring
            self.monitoring_task = asyncio.create_task(self.monitor_platform())
            logger.info("Platform monitoring started")

        except Exception as e:
            logger.error(f"Platform startup failed: {e}")
            self.running = False
            raise

    async def start_group(self, group_name: str) -> bool:
        """
        Start a service group

        Args:
            group_name: Name of the group to start

        Returns:
            True if all services started successfully
        """
        group = self.groups.get(group_name)
        if not group:
            logger.error(f"Unknown service group: {group_name}")
            return False

        logger.info(f"Starting group '{group_name}': {', '.join(group.services)}")

        # Wait for dependencies
        if not await self.wait_for_dependencies(group_name):
            logger.error(f"Dependencies not ready for group {group_name}")
            return False

        # Start each service in the group
        failed_services = []
        for service_name in group.services:
            logger.info(f"  Starting {service_name}...")

            # Register service
            await self.register_service(
                service_name=service_name,
                metadata={'group': group_name}
            )

            # Start Docker service
            success = await self.start_docker_service(service_name, timeout=300)

            if success:
                # Update status
                await self.service_registry.update_status(service_name, "running")
                await self.service_registry.update_health(service_name, "healthy")

                # Track in database
                await self._track_service_status(service_name, "running")

                logger.info(f"  ✓ {service_name} started")
            else:
                failed_services.append(service_name)
                logger.error(f"  ✗ {service_name} failed to start")

                # Track failure
                await self.service_registry.update_status(service_name, "failed")
                await self._track_service_status(service_name, "failed")

        # Check if group is ready
        if failed_services:
            logger.warning(f"Group {group_name} partially started - failed: {', '.join(failed_services)}")
            if group.critical:
                return False
            # Non-critical group can have failures
            return True

        # Publish group.ready event
        await self.publish_event(
            event_type=f'group.{group_name}.ready',
            data={
                'group': group_name,
                'services': group.services,
                'service_count': len(group.services)
            }
        )

        logger.info(f"✓ Group '{group_name}' ready")
        return True

    async def wait_for_dependencies(self, group_name: str, timeout: int = 300) -> bool:
        """
        Wait for group dependencies to be ready

        Args:
            group_name: Name of the group
            timeout: Maximum wait time in seconds

        Returns:
            True if dependencies ready
        """
        group = self.groups.get(group_name)
        if not group or not group.dependencies:
            return True

        logger.info(f"Waiting for dependencies of {group_name}: {', '.join(group.dependencies)}")

        start_time = datetime.utcnow()

        while (datetime.utcnow() - start_time).total_seconds() < timeout:
            all_ready = True

            for dep_name in group.dependencies:
                dep_group = self.groups.get(dep_name)
                if not dep_group:
                    logger.error(f"Unknown dependency: {dep_name}")
                    return False

                if not await dep_group.is_ready(self.service_registry):
                    all_ready = False
                    break

            if all_ready:
                logger.info(f"Dependencies ready for {group_name}")
                return True

            await asyncio.sleep(5)

        logger.error(f"Timeout waiting for dependencies of {group_name}")
        return False

    async def monitor_platform(self) -> None:
        """
        Continuous platform monitoring

        Checks:
        - Service health
        - Auto-restart unhealthy services
        - Publish service.failed events
        """
        logger.info("Platform monitoring loop started")

        while self.running:
            try:
                # Check all services
                for group_name, group in self.groups.items():
                    for service_name in group.services:
                        # Check health
                        healthy = await self.monitor_service_health(service_name)

                        if not healthy:
                            logger.warning(f"Service {service_name} unhealthy - attempting restart")

                            # Publish failure event
                            await self.publish_event(
                                event_type='service.failed',
                                data={
                                    'service': service_name,
                                    'group': group_name,
                                    'timestamp': datetime.utcnow().isoformat()
                                }
                            )

                            # Attempt restart
                            success = await self.restart_docker_service(service_name)

                            if success:
                                logger.info(f"Service {service_name} recovered")
                                await self.service_registry.update_health(service_name, "healthy")
                                await self._track_service_status(service_name, "running")
                            else:
                                logger.error(f"Service {service_name} restart failed")
                                await self.service_registry.update_status(service_name, "failed")
                                await self._track_service_status(service_name, "failed")

                # Sleep before next check
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(30)

        logger.info("Platform monitoring loop stopped")

    async def stop(self) -> None:
        """
        Stop the platform

        Shutdown sequence:
        1. Stop monitoring
        2. Stop services in reverse order
        3. Publish platform.stopped event
        4. Close connections
        """
        if not self.running:
            logger.warning("Platform not running")
            return

        logger.info("=" * 60)
        logger.info("STOPPING BCM PLATFORM")
        logger.info("=" * 60)

        self.running = False

        # Stop monitoring
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

        # Stop groups in reverse order
        startup_order = get_startup_order()
        for group_name in reversed(startup_order):
            await self.stop_group(group_name)

        # Publish platform.stopped event
        await self.publish_event(
            event_type='platform.stopped',
            data={'timestamp': datetime.utcnow().isoformat()}
        )

        # Close connections
        if self.redis_client:
            await self.redis_client.close()
        if self.pg_pool:
            await self.pg_pool.close()

        logger.info("Platform stopped")

    async def stop_group(self, group_name: str) -> bool:
        """Stop a service group"""
        group = self.groups.get(group_name)
        if not group:
            return False

        logger.info(f"Stopping group '{group_name}'")

        for service_name in group.services:
            await self.stop_docker_service(service_name)
            await self.service_registry.update_status(service_name, "stopped")

        return True

    async def get_status(self) -> Dict[str, Any]:
        """
        Get platform status

        Returns:
            Dictionary with platform status information
        """
        groups_status = {}

        for group_name, group in self.groups.items():
            group_ready = await group.is_ready(self.service_registry)

            services_status = {}
            for service_name in group.services:
                service = await self.service_registry.get_service(service_name)
                if service:
                    services_status[service_name] = {
                        'status': service.status,
                        'health': service.health_status
                    }
                else:
                    services_status[service_name] = {
                        'status': 'unknown',
                        'health': 'unknown'
                    }

            groups_status[group_name] = {
                'ready': group_ready,
                'services': services_status
            }

        return {
            'running': self.running,
            'startup_completed': self.startup_completed,
            'groups': groups_status,
            'timestamp': datetime.utcnow().isoformat()
        }

    async def _track_service_status(self, service_name: str, status: str) -> None:
        """Track service status in database"""
        if not self.pg_pool:
            return

        try:
            async with self.pg_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO platform_status (service_name, status)
                    VALUES ($1, $2)
                    ON CONFLICT (service_name)
                    DO UPDATE SET status = $2, last_check = CURRENT_TIMESTAMP
                """, service_name, status)
        except Exception as e:
            logger.error(f"Failed to track service status: {e}")