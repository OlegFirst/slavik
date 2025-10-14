"""
API Package for Simulation Service

Contains all API routers and endpoints.
"""

from .bridge_router import router as bridge_router
from .scenario_advanced_router import router as scenario_advanced_router
from .simulation_router import router as simulation_router
from .execution_router import router as execution_router
from .scenario_router import router as scenario_router
from .scenario_library_router import router as scenario_library_router

__all__ = [
    "bridge_router",
    "scenario_advanced_router",
    "simulation_router",
    "execution_router",
    "scenario_router",
    "scenario_library_router"
]
