"""
Shared Configuration
====================

Shared configuration settings for BCM Platform services.

Features:
- Environment-based configuration
- Database settings
- Redis settings
- RabbitMQ settings
- JWT settings
"""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class SharedSettings(BaseSettings):
    """
    Shared configuration settings.

    All BCM Platform services can extend this class for common configuration.

    Example:
        ```python
        # In validation service
        from shared.config import SharedSettings

        class ValidationSettings(SharedSettings):
            SERVICE_NAME: str = "validation"
            # Add service-specific settings here

        settings = ValidationSettings()
        ```
    """

    # Environment
    ENVIRONMENT: str = Field(
        "development",
        description="Environment: development, staging, production"
    )

    # Service Info
    SERVICE_NAME: str = Field(
        "bcm-service",
        description="Service name"
    )
    SERVICE_VERSION: str = Field(
        "1.0.0",
        description="Service version"
    )

    # Database Configuration
    DATABASE_URL: str = Field(
        ...,
        description="Database connection URL (postgresql+asyncpg://...)"
    )
    DB_POOL_SIZE: int = Field(
        20,
        description="Database connection pool size"
    )
    DB_MAX_OVERFLOW: int = Field(
        10,
        description="Maximum overflow connections"
    )
    DB_POOL_RECYCLE: int = Field(
        3600,
        description="Connection recycle time in seconds"
    )
    DB_ECHO: bool = Field(
        False,
        description="Echo SQL statements"
    )

    # Redis Configuration
    REDIS_URL: str = Field(
        "redis://localhost:6379/0",
        description="Redis connection URL"
    )
    CACHE_DEFAULT_TTL: int = Field(
        3600,
        description="Default cache TTL in seconds"
    )

    # RabbitMQ Configuration
    RABBITMQ_URL: str = Field(
        "amqp://guest:guest@localhost/",
        description="RabbitMQ connection URL"
    )
    EVENTBUS_EXCHANGE: str = Field(
        "bcm_events",
        description="EventBus exchange name"
    )

    # JWT Configuration
    JWT_SECRET_KEY: str = Field(
        ...,
        description="JWT secret key for signing tokens"
    )
    JWT_ALGORITHM: str = Field(
        "HS256",
        description="JWT algorithm"
    )
    JWT_EXPIRATION_HOURS: int = Field(
        24,
        description="JWT token expiration in hours"
    )

    # CORS Configuration
    CORS_ORIGINS: list[str] = Field(
        ["http://localhost:3000"],
        description="Allowed CORS origins"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        True,
        description="Allow credentials in CORS"
    )

    # Logging
    LOG_LEVEL: str = Field(
        "INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR"
    )
    LOG_FORMAT: str = Field(
        "json",
        description="Log format: json or text"
    )

    # Metrics
    METRICS_ENABLED: bool = Field(
        True,
        description="Enable Prometheus metrics"
    )
    METRICS_PORT: int = Field(
        9090,
        description="Metrics server port"
    )

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(
        True,
        description="Enable rate limiting"
    )
    RATE_LIMIT_PER_MINUTE: int = Field(
        60,
        description="Requests per minute per user"
    )

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = Field(
        100,
        description="Maximum upload size in MB"
    )
    ALLOWED_FILE_TYPES: list[str] = Field(
        [".pdf", ".docx", ".xlsx", ".jpg", ".png"],
        description="Allowed file extensions"
    )

    # External Services
    EVENTBUS_URL: Optional[str] = Field(
        None,
        description="EventBus service URL for cross-service communication"
    )

    # Security
    ENCRYPTION_KEY: Optional[str] = Field(
        None,
        description="Master encryption key for file encryption"
    )
    ENABLE_VIRUS_SCAN: bool = Field(
        True,
        description="Enable virus scanning for uploads"
    )

    # Email (for notifications)
    SMTP_HOST: Optional[str] = Field(
        None,
        description="SMTP server host"
    )
    SMTP_PORT: int = Field(
        587,
        description="SMTP server port"
    )
    SMTP_USER: Optional[str] = Field(
        None,
        description="SMTP username"
    )
    SMTP_PASSWORD: Optional[str] = Field(
        None,
        description="SMTP password"
    )
    SMTP_FROM_EMAIL: Optional[str] = Field(
        None,
        description="From email address"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


def get_settings() -> SharedSettings:
    """
    Get shared settings instance.

    Returns:
        SharedSettings: Settings instance

    Example:
        ```python
        settings = get_settings()
        print(f"Database: {settings.DATABASE_URL}")
        ```
    """
    return SharedSettings()
