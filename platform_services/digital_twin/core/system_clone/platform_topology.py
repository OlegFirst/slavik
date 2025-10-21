"""
Platform Topology Mapper
Discovers and maps all services in AI-Platform-ISO ecosystem

Features:
- Auto-discovery of all platform services
- Port scanning and health checking
- Service dependency mapping
- Real-time topology updates
"""

import logging
import httpx
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ServiceStatus(str, Enum):
    """Service status"""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    UNKNOWN = "unknown"


class ServiceType(str, Enum):
    """Service types in platform"""
    PLATFORM_SERVICE = "platform_service"
    INTELLIGENT_CORE = "intelligent_core"
    INFRASTRUCTURE = "infrastructure"
    FRONTEND = "frontend"


@dataclass
class ServiceInfo:
    """Information about a platform service"""
    name: str
    port: int
    service_type: ServiceType
    status: ServiceStatus = ServiceStatus.UNKNOWN
    health_endpoint: str = "/health"
    base_url: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    integrations: List[str] = field(default_factory=list)
    last_checked: Optional[str] = None
    response_time_ms: Optional[float] = None

    def __post_init__(self):
        if not self.base_url:
            self.base_url = f"http://localhost:{self.port}"


@dataclass
class PlatformTopology:
    """Complete platform topology"""
    services: Dict[str, ServiceInfo] = field(default_factory=dict)
    integration_map: Dict[str, List[str]] = field(default_factory=dict)
    discovered_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    total_services: int = 0
    running_services: int = 0

    def add_service(self, service: ServiceInfo):
        """Add service to topology"""
        self.services[service.name] = service
        self.total_services = len(self.services)
        self._update_counts()

    def _update_counts(self):
        """Update service counts"""
        self.running_services = sum(
            1 for s in self.services.values()
            if s.status == ServiceStatus.RUNNING
        )


class PlatformTopologyMapper:
    """
    Platform Topology Mapper

    Discovers all services in AI-Platform-ISO ecosystem and creates
    a complete map of the platform architecture.

    Features:
    - Service discovery via known ports
    - Health checking
    - Dependency mapping
    - Integration graph creation
    """

    # Known platform services with their ports
    KNOWN_SERVICES = {
        # Platform Services
        "eventbus": ServiceInfo("eventbus", 8055, ServiceType.PLATFORM_SERVICE,
                                description="Event choreography and pub/sub"),
        "simulation_service": ServiceInfo("simulation_service", 8095, ServiceType.PLATFORM_SERVICE,
                                         description="BCM simulations and modeling"),
        "digital_twin": ServiceInfo("digital_twin", 8096, ServiceType.PLATFORM_SERVICE,
                                   description="Organization digital twin and personal dashboard"),
        "workflow_intelligence": ServiceInfo("workflow_intelligence", 8037, ServiceType.PLATFORM_SERVICE,
                                            description="PDCA cycles and case library"),
        "knowledge_center": ServiceInfo("knowledge_center", 8038, ServiceType.PLATFORM_SERVICE,
                                       description="Best practices and RAG"),
        "community_intelligence": ServiceInfo("community_intelligence", 8030, ServiceType.PLATFORM_SERVICE,
                                             description="Community sharing and insights"),
        "predictive_journey": ServiceInfo("predictive_journey", 8031, ServiceType.PLATFORM_SERVICE,
                                         description="Outcome forecasting"),
        "ai_foundation": ServiceInfo("ai_foundation", 8025, ServiceType.PLATFORM_SERVICE,
                                    description="RAG, LLM, ML foundation"),
        "ai_orchestrator": ServiceInfo("ai_orchestrator", 8026, ServiceType.PLATFORM_SERVICE,
                                      description="Autonomous decision-making"),

        # Intelligent Core Modules
        "scenario_intelligence": ServiceInfo("scenario_intelligence", 8060, ServiceType.INTELLIGENT_CORE,
                                            description="Scenario generation and analysis"),
        "pdca_assistant": ServiceInfo("pdca_assistant", 8061, ServiceType.INTELLIGENT_CORE,
                                     description="Plan-Do-Check-Act automation"),

        # Infrastructure
        "api_gateway": ServiceInfo("api_gateway", 8000, ServiceType.INFRASTRUCTURE,
                                  description="Main API gateway"),

        # Frontend
        "unified_frontend": ServiceInfo("unified_frontend", 3000, ServiceType.FRONTEND,
                                       description="Next.js unified frontend"),
    }

    def __init__(self, timeout: float = 5.0):
        """
        Initialize topology mapper

        Args:
            timeout: HTTP request timeout in seconds
        """
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        self.topology = PlatformTopology()

    async def discover_all_services(self) -> PlatformTopology:
        """
        Discover all services in platform

        Returns:
            Complete platform topology
        """
        logger.info("Starting platform service discovery...")

        # Check all known services
        for service_name, service_info in self.KNOWN_SERVICES.items():
            logger.info(f"Checking service: {service_name} (port {service_info.port})")

            # Check health
            is_healthy = await self._check_service_health(service_info)

            if is_healthy:
                service_info.status = ServiceStatus.RUNNING
                logger.info(f" {service_name} is running")
            else:
                service_info.status = ServiceStatus.STOPPED
                logger.warning(f" {service_name} is not responding")

            # Add to topology
            self.topology.add_service(service_info)

        # Discover integrations
        await self._discover_integrations()

        logger.info(
            f"Discovery complete: {self.topology.running_services}/{self.topology.total_services} "
            f"services running"
        )

        return self.topology

    async def _check_service_health(self, service: ServiceInfo) -> bool:
        """
        Check if service is healthy

        Args:
            service: Service to check

        Returns:
            True if healthy, False otherwise
        """
        try:
            start_time = datetime.utcnow()

            response = await self.client.get(
                f"{service.base_url}{service.health_endpoint}",
                timeout=self.timeout
            )

            # Calculate response time
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            service.response_time_ms = response_time
            service.last_checked = datetime.utcnow().isoformat()

            if response.status_code == 200:
                # Try to extract version if available
                try:
                    health_data = response.json()
                    service.version = health_data.get("version")
                except:
                    pass

                return True

            return False

        except Exception as error:
            logger.debug(f"Health check failed for {service.name}: {error}")
            service.last_checked = datetime.utcnow().isoformat()
            return False

    async def _discover_integrations(self):
        """Discover service integrations"""
        # Known integration patterns based on architecture
        integration_map = {
            "simulation_service": [
                "eventbus",
                "ai_orchestrator",
                "workflow_intelligence",
                "knowledge_center",
                "community_intelligence",
                "ai_foundation",
                "digital_twin"
            ],
            "digital_twin": [
                "simulation_service",
                "eventbus",
                "workflow_intelligence",
                "knowledge_center"
            ],
            "workflow_intelligence": [
                "eventbus",
                "simulation_service",
                "knowledge_center",
                "ai_foundation"
            ],
            "eventbus": [
                # EventBus connects to all services
            ],
            "ai_foundation": [
                "eventbus",
                "simulation_service",
                "workflow_intelligence",
                "knowledge_center"
            ]
        }

        # Update service integrations
        for service_name, integrations in integration_map.items():
            if service_name in self.topology.services:
                self.topology.services[service_name].integrations = integrations

        # Build integration map
        self.topology.integration_map = integration_map

    async def get_service_info(self, service_name: str) -> Optional[ServiceInfo]:
        """
        Get information about specific service

        Args:
            service_name: Name of service

        Returns:
            Service info or None if not found
        """
        return self.topology.services.get(service_name)

    async def get_running_services(self) -> List[ServiceInfo]:
        """
        Get all running services

        Returns:
            List of running services
        """
        return [
            service for service in self.topology.services.values()
            if service.status == ServiceStatus.RUNNING
        ]

    async def get_services_by_type(self, service_type: ServiceType) -> List[ServiceInfo]:
        """
        Get services by type

        Args:
            service_type: Type of services to get

        Returns:
            List of services of specified type
        """
        return [
            service for service in self.topology.services.values()
            if service.service_type == service_type
        ]

    async def check_service_dependencies(self, service_name: str) -> Dict[str, bool]:
        """
        Check if all dependencies of a service are running

        Args:
            service_name: Name of service to check

        Returns:
            Dict mapping dependency name to running status
        """
        service = self.topology.services.get(service_name)
        if not service:
            return {}

        dependency_status = {}

        for integration in service.integrations:
            dep_service = self.topology.services.get(integration)
            if dep_service:
                dependency_status[integration] = (
                    dep_service.status == ServiceStatus.RUNNING
                )
            else:
                dependency_status[integration] = False

        return dependency_status

    async def get_topology_summary(self) -> Dict[str, Any]:
        """
        Get summary of platform topology

        Returns:
            Topology summary
        """
        services_by_type = {}
        for service_type in ServiceType:
            services = await self.get_services_by_type(service_type)
            services_by_type[service_type.value] = {
                "total": len(services),
                "running": sum(1 for s in services if s.status == ServiceStatus.RUNNING),
                "services": [s.name for s in services]
            }

        return {
            "discovered_at": self.topology.discovered_at,
            "total_services": self.topology.total_services,
            "running_services": self.topology.running_services,
            "services_by_type": services_by_type,
            "integration_count": len(self.topology.integration_map),
            "health_percentage": (
                self.topology.running_services / self.topology.total_services * 100
                if self.topology.total_services > 0 else 0
            )
        }

    async def export_topology_graph(self) -> Dict[str, Any]:
        """
        Export topology as graph for visualization

        Returns:
            Graph data (nodes and edges)
        """
        nodes = []
        edges = []

        # Create nodes
        for service_name, service_info in self.topology.services.items():
            nodes.append({
                "id": service_name,
                "label": service_name,
                "type": service_info.service_type.value,
                "status": service_info.status.value,
                "port": service_info.port,
                "description": service_info.description,
                "response_time_ms": service_info.response_time_ms
            })

        # Create edges
        for service_name, integrations in self.topology.integration_map.items():
            for target_service in integrations:
                edges.append({
                    "from": service_name,
                    "to": target_service,
                    "type": "integration"
                })

        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "generated_at": datetime.utcnow().isoformat()
            }
        }

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
