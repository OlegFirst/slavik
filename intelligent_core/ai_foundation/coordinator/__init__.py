"""
Subsystem Coordinator
=====================

Central coordinator for all federated AI subsystems across the platform.

Like the brain in a nervous system:
- Doesn't control every nerve directly
- Coordinates responses from distributed subsystems
- Aggregates results from multiple subsystems
- Routes requests to appropriate subsystems
- Monitors health of all subsystems

The coordinator knows about all subsystems but doesn't monopolize intelligence.
Each subsystem has its own domain expertise and implementation.
"""

from .subsystem_coordinator import SubsystemCoordinator

__all__ = ["SubsystemCoordinator"]
