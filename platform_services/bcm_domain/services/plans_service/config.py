"""
Plans Service Configuration
ISO 22301 Clause 8.4 - Business Continuity Plans and Procedures
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Plans Service Settings"""

    # Service
    SERVICE_NAME: str = "plans_service"
    SERVICE_PORT: int = 8023

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://bcm:bcm@localhost:5432/bcm"
    DB_POOL_SIZE: int = 20

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
