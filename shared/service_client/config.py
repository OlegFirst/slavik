"""
Service Configuration Models
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ServiceConfig:
    """Configuration for a microservice"""

    name: str
    service_type: str
    base_url: str
    port: int
    api_key: Optional[str] = None
    timeout: int = 30
    health_endpoint: str = "/health"

    def get_full_url(self) -> str:
        """Get full service URL"""
        return f"{self.base_url}:{self.port}"
