"""
Platform Orchestration - Infrastructure lifecycle management

Manages Docker services, service groups, dependencies, and platform startup/shutdown
"""

from .service_groups import ServiceGroup, SERVICE_GROUPS
from .platform_orchestrator import PlatformOrchestrator
from .deployment_manager import DeploymentManager

__all__ = [
    'ServiceGroup',
    'SERVICE_GROUPS',
    'PlatformOrchestrator',
    'DeploymentManager',
]