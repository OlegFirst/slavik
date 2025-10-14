"""
Database queries for System BCM Service
Provides async database query functions for management API
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncpg
from config import settings
import logging

logger = logging.getLogger(__name__)

# Database connection pool
_pool: Optional[asyncpg.Pool] = None

async def get_db_pool() -> asyncpg.Pool:
    """Get or create database connection pool"""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            min_size=5,
            max_size=settings.POSTGRES_POOL_SIZE
        )
    return _pool

async def close_db_pool():
    """Close database connection pool"""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None

# Dashboard Statistics
async def get_dashboard_stats() -> Dict[str, Any]:
    """Get comprehensive dashboard statistics"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # Cycle statistics
        cycle_stats = await conn.fetchrow("""
            SELECT
                COUNT(*) as total_cycles,
                COUNT(*) FILTER (WHERE status = 'completed') as successful_cycles,
                COUNT(*) FILTER (WHERE status = 'failed') as failed_cycles,
                AVG(rto_compliance_rate) as avg_rto_compliance,
                MAX(completed_at) as last_cycle_time
            FROM system_bcm_cycles
        """)

        # Recovery statistics
        recovery_stats = await conn.fetchrow("""
            SELECT
                COUNT(*) as total_recoveries,
                COUNT(*) FILTER (WHERE success = true) as successful_recoveries,
                AVG(CASE WHEN rto_met THEN 100.0 ELSE 0.0 END) as rto_compliance_rate
            FROM system_bcm_recovery_executions
        """)

        # Learning statistics
        learning_stats = await conn.fetchrow("""
            SELECT
                COUNT(*) as total_insights,
                COUNT(*) FILTER (WHERE status = 'pending') as insights_pending,
                COUNT(*) FILTER (WHERE applied = true) as insights_applied
            FROM system_bcm_insights
        """)

        # Improvement statistics
        improvement_stats = await conn.fetchrow("""
            SELECT
                COUNT(*) as total_improvements,
                AVG(effectiveness_score) as avg_effectiveness
            FROM system_bcm_improvements
        """)

        # Platform health
        health_stats = await conn.fetchrow("""
            SELECT
                COUNT(*) FILTER (WHERE status = 'healthy') as healthy_services,
                COUNT(*) as total_services
            FROM system_bcm_platform_health
            WHERE last_check > NOW() - INTERVAL '5 minutes'
        """)

        # Calculate derived metrics
        total_cycles = cycle_stats['total_cycles'] or 0
        successful_cycles = cycle_stats['successful_cycles'] or 0
        success_rate = (successful_cycles / total_cycles * 100) if total_cycles > 0 else 0

        total_recoveries = recovery_stats['total_recoveries'] or 0
        successful_recoveries = recovery_stats['successful_recoveries'] or 0
        recovery_success_rate = (successful_recoveries / total_recoveries * 100) if total_recoveries > 0 else 0

        healthy_services = health_stats['healthy_services'] or 0
        total_services = health_stats['total_services'] or 12  # Default to 12 services
        platform_health_score = (healthy_services / total_services * 100) if total_services > 0 else 0

        # Determine current status
        if platform_health_score >= 90:
            current_status = "healthy"
        elif platform_health_score >= 70:
            current_status = "degraded"
        else:
            current_status = "critical"

        # Calculate next cycle time (24 hours from last cycle)
        last_cycle_time = cycle_stats['last_cycle_time']
        next_cycle_time = last_cycle_time + timedelta(hours=24) if last_cycle_time else None

        return {
            "total_cycles": total_cycles,
            "successful_cycles": successful_cycles,
            "failed_cycles": cycle_stats['failed_cycles'] or 0,
            "success_rate": round(success_rate, 2),
            "total_recoveries": total_recoveries,
            "successful_recoveries": successful_recoveries,
            "recovery_success_rate": round(recovery_success_rate, 2),
            "rto_compliance_rate": round(recovery_stats['rto_compliance_rate'] or 0, 2),
            "total_insights": learning_stats['total_insights'] or 0,
            "insights_pending": learning_stats['insights_pending'] or 0,
            "insights_applied": learning_stats['insights_applied'] or 0,
            "total_improvements": improvement_stats['total_improvements'] or 0,
            "avg_improvement_effectiveness": round(improvement_stats['avg_effectiveness'] or 0, 2),
            "healthy_services": healthy_services,
            "total_services": total_services,
            "platform_health_score": round(platform_health_score, 2),
            "current_status": current_status,
            "last_cycle_time": last_cycle_time,
            "next_cycle_time": next_cycle_time
        }

# BCM Cycles
async def get_recent_cycles(limit: int = 50, offset: int = 0, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get recent BCM cycles"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        query = """
            SELECT
                id, cycle_id, started_at, completed_at, duration_seconds, status,
                insights_generated, improvements_applied, rto_compliance_rate, learning_effectiveness
            FROM system_bcm_cycles
        """

        if status_filter:
            query += f" WHERE status = $3"
            params = [limit, offset, status_filter]
        else:
            params = [limit, offset]

        query += " ORDER BY started_at DESC LIMIT $1 OFFSET $2"

        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]

async def get_cycle_by_id(cycle_id: str) -> Optional[Dict[str, Any]]:
    """Get specific BCM cycle by ID"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT * FROM system_bcm_cycles WHERE cycle_id = $1
        """, cycle_id)
        return dict(row) if row else None

# Recovery Executions
async def get_recent_recoveries(
    limit: int = 50,
    offset: int = 0,
    procedure_filter: Optional[str] = None,
    status_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get recent recovery executions"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        conditions = []
        params = []
        param_idx = 1

        if procedure_filter:
            conditions.append(f"procedure_name = ${param_idx}")
            params.append(procedure_filter)
            param_idx += 1

        if status_filter:
            conditions.append(f"status = ${param_idx}")
            params.append(status_filter)
            param_idx += 1

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

        params.extend([limit, offset])
        limit_idx = param_idx
        offset_idx = param_idx + 1

        query = f"""
            SELECT
                id, recovery_id, procedure_name, triggered_at, completed_at, status,
                duration_seconds, target_rto_seconds, rto_met, success
            FROM system_bcm_recovery_executions
            {where_clause}
            ORDER BY triggered_at DESC
            LIMIT ${limit_idx} OFFSET ${offset_idx}
        """

        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]

async def get_recovery_by_id(recovery_id: str) -> Optional[Dict[str, Any]]:
    """Get specific recovery execution by ID"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT * FROM system_bcm_recovery_executions WHERE recovery_id = $1
        """, recovery_id)
        return dict(row) if row else None

# Insights
async def get_recent_insights(
    limit: int = 100,
    offset: int = 0,
    status_filter: Optional[str] = None,
    type_filter: Optional[str] = None,
    priority_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get recent insights"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        conditions = []
        params = []
        param_idx = 1

        if status_filter:
            conditions.append(f"status = ${param_idx}")
            params.append(status_filter)
            param_idx += 1

        if type_filter:
            conditions.append(f"type = ${param_idx}")
            params.append(type_filter)
            param_idx += 1

        if priority_filter:
            conditions.append(f"priority = ${param_idx}")
            params.append(priority_filter)
            param_idx += 1

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

        params.extend([limit, offset])
        limit_idx = param_idx
        offset_idx = param_idx + 1

        query = f"""
            SELECT
                id, insight_id, generated_at, type, category, severity, title, description,
                evidence, recommendations, status, confidence_score, priority, applied,
                applied_at, effectiveness_score
            FROM system_bcm_insights
            {where_clause}
            ORDER BY generated_at DESC
            LIMIT ${limit_idx} OFFSET ${offset_idx}
        """

        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]

async def get_insight_by_id(insight_id: str) -> Optional[Dict[str, Any]]:
    """Get specific insight by ID"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT * FROM system_bcm_insights WHERE insight_id = $1
        """, insight_id)
        return dict(row) if row else None

# Platform Health
async def get_platform_health_current() -> List[Dict[str, Any]]:
    """Get current platform health for all services"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT
                service_name, status, response_time_ms, last_check, tier,
                dependency_level, error_message
            FROM system_bcm_platform_health
            WHERE last_check > NOW() - INTERVAL '5 minutes'
            ORDER BY dependency_level ASC, service_name ASC
        """)
        return [dict(row) for row in rows]

async def get_platform_health_history(service_filter: Optional[str] = None, hours: int = 24) -> List[Dict[str, Any]]:
    """Get platform health history"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        if service_filter:
            query = """
                SELECT service_name, status, response_time_ms, last_check
                FROM system_bcm_platform_health
                WHERE service_name = $1 AND last_check > NOW() - INTERVAL '$2 hours'
                ORDER BY last_check ASC
            """
            params = [service_filter, hours]
        else:
            query = """
                SELECT service_name, status, response_time_ms, last_check
                FROM system_bcm_platform_health
                WHERE last_check > NOW() - INTERVAL '$1 hours'
                ORDER BY last_check ASC
            """
            params = [hours]

        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]

# Patterns
async def get_recent_patterns(limit: int = 50, offset: int = 0, type_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get recent detected patterns"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        if type_filter:
            query = """
                SELECT
                    id, pattern_id, detected_at, pattern_type, description, frequency,
                    confidence_score, impact_level, related_services, time_pattern
                FROM system_bcm_patterns
                WHERE pattern_type = $3
                ORDER BY detected_at DESC
                LIMIT $1 OFFSET $2
            """
            params = [limit, offset, type_filter]
        else:
            query = """
                SELECT
                    id, pattern_id, detected_at, pattern_type, description, frequency,
                    confidence_score, impact_level, related_services, time_pattern
                FROM system_bcm_patterns
                ORDER BY detected_at DESC
                LIMIT $1 OFFSET $2
            """
            params = [limit, offset]

        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]

# Improvements
async def get_recent_improvements(limit: int = 50, offset: int = 0, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get recent applied improvements"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        if status_filter:
            query = """
                SELECT
                    id, improvement_id, applied_at, type, description, based_on_insight_id,
                    confidence_score, priority, changes_made, expected_impact, actual_impact,
                    effectiveness_score, status
                FROM system_bcm_improvements
                WHERE status = $3
                ORDER BY applied_at DESC
                LIMIT $1 OFFSET $2
            """
            params = [limit, offset, status_filter]
        else:
            query = """
                SELECT
                    id, improvement_id, applied_at, type, description, based_on_insight_id,
                    confidence_score, priority, changes_made, expected_impact, actual_impact,
                    effectiveness_score, status
                FROM system_bcm_improvements
                ORDER BY applied_at DESC
                LIMIT $1 OFFSET $2
            """
            params = [limit, offset]

        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]

# System Metrics
async def get_system_metrics() -> Dict[str, Any]:
    """Get current system metrics"""
    import psutil
    from datetime import datetime

    # Get process info
    process = psutil.Process()
    cpu_percent = process.cpu_percent(interval=0.1)
    memory_info = process.memory_info()
    memory_mb = memory_info.rss / 1024 / 1024
    memory_percent = process.memory_percent()

    # Get uptime
    create_time = datetime.fromtimestamp(process.create_time())
    uptime = (datetime.now() - create_time).total_seconds() / 3600  # hours

    # Get connection pool info
    pool = await get_db_pool()
    db_pool_size = pool.get_size() if pool else 0

    # Get Redis info (if available)
    eventbus_queue_size = 0
    try:
        from infrastructure.eventbus import get_eventbus
        eventbus = get_eventbus()
        if eventbus and hasattr(eventbus, 'get_queue_size'):
            eventbus_queue_size = await eventbus.get_queue_size()
    except:
        pass

    # Simulate response time (would be calculated from actual requests)
    response_time_ms = 350.0  # Default from performance tests

    return {
        "timestamp": datetime.utcnow(),
        "cpu_usage_percent": round(cpu_percent, 2),
        "memory_usage_mb": round(memory_mb, 2),
        "memory_usage_percent": round(memory_percent, 2),
        "active_connections": 0,  # Would track WebSocket connections
        "eventbus_queue_size": eventbus_queue_size,
        "database_pool_size": db_pool_size,
        "response_time_ms": response_time_ms,
        "uptime_hours": round(uptime, 2)
    }

# Export functions
__all__ = [
    "get_db_pool",
    "close_db_pool",
    "get_dashboard_stats",
    "get_recent_cycles",
    "get_cycle_by_id",
    "get_recent_recoveries",
    "get_recovery_by_id",
    "get_recent_insights",
    "get_insight_by_id",
    "get_platform_health_current",
    "get_platform_health_history",
    "get_recent_patterns",
    "get_recent_improvements",
    "get_system_metrics"
]
