"""
Shared Service Client Library

Unified API client for microservices communication with:
- Service discovery and configuration
- Health monitoring
- Unified error handling
- Authentication
- Multi-method support (GET/POST/PUT/DELETE)

Extracted from Odoo bcm_ai_service.py and adapted for v2.0 architecture
"""

from .config import ServiceConfig
from .health import ServiceHealthMonitor
from .registry import ServiceRegistry
from .client import ServiceClient

__all__ = [
    'ServiceConfig',
    'ServiceHealthMonitor',
    'ServiceRegistry',
    'ServiceClient',
]
