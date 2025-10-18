"""
Governance Service Configuration
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))

from shared.config import SharedSettings
from pydantic import Field


class GovernanceServiceSettings(SharedSettings):
    """Governance Service settings"""

    SERVICE_NAME: str = "governance"
    SERVICE_PORT: int = 8013
    SERVICE_VERSION: str = "1.0.0"

    # Governance specific
    ENABLE_DOMAIN_INTELLIGENCE: bool = True
    ENABLE_AI_RECOMMENDATIONS: bool = True

    # CORS configuration
    CORS_ALLOW_METHODS: list[str] = Field(
        default=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        description="Allowed HTTP methods"
    )
    CORS_ALLOW_HEADERS: list[str] = Field(
        default=["*"],
        description="Allowed HTTP headers"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = GovernanceServiceSettings()
