"""
Integration Clients for Digital Twin
Connects Digital Twin with all platform services
"""

from core.integrations.simulation_service_bridge import SimulationServiceBridge
from core.integrations.system_bcm_bridge import SystemBCMBridge

__all__ = [
    "SimulationServiceBridge",
    "SystemBCMBridge"
]
