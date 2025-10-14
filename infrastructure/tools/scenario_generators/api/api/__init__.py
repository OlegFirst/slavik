"""
API routes for Scenario Orchestrator
"""

from .generation_routes import router as generation_router
from .monitoring_routes import router as monitoring_router

__all__ = ["generation_router", "monitoring_router"]
