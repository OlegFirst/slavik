"""
External Adapters Integration Layer
Connects Digital Twin Core with external simulation adapters
"""

from core.adapters.external_adapter_client import ExternalAdapterClient
from core.adapters.adapter_router import AdapterRouter

__all__ = ["ExternalAdapterClient", "AdapterRouter"]
