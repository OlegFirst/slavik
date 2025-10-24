"""
Response Module - Configuration
ISO 22301:2019 Clause 8.4 - Incident Response

Complete configuration settings for Response service
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class Settings(BaseSettings):
    """
    Configuration settings for Response service

    All settings can be overridden via environment variables
    """

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # ========================================================================
    # Service Configuration
    # ========================================================================

    SERVICE_NAME: str = Field(default="response", description="Service name")
    SERVICE_VERSION: str = Field(default="1.0.0", description="Service version")
    SERVICE_DESCRIPTION: str = Field(
        default="Incident Response Service - ISO 22301:2019 Clause 8.4",
        description="Service description"
    )

    # API Configuration
    API_V1_PREFIX: str = Field(default="/api/v1/response", description="API v1 prefix")
    SERVICE_PORT: int = Field(default=8016, description="Service port")
    HOST: str = Field(default="0.0.0.0", description="Host to bind")
    PORT: int = Field(default=8016, description="Port to bind")
    DEBUG: bool = Field(default=False, description="Debug mode")
    SERVICE_TITLE: str = Field(default="Response Service", description="Service title")
    SERVICE_DESCRIPTION: str = Field(default="BCM Incident Response - ISO 22301 Clause 8.4", description="Service description")

    # ========================================================================
    # Database Configuration
    # ========================================================================

    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./response_dev.db",
        description="Database connection URL"
    )

    DB_SCHEMA: str = Field(default="response", description="Database schema name")
    DB_POOL_SIZE: int = Field(default=20, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=10, description="Database max overflow connections")
    DB_POOL_TIMEOUT: int = Field(default=30, description="Database pool timeout in seconds")
    DB_ECHO: bool = Field(default=False, description="Echo SQL statements")

    # ========================================================================
    # ISO 22301:2019 Configuration
    # ========================================================================

    ISO_STANDARD: str = Field(default="ISO 22301:2019", description="ISO standard")
    ISO_CLAUSE: str = Field(default="8.4", description="ISO clause - Incident response")

    # Default RTO/RPO (hours)
    DEFAULT_RTO_HOURS: float = Field(default=4.0, description="Default Recovery Time Objective (hours)")
    DEFAULT_RPO_HOURS: float = Field(default=1.0, description="Default Recovery Point Objective (hours)")

    # Incident Configuration
    AUTO_ESCALATE_CRITICAL: bool = Field(
        default=True,
        description="Auto-escalate critical incidents"
    )
    AUTO_CREATE_TIMELINE: bool = Field(
        default=True,
        description="Automatically create timeline entries"
    )
    REQUIRE_ROOT_CAUSE_ON_RESOLVE: bool = Field(
        default=True,
        description="Require root cause analysis when resolving incidents"
    )

    # Response Time Thresholds (minutes)
    RESPONSE_TIME_LOW: int = Field(default=240, description="Response time for low severity (minutes)")
    RESPONSE_TIME_MEDIUM: int = Field(default=120, description="Response time for medium severity (minutes)")
    RESPONSE_TIME_HIGH: int = Field(default=60, description="Response time for high severity (minutes)")
    RESPONSE_TIME_CRITICAL: int = Field(default=15, description="Response time for critical severity (minutes)")

    # ========================================================================
    # CORS Configuration
    # ========================================================================

    CORS_ORIGINS: list = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:8000",
            "https://*.vercel.app",
            "https://*.supabase.co"
        ],
        description="CORS allowed origins"
    )
    CORS_CREDENTIALS: bool = Field(default=True, description="CORS allow credentials")
    CORS_METHODS: list = Field(default=["*"], description="CORS allowed methods")
    CORS_HEADERS: list = Field(default=["*"], description="CORS allowed headers")

    # ========================================================================
    # Logging Configuration
    # ========================================================================

    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    LOG_FILE: Optional[str] = Field(default=None, description="Log file path")
    LOG_JSON: bool = Field(default=False, description="Log in JSON format")

    # ========================================================================
    # Event Bus Configuration
    # ========================================================================

    EVENT_BUS_ENABLED: bool = Field(default=False, description="Enable event bus integration")
    EVENT_BUS_TYPE: str = Field(default="memory", description="Event bus type (memory, rabbitmq, kafka)")

    # RabbitMQ Configuration
    RABBITMQ_HOST: str = Field(default="localhost", description="RabbitMQ host")
    RABBITMQ_PORT: int = Field(default=5672, description="RabbitMQ port")
    RABBITMQ_USER: str = Field(default="guest", description="RabbitMQ user")
    RABBITMQ_PASSWORD: str = Field(default="guest", description="RabbitMQ password")
    RABBITMQ_VHOST: str = Field(default="/", description="RabbitMQ virtual host")
    RABBITMQ_EXCHANGE: str = Field(default="bcm_events", description="RabbitMQ exchange")

    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = Field(default="localhost:9092", description="Kafka bootstrap servers")
    KAFKA_TOPIC_PREFIX: str = Field(default="bcm.response", description="Kafka topic prefix")

    # ========================================================================
    # External Service Configuration
    # ========================================================================

    # Risk Service
    RISK_SERVICE_URL: str = Field(
        default="http://localhost:8031",
        description="Risk analysis service URL"
    )

    # Impact Service
    IMPACT_SERVICE_URL: str = Field(
        default="http://localhost:8032",
        description="Impact analysis service URL"
    )

    # Recovery Service
    RECOVERY_SERVICE_URL: str = Field(
        default="http://localhost:8042",
        description="Recovery service URL"
    )

    # Notification Service
    NOTIFICATION_SERVICE_URL: Optional[str] = Field(
        default=None,
        description="External notification service URL"
    )

    # ========================================================================
    # Security Configuration
    # ========================================================================

    SECRET_KEY: str = Field(
        default="change-me-in-production",
        description="Secret key for signing tokens"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiration (minutes)")

    # JWT Authentication
    JWT_AUTH_ENABLED: bool = Field(
        default=False,
        description="Enable JWT authentication (set to false for development)"
    )
    JWT_SECRET_KEY: str = Field(
        default="dev-secret-CHANGE-IN-PRODUCTION-response-12345",
        description="JWT secret key for token signing/verification"
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )
    JWT_EXPIRATION_MINUTES: int = Field(
        default=30,
        description="JWT token expiration time in minutes"
    )

    # API Key for internal service communication
    API_KEY: Optional[str] = Field(default=None, description="API key for service authentication")

    # ========================================================================
    # Rate Limiting
    # ========================================================================

    RATE_LIMIT_ENABLED: bool = Field(default=False, description="Enable rate limiting")
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Max requests per window")
    RATE_LIMIT_WINDOW: int = Field(default=60, description="Rate limit window (seconds)")

    # ========================================================================
    # Monitoring & Health
    # ========================================================================

    HEALTH_CHECK_ENABLED: bool = Field(default=True, description="Enable health check endpoint")
    METRICS_ENABLED: bool = Field(default=True, description="Enable metrics collection")
    METRICS_PORT: int = Field(default=9090, description="Metrics port")

    # ========================================================================
    # Performance Configuration
    # ========================================================================

    MAX_CONNECTIONS_PER_INCIDENT: int = Field(
        default=100,
        description="Max concurrent connections per incident"
    )
    CACHE_TTL: int = Field(default=300, description="Cache TTL in seconds")
    CACHE_ENABLED: bool = Field(default=False, description="Enable caching")

    # Pagination
    DEFAULT_PAGE_SIZE: int = Field(default=20, description="Default page size")
    MAX_PAGE_SIZE: int = Field(default=100, description="Maximum page size")

    # ========================================================================
    # Feature Flags
    # ========================================================================

    FEATURE_AUTO_ESCALATION: bool = Field(default=True, description="Enable auto-escalation")
    FEATURE_STAKEHOLDER_NOTIFICATIONS: bool = Field(default=True, description="Enable stakeholder notifications")
    FEATURE_COMPLIANCE_CHECKS: bool = Field(default=True, description="Enable compliance checks")
    FEATURE_METRICS_VALIDATION: bool = Field(default=True, description="Enable metrics validation")
    FEATURE_TIMELINE_AUTO_CREATE: bool = Field(default=True, description="Auto-create timeline entries")

    # ========================================================================
    # Notification Configuration
    # ========================================================================

    EMAIL_ENABLED: bool = Field(default=False, description="Enable email notifications")
    SMS_ENABLED: bool = Field(default=False, description="Enable SMS notifications")
    WEBHOOK_ENABLED: bool = Field(default=False, description="Enable webhook notifications")

    EMAIL_FROM: str = Field(default="noreply@bcm-platform.com", description="Email from address")
    EMAIL_SMTP_HOST: Optional[str] = Field(default=None, description="SMTP host")
    EMAIL_SMTP_PORT: int = Field(default=587, description="SMTP port")
    EMAIL_SMTP_USER: Optional[str] = Field(default=None, description="SMTP user")
    EMAIL_SMTP_PASSWORD: Optional[str] = Field(default=None, description="SMTP password")

    # ========================================================================
    # Backup & Recovery
    # ========================================================================

    BACKUP_ENABLED: bool = Field(default=False, description="Enable automated backups")
    BACKUP_INTERVAL: int = Field(default=3600, description="Backup interval in seconds")
    BACKUP_RETENTION_DAYS: int = Field(default=30, description="Backup retention period in days")

    # ========================================================================
    # Helper Methods
    # ========================================================================

    @property
    def database_url_asyncpg(self) -> str:
        """Get database URL with asyncpg driver"""
        if self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.DATABASE_URL

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return os.getenv("ENVIRONMENT", "development").lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return not self.is_production

    def get_response_time_minutes(self, severity: str) -> int:
        """Get response time threshold for severity level"""
        severity_lower = severity.lower()
        if severity_lower == "critical":
            return self.RESPONSE_TIME_CRITICAL
        elif severity_lower == "high":
            return self.RESPONSE_TIME_HIGH
        elif severity_lower == "medium":
            return self.RESPONSE_TIME_MEDIUM
        else:
            return self.RESPONSE_TIME_LOW


# ============================================================================
# Global Settings Instance
# ============================================================================

# Load settings from environment
settings = Settings()


# ============================================================================
# Logging Configuration
# ============================================================================

def configure_logging():
    """Configure logging based on settings"""
    import logging.config

    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": settings.LOG_FORMAT
            },
            "json": {
                "format": '{"time":"%(asctime)s","name":"%(name)s","level":"%(levelname)s","message":"%(message)s"}'
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json" if settings.LOG_JSON else "default",
                "stream": "ext://sys.stdout"
            }
        },
        "root": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console"]
        },
        "loggers": {
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "sqlalchemy": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            }
        }
    }

    # Add file handler if log file is specified
    if settings.LOG_FILE:
        log_config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json" if settings.LOG_JSON else "default",
            "filename": settings.LOG_FILE,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
        log_config["root"]["handlers"].append("file")

    logging.config.dictConfig(log_config)


# Configure logging on import
configure_logging()
