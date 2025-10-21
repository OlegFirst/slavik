"""
Compliance Service Configuration

Inherits from shared SharedSettings with Compliance-specific settings.
"""

from typing import List
from shared.config import SharedSettings


class ComplianceSettings(SharedSettings):
    """Compliance Service Settings"""

    # Service Identity (override defaults)
    SERVICE_NAME: str = "compliance"
    SERVICE_TITLE: str = "BCM Compliance Service - ISO 22301:2019"
    SERVICE_PORT: int = 8014
    API_PREFIX: str = "/api"

    # NOTE: These are development defaults
    # In production, set via environment variables:
    # - COMPLIANCE_DATABASE_URL
    # - COMPLIANCE_JWT_SECRET

    # Development defaults (override in production via env vars)
    DATABASE_URL: str = "sqlite+aiosqlite:///./compliance_dev.db"
    JWT_SECRET_KEY: str = "dev-secret-CHANGE-IN-PRODUCTION-12345"

    # Compliance-Specific Settings
    AI_ENABLED: bool = True  # AI-powered compliance scanning
    DEBUG_MODE: bool = False

    # ISO 22301 Clauses covered
    ISO_CLAUSES: List[str] = ["9.2", "10.1", "10.2"]

    # Features
    ASSESSMENT_ENGINE_ENABLED: bool = True
    GAP_ANALYSIS_ENABLED: bool = True
    EVIDENCE_WORKFLOW_ENABLED: bool = True
    NONCONFORMITY_MANAGEMENT_ENABLED: bool = True
    AUDIT_SUPPORT_ENABLED: bool = True
    IMPROVEMENT_INITIATIVES_ENABLED: bool = True

    # EventBus Topics (Compliance subscribes to these)
    SUBSCRIBE_TOPICS: List[str] = [
        "governance.organization.created",  # Auto-create compliance framework
        "incident.major_incident_declared",  # Create NC from incident
        "exercise.completed",  # Post-exercise assessment
    ]

    class Config:
        env_prefix = "COMPLIANCE_"  # Environment variables: COMPLIANCE_SERVICE_PORT, etc.


# Global settings instance
settings = ComplianceSettings()
