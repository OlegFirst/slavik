"""
Database High Availability Manager
AI Platform ISO 22301 - Production Ready

Управление HA конфигурацией для PostgreSQL, Redis и Qdrant
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
import yaml
import os

from redis.sentinel import Sentinel
from redis import Redis
import asyncpg
from qdrant_client import QdrantClient

logger = logging.getLogger(__name__)


class DatabaseHAManager:
    """Менеджер высокой доступности для всех баз данных"""

    def __init__(self, config_path: str = "infrastructure/database/ha_config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()

        # Connections
        self.pg_pool: Optional[asyncpg.Pool] = None
        self.redis_sentinel: Optional[Sentinel] = None
        self.redis_master: Optional[Redis] = None
        self.qdrant_client: Optional[QdrantClient] = None

        # Health status
        self.health_status = {
            "postgresql": {"status": "unknown", "last_check": None},
            "redis": {"status": "unknown", "last_check": None},
            "qdrant": {"status": "unknown", "last_check": None}
        }

    def _load_config(self) -> Dict:
        """Загрузка HA конфигурации"""
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    # =========================================================================
    # PostgreSQL HA Management
    # =========================================================================

    async def init_postgresql(self):
        """Инициализация PostgreSQL с HA"""
        pg_config = self.config['postgresql']

        # Connection pool с failover support
        self.pg_pool = await asyncpg.create_pool(
            host=os.getenv('SUPABASE_HOST'),
            port=pg_config['primary']['port'],
            database=os.getenv('SUPABASE_DB'),
            user=os.getenv('SUPABASE_USER'),
            password=os.getenv('SUPABASE_PASSWORD'),
            ssl='require',
            min_size=pg_config['ha']['pooling']['pool_size'],
            max_size=pg_config['ha']['pooling']['max_client_conn'],
            max_inactive_connection_lifetime=300,
            command_timeout=10.0
        )

        logger.info("PostgreSQL HA pool initialized")

    async def check_postgresql_health(self) -> Dict:
        """Проверка здоровья PostgreSQL"""
        try:
            async with self.pg_pool.acquire() as conn:
                start = datetime.now()
                result = await conn.fetchval("SELECT 1")
                latency = (datetime.now() - start).total_seconds() * 1000

                self.health_status["postgresql"] = {
                    "status": "healthy",
                    "latency_ms": latency,
                    "last_check": datetime.now().isoformat()
                }

                return self.health_status["postgresql"]
        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {e}")
            self.health_status["postgresql"] = {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
            return self.health_status["postgresql"]

    async def get_postgresql_replication_status(self) -> Dict:
        """Получение статуса репликации PostgreSQL"""
        query = """
        SELECT
            client_addr,
            state,
            sync_state,
            replay_lag
        FROM pg_stat_replication
        """

        async with self.pg_pool.acquire() as conn:
            rows = await conn.fetch(query)
            return {
                "replicas": [dict(row) for row in rows],
                "replica_count": len(rows)
            }

    # =========================================================================
    # Redis Sentinel HA Management
    # =========================================================================

    def init_redis_sentinel(self):
        """Инициализация Redis Sentinel"""
        redis_config = self.config['redis']
        sentinel_config = redis_config['sentinel']

        # Sentinel connections
        sentinel_hosts = [
            (s['host'], s['port'])
            for s in sentinel_config['sentinels']
        ]

        self.redis_sentinel = Sentinel(
            sentinel_hosts,
            socket_timeout=5.0,
            socket_connect_timeout=5.0
        )

        # Get master connection
        self.redis_master = self.redis_sentinel.master_for(
            sentinel_config['master_name'],
            socket_timeout=5.0,
            socket_connect_timeout=5.0,
            retry_on_timeout=True,
            health_check_interval=30
        )

        logger.info("Redis Sentinel initialized")

    def check_redis_health(self) -> Dict:
        """Проверка здоровья Redis"""
        try:
            start = datetime.now()
            result = self.redis_master.ping()
            latency = (datetime.now() - start).total_seconds() * 1000

            # Get memory info
            info = self.redis_master.info('memory')

            self.health_status["redis"] = {
                "status": "healthy",
                "latency_ms": latency,
                "memory_usage_mb": info['used_memory'] / 1024 / 1024,
                "memory_usage_percent": info['used_memory'] / info['maxmemory'] * 100 if info.get('maxmemory') else 0,
                "last_check": datetime.now().isoformat()
            }

            return self.health_status["redis"]
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            self.health_status["redis"] = {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
            return self.health_status["redis"]

    def get_redis_sentinel_status(self) -> Dict:
        """Получение статуса Sentinel"""
        sentinel_config = self.config['redis']['sentinel']
        master_name = sentinel_config['master_name']

        # Master info
        master_addr = self.redis_sentinel.discover_master(master_name)

        # Slaves info
        slaves = self.redis_sentinel.discover_slaves(master_name)

        # Sentinel info
        sentinels = self.redis_sentinel.discover_sentinels(master_name)

        return {
            "master": {
                "host": master_addr[0],
                "port": master_addr[1]
            },
            "slaves": [
                {"host": slave[0], "port": slave[1]}
                for slave in slaves
            ],
            "sentinels": [
                {"host": sent[0], "port": sent[1]}
                for sent in sentinels
            ],
            "slave_count": len(slaves),
            "sentinel_count": len(sentinels)
        }

    def trigger_redis_failover(self):
        """Принудительный failover Redis (только для тестов!)"""
        sentinel_config = self.config['redis']['sentinel']
        master_name = sentinel_config['master_name']

        logger.warning(f"Triggering manual failover for {master_name}")

        # This will trigger Sentinel to perform failover
        for sentinel in self.redis_sentinel.sentinels:
            try:
                sentinel.sentinel_failover(master_name)
                logger.info("Failover triggered successfully")
                return True
            except Exception as e:
                logger.error(f"Failover failed: {e}")
                continue

        return False

    # =========================================================================
    # Qdrant HA Management
    # =========================================================================

    def init_qdrant_cluster(self):
        """Инициализация Qdrant Cluster"""
        qdrant_config = self.config['qdrant']
        cluster_config = qdrant_config['cluster']

        # Primary node
        node_1 = cluster_config['node_1']

        self.qdrant_client = QdrantClient(
            host=node_1['host'],
            port=node_1['port'],
            grpc_port=node_1['grpc_port'],
            prefer_grpc=True,
            timeout=30
        )

        logger.info("Qdrant cluster client initialized")

    def check_qdrant_health(self) -> Dict:
        """Проверка здоровья Qdrant"""
        try:
            start = datetime.now()

            # Health check via API
            collections = self.qdrant_client.get_collections()

            latency = (datetime.now() - start).total_seconds() * 1000

            self.health_status["qdrant"] = {
                "status": "healthy",
                "latency_ms": latency,
                "collections_count": len(collections.collections),
                "last_check": datetime.now().isoformat()
            }

            return self.health_status["qdrant"]
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            self.health_status["qdrant"] = {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
            return self.health_status["qdrant"]

    def get_qdrant_cluster_status(self) -> Dict:
        """Получение статуса Qdrant кластера"""
        try:
            # Cluster info (если поддерживается API)
            # В текущей версии Qdrant нет прямого API для cluster status
            # Можно использовать telemetry или health endpoints

            collections = self.qdrant_client.get_collections()

            cluster_info = {
                "collections": [c.name for c in collections.collections],
                "total_collections": len(collections.collections)
            }

            return cluster_info
        except Exception as e:
            logger.error(f"Failed to get Qdrant cluster status: {e}")
            return {"error": str(e)}

    # =========================================================================
    # Global Health Check
    # =========================================================================

    async def check_all_health(self) -> Dict:
        """Проверка здоровья всех баз данных"""
        results = {}

        # PostgreSQL
        results["postgresql"] = await self.check_postgresql_health()

        # Redis
        results["redis"] = self.check_redis_health()

        # Qdrant
        results["qdrant"] = self.check_qdrant_health()

        # Overall status
        all_healthy = all(
            r["status"] == "healthy"
            for r in results.values()
        )

        results["overall"] = {
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": datetime.now().isoformat()
        }

        return results

    def get_all_status(self) -> Dict:
        """Получение полного статуса всех систем"""
        status = {
            "postgresql": {
                "health": self.health_status["postgresql"],
                "replication": None
            },
            "redis": {
                "health": self.health_status["redis"],
                "sentinel": None
            },
            "qdrant": {
                "health": self.health_status["qdrant"],
                "cluster": None
            }
        }

        # Get replication status (sync)
        try:
            loop = asyncio.get_event_loop()
            status["postgresql"]["replication"] = loop.run_until_complete(
                self.get_postgresql_replication_status()
            )
        except:
            pass

        # Get Sentinel status
        try:
            status["redis"]["sentinel"] = self.get_redis_sentinel_status()
        except:
            pass

        # Get Qdrant cluster status
        try:
            status["qdrant"]["cluster"] = self.get_qdrant_cluster_status()
        except:
            pass

        return status

    # =========================================================================
    # Monitoring & Alerts
    # =========================================================================

    async def start_monitoring(self, interval: int = 30):
        """Запуск постоянного мониторинга"""
        logger.info(f"Starting HA monitoring (interval: {interval}s)")

        while True:
            try:
                health = await self.check_all_health()

                # Check for alerts
                self._check_alerts(health)

                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(interval)

    def _check_alerts(self, health: Dict):
        """Проверка условий для алертов"""
        # PostgreSQL alerts
        if health["postgresql"]["status"] == "unhealthy":
            self._send_alert("CRITICAL", "PostgreSQL", "Database is unhealthy")
        elif health["postgresql"].get("latency_ms", 0) > 100:
            self._send_alert("WARNING", "PostgreSQL", f"High latency: {health['postgresql']['latency_ms']}ms")

        # Redis alerts
        if health["redis"]["status"] == "unhealthy":
            self._send_alert("CRITICAL", "Redis", "Redis is unhealthy")
        elif health["redis"].get("memory_usage_percent", 0) > 90:
            self._send_alert("WARNING", "Redis", f"High memory usage: {health['redis']['memory_usage_percent']}%")

        # Qdrant alerts
        if health["qdrant"]["status"] == "unhealthy":
            self._send_alert("CRITICAL", "Qdrant", "Qdrant is unhealthy")

    def _send_alert(self, level: str, component: str, message: str):
        """Отправка алерта"""
        logger.warning(f"[ALERT] [{level}] {component}: {message}")
        # TODO: Интеграция с alerting system (PagerDuty, Slack, etc.)

    # =========================================================================
    # Cleanup
    # =========================================================================

    async def close(self):
        """Закрытие всех соединений"""
        if self.pg_pool:
            await self.pg_pool.close()

        if self.redis_master:
            self.redis_master.close()

        if self.qdrant_client:
            self.qdrant_client.close()

        logger.info("All HA connections closed")


# Global instance
_ha_manager: Optional[DatabaseHAManager] = None


def get_ha_manager() -> DatabaseHAManager:
    """Получение глобального экземпляра HA Manager"""
    global _ha_manager

    if _ha_manager is None:
        _ha_manager = DatabaseHAManager()

    return _ha_manager


async def initialize_all_ha():
    """Инициализация всех HA систем"""
    manager = get_ha_manager()

    await manager.init_postgresql()
    manager.init_redis_sentinel()
    manager.init_qdrant_cluster()

    # Initial health check
    health = await manager.check_all_health()
    logger.info(f"HA initialization complete. Status: {health['overall']['status']}")

    return health


# CLI for testing
if __name__ == "__main__":
    import sys

    async def main():
        # Initialize
        health = await initialize_all_ha()
        print("=" * 60)
        print("HA INITIALIZATION COMPLETE")
        print("=" * 60)

        # Show status
        manager = get_ha_manager()
        status = manager.get_all_status()

        print("\nPostgreSQL:")
        print(f"  Status: {status['postgresql']['health']['status']}")
        if status['postgresql']['replication']:
            print(f"  Replicas: {status['postgresql']['replication']['replica_count']}")

        print("\nRedis:")
        print(f"  Status: {status['redis']['health']['status']}")
        if status['redis']['sentinel']:
            print(f"  Slaves: {status['redis']['sentinel']['slave_count']}")
            print(f"  Sentinels: {status['redis']['sentinel']['sentinel_count']}")

        print("\nQdrant:")
        print(f"  Status: {status['qdrant']['health']['status']}")
        if status['qdrant']['cluster']:
            print(f"  Collections: {status['qdrant']['cluster']['total_collections']}")

        print("\n" + "=" * 60)

        # Start monitoring if requested
        if "--monitor" in sys.argv:
            print("Starting continuous monitoring...")
            await manager.start_monitoring()
        else:
            await manager.close()

    asyncio.run(main())
