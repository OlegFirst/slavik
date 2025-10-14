"""
Platform Orchestrator - Main Control Center for BCM Platform
ISO 22301 Business Continuity Management System
"""

import asyncio
import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import docker
import aiohttp
from asyncpg import create_pool
import redis.asyncio as redis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

class ServiceGroup:
    """Represents a group of related services"""

    def __init__(self, name: str, services: List[str], dependencies: List[str] = None):
        self.name = name
        self.services = services
        self.dependencies = dependencies or []
        self.status = "pending"

    async def is_ready(self) -> bool:
        """Check if all services in group are healthy"""
        docker_client = docker.from_env()

        for service_name in self.services:
            try:
                container = docker_client.containers.get(f"iso-22301-{service_name}-1")
                if container.status != "running":
                    return False

                # Check health if available
                if container.attrs.get('State', {}).get('Health'):
                    health = container.attrs['State']['Health']['Status']
                    if health != 'healthy':
                        return False
            except docker.errors.NotFound:
                return False

        self.status = "ready"
        return True

class PlatformOrchestrator:
    """
    Main orchestrator for the entire BCM platform
    Manages service startup order, health checks, and dependencies
    """

    def __init__(self):
        self.docker_client = docker.from_env()
        self.redis_client = None
        self.pg_pool = None

        # Define service groups with proper dependencies
        self.groups = {
            'foundation': ServiceGroup(
                'foundation',
                ['postgres', 'redis', 'rabbitmq'],
                []
            ),
            'infrastructure': ServiceGroup(
                'infrastructure',
                ['eventbus', 'unified_database_gateway', 'unified_api_gateway'],
                ['foundation']
            ),
            'business': ServiceGroup(
                'business',
                ['odoo', 'bia_engine', 'compliance_checker', 'bpmn_service'],
                ['foundation', 'infrastructure']
            ),
            'intelligence': ServiceGroup(
                'intelligence',
                ['ai_orchestrator', 'ai_control_center', 'digital_twin'],
                ['foundation', 'infrastructure']
            ),
            'applications': ServiceGroup(
                'applications',
                ['admin_panel', 'web_portal', 'mobile_backend'],
                ['foundation', 'infrastructure', 'business', 'intelligence']
            )
        }

    async def connect_services(self):
        """Connect to Redis and PostgreSQL"""
        try:
            # Connect to Redis
            self.redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("✅ Connected to Redis")

            # Connect to PostgreSQL
            self.pg_pool = await create_pool(
                host=os.getenv('POSTGRES_HOST', 'localhost'),
                port=int(os.getenv('POSTGRES_PORT', 5432)),
                user=os.getenv('POSTGRES_USER', 'odoo'),
                password=os.getenv('POSTGRES_PASSWORD', 'postgres123'),
                database=os.getenv('POSTGRES_DB', 'bcm_platform'),
                min_size=2,
                max_size=10
            )
            logger.info("✅ Connected to PostgreSQL")

        except Exception as e:
            logger.error(f"Failed to connect to services: {e}")
            raise

    async def wait_for_dependencies(self, group_name: str):
        """Wait for all dependency groups to be ready"""
        group = self.groups[group_name]

        for dep_name in group.dependencies:
            dep_group = self.groups[dep_name]

            logger.info(f"⏳ Waiting for {dep_name} group...")

            while not await dep_group.is_ready():
                await asyncio.sleep(2)

            logger.info(f"✅ {dep_name} group is ready")

    async def start_group(self, group_name: str):
        """Start all services in a group"""
        group = self.groups[group_name]

        logger.info(f"🚀 Starting {group_name} group with services: {group.services}")

        # Wait for dependencies
        await self.wait_for_dependencies(group_name)

        # Start services using docker-compose
        for service in group.services:
            try:
                logger.info(f"  Starting {service}...")

                # Use docker-compose to start the service
                os.system(f"docker-compose up -d {service} 2>/dev/null")

                # Small delay between services
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"  ❌ Failed to start {service}: {e}")

        # Wait for group to be healthy
        logger.info(f"  Waiting for {group_name} group to be healthy...")

        max_retries = 30
        for i in range(max_retries):
            if await group.is_ready():
                logger.info(f"✅ {group_name} group is healthy!")

                # Publish event to Redis
                if self.redis_client:
                    await self.redis_client.publish(
                        'platform_events',
                        json.dumps({
                            'event': f'group.{group_name}.ready',
                            'timestamp': datetime.now().isoformat()
                        })
                    )
                break

            await asyncio.sleep(2)

            if i == max_retries - 1:
                logger.warning(f"⚠️ {group_name} group not healthy after {max_retries} retries")

    async def initialize_database(self):
        """Initialize database with required schemas and data"""
        logger.info("🗄️ Initializing database...")

        if not self.pg_pool:
            logger.warning("No PostgreSQL connection")
            return

        async with self.pg_pool.acquire() as conn:
            # Create bcm_platform database if not exists
            try:
                await conn.execute("""
                    CREATE DATABASE bcm_platform;
                """)
                logger.info("  Created bcm_platform database")
            except:
                logger.info("  bcm_platform database already exists")

            # Create required tables
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS platform_status (
                    id SERIAL PRIMARY KEY,
                    service_name VARCHAR(100),
                    status VARCHAR(50),
                    last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB
                );
            """)

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS platform_events (
                    id SERIAL PRIMARY KEY,
                    event_type VARCHAR(100),
                    event_data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            logger.info("✅ Database initialized")

    async def start_platform(self):
        """Main entry point to start the entire platform"""
        logger.info("=" * 60)
        logger.info("🎯 BCM PLATFORM ORCHESTRATOR - Starting Platform")
        logger.info("=" * 60)

        try:
            # Level 1: Start foundation services first
            await self.start_group('foundation')

            # Connect to services
            await self.connect_services()

            # Initialize database
            await self.initialize_database()

            # Level 2: Start infrastructure
            await self.start_group('infrastructure')

            # Level 3: Start business and intelligence in parallel
            await asyncio.gather(
                self.start_group('business'),
                self.start_group('intelligence')
            )

            # Level 4: Start applications
            await self.start_group('applications')

            logger.info("=" * 60)
            logger.info("🎉 PLATFORM SUCCESSFULLY STARTED!")
            logger.info("=" * 60)
            logger.info("Access points:")
            logger.info("  • Odoo: http://localhost:8069")
            logger.info("  • Admin Panel: http://localhost:3001")
            logger.info("  • RabbitMQ: http://localhost:15672")
            logger.info("  • EventBus: http://localhost:8001")
            logger.info("=" * 60)

            # Publish platform ready event
            if self.redis_client:
                await self.redis_client.publish(
                    'platform_events',
                    json.dumps({
                        'event': 'platform.ready',
                        'timestamp': datetime.now().isoformat(),
                        'services': {
                            group_name: group.status
                            for group_name, group in self.groups.items()
                        }
                    })
                )

        except Exception as e:
            logger.error(f"❌ Platform startup failed: {e}")
            raise

    async def monitor_platform(self):
        """Continuously monitor platform health"""
        logger.info("👁️ Starting platform monitoring...")

        while True:
            try:
                # Check each group health
                for group_name, group in self.groups.items():
                    is_healthy = await group.is_ready()

                    if not is_healthy and group.status == "ready":
                        logger.warning(f"⚠️ {group_name} group became unhealthy!")

                        # Try to restart unhealthy services
                        await self.start_group(group_name)

                # Wait before next check
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(10)

async def main():
    """Main entry point"""
    orchestrator = PlatformOrchestrator()

    # Start platform
    await orchestrator.start_platform()

    # Start monitoring in background
    monitor_task = asyncio.create_task(orchestrator.monitor_platform())

    # Keep running
    await monitor_task

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n👋 Platform Orchestrator stopped")