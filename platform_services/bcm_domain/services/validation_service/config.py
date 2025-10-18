"""
Validation Service Configuration
ISO 22301 Clauses 8.5, 9.1, 9.2, 9.3, 10
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Validation Service Settings"""

    # Service Identity
    SERVICE_NAME: str = "validation"
    SERVICE_PORT: int = 8022
    SERVICE_VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # RabbitMQ / Message Queue
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Event Bus
    EVENTBUS_URL: str = "http://localhost:8001"
    ORCHESTRATOR_URL: str = "http://localhost:8002"

    # KPI Auto-Collection Settings
    KPI_COLLECTION_INTERVAL_HOURS: int = 24
    KPI_ALERT_CHECK_INTERVAL_HOURS: int = 1
    ALERT_THRESHOLD_CRITICAL: float = 0.8
    ALERT_THRESHOLD_WARNING: float = 0.9

    # Email Configuration for KPI Alerts
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USERNAME: str = ""
    EMAIL_PASSWORD: str = ""
    EMAIL_FROM: str = "bcms-alerts@example.com"
    EMAIL_USE_TLS: bool = True

    # JWT Authentication
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # CORS
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"

    # Multi-tenancy
    ENABLE_ROW_LEVEL_SECURITY: bool = True

    # Integration URLs (other BCM services)
    GOVERNANCE_SERVICE_URL: str = "http://localhost:8020"
    PLANS_SERVICE_URL: str = "http://localhost:8021"
    INCIDENTS_SERVICE_URL: str = "http://localhost:8023"
    COMPLIANCE_SERVICE_URL: str = "http://localhost:8006"

    # Feature Flags
    ENABLE_KPI_AUTO_COLLECTION: bool = True
    ENABLE_KPI_ALERTING: bool = True
    ENABLE_EMAIL_NOTIFICATIONS: bool = True

    # Performance
    MAX_CONCURRENT_TASKS: int = 10
    API_RATE_LIMIT: str = "100/minute"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Singleton instance
settings = Settings()
