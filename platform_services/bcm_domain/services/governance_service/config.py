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
    SERVICE_PORT: int = 8018
    SERVICE_VERSION: str = "1.0.0"
    SERVICE_TITLE: str = "Governance Service"
    SERVICE_DESCRIPTION: str = "BCM Governance & Leadership - ISO 22301 Clause 5"

    # Database - Development defaults (override in production)
    DATABASE_URL: str = "sqlite+aiosqlite:///./governance_dev.db"

    # JWT Secret - MUST be set in production
    JWT_SECRET_KEY: str = "dev-secret-CHANGE-IN-PRODUCTION-governance-12345"

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
