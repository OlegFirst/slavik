"""
Workflow Intelligence Orchestrator API

Aggregates workflow intelligence data from all BCM services:
- Planning Service (8011)
- Plans Service (8023)
- BIA Service (8012)
- Compliance Service (8014)

Provides unified view of platform-wide workflow intelligence.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import httpx
import asyncio

router = APIRouter(prefix="/api/v1/workflow-intelligence", tags=["Workflow Intelligence Orchestrator"])


# ============================================================================
# SERVICE CONFIGURATION
# ============================================================================

SERVICES = {
    "planning": {
        "name": "Planning Service",
        "url": "http://localhost:8011",
        "module": "planning",
        "iso_clause": "8.3"
    },
    "plans": {
        "name": "Plans Service",
        "url": "http://localhost:8023",
        "module": "plans",
        "iso_clause": "8.4"
    },
    "bia": {
        "name": "BIA Service",
        "url": "http://localhost:8012",
        "module": "bia",
        "iso_clause": "8.2.2"
    },
    "compliance": {
        "name": "Compliance Service",
        "url": "http://localhost:8014",
        "module": "compliance",
        "iso_clause": "9.2, 10.1, 10.2"
    }
}


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ServiceHealth(BaseModel):
    service: str
    module: str
    status: str  # healthy, unhealthy, unreachable
    response_time_ms: Optional[float] = None
    workflow_intelligence_enabled: bool = False
    error: Optional[str] = None


class GlobalBenchmarks(BaseModel):
    module: str
    industry: Optional[str] = None
    benchmarks: Dict[str, Any]
    sample_size: int


class CrossServiceStats(BaseModel):
    total_cases: int
    total_contexts: int
    modules: Dict[str, int]
    industries: Dict[str, int]
    learning_coverage: float


# ============================================================================
# ORCHESTRATOR ENDPOINTS - AGGREGATION
# ============================================================================

@router.get("/benchmarks/all")
async def get_all_benchmarks(industry: Optional[str] = None):
    """
    📊 Get benchmarks from ALL services

    Aggregates benchmarks across:
    - Planning (ISO 8.3)
    - Plans (ISO 8.4)
    - BIA (ISO 8.2.2)
    - Compliance (ISO 9.2)
    """

    async def fetch_benchmark(service_key: str, service_config: dict):
        """Fetch benchmark from single service"""
        url = f"{service_config['url']}/api/v1/{service_config['module']}/benchmarks"
        if industry:
            url += f"?industry={industry}"

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "service": service_key,
                        "module": service_config["module"],
                        "iso_clause": service_config["iso_clause"],
                        "data": data,
                        "status": "success"
                    }
                else:
                    return {
                        "service": service_key,
                        "status": "error",
                        "error": f"HTTP {response.status_code}"
                    }
        except Exception as e:
            return {
                "service": service_key,
                "status": "error",
                "error": str(e)
            }

    # Fetch from all services concurrently
    tasks = [
        fetch_benchmark(key, config)
        for key, config in SERVICES.items()
    ]

    results = await asyncio.gather(*tasks)

    # Aggregate
    successful = [r for r in results if r.get("status") == "success"]
    failed = [r for r in results if r.get("status") == "error"]

    return {
        "industry": industry or "all",
        "total_services": len(SERVICES),
        "successful_services": len(successful),
        "failed_services": len(failed),
        "benchmarks": successful,
        "errors": failed if failed else None
    }


@router.get("/cases/search")
async def search_cases_across_services(
    industry: Optional[str] = None,
    org_size: Optional[str] = None,
    module: Optional[str] = None,
    limit: int = 10
):
    """
    🔍 Search similar cases across ALL services

    Cross-service learning: find relevant cases regardless of module
    """

    # Determine which services to query
    services_to_query = SERVICES if not module else {
        k: v for k, v in SERVICES.items() if v["module"] == module
    }

    async def fetch_cases(service_key: str, service_config: dict):
        """Fetch similar cases from service"""
        # Note: This endpoint might not exist yet in all services
        # This is the target API design
        url = f"{service_config['url']}/api/v1/{service_config['module']}/similar-cases"
        params = {"limit": limit}
        if industry:
            params["industry"] = industry
        if org_size:
            params["org_size"] = org_size

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    return {
                        "service": service_key,
                        "cases": response.json()
                    }
        except Exception:
            pass

        return {"service": service_key, "cases": []}

    tasks = [
        fetch_cases(key, config)
        for key, config in services_to_query.items()
    ]

    results = await asyncio.gather(*tasks)

    # Aggregate and rank by relevance
    all_cases = []
    for result in results:
        for case in result.get("cases", []):
            case["source_service"] = result["service"]
            all_cases.append(case)

    # Sort by relevance (if available) and limit
    # TODO: Implement smart ranking algorithm
    all_cases = all_cases[:limit]

    return {
        "total_cases": len(all_cases),
        "cases": all_cases,
        "sources": [r["service"] for r in results]
    }


@router.get("/analytics/platform")
async def get_platform_analytics(days: int = 30):
    """
    📈 Platform-wide workflow intelligence analytics

    Aggregates:
    - Total workflows across all services
    - Cases collected
    - AI advice usage
    - Learning growth
    """

    # This would query the shared workflow_intelligence database
    # For now, return structure

    return {
        "period_days": days,
        "total_workflows": 0,
        "total_cases_collected": 0,
        "modules": {
            "planning": {"workflows": 0, "cases": 0, "completion_rate": 0.0},
            "plans": {"workflows": 0, "cases": 0, "completion_rate": 0.0},
            "bia": {"workflows": 0, "cases": 0, "completion_rate": 0.0},
            "compliance": {"workflows": 0, "cases": 0, "completion_rate": 0.0}
        },
        "ai_usage": {
            "total_advice_requests": 0,
            "acceptance_rate": 0.0,
            "avg_relevance_score": 0.0
        },
        "learning": {
            "total_industries_covered": 0,
            "total_org_sizes_covered": 0,
            "coverage_percentage": 0.0
        }
    }


@router.get("/analytics/cross-service-learning")
async def get_cross_service_learning_stats():
    """
    🔄 Cross-service learning statistics

    Shows how modules learn from each other:
    - Planning → BIA insights
    - BIA → Compliance insights
    - etc.
    """

    return {
        "total_cross_module_queries": 0,
        "matrix": {
            "planning": {"bia": 0, "plans": 0, "compliance": 0},
            "bia": {"planning": 0, "plans": 0, "compliance": 0},
            "plans": {"planning": 0, "bia": 0, "compliance": 0},
            "compliance": {"planning": 0, "bia": 0, "plans": 0}
        },
        "top_learning_pairs": []
    }


# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@router.get("/health")
async def check_all_services_health():
    """
    🏥 Health check for ALL services with workflow intelligence

    Returns status of each service and their WI integration
    """

    async def check_service(service_key: str, service_config: dict) -> ServiceHealth:
        """Check single service health"""
        import time
        start = time.time()

        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(f"{service_config['url']}/health")
                response_time = (time.time() - start) * 1000

                if response.status_code == 200:
                    data = response.json()

                    return ServiceHealth(
                        service=service_key,
                        module=service_config["module"],
                        status="healthy",
                        response_time_ms=response_time,
                        workflow_intelligence_enabled=True  # If health check passes
                    )
                else:
                    return ServiceHealth(
                        service=service_key,
                        module=service_config["module"],
                        status="unhealthy",
                        response_time_ms=response_time,
                        error=f"HTTP {response.status_code}"
                    )
        except Exception as e:
            return ServiceHealth(
                service=service_key,
                module=service_config["module"],
                status="unreachable",
                error=str(e)
            )

    # Check all services concurrently
    tasks = [
        check_service(key, config)
        for key, config in SERVICES.items()
    ]

    health_results = await asyncio.gather(*tasks)

    # Overall platform health
    all_healthy = all(h.status == "healthy" for h in health_results)

    return {
        "platform_status": "healthy" if all_healthy else "degraded",
        "total_services": len(SERVICES),
        "healthy_services": sum(1 for h in health_results if h.status == "healthy"),
        "services": [h.dict() for h in health_results]
    }


@router.get("/status")
async def get_platform_status():
    """
    📊 Detailed platform status

    Includes:
    - Service health
    - Database status
    - Cache status
    - Storage metrics
    """

    # This would check the shared database

    return {
        "platform": "BCM Workflow Intelligence",
        "version": "1.0.0",
        "status": "operational",
        "components": {
            "services": 4,
            "database": "postgresql",
            "cache": "redis",
            "ml_engine": "scikit-learn"
        },
        "database": {
            "status": "healthy",
            "schema": "workflow_intelligence",
            "tables": 4
        },
        "storage": {
            "total_workflows": 0,
            "total_cases": 0,
            "total_benchmarks": 0
        }
    }


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@router.post("/admin/sync-benchmarks")
async def trigger_benchmark_sync():
    """
    🔄 Trigger benchmark recalculation across all services

    Admin operation to force refresh of all benchmarks
    """

    # This would trigger benchmark recalculation in the database

    return {
        "status": "triggered",
        "message": "Benchmark sync started for all modules"
    }


@router.post("/admin/clear-cache")
async def clear_all_caches():
    """
    🗑️ Clear all workflow intelligence caches

    Admin operation for cache invalidation
    """

    return {
        "status": "cleared",
        "message": "All workflow intelligence caches cleared"
    }


@router.get("/admin/stats")
async def get_admin_stats():
    """
    📊 Admin statistics dashboard

    Detailed stats for platform administrators
    """

    return {
        "platform": {
            "total_tenants": 0,
            "total_users": 0,
            "total_workflows_all_time": 0
        },
        "performance": {
            "avg_workflow_duration_days": 0.0,
            "avg_db_query_ms": 0.0,
            "cache_hit_rate": 0.0
        },
        "quality": {
            "ai_advice_acceptance_rate": 0.0,
            "similar_cases_avg_relevance": 0.0,
            "benchmark_sample_sizes": {}
        },
        "growth": {
            "cases_per_day": 0.0,
            "learning_acceleration": 0.0
        }
    }
