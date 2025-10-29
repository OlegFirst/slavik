"""
Production Integrations Module
Redis, PostgreSQL, Docker integrations for hybrid architecture
"""

import asyncio
import asyncpg
import aioredis
import docker
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RedisClient:
    """Production Redis client with async support"""

    def __init__(self, url: str = "redis://localhost:6379", max_connections: int = 10):
        self.url = url
        self.max_connections = max_connections
        self.pool = None
        self.redis = None

    async def connect(self):
        """Establish Redis connection"""
        try:
            self.pool = aioredis.ConnectionPool.from_url(
                self.url,
                max_connections=self.max_connections,
                decode_responses=True
            )
            self.redis = aioredis.Redis(connection_pool=self.pool)

            # Test connection
            await self.redis.ping()
            logger.info("✅ Redis connected successfully")

        except Exception as error:
            logger.error(f"❌ Redis connection failed: {error}")
            raise

    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
        if self.pool:
            await self.pool.disconnect()
        logger.info("🛑 Redis disconnected")

    async def health_check(self) -> bool:
        """Check Redis health"""
        try:
            await self.redis.ping()
            return True
        except Exception:
            return False

    # Basic operations
    async def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        try:
            return await self.redis.get(key)
        except Exception as error:
            logger.error(f"Redis GET error: {error}")
            return None

    async def set(self, key: str, value: Union[str, Dict, List], ex: int = None) -> bool:
        """Set key-value pair with optional expiration"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)

            await self.redis.set(key, value, ex=ex)
            return True
        except Exception as error:
            logger.error(f"Redis SET error: {error}")
            return False

    async def setex(self, key: str, seconds: int, value: Union[str, Dict, List]) -> bool:
        """Set with expiration"""
        return await self.set(key, value, ex=seconds)

    async def delete(self, key: str) -> bool:
        """Delete key"""
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception as error:
            logger.error(f"Redis DELETE error: {error}")
            return False

    # List operations
    async def lpush(self, key: str, value: Union[str, Dict, List]) -> int:
        """Left push to list"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            return await self.redis.lpush(key, value)
        except Exception as error:
            logger.error(f"Redis LPUSH error: {error}")
            return 0

    async def rpop(self, key: str) -> Optional[str]:
        """Right pop from list"""
        try:
            return await self.redis.rpop(key)
        except Exception as error:
            logger.error(f"Redis RPOP error: {error}")
            return None

    async def ltrim(self, key: str, start: int, end: int) -> bool:
        """Trim list"""
        try:
            await self.redis.ltrim(key, start, end)
            return True
        except Exception as error:
            logger.error(f"Redis LTRIM error: {error}")
            return False

    # Pub/Sub operations
    async def publish(self, channel: str, message: Union[str, Dict]) -> int:
        """Publish message to channel"""
        try:
            if isinstance(message, dict):
                message = json.dumps(message)
            return await self.redis.publish(channel, message)
        except Exception as error:
            logger.error(f"Redis PUBLISH error: {error}")
            return 0

    async def subscribe(self, channels: List[str], callback=None):
        """Subscribe to channels"""
        try:
            pubsub = self.redis.pubsub()
            await pubsub.subscribe(*channels)

            async for message in pubsub.listen():
                if message['type'] == 'message':
                    if callback:
                        await callback(message['channel'], message['data'])

        except Exception as error:
            logger.error(f"Redis SUBSCRIBE error: {error}")

    # Stats and monitoring
    async def get_info(self) -> Dict[str, Any]:
        """Get Redis info"""
        try:
            info = await self.redis.info()
            return {
                "memory_used": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands_processed": info.get("total_commands_processed"),
                "uptime": info.get("uptime_in_seconds")
            }
        except Exception as error:
            logger.error(f"Redis INFO error: {error}")
            return {}

    async def get_stats(self) -> Dict[str, Any]:
        """Get Redis statistics"""
        info = await self.get_info()
        return {
            "status": "connected" if await self.health_check() else "disconnected",
            **info
        }


class PostgreSQLClient:
    """Production PostgreSQL client with async support"""

    def __init__(self, url: str = "postgresql://postgres:postgres@localhost:5432/cognitive_orchestration"):
        self.url = url
        self.pool = None

    async def connect(self):
        """Establish PostgreSQL connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.url,
                min_size=5,
                max_size=20,
                command_timeout=30
            )

            # Test connection and create tables
            await self.initialize_schema()
            logger.info("✅ PostgreSQL connected successfully")

        except Exception as error:
            logger.error(f"❌ PostgreSQL connection failed: {error}")
            raise

    async def disconnect(self):
        """Close PostgreSQL connection pool"""
        if self.pool:
            await self.pool.close()
        logger.info("🛑 PostgreSQL disconnected")

    async def health_check(self) -> bool:
        """Check PostgreSQL health"""
        try:
            async with self.pool.acquire() as connection:
                await connection.execute("SELECT 1")
            return True
        except Exception:
            return False

    async def initialize_schema(self):
        """Initialize database schema for cognitive orchestration"""
        schema_sql = """
        -- System tables
        CREATE TABLE IF NOT EXISTS system_requests (
            id SERIAL PRIMARY KEY,
            request_id VARCHAR(255) UNIQUE,
            request_type VARCHAR(100),
            orchestrator VARCHAR(50),
            data JSONB,
            result JSONB,
            duration FLOAT,
            success BOOLEAN,
            timestamp TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS orchestrator_health (
            id SERIAL PRIMARY KEY,
            orchestrator_name VARCHAR(50),
            status VARCHAR(20),
            services_loaded INTEGER,
            memory_usage BIGINT,
            error_message TEXT,
            timestamp TIMESTAMP DEFAULT NOW()
        );

        -- BCM specific tables
        CREATE TABLE IF NOT EXISTS bcm_operations (
            id SERIAL PRIMARY KEY,
            module VARCHAR(100),
            action VARCHAR(100),
            data JSONB,
            result JSONB,
            user_id VARCHAR(255),
            timestamp TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS program_executions (
            id SERIAL PRIMARY KEY,
            domain VARCHAR(100),
            module VARCHAR(100),
            action VARCHAR(100),
            result JSONB,
            timestamp TIMESTAMP DEFAULT NOW()
        );

        -- Evolution and experiments
        CREATE TABLE IF NOT EXISTS evolution_improvements (
            id SERIAL PRIMARY KEY,
            component VARCHAR(255),
            improvement_factor FLOAT,
            parameters JSONB,
            timestamp TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS sandbox_experiments (
            id SERIAL PRIMARY KEY,
            experiment_id VARCHAR(255) UNIQUE,
            name VARCHAR(255),
            code TEXT,
            result JSONB,
            success BOOLEAN,
            timestamp TIMESTAMP DEFAULT NOW()
        );

        -- User and session management
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) UNIQUE,
            username VARCHAR(100),
            email VARCHAR(255),
            profile JSONB,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS user_sessions (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) UNIQUE,
            user_id VARCHAR(255),
            data JSONB,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_system_requests_type ON system_requests(request_type);
        CREATE INDEX IF NOT EXISTS idx_system_requests_timestamp ON system_requests(timestamp);
        CREATE INDEX IF NOT EXISTS idx_bcm_operations_module ON bcm_operations(module);
        CREATE INDEX IF NOT EXISTS idx_bcm_operations_timestamp ON bcm_operations(timestamp);
        """

        try:
            async with self.pool.acquire() as connection:
                await connection.execute(schema_sql)
            logger.info("✅ Database schema initialized")

        except Exception as error:
            logger.error(f"❌ Schema initialization failed: {error}")
            raise

    # Query methods
    async def execute(self, query: str, *args) -> str:
        """Execute query with parameters"""
        try:
            async with self.pool.acquire() as connection:
                return await connection.execute(query, *args)
        except Exception as error:
            logger.error(f"PostgreSQL EXECUTE error: {error}")
            raise

    async def fetch(self, query: str, *args) -> List[Dict[str, Any]]:
        """Fetch multiple rows"""
        try:
            async with self.pool.acquire() as connection:
                rows = await connection.fetch(query, *args)
                return [dict(row) for row in rows]
        except Exception as error:
            logger.error(f"PostgreSQL FETCH error: {error}")
            return []

    async def fetchrow(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Fetch single row"""
        try:
            async with self.pool.acquire() as connection:
                row = await connection.fetchrow(query, *args)
                return dict(row) if row else None
        except Exception as error:
            logger.error(f"PostgreSQL FETCHROW error: {error}")
            return None

    async def fetchval(self, query: str, *args) -> Any:
        """Fetch single value"""
        try:
            async with self.pool.acquire() as connection:
                return await connection.fetchval(query, *args)
        except Exception as error:
            logger.error(f"PostgreSQL FETCHVAL error: {error}")
            return None

    # Convenience methods for cognitive orchestration
    async def log_request(self, request_id: str, request_type: str, orchestrator: str,
                         data: Dict[str, Any], result: Dict[str, Any],
                         duration: float, success: bool):
        """Log system request"""
        await self.execute("""
            INSERT INTO system_requests
            (request_id, request_type, orchestrator, data, result, duration, success)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """, request_id, request_type, orchestrator, json.dumps(data),
             json.dumps(result), duration, success)

    async def get_recent_requests(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent system requests"""
        return await self.fetch("""
            SELECT * FROM system_requests
            ORDER BY timestamp DESC LIMIT $1
        """, limit)

    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        return {
            "pool_size": self.pool.get_size(),
            "pool_max_size": self.pool.get_max_size(),
            "pool_min_size": self.pool.get_min_size()
        }

    async def get_stats(self) -> Dict[str, Any]:
        """Get PostgreSQL statistics"""
        stats = await self.get_connection_stats()
        stats["status"] = "connected" if await self.health_check() else "disconnected"
        return stats


class DockerManager:
    """Production Docker management with async support"""

    def __init__(self, socket_url: str = "unix:///var/run/docker.sock"):
        self.socket_url = socket_url
        self.client = None
        self.containers = {}

    async def initialize(self):
        """Initialize Docker client"""
        try:
            # Use sync docker client (docker-py doesn't have proper async support)
            self.client = docker.DockerClient(base_url=self.socket_url)

            # Test connection
            self.client.ping()
            logger.info("✅ Docker connected successfully")

        except Exception as error:
            logger.error(f"❌ Docker connection failed: {error}")
            raise

    async def cleanup(self):
        """Cleanup Docker resources"""
        if self.client:
            # Stop all managed containers
            for container_id in list(self.containers.keys()):
                await self.cleanup_container(container_id)

            self.client.close()
        logger.info("🛑 Docker manager cleaned up")

    async def health_check(self) -> bool:
        """Check Docker daemon health"""
        try:
            self.client.ping()
            return True
        except Exception:
            return False

    async def create_sandbox(self, image: str, code: str, constraints: Dict[str, Any] = None) -> str:
        """Create isolated sandbox container"""
        try:
            constraints = constraints or {}

            # Prepare container configuration
            config = {
                "image": image,
                "command": ["python", "-c", code],
                "detach": True,
                "remove": True,
                "mem_limit": f"{constraints.get('max_memory_mb', 512)}m",
                "nano_cpus": int(constraints.get('max_cpu_seconds', 30) * 1e9),
                "network_mode": "none" if not constraints.get('allowed_domains') else "bridge",
                "read_only": True,
                "security_opt": ["no-new-privileges:true"],
                "cap_drop": ["ALL"]
            }

            # Create and start container
            container = self.client.containers.run(**config)
            container_id = container.id

            # Track container
            self.containers[container_id] = container

            logger.info(f"✅ Sandbox container created: {container_id[:12]}")
            return container_id

        except Exception as error:
            logger.error(f"❌ Failed to create sandbox: {error}")
            raise

    async def get_container_logs(self, container_id: str) -> str:
        """Get container logs"""
        try:
            container = self.containers.get(container_id)
            if container:
                logs = container.logs().decode()
                return logs
            return ""

        except Exception as error:
            logger.error(f"Failed to get container logs: {error}")
            return ""

    async def cleanup_container(self, container_id: str):
        """Cleanup specific container"""
        try:
            container = self.containers.get(container_id)
            if container:
                container.stop(timeout=5)
                container.remove()
                del self.containers[container_id]
                logger.info(f"✅ Container cleaned up: {container_id[:12]}")

        except Exception as error:
            logger.warning(f"Container cleanup warning: {error}")

    async def get_container_stats(self) -> Dict[str, Any]:
        """Get Docker container statistics"""
        try:
            all_containers = self.client.containers.list(all=True)

            stats = {
                "total_containers": len(all_containers),
                "running_containers": len([c for c in all_containers if c.status == "running"]),
                "managed_containers": len(self.containers),
                "images_count": len(self.client.images.list())
            }

            return stats

        except Exception as error:
            logger.error(f"Failed to get container stats: {error}")
            return {}

    async def get_stats(self) -> Dict[str, Any]:
        """Get Docker statistics"""
        stats = await self.get_container_stats()
        stats["status"] = "connected" if await self.health_check() else "disconnected"
        return stats


# Integration factory functions

async def create_redis_client(url: str = None) -> RedisClient:
    """Create and connect Redis client"""
    client = RedisClient(url or "redis://localhost:6379")
    await client.connect()
    return client


async def create_postgres_client(url: str = None) -> PostgreSQLClient:
    """Create and connect PostgreSQL client"""
    client = PostgreSQLClient(url or "postgresql://postgres:postgres@localhost:5432/cognitive_orchestration")
    await client.connect()
    return client


async def create_docker_manager(socket_url: str = None) -> DockerManager:
    """Create and initialize Docker manager"""
    manager = DockerManager(socket_url or "unix:///var/run/docker.sock")
    await manager.initialize()
    return manager


# Integration health checker
async def check_all_integrations(redis_url: str = None, postgres_url: str = None, docker_socket: str = None) -> Dict[str, bool]:
    """Check health of all integrations"""
    health = {}

    # Test Redis
    try:
        redis = await create_redis_client(redis_url)
        health["redis"] = await redis.health_check()
        await redis.disconnect()
    except Exception:
        health["redis"] = False

    # Test PostgreSQL
    try:
        postgres = await create_postgres_client(postgres_url)
        health["postgres"] = await postgres.health_check()
        await postgres.disconnect()
    except Exception:
        health["postgres"] = False

    # Test Docker
    try:
        docker_mgr = await create_docker_manager(docker_socket)
        health["docker"] = await docker_mgr.health_check()
        await docker_mgr.cleanup()
    except Exception:
        health["docker"] = False

    return health