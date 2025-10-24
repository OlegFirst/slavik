"""
Configuration Settings for Documents Service
Uses pydantic_settings for environment-based configuration
"""

from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Service Information
    SERVICE_NAME: str = "documents"
    SERVICE_PORT: int = 8017
    SERVICE_VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/bcm_platform"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Storage
    STORAGE_PATH: str = "./storage/documents"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB

    # EventBus
    EVENTBUS_URL: str = "amqp://guest:guest@localhost:5672/"
    EVENTBUS_EXCHANGE: str = "bcm_events"

    # Orchestrator
    ORCHESTRATOR_URL: str = "http://localhost:8002"
    REGISTER_WITH_ORCHESTRATOR: bool = True

    # AI Services
    AI_INTELLIGENCE_URL: str = "http://localhost:8000"
    OPENAI_API_KEY: Optional[str] = None

    # Retention Defaults
    DEFAULT_RETENTION_YEARS: int = 7
    ARCHIVE_AFTER_DAYS: int = 365

    # Security
    SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: list = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
