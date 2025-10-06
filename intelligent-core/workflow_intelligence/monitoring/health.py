"""
Health Checker for Workflow Intelligence
Monitors component health and dependencies
"""

from typing import Dict, Any, Optional
from datetime import datetime
import asyncio


class HealthChecker:
    """Health monitoring for Workflow Intelligence components"""

    def __init__(self):
        self.last_check: Optional[datetime] = None
        self.components_status: Dict[str, bool] = {}

    async def check_database(self, storage_adapter) -> bool:
        """Check database connectivity and schema"""
        try:
            if not storage_adapter or not storage_adapter.pool:
                return False

            # Test connection
            async with storage_adapter.pool.acquire() as conn:
                # Check schema exists
                schema_exists = await conn.fetchval(
                    "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = 'workflow_intelligence')"
                )

                if not schema_exists:
                    return False

                # Check tables exist
                tables = await conn.fetch(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'workflow_intelligence'"
                )

                required_tables = {'workflow_contexts', 'workflow_cases', 'benchmarks'}
                existing_tables = {row['table_name'] for row in tables}

                return required_tables.issubset(existing_tables)

        except Exception as e:
            print(f"Database health check failed: {e}")
            return False

    async def check_cache(self, cache_client) -> bool:
        """Check Redis cache connectivity"""
        try:
            if not cache_client:
                return False

            # Test ping
            return await cache_client.ping()

        except Exception:
            return False

    async def check_storage_size(self, storage_adapter) -> Dict[str, int]:
        """Check storage size for each table"""
        try:
            async with storage_adapter.pool.acquire() as conn:
                sizes = {}

                tables = ['workflow_contexts', 'workflow_cases', 'benchmarks', 'ml_predictions']

                for table in tables:
                    count = await conn.fetchval(
                        f"SELECT COUNT(*) FROM workflow_intelligence.{table}"
                    )
                    sizes[table] = count

                return sizes

        except Exception as e:
            print(f"Storage size check failed: {e}")
            return {}

    async def check_connection_pool(self, storage_adapter) -> Dict[str, int]:
        """Check database connection pool status"""
        try:
            if not storage_adapter or not storage_adapter.pool:
                return {"active": 0, "idle": 0, "max": 0}

            pool = storage_adapter.pool

            return {
                "active": pool.get_size() - pool.get_idle_size(),
                "idle": pool.get_idle_size(),
                "max": pool.get_max_size()
            }

        except Exception as e:
            print(f"Connection pool check failed: {e}")
            return {"active": 0, "idle": 0, "max": 0}

    async def full_health_check(
        self,
        storage_adapter,
        cache_client=None
    ) -> Dict[str, Any]:
        """Perform full health check of all components"""

        # Run all checks concurrently
        db_healthy = await self.check_database(storage_adapter)
        cache_healthy = await self.check_cache(cache_client) if cache_client else None
        storage_sizes = await self.check_storage_size(storage_adapter)
        pool_status = await self.check_connection_pool(storage_adapter)

        # Update component status
        self.components_status = {
            "database": db_healthy,
            "cache": cache_healthy if cache_healthy is not None else True,  # Optional
            "storage": bool(storage_sizes)
        }

        self.last_check = datetime.utcnow()

        # Overall health
        overall_healthy = all([
            db_healthy,
            cache_healthy if cache_healthy is not None else True
        ])

        return {
            "status": "healthy" if overall_healthy else "unhealthy",
            "timestamp": self.last_check.isoformat(),
            "components": {
                "database": {
                    "status": "healthy" if db_healthy else "unhealthy",
                    "connection_pool": pool_status
                },
                "cache": {
                    "status": "healthy" if cache_healthy else "unhealthy" if cache_healthy is not None else "not_configured"
                },
                "storage": {
                    "status": "healthy" if storage_sizes else "unhealthy",
                    "sizes": storage_sizes
                }
            },
            "metrics": {
                "total_contexts": storage_sizes.get("workflow_contexts", 0),
                "total_cases": storage_sizes.get("workflow_cases", 0),
                "total_benchmarks": storage_sizes.get("benchmarks", 0),
                "db_connections_active": pool_status.get("active", 0),
                "db_connections_idle": pool_status.get("idle", 0)
            }
        }

    def is_healthy(self) -> bool:
        """Quick health status check"""
        return all(self.components_status.values())

    def get_status(self) -> str:
        """Get current status string"""
        if not self.components_status:
            return "unknown"

        return "healthy" if self.is_healthy() else "unhealthy"


# Global instance
health_checker = HealthChecker()
