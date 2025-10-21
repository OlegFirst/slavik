"""
Workflow Intelligence Monitoring API

Provides Prometheus metrics and monitoring endpoints for:
- Performance tracking
- Quality metrics
- Business KPIs
- Health monitoring
"""

from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from typing import Optional
from datetime import datetime, timedelta

from ..monitoring.metrics import workflow_metrics
from ..monitoring.health import health_checker

router = APIRouter(prefix="/api/v1/monitoring", tags=["Monitoring"])


# ============================================================================
# PROMETHEUS METRICS ENDPOINT
# ============================================================================

@router.get("/metrics")
async def prometheus_metrics():
    """
     Prometheus metrics endpoint

    Returns all workflow intelligence metrics in Prometheus format:
    - workflow_intelligence_actions_total
    - workflow_intelligence_action_duration_seconds
    - workflow_intelligence_db_query_duration_seconds
    - workflow_intelligence_cases_collected_total
    - workflow_intelligence_ai_advice_total
    - workflow_intelligence_errors_total
    - ... and 30+ more metrics
    """
    metrics = generate_latest()
    return Response(content=metrics, media_type=CONTENT_TYPE_LATEST)


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@router.get("/health")
async def health_check(storage_adapter=None, cache_client=None):
    """
     Health check endpoint

    Returns:
    - Overall health status
    - Component health (database, cache, storage)
    - Connection pool status
    - Storage sizes
    """

    # This would be injected via dependency injection in real service
    # For now, return structure
    if not storage_adapter:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "database": {"status": "not_initialized"},
                "cache": {"status": "not_initialized"},
                "storage": {"status": "not_initialized"}
            }
        }

    health = await health_checker.full_health_check(storage_adapter, cache_client)
    return health


@router.get("/health/live")
async def liveness_probe():
    """
     Kubernetes liveness probe

    Simple check that service is running
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}


@router.get("/health/ready")
async def readiness_probe(storage_adapter=None):
    """
     Kubernetes readiness probe

    Checks that service is ready to accept traffic
    """

    if not storage_adapter:
        return {"status": "not_ready", "reason": "storage_not_initialized"}

    db_healthy = await health_checker.check_database(storage_adapter)

    if db_healthy:
        return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
    else:
        return {"status": "not_ready", "reason": "database_unhealthy"}


# ============================================================================
# METRICS DASHBOARD ENDPOINTS
# ============================================================================

@router.get("/dashboard/performance")
async def get_performance_metrics():
    """
     Performance metrics for dashboard

    Returns:
    - Average action duration
    - Database query performance
    - Cache hit rate
    - Throughput
    """

    # These would be calculated from actual Prometheus metrics
    # For now, return structure for dashboard

    return {
        "period": "last_24h",
        "workflow_actions": {
            "total": 0,
            "avg_duration_ms": 0.0,
            "p50_ms": 0.0,
            "p95_ms": 0.0,
            "p99_ms": 0.0
        },
        "database": {
            "total_queries": 0,
            "avg_duration_ms": 0.0,
            "slow_queries": 0,
            "connection_pool_usage": 0.0
        },
        "cache": {
            "hit_rate": 0.0,
            "total_requests": 0
        },
        "throughput": {
            "actions_per_second": 0.0,
            "cases_per_hour": 0.0
        }
    }


@router.get("/dashboard/quality")
async def get_quality_metrics():
    """
     Quality metrics for dashboard

    Returns:
    - AI advice acceptance rate
    - Similar cases relevance
    - Benchmark accuracy
    - ML prediction confidence
    """

    return {
        "period": "last_7d",
        "ai_advice": {
            "total_requests": 0,
            "acceptance_rate": 0.0,
            "avg_relevance_score": 0.0
        },
        "similar_cases": {
            "avg_cases_found": 0.0,
            "avg_relevance_score": 0.0
        },
        "benchmarks": {
            "total_calculated": 0,
            "avg_sample_size": 0,
            "coverage": {
                "industries": 0,
                "org_sizes": 0
            }
        },
        "ml_predictions": {
            "total": 0,
            "avg_confidence": 0.0,
            "accuracy": 0.0
        }
    }


@router.get("/dashboard/business")
async def get_business_metrics():
    """
     Business metrics for dashboard

    Returns:
    - Cases collected
    - Learning growth
    - Platform adoption
    - Knowledge accumulation
    """

    return {
        "period": "last_30d",
        "cases": {
            "total_collected": 0,
            "success_rate": 0.0,
            "per_module": {
                "planning": 0,
                "plans": 0,
                "bia": 0,
                "compliance": 0
            }
        },
        "learning": {
            "total_cases_library": 0,
            "growth_rate": 0.0,
            "industries_covered": 0,
            "org_sizes_covered": 0
        },
        "adoption": {
            "workflows_using_wi": 0,
            "ai_advice_adoption": 0.0,
            "cross_service_queries": 0
        },
        "knowledge": {
            "total_contexts": 0,
            "total_benchmarks": 0,
            "total_predictions": 0
        }
    }


@router.get("/dashboard/errors")
async def get_error_metrics():
    """
    ️ Error tracking for dashboard

    Returns:
    - Total errors
    - Errors by type
    - Errors by module
    - Error rate trends
    """

    return {
        "period": "last_24h",
        "total_errors": 0,
        "error_rate": 0.0,
        "by_type": {
            "DatabaseError": 0,
            "ValidationError": 0,
            "NotFoundError": 0,
            "TimeoutError": 0
        },
        "by_module": {
            "planning": 0,
            "plans": 0,
            "bia": 0,
            "compliance": 0
        },
        "by_operation": {
            "save_context": 0,
            "get_similar_cases": 0,
            "calculate_benchmarks": 0,
            "ai_advice": 0
        },
        "recent_errors": []
    }


# ============================================================================
# ALERTING ENDPOINTS
# ============================================================================

@router.get("/alerts/active")
async def get_active_alerts():
    """
     Get active alerts

    Returns currently firing alerts based on thresholds
    """

    # This would check Prometheus alert status
    # For now, return structure

    return {
        "total_active": 0,
        "alerts": [
            # Example alert structure
            # {
            #     "name": "HighErrorRate",
            #     "severity": "warning",
            #     "module": "planning",
            #     "message": "Error rate > 5% for 5 minutes",
            #     "started_at": "2025-10-03T10:00:00Z",
            #     "value": 7.5
            # }
        ]
    }


@router.get("/alerts/history")
async def get_alert_history(days: int = 7):
    """
     Alert history

    Returns recent alert history for analysis
    """

    return {
        "period_days": days,
        "total_alerts": 0,
        "by_severity": {
            "critical": 0,
            "warning": 0,
            "info": 0
        },
        "by_alert_type": {},
        "history": []
    }


# ============================================================================
# STORAGE & CAPACITY ENDPOINTS
# ============================================================================

@router.get("/storage/size")
async def get_storage_size(storage_adapter=None):
    """
     Storage size metrics

    Returns:
    - Total records per table
    - Growth trends
    - Capacity projections
    """

    if not storage_adapter:
        return {
            "status": "not_initialized",
            "tables": {}
        }

    sizes = await health_checker.check_storage_size(storage_adapter)

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "tables": {
            "workflow_contexts": sizes.get("workflow_contexts", 0),
            "workflow_cases": sizes.get("workflow_cases", 0),
            "benchmarks": sizes.get("benchmarks", 0),
            "ml_predictions": sizes.get("ml_predictions", 0)
        },
        "total_records": sum(sizes.values()),
        "growth": {
            "daily_avg": 0,
            "weekly_avg": 0
        }
    }


@router.get("/storage/capacity")
async def get_capacity_metrics():
    """
     Capacity planning metrics

    Projections for storage growth and capacity planning
    """

    return {
        "current_size_mb": 0,
        "projected_30d_mb": 0,
        "projected_90d_mb": 0,
        "recommended_actions": []
    }


# ============================================================================
# PERFORMANCE ANALYSIS ENDPOINTS
# ============================================================================

@router.get("/performance/slow-queries")
async def get_slow_queries(limit: int = 10):
    """
     Slow query analysis

    Returns slowest database queries for optimization
    """

    return {
        "period": "last_24h",
        "threshold_ms": 100,
        "slow_queries": []
    }


@router.get("/performance/bottlenecks")
async def get_performance_bottlenecks():
    """
     Performance bottleneck analysis

    Identifies performance bottlenecks in the system
    """

    return {
        "bottlenecks": [
            # Example:
            # {
            #     "component": "database",
            #     "operation": "find_similar_cases",
            #     "avg_duration_ms": 250,
            #     "recommendation": "Add index on industry + org_size"
            # }
        ]
    }


# ============================================================================
# TREND ANALYSIS ENDPOINTS
# ============================================================================

@router.get("/trends/usage")
async def get_usage_trends(days: int = 30):
    """
     Usage trends over time

    Returns historical usage patterns
    """

    return {
        "period_days": days,
        "daily_stats": [
            # {
            #     "date": "2025-10-01",
            #     "workflows": 45,
            #     "cases_collected": 12,
            #     "ai_advice_requests": 89
            # }
        ]
    }


@router.get("/trends/learning")
async def get_learning_trends(days: int = 30):
    """
     Learning growth trends

    Shows how platform knowledge grows over time
    """

    return {
        "period_days": days,
        "total_cases_start": 0,
        "total_cases_end": 0,
        "growth_rate": 0.0,
        "daily_growth": []
    }
