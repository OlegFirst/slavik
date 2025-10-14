"""
Database Intelligence Service REST API

FastAPI application providing database monitoring and optimization endpoints.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import logging

from db_intelligence_service import (
    get_db_intelligence,
    start_db_intelligence,
    stop_db_intelligence
)

logger = logging.getLogger(__name__)

# =============================================================================
# FASTAPI APP
# =============================================================================

app = FastAPI(
    title="Database Intelligence Service",
    description="AI-powered database monitoring, optimization, and management",
    version="1.0.0"
)


# =============================================================================
# MODELS
# =============================================================================

class QueryAnalysisRequest(BaseModel):
    """Request model for query analysis"""
    query: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    postgres_connected: bool
    redis_connected: bool
    rabbitmq_connected: bool
    connection_pool_ok: bool
    slow_queries_count: int


# =============================================================================
# LIFECYCLE
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Start DB Intelligence service on app startup"""
    logger.info("Starting Database Intelligence Service...")
    await start_db_intelligence()


@app.on_event("shutdown")
async def shutdown_event():
    """Stop DB Intelligence service on app shutdown"""
    logger.info("Shutting down Database Intelligence Service...")
    await stop_db_intelligence()


# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "service": "Database Intelligence Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "slow_queries": "/slow-queries",
            "suggestions": "/suggestions",
            "analyze": "/analyze",
            "tables": "/tables"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Get database health status

    Returns comprehensive health information including:
    - Database connectivity
    - Connection pool status
    - System resources
    - Slow queries count
    """
    try:
        service = get_db_intelligence()
        health = await service.get_health()
        return JSONResponse(content=health)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics", tags=["Monitoring"])
async def get_metrics():
    """
    Get service metrics summary

    Returns:
    - Total queries tracked
    - Slow queries count
    - Optimization suggestions count
    - Service configuration
    """
    try:
        service = get_db_intelligence()
        metrics = await service.get_metrics_summary()
        return JSONResponse(content=metrics)
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/query-metrics", tags=["Monitoring"])
async def get_query_metrics(
    limit: int = Query(20, description="Number of queries to return", ge=1, le=100)
):
    """
    Get query performance metrics

    Returns metrics for top queries by average execution time:
    - Query text
    - Execution count
    - Average/min/max duration
    - Total duration
    """
    try:
        service = get_db_intelligence()
        metrics = await service.get_query_metrics(limit=limit)
        return JSONResponse(content={"queries": metrics, "total": len(metrics)})
    except Exception as e:
        logger.error(f"Failed to get query metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/slow-queries", tags=["Monitoring"])
async def get_slow_queries(
    limit: int = Query(10, description="Number of slow queries to return", ge=1, le=50)
):
    """
    Get list of slow queries

    Returns queries exceeding the slow query threshold (default 1000ms):
    - Query text
    - Execution statistics
    - Performance metrics
    """
    try:
        service = get_db_intelligence()
        slow_queries = await service.get_slow_queries(limit=limit)
        return JSONResponse(content={
            "slow_queries": slow_queries,
            "total": len(slow_queries),
            "threshold_ms": service.slow_query_threshold_ms
        })
    except Exception as e:
        logger.error(f"Failed to get slow queries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/suggestions", tags=["Optimization"])
async def get_optimization_suggestions(
    limit: int = Query(10, description="Number of suggestions to return", ge=1, le=50)
):
    """
    Get query optimization suggestions

    Returns AI-powered optimization suggestions:
    - Issue type (missing index, full table scan, etc.)
    - Severity (critical, warning, info)
    - Suggested fix
    - Estimated improvement
    """
    try:
        service = get_db_intelligence()
        suggestions = await service.get_optimization_suggestions(limit=limit)
        return JSONResponse(content={
            "suggestions": suggestions,
            "total": len(suggestions)
        })
    except Exception as e:
        logger.error(f"Failed to get suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze", tags=["Optimization"])
async def analyze_query(request: QueryAnalysisRequest):
    """
    Analyze a specific query

    Performs EXPLAIN ANALYZE and provides:
    - Execution plan
    - Query cost
    - Optimization suggestions
    - Index recommendations

    **Note:** This executes the query with EXPLAIN ANALYZE
    """
    try:
        service = get_db_intelligence()
        analysis = await service.analyze_query(request.query)
        return JSONResponse(content=analysis)
    except Exception as e:
        logger.error(f"Query analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tables", tags=["Monitoring"])
async def get_table_statistics():
    """
    Get table size and statistics

    Returns for each table:
    - Schema and table name
    - Total size
    - Row count
    - Dead rows
    - Last vacuum/analyze timestamp
    """
    try:
        service = get_db_intelligence()
        tables = await service.get_table_statistics()
        return JSONResponse(content={
            "tables": tables,
            "total": len(tables)
        })
    except Exception as e:
        logger.error(f"Failed to get table statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/config", tags=["Configuration"])
async def get_configuration():
    """
    Get service configuration

    Returns current service settings:
    - Monitoring interval
    - Slow query threshold
    - Max stored metrics
    """
    service = get_db_intelligence()
    return {
        "monitoring_interval_seconds": service.monitoring_interval,
        "slow_query_threshold_ms": service.slow_query_threshold_ms,
        "max_stored_metrics": service.max_stored_metrics
    }


@app.put("/config", tags=["Configuration"])
async def update_configuration(
    monitoring_interval: Optional[int] = Query(None, description="Monitoring interval in seconds", ge=10, le=3600),
    slow_query_threshold_ms: Optional[int] = Query(None, description="Slow query threshold in ms", ge=100, le=60000)
):
    """
    Update service configuration

    Allows dynamic configuration changes:
    - monitoring_interval: How often to collect metrics
    - slow_query_threshold_ms: When to flag queries as slow
    """
    service = get_db_intelligence()

    if monitoring_interval is not None:
        service.monitoring_interval = monitoring_interval

    if slow_query_threshold_ms is not None:
        service.slow_query_threshold_ms = slow_query_threshold_ms

    return {
        "message": "Configuration updated successfully",
        "config": {
            "monitoring_interval_seconds": service.monitoring_interval,
            "slow_query_threshold_ms": service.slow_query_threshold_ms
        }
    }


# =============================================================================
# PROMETHEUS METRICS ENDPOINT
# =============================================================================

@app.get("/metrics/prometheus", tags=["Monitoring"])
async def prometheus_metrics():
    """
    Prometheus-compatible metrics endpoint

    Exports metrics in Prometheus format for scraping
    """
    try:
        service = get_db_intelligence()
        health = await service.get_health()
        metrics_summary = await service.get_metrics_summary()

        # Generate Prometheus metrics
        metrics = []

        # Health status (1 = healthy, 0.5 = degraded, 0 = unhealthy)
        status_value = {"healthy": 1, "degraded": 0.5, "unhealthy": 0}.get(health["status"], 0)
        metrics.append(f'db_health_status {status_value}')

        # Connection status
        metrics.append(f'db_postgres_connected {int(health["postgres_connected"])}')
        metrics.append(f'db_redis_connected {int(health["redis_connected"])}')
        metrics.append(f'db_rabbitmq_connected {int(health["rabbitmq_connected"])}')

        # Counts
        metrics.append(f'db_slow_queries_count {health["slow_queries_count"]}')
        metrics.append(f'db_active_connections {health["active_connections"]}')
        metrics.append(f'db_queries_tracked_total {metrics_summary["total_queries_tracked"]}')
        metrics.append(f'db_optimization_suggestions_total {metrics_summary["optimization_suggestions_count"]}')

        # System resources
        metrics.append(f'db_cpu_percent {health["cpu_percent"]}')
        metrics.append(f'db_memory_percent {health["memory_percent"]}')
        metrics.append(f'db_disk_usage_percent {health["disk_usage_percent"]}')

        return "\n".join(metrics)

    except Exception as e:
        logger.error(f"Failed to generate Prometheus metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# ADMIN OPERATIONS
# =============================================================================

class AdminCommand(BaseModel):
    """Admin command request"""
    command_type: str  # vacuum, analyze, reindex, create_index, kill_query
    parameters: Dict[str, Any]
    dry_run: bool = False
    reason: str = "Manual admin operation"


@app.post("/admin/execute", tags=["Admin"])
async def execute_admin_command(command: AdminCommand):
    """
    Execute database administration command

    CLI Access to database tools via REST API.

    Supported commands:
    - vacuum_table: Run VACUUM on table
    - analyze_table: Update table statistics
    - create_index: Create database index
    - reindex_table: Rebuild table indexes
    - kill_query: Terminate query by PID

    Examples:

    ```bash
    # VACUUM table
    curl -X POST http://localhost:8050/admin/execute \\
      -H "Content-Type: application/json" \\
      -d '{
        "command_type": "vacuum_table",
        "parameters": {"schema": "public", "table": "organizations", "full": false},
        "reason": "Cleanup dead tuples"
      }'

    # Create index
    curl -X POST http://localhost:8050/admin/execute \\
      -H "Content-Type: application/json" \\
      -d '{
        "command_type": "create_index",
        "parameters": {"table": "workflows", "column": "status", "concurrent": true},
        "reason": "Optimize status queries"
      }'

    # Kill long-running query
    curl -X POST http://localhost:8050/admin/execute \\
      -H "Content-Type: application/json" \\
      -d '{
        "command_type": "kill_query",
        "parameters": {"pid": 12345},
        "reason": "Query timeout"
      }'
    ```
    """
    try:
        from command_handler import CommandHandler
        from orchestrator_integration import OrchestratorCommand
        from datetime import datetime
        import uuid

        service = get_db_intelligence()

        # Create command object
        orchestrator_command = OrchestratorCommand(
            command_id=str(uuid.uuid4()),
            command_type=command.command_type,
            parameters=command.parameters,
            priority="normal",
            requested_by="manual_cli",
            timestamp=datetime.now()
        )

        # Initialize command handler if not exists
        if not service.command_handler:
            service.command_handler = CommandHandler(service)

        # Dry run mode - just validate
        if command.dry_run:
            return {
                "status": "validated",
                "command": command.command_type,
                "parameters": command.parameters,
                "message": "Dry run - command would be executed with these parameters",
                "warning": "Set dry_run=false to execute"
            }

        # Execute command
        logger.info(f"🔧 Executing admin command: {command.command_type}")
        result = await service.command_handler.handle_command(orchestrator_command)

        return {
            "status": result.status,
            "command_id": result.command_id,
            "command_type": command.command_type,
            "result": result.result,
            "error": result.error,
            "execution_time_ms": result.execution_time_ms,
            "timestamp": result.timestamp.isoformat(),
            "reason": command.reason
        }

    except Exception as e:
        logger.error(f"Admin command execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/running-queries", tags=["Admin"])
async def get_running_queries():
    """
    Get list of currently running queries

    Useful for identifying long-running or problematic queries.
    """
    try:
        from infrastructure.database import get_database
        from sqlalchemy import text

        db = await get_database()
        async with db.get_session() as session:
            result = await session.execute(text("""
                SELECT
                    pid,
                    usename,
                    application_name,
                    client_addr,
                    state,
                    query,
                    EXTRACT(EPOCH FROM (NOW() - query_start)) * 1000 as duration_ms,
                    wait_event_type,
                    wait_event
                FROM pg_stat_activity
                WHERE state = 'active'
                    AND pid != pg_backend_pid()
                    AND query NOT LIKE '%pg_stat_activity%'
                ORDER BY query_start ASC
                LIMIT 50
            """))

            rows = result.fetchall()
            return {
                "running_queries": [
                    {
                        "pid": row[0],
                        "user": row[1],
                        "application": row[2],
                        "client_addr": str(row[3]) if row[3] else None,
                        "state": row[4],
                        "query": row[5][:500],  # Truncate long queries
                        "duration_ms": float(row[6]) if row[6] else 0,
                        "wait_event_type": row[7],
                        "wait_event": row[8]
                    }
                    for row in rows
                ],
                "count": len(rows)
            }

    except Exception as e:
        logger.error(f"Failed to get running queries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/locks", tags=["Admin"])
async def get_database_locks():
    """
    Get list of database locks

    Identifies blocking queries and deadlocks.
    """
    try:
        from infrastructure.database import get_database
        from sqlalchemy import text

        db = await get_database()
        async with db.get_session() as session:
            result = await session.execute(text("""
                SELECT
                    l.locktype,
                    l.database,
                    l.relation::regclass as relation,
                    l.page,
                    l.tuple,
                    l.virtualxid,
                    l.transactionid,
                    l.classid,
                    l.objid,
                    l.objsubid,
                    l.virtualtransaction,
                    l.pid,
                    l.mode,
                    l.granted,
                    a.query
                FROM pg_locks l
                LEFT JOIN pg_stat_activity a ON l.pid = a.pid
                WHERE NOT l.granted
                ORDER BY l.pid
                LIMIT 50
            """))

            rows = result.fetchall()
            return {
                "locks": [
                    {
                        "locktype": row[0],
                        "database": row[1],
                        "relation": str(row[2]) if row[2] else None,
                        "pid": row[11],
                        "mode": row[12],
                        "granted": row[13],
                        "query": row[14][:200] if row[14] else None
                    }
                    for row in rows
                ],
                "count": len(rows),
                "message": "No locks found" if len(rows) == 0 else f"{len(rows)} locks detected"
            }

    except Exception as e:
        logger.error(f"Failed to get database locks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# ARCHIVE SERVICE ENDPOINTS
# =============================================================================

@app.get("/archive/status")
async def get_archive_status():
    """Get archive status for all configured tables"""
    try:
        from archive_service import ArchiveService

        async with get_db_session() as session:
            service = ArchiveService(session)
            return await service.check_archive_status()

    except Exception as e:
        logger.error(f"Failed to get archive status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/archive/configs")
async def get_archive_configs():
    """Get all archive configurations"""
    try:
        from archive_service import ArchiveService

        async with get_db_session() as session:
            service = ArchiveService(session)
            return await service.get_archive_configs()

    except Exception as e:
        logger.error(f"Failed to get archive configs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/archive/export/{schema}/{table}")
async def export_to_archive(
    schema: str,
    table: str,
    days_old: int = 90,
    dry_run: bool = True
):
    """Export old data to archive"""
    try:
        from datetime import datetime, timedelta
        from archive_service import ArchiveService

        date_threshold = datetime.now() - timedelta(days=days_old)

        async with get_db_session() as session:
            service = ArchiveService(session)
            return await service.export_to_archive(schema, table, date_threshold, dry_run)

    except Exception as e:
        logger.error(f"Failed to export to archive: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/archive/list")
async def list_archives(
    schema: str = None,
    table: str = None,
    limit: int = 100
):
    """List archives from catalog"""
    try:
        from archive_service import ArchiveService

        async with get_db_session() as session:
            service = ArchiveService(session)
            return await service.list_archives(schema, table, limit)

    except Exception as e:
        logger.error(f"Failed to list archives: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/archive/stats")
async def get_archive_stats():
    """Get archive statistics"""
    try:
        from archive_service import ArchiveService

        async with get_db_session() as session:
            service = ArchiveService(session)
            return await service.get_archive_stats()

    except Exception as e:
        logger.error(f"Failed to get archive stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/archive/restore/{filename}")
async def restore_from_archive(
    filename: str,
    dry_run: bool = True
):
    """Restore data from archive"""
    try:
        from archive_service import ArchiveService

        async with get_db_session() as session:
            service = ArchiveService(session)
            return await service.restore_from_archive(filename, dry_run)

    except Exception as e:
        logger.error(f"Failed to restore from archive: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# PARTITIONING ENDPOINTS
# =============================================================================

@app.get("/partitioning/status")
async def get_partitioning_status():
    """Get partitioning status for all configured tables"""
    try:
        from partitioning_manager import PartitioningManager

        async with get_db_session() as session:
            manager = PartitioningManager(session)
            return await manager.check_partitioning_status()

    except Exception as e:
        logger.error(f"Failed to get partitioning status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/partitioning/configs")
async def get_partitioning_configs():
    """Get all partitioning configurations"""
    try:
        from partitioning_manager import PartitioningManager

        async with get_db_session() as session:
            manager = PartitioningManager(session)
            return await manager.get_partitioning_configs()

    except Exception as e:
        logger.error(f"Failed to get partitioning configs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/partitioning/create/{schema}/{table}")
async def create_partitions(
    schema: str,
    table: str,
    months_ahead: int = 3,
    dry_run: bool = True
):
    """Create future partitions for a table"""
    try:
        from partitioning_manager import PartitioningManager

        async with get_db_session() as session:
            manager = PartitioningManager(session)
            return await manager.create_partitions(schema, table, months_ahead, dry_run)

    except Exception as e:
        logger.error(f"Failed to create partitions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/partitioning/drop-old/{schema}/{table}")
async def drop_old_partitions(
    schema: str,
    table: str,
    dry_run: bool = True
):
    """Drop old partitions that exceed retention"""
    try:
        from partitioning_manager import PartitioningManager

        async with get_db_session() as session:
            manager = PartitioningManager(session)
            return await manager.drop_old_partitions(schema, table, dry_run)

    except Exception as e:
        logger.error(f"Failed to drop old partitions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/partitioning/stats/{schema}/{table}")
async def get_partition_stats(schema: str, table: str):
    """Get statistics for all partitions of a table"""
    try:
        from partitioning_manager import PartitioningManager

        async with get_db_session() as session:
            manager = PartitioningManager(session)
            return await manager.get_partition_stats(schema, table)

    except Exception as e:
        logger.error(f"Failed to get partition stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# DATA RETENTION ENDPOINTS
# =============================================================================

@app.get("/retention/status")
async def get_retention_status():
    """Get retention status for all tables"""
    try:
        from retention_manager import DataRetentionManager

        async with get_db_session() as session:
            manager = DataRetentionManager(session)
            return await manager.check_retention_status()

    except Exception as e:
        logger.error(f"Failed to get retention status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/retention/policies")
async def get_retention_policies():
    """Get all retention policies"""
    try:
        from retention_manager import DataRetentionManager

        async with get_db_session() as session:
            manager = DataRetentionManager(session)
            return await manager.get_retention_policies()

    except Exception as e:
        logger.error(f"Failed to get retention policies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retention/archive/{schema}/{table}")
async def archive_table_data(
    schema: str,
    table: str,
    dry_run: bool = True
):
    """Archive old data from table"""
    try:
        from retention_manager import DataRetentionManager

        async with get_db_session() as session:
            manager = DataRetentionManager(session)
            return await manager.archive_old_data(schema, table, dry_run)

    except Exception as e:
        logger.error(f"Failed to archive data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retention/cleanup/{schema}/{table}")
async def cleanup_table_data(
    schema: str,
    table: str,
    dry_run: bool = True
):
    """Delete old data that exceeded retention period"""
    try:
        from retention_manager import DataRetentionManager

        async with get_db_session() as session:
            manager = DataRetentionManager(session)
            return await manager.cleanup_old_data(schema, table, dry_run)

    except Exception as e:
        logger.error(f"Failed to cleanup data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )
