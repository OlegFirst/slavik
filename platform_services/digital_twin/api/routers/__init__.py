"""
API Routers

REST API route handlers
"""

# Existing routers
from . import (
    auth,
    organizations,
    simulations,
    metrics,
    health,
    bridges,
    import_data,
    visualize,
    integrations,
    scenarios,
    exercises,
    predictions,
    bia
)

# NEW: System Clone & Integration routers
from . import (
    topology,
    system_clone,
    platform_bridges,
    data_collector
)

__all__ = [
    # Existing
    "auth",
    "organizations",
    "simulations",
    "metrics",
    "health",
    "bridges",
    "import_data",
    "visualize",
    "integrations",
    "scenarios",
    "exercises",
    "predictions",
    "bia",
    # NEW
    "topology",
    "system_clone",
    "platform_bridges",
    "data_collector"
]
