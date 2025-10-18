"""
BIA Service Configuration

Inherits from shared SharedSettings with BIA-specific settings.
"""

from typing import List
from shared.config import SharedSettings


class BIASettings(SharedSettings):
    """BIA Service Settings"""

    # Service Identity (override defaults)
    SERVICE_NAME: str = "bia"
    SERVICE_TITLE: str = "BIA Service - Business Impact Analysis"
    SERVICE_PORT: int = 8012
    API_PREFIX: str = "/api/bia"

    # NOTE: These are development defaults
    # In production, set via environment variables:
    # - BIA_DATABASE_URL
    # - BIA_JWT_SECRET

    # Development defaults (override in production via env vars)
    DATABASE_URL: str = "sqlite+aiosqlite:///./bia_dev.db"
    JWT_SECRET_KEY: str = "dev-secret-CHANGE-IN-PRODUCTION-12345"

    # BIA-Specific Settings
    WHO_TIER_ENABLED: bool = True  # WHO Essential Services (healthcare)
    SUPPLY_CHAIN_ENABLED: bool = True  # Supply Chain BCM module

    # EventBus Topics (BIA subscribes to these)
    SUBSCRIBE_TOPICS: List[str] = [
        "governance.organization.created",  # Auto-create BIA template
        "risk.critical_risk_identified",     # Link to BIA process
    ]

    class Config:
        env_prefix = "BIA_"  # Environment variables: BIA_SERVICE_PORT, etc.


# Global settings instance
settings = BIASettings()
