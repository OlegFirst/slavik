"""
Database Intelligence Service

AI-powered database monitoring, optimization, and management service.
Orchestrated by AI Orchestrator as a critical infrastructure component.

Responsibilities:
- Query performance monitoring and analysis
- Automatic query optimization suggestions
- Connection pool management
- Slow query detection and alerting
- Database health monitoring
- Migration tracking and validation
- RLS policy verification
- Table statistics and index recommendations

Integration:
- Registers with AI Orchestrator as 'db-intelligence' service
- Publishes metrics to Prometheus
- Sends alerts via EventBus
- Provides REST API for queries
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import psutil

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class QueryMetrics:
    """Metrics for a single query"""
    query_hash: str
    query_text: str
    execution_count: int
    avg_duration_ms: float
    max_duration_ms: float
    min_duration_ms: float
    total_duration_ms: float
    last_executed: datetime
    slow_query: bool = False


@dataclass
class ConnectionPoolStats:
    """Connection pool statistics"""
    pool_size: int
    active_connections: int
    idle_connections: int
    waiting_connections: int
    utilization_percent: float
    timestamp: datetime


@dataclass
class DatabaseHealth:
    """Overall database health"""
    status: str  # healthy, degraded, unhealthy
    postgres_connected: bool
    redis_connected: bool
    rabbitmq_connected: bool
    connection_pool_ok: bool
    slow_queries_count: int
    active_connections: int
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    timestamp: datetime


@dataclass
class OptimizationSuggestion:
    """Query optimization suggestion"""
    query_hash: str
    query_text: str
    issue_type: str  # missing_index, full_table_scan, n_plus_one, etc.
    severity: str  # critical, warning, info
    suggestion: str
    estimated_improvement: str
    created_at: datetime


# =============================================================================
# DATABASE INTELLIGENCE SERVICE
# =============================================================================

class DatabaseIntelligenceService:
    """
    AI-Powered Database Intelligence Service

    This service monitors and optimizes database operations across the platform.
    """

    def __init__(self):
        self.service_name = "db-intelligence"
        self.version = "1.0.0"

        # Metrics storage (in-memory, can be moved to Redis later)
        self.query_metrics: Dict[str, QueryMetrics] = {}
        self.slow_queries: List[QueryMetrics] = []
        self.optimization_suggestions: List[OptimizationSuggestion] = []

        # Configuration
        self.slow_query_threshold_ms = 1000  # 1 second
        self.monitoring_interval = 60  # 1 minute
        self.max_stored_metrics = 1000

        # State
        self.monitoring_task: Optional[asyncio.Task] = None
        self.command_polling_task: Optional[asyncio.Task] = None
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.is_running = False

        # Integrations
        self.security_monitor = None  # Initialized on start
        self.ai_integration = None    # Initialized on start
        self.orchestrator_client = None  # Direct Orchestrator integration
        self.command_handler = None   # Handles Orchestrator commands

    async def start(self):
        """Start the intelligence service"""
        if self.is_running:
            logger.warning("Database Intelligence Service already running")
            return

        logger.info("🧠 Starting Database Intelligence Service...")
        self.is_running = True

        # Initialize integrations
        from security_monitor import SecurityMonitor
        from ai_integration import get_ai_integration
        from orchestrator_integration import get_orchestrator_client
        from command_handler import CommandHandler

        self.security_monitor = SecurityMonitor()
        self.ai_integration = get_ai_integration()
        self.orchestrator_client = get_orchestrator_client()
        self.command_handler = CommandHandler(self)

        # Subscribe to AI events (EventBus)
        try:
            await self.ai_integration.subscribe_to_ai_events()
            logger.info("✅ Subscribed to AI events")
        except Exception as e:
            logger.warning(f"Could not subscribe to AI events: {e}")

        # Register with Orchestrator (Direct API)
        try:
            success = await self.orchestrator_client.register()
            if success:
                logger.info("✅ Registered with AI Orchestrator")
            else:
                logger.warning("⚠️  Could not register with Orchestrator (will retry)")
        except Exception as e:
            logger.warning(f"Orchestrator registration failed: {e}")

        # Start background tasks
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.command_polling_task = asyncio.create_task(self._command_polling_loop())
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())

        logger.info("✅ Database Intelligence Service started")

    async def stop(self):
        """Stop the intelligence service"""
        logger.info("Stopping Database Intelligence Service...")
        self.is_running = False

        # Deregister from Orchestrator
        if self.orchestrator_client:
            try:
                await self.orchestrator_client.deregister()
                logger.info("✅ Deregistered from Orchestrator")
            except Exception as e:
                logger.warning(f"Deregistration failed: {e}")

        # Cancel all background tasks
        tasks = [
            self.monitoring_task,
            self.command_polling_task,
            self.heartbeat_task
        ]

        for task in tasks:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        logger.info("✅ Database Intelligence Service stopped")

    # =========================================================================
    # MONITORING
    # =========================================================================

    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                # Collect metrics
                await self._collect_metrics()

                # Analyze performance
                await self._analyze_performance()

                # Check health
                health = await self._check_health()

                # Security checks (every cycle)
                await self._run_security_checks()

                # Publish alerts if needed
                await self._publish_alerts_to_ai(health)

                await asyncio.sleep(self.monitoring_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def _collect_metrics(self):
        """Collect database metrics"""
        try:
            from infrastructure.database import get_database
            db = await get_database()

            async with db.get_session() as session:
                # Get pg_stat_statements data (if extension is available)
                try:
                    result = await session.execute(text("""
                        SELECT
                            queryid,
                            query,
                            calls,
                            mean_exec_time,
                            max_exec_time,
                            min_exec_time,
                            total_exec_time
                        FROM pg_stat_statements
                        WHERE query NOT LIKE '%pg_stat_statements%'
                        ORDER BY mean_exec_time DESC
                        LIMIT 100
                    """))

                    rows = result.fetchall()
                    for row in rows:
                        query_hash = str(row[0])
                        self.query_metrics[query_hash] = QueryMetrics(
                            query_hash=query_hash,
                            query_text=row[1][:500],  # Truncate long queries
                            execution_count=row[2],
                            avg_duration_ms=row[3],
                            max_duration_ms=row[4],
                            min_duration_ms=row[5],
                            total_duration_ms=row[6],
                            last_executed=datetime.now(),
                            slow_query=row[3] > self.slow_query_threshold_ms
                        )

                    logger.debug(f"Collected metrics for {len(rows)} queries")

                except Exception as e:
                    logger.debug(f"pg_stat_statements not available: {e}")

        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")

    async def _analyze_performance(self):
        """Analyze query performance and generate suggestions"""
        # Find slow queries
        self.slow_queries = [
            m for m in self.query_metrics.values()
            if m.slow_query
        ]

        # Generate optimization suggestions
        for query in self.slow_queries[:10]:  # Top 10 slow queries
            if not any(s.query_hash == query.query_hash for s in self.optimization_suggestions):
                suggestion = await self._generate_optimization_suggestion(query)
                if suggestion:
                    self.optimization_suggestions.append(suggestion)

        # Limit stored suggestions
        if len(self.optimization_suggestions) > 100:
            self.optimization_suggestions = self.optimization_suggestions[-100:]

    async def _generate_optimization_suggestion(
        self,
        query: QueryMetrics
    ) -> Optional[OptimizationSuggestion]:
        """Generate AI-powered optimization suggestion"""

        # Simple heuristics (can be enhanced with AI later)
        issue_type = "slow_query"
        severity = "warning"
        suggestion = ""

        if query.avg_duration_ms > 5000:
            severity = "critical"
            suggestion = "Query taking >5s. Consider adding indexes or optimizing joins."
        elif query.avg_duration_ms > 1000:
            suggestion = "Query taking >1s. Review execution plan with EXPLAIN ANALYZE."

        if "SELECT *" in query.query_text.upper():
            issue_type = "select_star"
            suggestion += " Avoid SELECT *, specify needed columns only."

        if suggestion:
            return OptimizationSuggestion(
                query_hash=query.query_hash,
                query_text=query.query_text[:200],
                issue_type=issue_type,
                severity=severity,
                suggestion=suggestion,
                estimated_improvement="20-50% faster",
                created_at=datetime.now()
            )

        return None

    async def _check_health(self) -> DatabaseHealth:
        """Check overall database health"""
        try:
            from infrastructure.database import health_check

            health_data = await health_check()

            # System resources
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Connection pool stats
            active_conns = len([m for m in self.query_metrics.values()])

            # Determine status
            status = "healthy"
            if not health_data["primary_db"].get("postgres"):
                status = "unhealthy"
            elif len(self.slow_queries) > 10:
                status = "degraded"
            elif cpu_percent > 80 or memory.percent > 90:
                status = "degraded"

            health = DatabaseHealth(
                status=status,
                postgres_connected=health_data["primary_db"].get("postgres", False),
                redis_connected=True,  # TODO: Check Redis
                rabbitmq_connected=True,  # TODO: Check RabbitMQ
                connection_pool_ok=active_conns < 100,
                slow_queries_count=len(self.slow_queries),
                active_connections=active_conns,
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage_percent=disk.percent,
                timestamp=datetime.now()
            )

            # Log warnings
            if status != "healthy":
                logger.warning(f"Database health: {status} - {health}")

            return health

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return DatabaseHealth(
                status="unhealthy",
                postgres_connected=False,
                redis_connected=False,
                rabbitmq_connected=False,
                connection_pool_ok=False,
                slow_queries_count=0,
                active_connections=0,
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_usage_percent=0.0,
                timestamp=datetime.now()
            )

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    async def get_health(self) -> Dict[str, Any]:
        """Get current database health"""
        health = await self._check_health()
        return asdict(health)

    async def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get list of slow queries"""
        return [asdict(q) for q in self.slow_queries[:limit]]

    async def get_optimization_suggestions(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get optimization suggestions"""
        return [asdict(s) for s in self.optimization_suggestions[:limit]]

    async def get_query_metrics(
        self,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get query metrics"""
        sorted_metrics = sorted(
            self.query_metrics.values(),
            key=lambda x: x.avg_duration_ms,
            reverse=True
        )
        return [asdict(m) for m in sorted_metrics[:limit]]

    async def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze a specific query and provide optimization suggestions

        Args:
            query: SQL query to analyze

        Returns:
            Analysis results with suggestions
        """
        try:
            from infrastructure.database import get_database
            db = await get_database()

            async with db.get_session() as session:
                # Get EXPLAIN ANALYZE
                result = await session.execute(text(f"EXPLAIN ANALYZE {query}"))
                explain = result.fetchall()

                analysis = {
                    "query": query,
                    "explain": [row[0] for row in explain],
                    "suggestions": [],
                    "estimated_cost": None
                }

                # Parse EXPLAIN output for insights
                explain_text = "\n".join(analysis["explain"])

                if "Seq Scan" in explain_text:
                    analysis["suggestions"].append({
                        "type": "missing_index",
                        "severity": "warning",
                        "message": "Sequential scan detected. Consider adding index."
                    })

                if "cost=" in explain_text:
                    # Extract cost
                    import re
                    match = re.search(r'cost=(\d+\.\d+)\.\.(\d+\.\d+)', explain_text)
                    if match:
                        analysis["estimated_cost"] = float(match.group(2))

                return analysis

        except Exception as e:
            logger.error(f"Query analysis failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "suggestions": []
            }

    async def get_table_statistics(self) -> List[Dict[str, Any]]:
        """Get table size and statistics"""
        try:
            from infrastructure.database import get_database
            db = await get_database()

            async with db.get_session() as session:
                result = await session.execute(text("""
                    SELECT
                        schemaname,
                        tablename,
                        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                        n_live_tup as row_count,
                        n_dead_tup as dead_rows,
                        last_vacuum,
                        last_analyze
                    FROM pg_stat_user_tables
                    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                    LIMIT 50
                """))

                rows = result.fetchall()
                return [
                    {
                        "schema": row[0],
                        "table": row[1],
                        "size": row[2],
                        "row_count": row[3],
                        "dead_rows": row[4],
                        "last_vacuum": row[5].isoformat() if row[5] else None,
                        "last_analyze": row[6].isoformat() if row[6] else None
                    }
                    for row in rows
                ]

        except Exception as e:
            logger.error(f"Failed to get table statistics: {e}")
            return []

    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        return {
            "service": self.service_name,
            "version": self.version,
            "status": "running" if self.is_running else "stopped",
            "total_queries_tracked": len(self.query_metrics),
            "slow_queries_count": len(self.slow_queries),
            "optimization_suggestions_count": len(self.optimization_suggestions),
            "monitoring_interval_seconds": self.monitoring_interval,
            "slow_query_threshold_ms": self.slow_query_threshold_ms
        }

    # =========================================================================
    # SECURITY INTEGRATION
    # =========================================================================

    async def _run_security_checks(self):
        """Run security monitoring checks"""
        if not self.security_monitor:
            return

        try:
            from infrastructure.database import get_database
            db = await get_database()

            async with db.get_session() as session:
                # Run all security checks
                alerts = await self.security_monitor.run_all_checks(
                    session,
                    self.query_metrics
                )

                # Publish critical alerts to AI
                for alert in alerts:
                    if alert.severity in ["critical", "high"]:
                        await self.ai_integration.publish_alert(
                            alert_type=alert.alert_type,
                            severity=alert.severity,
                            message=alert.message,
                            details=alert.details
                        )

                        # Notify orchestrator immediately for critical issues
                        if alert.severity == "critical":
                            await self.ai_integration.notify_orchestrator_of_critical_issue(
                                issue_type=alert.alert_type,
                                severity=alert.severity,
                                details=alert.details
                            )

        except Exception as e:
            logger.error(f"Security checks failed: {e}")

    # =========================================================================
    # AI INTEGRATION
    # =========================================================================

    async def _publish_alerts_to_ai(self, health: DatabaseHealth):
        """Publish alerts to AI Orchestrator via EventBus"""
        if not self.ai_integration:
            return

        try:
            # Health degradation
            if health.status != "healthy":
                await self.ai_integration.publish_alert(
                    alert_type="health_degraded",
                    severity="warning" if health.status == "degraded" else "critical",
                    message=f"Database health: {health.status}",
                    details=asdict(health)
                )

            # Too many slow queries
            if health.slow_queries_count > 10:
                await self.ai_integration.publish_alert(
                    alert_type="slow_queries",
                    severity="warning",
                    message=f"{health.slow_queries_count} slow queries detected",
                    details={"slow_queries": [asdict(q) for q in self.slow_queries[:10]]}
                )

            # Publish optimization suggestions to AI
            for suggestion in self.optimization_suggestions:
                if suggestion.severity == "critical":
                    # Get AI recommendation
                    ai_recommendation = await self.ai_integration.get_ai_recommendation_for_suggestion(
                        asdict(suggestion)
                    )

                    if ai_recommendation.get('should_apply') and ai_recommendation.get('confidence', 0) > 0.8:
                        # Request orchestrator to apply
                        await self.ai_integration.request_orchestrator_action(
                            action_type="apply_db_optimization",
                            action_data={
                                "suggestion": asdict(suggestion),
                                "ai_recommendation": ai_recommendation
                            },
                            priority="high"
                        )

        except Exception as e:
            logger.error(f"Failed to publish alerts to AI: {e}")

    # =========================================================================
    # ORCHESTRATOR DIRECT INTEGRATION
    # =========================================================================

    async def _command_polling_loop(self):
        """
        Poll Orchestrator for commands

        Dual integration approach:
        - EventBus for async alerts/pub-sub
        - Direct API for sync commands/orchestration
        """
        while self.is_running:
            try:
                if not self.orchestrator_client or not self.command_handler:
                    await asyncio.sleep(30)
                    continue

                # Poll for commands
                commands = await self.orchestrator_client.poll_commands()

                # Execute each command
                for command in commands:
                    logger.info(f"📥 Received command from Orchestrator: {command.command_type}")

                    # Execute command
                    result = await self.command_handler.handle_command(command)

                    # Report result back
                    await self.orchestrator_client.report_command_result(result)

                    logger.info(f"✅ Command {command.command_id} completed: {result.status}")

                # Poll every 30 seconds
                await asyncio.sleep(30)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in command polling loop: {e}")
                await asyncio.sleep(30)

    async def _heartbeat_loop(self):
        """
        Send periodic heartbeat to Orchestrator

        Keeps Orchestrator informed of service health
        """
        while self.is_running:
            try:
                if not self.orchestrator_client:
                    await asyncio.sleep(60)
                    continue

                # Get current health
                health = await self._check_health()

                # Send heartbeat
                await self.orchestrator_client.heartbeat(asdict(health))

                # Also push metrics periodically
                metrics = {
                    "query_metrics_count": len(self.query_metrics),
                    "slow_queries_count": len(self.slow_queries),
                    "optimization_suggestions_count": len(self.optimization_suggestions),
                    "health_status": health.status,
                    "cpu_percent": health.cpu_percent,
                    "memory_percent": health.memory_percent
                }
                await self.orchestrator_client.push_metrics(metrics)

                # Heartbeat every 60 seconds
                await asyncio.sleep(60)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug(f"Heartbeat failed: {e}")
                await asyncio.sleep(60)


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

# Singleton instance
_db_intelligence: Optional[DatabaseIntelligenceService] = None


def get_db_intelligence() -> DatabaseIntelligenceService:
    """Get global DB Intelligence service instance"""
    global _db_intelligence
    if _db_intelligence is None:
        _db_intelligence = DatabaseIntelligenceService()
    return _db_intelligence


async def start_db_intelligence():
    """Start DB Intelligence service"""
    service = get_db_intelligence()
    await service.start()


async def stop_db_intelligence():
    """Stop DB Intelligence service"""
    service = get_db_intelligence()
    await service.stop()
