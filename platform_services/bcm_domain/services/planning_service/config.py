"""
Planning Service Configuration
ISO 22301 Clause 8.3 - Business Continuity Strategy
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Planning Service Settings"""

    # Service
    SERVICE_NAME: str = "planning_service"
    SERVICE_PORT: int = 8015

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

    # Vector DB
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_INDEX: str = "bcm-knowledge"

    # Auth - JWT Configuration
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"  # Fallback for HS256
    JWT_ALGORITHM: str = "RS256"  # Default to RS256 for production
    JWT_PUBLIC_KEY: str = "PLACEHOLDER_DEV_MODE"  # RSA public key for token validation
    JWT_AUDIENCE: Optional[str] = "bcm-platform"  # Expected audience in JWT token

    # Integration Services
    BIA_SERVICE_URL: str = "http://localhost:8012"
    RISK_SERVICE_URL: str = "http://localhost:8006"

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
