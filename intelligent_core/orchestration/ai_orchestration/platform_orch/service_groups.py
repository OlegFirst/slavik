"""
Service Groups - Service grouping and dependency management

Defines service groups with their dependencies for orchestrated startup
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class ServiceGroup:
    """
    Service group definition with dependencies

    Groups services by their role and defines startup order through dependencies
    """
    name: str
    services: List[str]
    dependencies: List[str] = field(default_factory=list)
    description: str = ""
    critical: bool = False  # If true, failure stops deployment

    def __post_init__(self):
        """Validate service group"""
        if not self.name:
            raise ValueError("Service group must have a name")
        if not self.services:
            raise ValueError(f"Service group {self.name} must have at least one service")

    async def is_ready(self, service_registry) -> bool:
        """
        Check if all services in group are ready

        Args:
            service_registry: ServiceRegistry instance

        Returns:
            True if all services running and healthy
        """
        for service_name in self.services:
            service = await service_registry.get_service(service_name)
            if not service:
                logger.debug(f"Service {service_name} not found in registry")
                return False

            if service.status != "running":
                logger.debug(f"Service {service_name} not running (status: {service.status})")
                return False

            if service.health_status and service.health_status != "healthy":
                logger.debug(f"Service {service_name} not healthy (health: {service.health_status})")
                return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'services': self.services,
            'dependencies': self.dependencies,
            'description': self.description,
            'critical': self.critical
        }


# ============================================
# SERVICE GROUP DEFINITIONS
# ============================================
# Based on analysis from platform_orchestrator source #1

SERVICE_GROUPS = {
    # Foundation services (postgres, redis, rabbitmq) managed externally

    'infrastructure': ServiceGroup(
        name='infrastructure',
        services=['eventbus', 'unified_database_gateway', 'unified_api_gateway'],
        dependencies=[],  # No dependencies - foundation external
        description='Core infrastructure services (gateways, event bus)',
        critical=True
    ),

    'business': ServiceGroup(
        name='business',
        services=['odoo', 'bia_engine', 'compliance_checker', 'bpmn_service'],
        dependencies=['infrastructure'],
        description='Business logic services (Odoo, BCM engines)',
        critical=False
    ),

    'intelligence': ServiceGroup(
        name='intelligence',
        services=['ai_orchestrator', 'ai_control_center', 'digital_twin'],
        dependencies=['infrastructure'],
        description='AI and intelligence services',
        critical=False
    ),

    'applications': ServiceGroup(
        name='applications',
        services=['admin_panel', 'web_portal', 'mobile_backend'],
        dependencies=['infrastructure', 'business', 'intelligence'],
        description='User-facing applications',
        critical=False
    )
}


def get_startup_order() -> List[str]:
    """
    Get service group startup order based on dependencies

    Returns:
        List of group names in startup order
    """
    # Topological sort of dependencies
    order = []
    visited = set()

    def visit(group_name: str):
        if group_name in visited:
            return

        group = SERVICE_GROUPS.get(group_name)
        if not group:
            logger.warning(f"Unknown service group: {group_name}")
            return

        # Visit dependencies first
        for dep in group.dependencies:
            visit(dep)

        visited.add(group_name)
        order.append(group_name)

    # Visit all groups
    for group_name in SERVICE_GROUPS.keys():
        visit(group_name)

    return order


def get_parallel_groups() -> List[List[str]]:
    """
    Get groups that can start in parallel

    Returns:
        List of lists, each inner list can start in parallel
    """
    order = get_startup_order()

    # Group by dependency level
    levels: Dict[int, List[str]] = {}

    for group_name in order:
        group = SERVICE_GROUPS[group_name]

        # Calculate level (max dependency level + 1)
        level = 0
        for dep in group.dependencies:
            dep_level = next(
                (lvl for lvl, groups in levels.items() if dep in groups),
                0
            )
            level = max(level, dep_level + 1)

        if level not in levels:
            levels[level] = []
        levels[level].append(group_name)

    # Convert to list of lists
    parallel = [levels[i] for i in sorted(levels.keys())]

    return parallel


def validate_service_groups() -> bool:
    """
    Validate service group definitions

    Checks:
    - No circular dependencies
    - All dependencies exist
    - No duplicate services

    Returns:
        True if valid
    """
    # Check for circular dependencies
    def has_cycle(group_name: str, visited: set, stack: set) -> bool:
        visited.add(group_name)
        stack.add(group_name)

        group = SERVICE_GROUPS.get(group_name)
        if group:
            for dep in group.dependencies:
                if dep not in visited:
                    if has_cycle(dep, visited, stack):
                        return True
                elif dep in stack:
                    return True

        stack.remove(group_name)
        return False

    visited = set()
    for group_name in SERVICE_GROUPS.keys():
        if group_name not in visited:
            if has_cycle(group_name, visited, set()):
                logger.error(f"Circular dependency detected involving {group_name}")
                return False

    # Check all dependencies exist
    for group_name, group in SERVICE_GROUPS.items():
        for dep in group.dependencies:
            if dep not in SERVICE_GROUPS:
                logger.error(f"Unknown dependency {dep} in group {group_name}")
                return False

    # Check for duplicate services
    all_services = []
    for group in SERVICE_GROUPS.values():
        all_services.extend(group.services)

    if len(all_services) != len(set(all_services)):
        duplicates = [s for s in all_services if all_services.count(s) > 1]
        logger.error(f"Duplicate services found: {set(duplicates)}")
        return False

    logger.info("Service group validation passed")
    return True


# Validate on module import
if not validate_service_groups():
    logger.warning("Service group validation failed - check configuration")