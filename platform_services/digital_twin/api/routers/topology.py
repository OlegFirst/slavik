"""
Platform Topology API
Endpoints for platform service discovery and topology visualization
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from core.system_clone.platform_topology import PlatformTopologyMapper
from core.system_clone.integration_graph import IntegrationGraph
from api.auth.dependencies import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class ServiceInfoResponse(BaseModel):
    """Service information response"""
    name: str
    base_url: str
    port: int
    status: str  # running, stopped, unknown
    health_data: Optional[Dict[str, Any]] = None
    discovered_at: str


class TopologyResponse(BaseModel):
    """Platform topology response"""
    total_services: int
    running_services: int
    stopped_services: int
    platform_health_percentage: float
    services: List[ServiceInfoResponse]
    discovered_at: str


class TopologyGraphResponse(BaseModel):
    """Topology graph for visualization"""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class ServiceDependenciesResponse(BaseModel):
    """Service dependencies response"""
    service_name: str
    direct_dependencies: List[str]
    transitive_dependencies: List[str]
    dependent_services: List[str]
    transitive_dependents: List[str]
    is_critical: bool
    criticality_score: float


class ImpactAnalysisResponse(BaseModel):
    """Service failure impact analysis"""
    service_name: str
    directly_affected: int
    transitively_affected: int
    affected_services: List[str]
    impact_level: str  # low, medium, high, critical
    recommendations: List[str]


# ============================================
# ENDPOINTS
# ============================================

@router.get("/", response_model=TopologyResponse)
async def discover_platform_topology(
    force_refresh: bool = Query(False, description="Force fresh discovery"),
    current_user = Depends(get_current_active_user)
):
    """
    Discover complete platform topology

    Discovers all 13 platform services and their health status.
    Returns comprehensive topology information.

    **Multi-tenancy:** Available to all authenticated users.
    **Permission:** Requires authentication only.
    """
    try:
        logger.info(f"User {current_user.get('id')} discovering platform topology")

        # Create topology mapper
        mapper = PlatformTopologyMapper()

        # Discover all services
        topology = await mapper.discover_all_services()

        # Build response
        services_list = []
        for service_name, service_info in topology.services.items():
            services_list.append(ServiceInfoResponse(
                name=service_info.name,
                base_url=service_info.base_url,
                port=service_info.port,
                status=service_info.status.value,
                health_data=service_info.health_data,
                discovered_at=service_info.last_checked.isoformat()
            ))

        return TopologyResponse(
            total_services=topology.total_services,
            running_services=topology.running_services,
            stopped_services=topology.stopped_services,
            platform_health_percentage=topology.platform_health_percentage,
            services=services_list,
            discovered_at=datetime.utcnow().isoformat()
        )

    except Exception as e:
        logger.error(f"Failed to discover topology: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph", response_model=TopologyGraphResponse)
async def get_topology_graph(
    current_user = Depends(get_current_active_user)
):
    """
    Get platform topology as graph for visualization

    Returns nodes and edges suitable for D3.js, Cytoscape.js, or other
    graph visualization libraries.

    **Format:**
    - Nodes: List of services with metadata
    - Edges: List of integrations between services

    **Multi-tenancy:** Available to all authenticated users.
    """
    try:
        logger.info(f"User {current_user.get('id')} requesting topology graph")

        # Discover topology
        mapper = PlatformTopologyMapper()
        topology = await mapper.discover_all_services()

        # Export as graph
        graph = await mapper.export_topology_graph(topology)

        return TopologyGraphResponse(
            nodes=graph["nodes"],
            edges=graph["edges"],
            metadata=graph["metadata"]
        )

    except Exception as e:
        logger.error(f"Failed to get topology graph: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/service/{service_name}")
async def get_service_details(
    service_name: str,
    current_user = Depends(get_current_active_user)
):
    """
    Get detailed information about specific service

    Returns comprehensive service details including health, integrations,
    and dependencies.
    """
    try:
        logger.info(f"User {current_user.get('id')} requesting service details: {service_name}")

        # Discover topology
        mapper = PlatformTopologyMapper()
        topology = await mapper.discover_all_services()

        # Get service
        service_info = topology.services.get(service_name)

        if not service_info:
            raise HTTPException(
                status_code=404,
                detail=f"Service not found: {service_name}"
            )

        # Get dependencies
        dependencies = topology.get_service_dependencies(service_name)
        dependent_services = topology.get_dependent_services(service_name)

        return {
            "name": service_info.name,
            "base_url": service_info.base_url,
            "port": service_info.port,
            "status": service_info.status.value,
            "health_data": service_info.health_data,
            "integrations": service_info.integrations,
            "dependencies": dependencies,
            "dependent_services": dependent_services,
            "last_checked": service_info.last_checked.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get service details: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dependencies/{service_name}", response_model=ServiceDependenciesResponse)
async def analyze_service_dependencies(
    service_name: str,
    current_user = Depends(get_current_active_user)
):
    """
    Analyze service dependencies and dependents

    Returns comprehensive dependency analysis including:
    - Direct dependencies
    - Transitive dependencies (full tree)
    - Direct dependents
    - Transitive dependents
    - Criticality assessment
    """
    try:
        logger.info(f"User {current_user.get('id')} analyzing dependencies: {service_name}")

        # Discover topology
        mapper = PlatformTopologyMapper()
        topology = await mapper.discover_all_services()

        # Build integration graph
        graph = IntegrationGraph()

        for svc_name, svc_info in topology.services.items():
            graph.add_service(svc_name)
            for dep in svc_info.integrations:
                graph.add_integration(svc_name, dep, "depends_on")

        # Analyze
        direct_deps = topology.get_service_dependencies(service_name)
        transitive_deps = list(graph.get_transitive_dependencies(service_name))

        direct_dependents = topology.get_dependent_services(service_name)
        transitive_dependents = list(graph.get_transitive_dependents(service_name))

        critical_services = graph.identify_critical_services()
        is_critical = service_name in critical_services

        criticality_score = len(transitive_dependents) / max(len(topology.services), 1)

        return ServiceDependenciesResponse(
            service_name=service_name,
            direct_dependencies=direct_deps,
            transitive_dependencies=transitive_deps,
            dependent_services=direct_dependents,
            transitive_dependents=transitive_dependents,
            is_critical=is_critical,
            criticality_score=criticality_score
        )

    except Exception as e:
        logger.error(f"Failed to analyze dependencies: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/impact-analysis/{service_name}", response_model=ImpactAnalysisResponse)
async def analyze_failure_impact(
    service_name: str,
    current_user = Depends(get_current_active_user)
):
    """
    Analyze impact if service fails

    Returns impact analysis showing:
    - How many services would be affected
    - Which services would be affected
    - Impact severity level
    - Recommendations

    Useful for:
    - Capacity planning
    - Risk assessment
    - BCM scenario planning
    """
    try:
        logger.info(f"User {current_user.get('id')} analyzing failure impact: {service_name}")

        # Discover topology
        mapper = PlatformTopologyMapper()
        topology = await mapper.discover_all_services()

        # Build integration graph
        graph = IntegrationGraph()

        for svc_name, svc_info in topology.services.items():
            graph.add_service(svc_name)
            for dep in svc_info.integrations:
                graph.add_integration(svc_name, dep, "depends_on")

        # Analyze impact
        impact = graph.assess_impact_if_service_fails(service_name)

        # Determine impact level
        total_services = len(topology.services)
        affected_percentage = impact["total_affected"] / max(total_services, 1)

        if affected_percentage >= 0.7:
            impact_level = "critical"
        elif affected_percentage >= 0.4:
            impact_level = "high"
        elif affected_percentage >= 0.2:
            impact_level = "medium"
        else:
            impact_level = "low"

        # Generate recommendations
        recommendations = []

        if impact_level in ["critical", "high"]:
            recommendations.append(f"️  {service_name} is CRITICAL - implement redundancy")
            recommendations.append("Consider hot standby or active-active deployment")
            recommendations.append("Implement circuit breakers in dependent services")

        if impact["total_affected"] > 5:
            recommendations.append("High dependency count - review architecture")
            recommendations.append("Consider service decomposition or caching")

        recommendations.append(f"Create BCM recovery plan for {service_name} failure")
        recommendations.append("Test failure scenarios regularly")

        return ImpactAnalysisResponse(
            service_name=service_name,
            directly_affected=impact["directly_affected"],
            transitively_affected=impact["total_affected"],
            affected_services=impact["affected_services"],
            impact_level=impact_level,
            recommendations=recommendations
        )

    except Exception as e:
        logger.error(f"Failed to analyze failure impact: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/critical-services")
async def get_critical_services(
    current_user = Depends(get_current_active_user)
):
    """
    Get list of critical services

    Critical services are services that many other services depend on.
    Failure of critical services has cascading impact.

    Returns ranked list of critical services.
    """
    try:
        logger.info(f"User {current_user.get('id')} requesting critical services")

        # Discover topology
        mapper = PlatformTopologyMapper()
        topology = await mapper.discover_all_services()

        # Build integration graph
        graph = IntegrationGraph()

        for svc_name, svc_info in topology.services.items():
            graph.add_service(svc_name)
            for dep in svc_info.integrations:
                graph.add_integration(svc_name, dep, "depends_on")

        # Identify critical services
        critical_services = graph.identify_critical_services()

        # Rank by impact
        ranked = []
        for service_name in critical_services:
            impact = graph.assess_impact_if_service_fails(service_name)
            ranked.append({
                "service_name": service_name,
                "dependent_count": len(graph.get_transitive_dependents(service_name)),
                "impact_if_fails": impact["total_affected"],
                "status": topology.services[service_name].status.value
            })

        # Sort by impact
        ranked.sort(key=lambda x: x["impact_if_fails"], reverse=True)

        return {
            "total_critical_services": len(critical_services),
            "critical_services": ranked,
            "recommendation": "Ensure high availability for critical services"
        }

    except Exception as e:
        logger.error(f"Failed to get critical services: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh")
async def refresh_topology(
    current_user = Depends(get_current_active_user)
):
    """
    Force refresh platform topology

    Triggers immediate re-discovery of all services.
    Use when you've started/stopped services.
    """
    try:
        logger.info(f"User {current_user.get('id')} forcing topology refresh")

        # Create mapper and discover
        mapper = PlatformTopologyMapper()
        topology = await mapper.discover_all_services()

        return {
            "status": "refreshed",
            "total_services": topology.total_services,
            "running_services": topology.running_services,
            "platform_health": f"{topology.platform_health_percentage:.1f}%",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to refresh topology: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
