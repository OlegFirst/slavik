"""
Plans Service Configuration
ISO 22301 Clause 8.4 - Business Continuity Plans and Procedures
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Plans Service Settings"""

    # Service
    SERVICE_NAME: str = "plans"
    SERVICE_TITLE: str = "Plans Service"
    SERVICE_DESCRIPTION: str = "BCM Plans & Procedures - ISO 22301 Clause 8.4"
    SERVICE_VERSION: str = "1.0.0"
    SERVICE_PORT: int = 8020

    # Database - Development defaults (override in production)
    DATABASE_URL: str = "sqlite+aiosqlite:///./plans_dev.db"
    DB_POOL_SIZE: int = 20
    DB_ECHO: bool = False

    # JWT Secret - MUST be set in production
    JWT_SECRET_KEY: str = "dev-secret-CHANGE-IN-PRODUCTION-plans-12345"
    LOG_LEVEL: str = "INFO"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # EventBus
    EVENTBUS_URL: str = "http://localhost:8001"

    # Orchestrator
    ORCHESTRATOR_URL: str = "http://localhost:8002"

    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # Auth - JWT Token Validation
    JWT_PUBLIC_KEY: str = ""  # RSA public key for token validation (empty = dev mode)
    JWT_ALGORITHM: str = "RS256"  # RSA256 for production, HS256 for symmetric keys
    JWT_AUDIENCE: Optional[str] = None  # Expected audience claim (optional)

    # Legacy (kept for backward compatibility)
    JWT_SECRET: str = "your-secret-key-change-in-production"

    # Integration Services
    BIA_SERVICE_URL: str = "http://localhost:8012"
    RISK_SERVICE_URL: str = "http://localhost:8006"
    PLANNING_SERVICE_URL: str = "http://localhost:8011"
    INCIDENT_SERVICE_URL: str = "http://localhost:8007"

    # CORS Configuration
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",  # React dev server
        "http://localhost:3001",  # Alternative frontend
        "https://app.yourdomain.com",  # Production frontend
        "https://admin.yourdomain.com",  # Admin frontend
    ]
    ALLOWED_METHODS: list = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    ALLOWED_HEADERS: list = ["Authorization", "Content-Type", "X-Request-ID"]

    class Config:
        env_file = ".env"


settings = Settings()
