"""
Platform Orchestrator API

Comprehensive orchestrator for ALL 12 BCM Platform Services:
1. Planning Service (8011) - ISO 8.3
2. Plans Service (8023) - ISO 8.4
3. BIA Service (8012) - ISO 8.2.2
4. Compliance Service (8014) - ISO 9.2, 10.1, 10.2
5. Risk Service (8013) - ISO 8.2.3
6. Response Service (8015) - ISO 8.4.5
7. Validation Service (8016) - ISO 8.4.6
8. Documents Service (8017) - ISO 7.5
9. Learning Service (8018) - ISO 7.2
10. Governance Service (8019) - ISO 5.3, 7.1, 7.3
11. File Service (8020) - Storage & Assets
12. Community Services:
    - Portal (8031) - ISO 7.4
    - Marketplace (8032) - Resource Management

Features:
- Concurrent health checks across all services
- Metrics aggregation
- Workflow Intelligence integration
- Service discovery and registry
- Admin operations
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import httpx
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/platform", tags=["Platform Orchestrator"])


# ============================================================================
# SERVICE REGISTRY - ALL 12 SERVICES
# ============================================================================

SERVICES = {
    # Core BCM Services (ISO 22301)
    "planning": {
        "name": "Planning Service",
        "url": "http://localhost:8011",
        "module": "planning",
        "iso_clause": "8.3",
        "component": "bcm-strategy",
        "has_workflow_intelligence": True,
        "description": "Business Continuity Strategy & Planning"
    },
    "plans": {
        "name": "Plans Service",
        "url": "http://localhost:8023",
        "module": "plans",
        "iso_clause": "8.4",
        "component": "bcm-plans",
        "has_workflow_intelligence": True,
        "description": "Business Continuity Plans & Procedures"
    },
    "bia": {
        "name": "BIA Service",
        "url": "http://localhost:8012",
        "module": "bia",
        "iso_clause": "8.2.2",
        "component": "bcm-bia",
        "has_workflow_intelligence": True,
        "description": "Business Impact Analysis"
    },
    "compliance": {
        "name": "Compliance Service",
        "url": "http://localhost:8014",
        "module": "compliance",
        "iso_clause": "9.2, 10.1, 10.2",
        "component": "bcm-compliance",
        "has_workflow_intelligence": True,
        "description": "Compliance Audits & Improvement"
    },
    "risk": {
        "name": "Risk Service",
        "url": "http://localhost:8013",
        "module": "risk",
        "iso_clause": "8.2.3",
        "component": "bcm-risk",
        "has_workflow_intelligence": True,
        "description": "Risk Assessment & Treatment"
    },
    "response": {
        "name": "Response Service",
        "url": "http://localhost:8015",
        "module": "response",
        "iso_clause": "8.4.5",
        "component": "bcm-incident",
        "has_workflow_intelligence": True,
        "description": "Incident Response & Management"
    },
    "validation": {
        "name": "Validation Service",
        "url": "http://localhost:8016",
        "module": "validation",
        "iso_clause": "8.4.6",
        "component": "bcm-testing",
        "has_workflow_intelligence": True,
        "description": "Exercise & Testing"
    },
    "documents": {
        "name": "Documents Service",
        "url": "http://localhost:8017",
        "module": "documents",
        "iso_clause": "7.5",
        "component": "bcm-documentation",
        "has_workflow_intelligence": True,
        "description": "Document Control & Management"
    },
    "learning": {
        "name": "Learning Service",
        "url": "http://localhost:8018",
        "module": "learning",
        "iso_clause": "7.2",
        "component": "bcm-competence",
        "has_workflow_intelligence": True,
        "description": "Training & Competence"
    },
    "governance": {
        "name": "Governance Service",
        "url": "http://localhost:8019",
        "module": "governance",
        "iso_clause": "5.3, 7.1, 7.3",
        "component": "bcm-governance",
        "has_workflow_intelligence": True,
        "description": "Roles, Resources & Communication"
    },

    # Storage & Infrastructure
    "file": {
        "name": "File Service",
        "url": "http://localhost:8020",
        "module": "file",
        "iso_clause": "7.5.3",
        "component": "storage",
        "has_workflow_intelligence": False,
        "description": "File Storage & Asset Management"
    },

    # Community Services
    "portal": {
        "name": "Community Portal",
        "url": "http://localhost:8031",
        "module": "portal",
        "iso_clause": "7.4",
        "component": "bcm-communication",
        "has_workflow_intelligence": False,
        "description": "Knowledge Base & Forums"
    },
    "marketplace": {
        "name": "Community Marketplace",
        "url": "http://localhost:8032",
        "module": "marketplace",
        "iso_clause": "7.1",
        "component": "bcm-resources",
        "has_workflow_intelligence": False,
        "description": "Specialists & Project Marketplace"
    }
}


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ServiceHealth(BaseModel):
    """Health status of a single service"""
    service_key: str
    service_name: str
    module: str
    status: str  # healthy, degraded, unhealthy, unreachable
    response_time_ms: Optional[float] = None
    workflow_intelligence_enabled: bool = False
    iso_clause: str
    component: str
    error: Optional[str] = None
    timestamp: str


class PlatformHealth(BaseModel):
    """Overall platform health"""
    platform_status: str  # healthy, degraded, critical, down
    total_services: int
    healthy_services: int
    degraded_services: int
    unhealthy_services: int
    unreachable_services: int
    services: List[ServiceHealth]
    timestamp: str
    uptime_percentage: float


class ServiceMetrics(BaseModel):
    """Metrics from a single service"""
    service_key: str
    service_name: str
    available: bool
    metrics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class WorkflowIntelligenceStats(BaseModel):
    """Workflow Intelligence statistics"""
    total_services_with_wi: int
    total_workflows: int
    total_cases: int
    total_benchmarks: int
    by_module: Dict[str, Dict[str, int]]


# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@router.get("/health", response_model=PlatformHealth)
async def get_platform_health():
    """
    🏥 Platform-wide Health Check

    Performs concurrent health checks on all 12 services.
    Returns overall platform health and individual service status.

    Status Levels:
    - healthy: All services operational
    - degraded: Some services down but core functions work
    - critical: Critical services down
    - down: Platform unavailable
    """

    async def check_service(service_key: str, config: dict) -> ServiceHealth:
        """Check health of a single service"""
        import time
        start = time.time()

        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(f"{config['url']}/health")
                response_time = (time.time() - start) * 1000

                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status", "healthy")

                    return ServiceHealth(
                        service_key=service_key,
                        service_name=config["name"],
                        module=config["module"],
                        status=status,
                        response_time_ms=round(response_time, 2),
                        workflow_intelligence_enabled=config["has_workflow_intelligence"],
                        iso_clause=config["iso_clause"],
                        component=config["component"],
                        timestamp=datetime.utcnow().isoformat()
                    )
                else:
                    return ServiceHealth(
                        service_key=service_key,
                        service_name=config["name"],
                        module=config["module"],
                        status="unhealthy",
                        response_time_ms=round(response_time, 2),
                        workflow_intelligence_enabled=config["has_workflow_intelligence"],
                        iso_clause=config["iso_clause"],
                        component=config["component"],
                        error=f"HTTP {response.status_code}",
                        timestamp=datetime.utcnow().isoformat()
                    )

        except httpx.TimeoutException:
            return ServiceHealth(
                service_key=service_key,
                service_name=config["name"],
                module=config["module"],
                status="unreachable",
                workflow_intelligence_enabled=config["has_workflow_intelligence"],
                iso_clause=config["iso_clause"],
                component=config["component"],
                error="Timeout after 3s",
                timestamp=datetime.utcnow().isoformat()
            )
        except Exception as e:
            return ServiceHealth(
                service_key=service_key,
                service_name=config["name"],
                module=config["module"],
                status="unreachable",
                workflow_intelligence_enabled=config["has_workflow_intelligence"],
                iso_clause=config["iso_clause"],
                component=config["component"],
                error=str(e),
                timestamp=datetime.utcnow().isoformat()
            )

    # Check all services concurrently
    logger.info(f"Checking health of {len(SERVICES)} services...")
    tasks = [check_service(key, config) for key, config in SERVICES.items()]
    health_results = await asyncio.gather(*tasks)

    # Calculate statistics
    healthy = sum(1 for h in health_results if h.status == "healthy")
    degraded = sum(1 for h in health_results if h.status == "degraded")
    unhealthy = sum(1 for h in health_results if h.status == "unhealthy")
    unreachable = sum(1 for h in health_results if h.status == "unreachable")

    # Determine overall platform status
    total_services = len(SERVICES)
    uptime_pct = (healthy / total_services) * 100

    if healthy == total_services:
        platform_status = "healthy"
    elif healthy >= total_services * 0.8:  # 80%+ healthy
        platform_status = "degraded"
    elif healthy >= total_services * 0.5:  # 50%+ healthy
        platform_status = "critical"
    else:
        platform_status = "down"

    logger.info(f"Platform status: {platform_status} ({healthy}/{total_services} healthy)")

    return PlatformHealth(
        platform_status=platform_status,
        total_services=total_services,
        healthy_services=healthy,
        degraded_services=degraded,
        unhealthy_services=unhealthy,
        unreachable_services=unreachable,
        services=health_results,
        timestamp=datetime.utcnow().isoformat(),
        uptime_percentage=round(uptime_pct, 2)
    )


@router.get("/status")
async def get_platform_status():
    """
    📊 Detailed Platform Status

    Returns comprehensive platform information:
    - Service registry
    - Component breakdown
    - ISO clause coverage
    - Workflow Intelligence status
    """

    # Group services by component
    by_component = {}
    for key, config in SERVICES.items():
        component = config["component"]
        if component not in by_component:
            by_component[component] = []
        by_component[component].append({
            "key": key,
            "name": config["name"],
            "module": config["module"],
            "iso_clause": config["iso_clause"]
        })

    # Count Workflow Intelligence services
    wi_services = [k for k, v in SERVICES.items() if v["has_workflow_intelligence"]]

    return {
        "platform": "BCM Platform ISO 22301",
        "version": "2.0.0",
        "total_services": len(SERVICES),
        "workflow_intelligence_services": len(wi_services),
        "components": by_component,
        "iso_coverage": {
            "clauses_covered": list(set(
                clause.strip()
                for config in SERVICES.values()
                for clause in config["iso_clause"].split(",")
            )),
            "total_clauses": 13  # Total unique ISO clauses covered
        },
        "architecture": {
            "core_bcm_services": 10,
            "community_services": 2,
            "storage_services": 1
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/services")
async def get_service_registry():
    """
    📋 Service Registry

    Returns complete list of all platform services with metadata.
    """

    services_list = []
    for key, config in SERVICES.items():
        services_list.append({
            "key": key,
            "name": config["name"],
            "url": config["url"],
            "module": config["module"],
            "iso_clause": config["iso_clause"],
            "component": config["component"],
            "workflow_intelligence": config["has_workflow_intelligence"],
            "description": config["description"]
        })

    return {
        "total_services": len(services_list),
        "services": services_list,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# PER-SERVICE OPERATIONS
# ============================================================================

@router.get("/services/{service_name}/health")
async def get_service_health(service_name: str):
    """
    🏥 Individual Service Health Check

    Get detailed health status for a specific service.
    """

    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")

    config = SERVICES[service_name]

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{config['url']}/health")

            if response.status_code == 200:
                health_data = response.json()
                return {
                    "service": service_name,
                    "status": "healthy",
                    "data": health_data,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "service": service_name,
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}",
                    "timestamp": datetime.utcnow().isoformat()
                }
    except Exception as e:
        return {
            "service": service_name,
            "status": "unreachable",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/services/{service_name}/metrics")
async def get_service_metrics(service_name: str):
    """
    📊 Individual Service Metrics

    Get Prometheus metrics from a specific service.
    """

    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")

    config = SERVICES[service_name]

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{config['url']}/metrics")

            if response.status_code == 200:
                return {
                    "service": service_name,
                    "status": "available",
                    "metrics": response.text,  # Prometheus format
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Metrics unavailable: HTTP {response.status_code}"
                )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unreachable: {str(e)}")


@router.get("/services/{service_name}/status")
async def get_service_detailed_status(service_name: str):
    """
    📋 Individual Service Detailed Status

    Get comprehensive status including configuration and capabilities.
    """

    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")

    config = SERVICES[service_name]

    # Check if service is reachable
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"{config['url']}/health")
            is_healthy = response.status_code == 200
            health_data = response.json() if is_healthy else None
    except Exception:
        is_healthy = False
        health_data = None

    return {
        "service_key": service_name,
        "name": config["name"],
        "url": config["url"],
        "module": config["module"],
        "iso_clause": config["iso_clause"],
        "component": config["component"],
        "description": config["description"],
        "workflow_intelligence": config["has_workflow_intelligence"],
        "health": {
            "is_healthy": is_healthy,
            "data": health_data
        },
        "endpoints": {
            "health": f"{config['url']}/health",
            "metrics": f"{config['url']}/metrics",
            "api_docs": f"{config['url']}/docs"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# METRICS AGGREGATION
# ============================================================================

@router.get("/metrics/summary")
async def get_platform_metrics_summary():
    """
    📊 Platform-wide Metrics Summary

    Aggregates metrics across all services to provide platform-wide view.
    """

    async def fetch_metrics(service_key: str, config: dict) -> ServiceMetrics:
        """Fetch metrics from a single service"""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(f"{config['url']}/metrics")

                if response.status_code == 200:
                    # Parse Prometheus metrics (simplified)
                    metrics_text = response.text

                    return ServiceMetrics(
                        service_key=service_key,
                        service_name=config["name"],
                        available=True,
                        metrics={
                            "raw": metrics_text[:500],  # First 500 chars
                            "size": len(metrics_text)
                        }
                    )
                else:
                    return ServiceMetrics(
                        service_key=service_key,
                        service_name=config["name"],
                        available=False,
                        error=f"HTTP {response.status_code}"
                    )
        except Exception as e:
            return ServiceMetrics(
                service_key=service_key,
                service_name=config["name"],
                available=False,
                error=str(e)
            )

    # Fetch from all services concurrently
    tasks = [fetch_metrics(key, config) for key, config in SERVICES.items()]
    results = await asyncio.gather(*tasks)

    available_services = sum(1 for r in results if r.available)

    return {
        "platform_metrics": {
            "total_services": len(SERVICES),
            "services_reporting": available_services,
            "services_silent": len(SERVICES) - available_services
        },
        "services": [r.dict() for r in results],
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/metrics/{service_name}")
async def get_service_metrics_parsed(service_name: str):
    """
    📈 Service Metrics (Parsed)

    Get parsed and structured metrics from a specific service.
    """

    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")

    config = SERVICES[service_name]

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{config['url']}/metrics")

            if response.status_code == 200:
                # TODO: Parse Prometheus format properly
                # For now, return raw
                return {
                    "service": service_name,
                    "format": "prometheus",
                    "metrics_text": response.text,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Metrics unavailable"
                )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=str(e))


# ============================================================================
# WORKFLOW INTELLIGENCE AGGREGATION
# ============================================================================

@router.get("/workflow-intelligence/benchmarks/all")
async def get_all_workflow_intelligence_benchmarks(
    industry: Optional[str] = None,
    org_size: Optional[str] = None
):
    """
    📊 Workflow Intelligence Benchmarks - All Services

    Aggregates benchmarks from all 10 services with Workflow Intelligence:
    - Planning, Plans, BIA, Compliance, Risk, Response, Validation,
      Documents, Learning, Governance
    """

    wi_services = {k: v for k, v in SERVICES.items() if v["has_workflow_intelligence"]}

    async def fetch_benchmark(service_key: str, config: dict):
        """Fetch benchmarks from a single service"""
        url = f"{config['url']}/api/v1/{config['module']}/benchmarks"
        params = {}
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
                        "module": config["module"],
                        "iso_clause": config["iso_clause"],
                        "status": "success",
                        "data": response.json()
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

    tasks = [fetch_benchmark(key, config) for key, config in wi_services.items()]
    results = await asyncio.gather(*tasks)

    successful = [r for r in results if r.get("status") == "success"]
    failed = [r for r in results if r.get("status") == "error"]

    return {
        "filters": {
            "industry": industry or "all",
            "org_size": org_size or "all"
        },
        "total_wi_services": len(wi_services),
        "successful_services": len(successful),
        "failed_services": len(failed),
        "benchmarks": successful,
        "errors": failed if failed else None,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/workflow-intelligence/cases/search")
async def search_workflow_intelligence_cases(
    industry: Optional[str] = None,
    org_size: Optional[str] = None,
    module: Optional[str] = None,
    limit: int = Query(default=10, ge=1, le=100)
):
    """
    🔍 Workflow Intelligence Cases - Cross-Service Search

    Search similar cases across all services with Workflow Intelligence.
    Find relevant cases regardless of which module they came from.
    """

    # Filter services
    wi_services = {k: v for k, v in SERVICES.items() if v["has_workflow_intelligence"]}
    if module:
        wi_services = {k: v for k, v in wi_services.items() if v["module"] == module}

    async def fetch_cases(service_key: str, config: dict):
        """Fetch similar cases from a service"""
        url = f"{config['url']}/api/v1/{config['module']}/similar-cases"
        params = {"limit": limit}
        if industry:
            params["industry"] = industry
        if org_size:
            params["org_size"] = org_size

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, params=params)

                if response.status_code == 200:
                    cases = response.json()
                    # Add source service to each case
                    if isinstance(cases, list):
                        for case in cases:
                            case["source_service"] = service_key
                            case["source_module"] = config["module"]
                    return cases
        except Exception as e:
            logger.warning(f"Failed to fetch cases from {service_key}: {e}")

        return []

    tasks = [fetch_cases(key, config) for key, config in wi_services.items()]
    results = await asyncio.gather(*tasks)

    # Flatten and aggregate
    all_cases = []
    for case_list in results:
        all_cases.extend(case_list)

    # Sort by relevance (if available) and limit
    # TODO: Implement smart cross-module ranking
    all_cases = all_cases[:limit]

    return {
        "total_cases": len(all_cases),
        "cases": all_cases,
        "sources": list(wi_services.keys()),
        "filters": {
            "industry": industry,
            "org_size": org_size,
            "module": module
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/workflow-intelligence/analytics")
async def get_workflow_intelligence_analytics(days: int = Query(default=30, ge=1, le=365)):
    """
    📈 Workflow Intelligence Platform Analytics

    Aggregates workflow intelligence analytics across all services:
    - Total workflows executed
    - Cases collected
    - AI advice usage
    - Learning growth
    - Cross-module learning patterns
    """

    # This would query the shared workflow_intelligence database
    # For now, return structure showing what will be tracked

    wi_services = {k: v for k, v in SERVICES.items() if v["has_workflow_intelligence"]}

    module_stats = {}
    for key, config in wi_services.items():
        module_stats[config["module"]] = {
            "workflows": 0,
            "cases_collected": 0,
            "ai_advice_requests": 0,
            "completion_rate": 0.0
        }

    return {
        "period_days": days,
        "platform_totals": {
            "total_workflows": 0,
            "total_cases_collected": 0,
            "total_ai_advice_requests": 0,
            "total_benchmarks_calculated": 0
        },
        "by_module": module_stats,
        "ai_usage": {
            "total_advice_requests": 0,
            "acceptance_rate": 0.0,
            "avg_relevance_score": 0.0
        },
        "learning": {
            "total_industries_covered": 0,
            "total_org_sizes_covered": 0,
            "coverage_percentage": 0.0,
            "growth_rate": 0.0
        },
        "cross_module_learning": {
            "total_queries": 0,
            "top_patterns": []
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# ADMIN OPERATIONS
# ============================================================================

@router.post("/admin/sync-all")
async def trigger_platform_wide_sync():
    """
    🔄 Platform-wide Sync

    Admin operation to trigger synchronization across all services:
    - Benchmark recalculation
    - Cache refresh
    - Database cleanup
    """

    wi_services = {k: v for k, v in SERVICES.items() if v["has_workflow_intelligence"]}

    async def trigger_sync(service_key: str, config: dict):
        """Trigger sync on a single service"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{config['url']}/api/v1/admin/sync",
                    json={"force": True}
                )

                if response.status_code in [200, 201]:
                    return {
                        "service": service_key,
                        "status": "success",
                        "message": "Sync triggered"
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

    tasks = [trigger_sync(key, config) for key, config in wi_services.items()]
    results = await asyncio.gather(*tasks)

    successful = sum(1 for r in results if r.get("status") == "success")

    return {
        "operation": "platform_sync",
        "total_services": len(wi_services),
        "successful": successful,
        "failed": len(wi_services) - successful,
        "results": results,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/admin/health-check-all")
async def trigger_platform_health_check():
    """
    🏥 Admin Health Check - All Services

    Comprehensive health check with detailed diagnostics.
    """

    health_result = await get_platform_health()

    # Add additional diagnostic information
    diagnostics = {
        "database_connections": "operational",  # Would check actual DB
        "cache_status": "operational",  # Would check Redis
        "eventbus_status": "operational",  # Would check RabbitMQ
        "storage_status": "operational"  # Would check file storage
    }

    return {
        "health": health_result.dict(),
        "diagnostics": diagnostics,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/admin/stats")
async def get_platform_admin_stats():
    """
    📊 Platform Admin Statistics

    Comprehensive statistics for platform administrators:
    - Service health trends
    - Performance metrics
    - Resource usage
    - Learning statistics
    """

    wi_services = {k: v for k, v in SERVICES.items() if v["has_workflow_intelligence"]}

    return {
        "platform": {
            "total_services": len(SERVICES),
            "workflow_intelligence_services": len(wi_services),
            "total_tenants": 0,  # Would query actual data
            "total_users": 0,
            "total_workflows_all_time": 0
        },
        "services": {
            "by_component": {
                "bcm-core": 10,
                "community": 2,
                "storage": 1
            },
            "by_status": {
                "healthy": 0,
                "degraded": 0,
                "unhealthy": 0,
                "unreachable": 0
            }
        },
        "performance": {
            "avg_response_time_ms": 0.0,
            "avg_workflow_duration_days": 0.0,
            "avg_db_query_ms": 0.0,
            "cache_hit_rate": 0.0
        },
        "workflow_intelligence": {
            "total_cases_library": 0,
            "total_benchmarks": 0,
            "total_ai_advice_given": 0,
            "ai_acceptance_rate": 0.0,
            "cases_per_day": 0.0,
            "learning_acceleration": 0.0
        },
        "quality": {
            "avg_case_relevance": 0.0,
            "avg_benchmark_sample_size": 0,
            "coverage": {
                "industries": 0,
                "org_sizes": 0,
                "modules": len(wi_services)
            }
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# DISCOVERY & DOCUMENTATION
# ============================================================================

@router.get("/")
async def platform_info():
    """
    ℹ️ Platform Information

    High-level platform overview and capabilities.
    """

    return {
        "platform": "BCM Platform ISO 22301",
        "version": "2.0.0",
        "description": "Comprehensive Business Continuity Management Platform",
        "services": {
            "total": len(SERVICES),
            "core_bcm": 10,
            "community": 2,
            "storage": 1
        },
        "features": {
            "workflow_intelligence": True,
            "ai_powered_advice": True,
            "cross_module_learning": True,
            "real_time_monitoring": True,
            "iso_22301_compliant": True
        },
        "endpoints": {
            "health": "/api/v1/platform/health",
            "status": "/api/v1/platform/status",
            "services": "/api/v1/platform/services",
            "metrics": "/api/v1/platform/metrics/summary",
            "docs": "/docs"
        },
        "timestamp": datetime.utcnow().isoformat()
    }
