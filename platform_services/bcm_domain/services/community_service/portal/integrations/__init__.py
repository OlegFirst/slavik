"""
Portal Service - Integrations Package
HTTP clients for communication with other BCM services
"""

from .clients_client import ClientsClient
from .validation_client import ValidationClient
from .ai_client import AIClient

__all__ = [
    "ClientsClient",
    "ValidationClient",
    "AIClient",
]
