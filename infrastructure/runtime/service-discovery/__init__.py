"""
Service Discovery Module

Complete service discovery, registry, and health monitoring system
combining service registry, health checks, and ISO 22301 mapping.

Extracted from:
- intelligent-core/orchestrator_обьединенный/core/service_registry.py
- intelligent-core/orchestrator_обьединенный/core/health_monitor.py
- intelligent-core/platform-orchestrator/platform_orchestrator.py (SERVICES dict)
Date: 2025-10-04
"""

from .service_registry import ServiceRegistry, Service
from .health_monitor import HealthMonitor, HealthCheck, HealthCheckResult, HealthStatus
from .iso_service_map import ISO_SERVICE_REGISTRY

__all__ = [
    'ServiceRegistry',
    'Service',
    'HealthMonitor',
    'HealthCheck',
    'HealthCheckResult',
    'HealthStatus',
    'ISO_SERVICE_REGISTRY'
]
