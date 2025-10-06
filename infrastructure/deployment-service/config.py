"""
Deployment Service Configuration
=================================

Configuration management using environment variables with validation.
"""

import os
from typing import Optional
from pydantic import BaseSettings, Field, validator


class DeploymentConfig(BaseSettings):
    """
    Deployment Service Configuration

    All settings loaded from environment variables with sensible defaults.
    """

    # Service Identity
    SERVICE_NAME: str = "deployment-service"
    SERVICE_VERSION: str = "2.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8002

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/bcm_db",
        env="DATABASE_URL"
    )

    # EventBus Configuration
    EVENTBUS_BACKEND: str = Field(default="redis", env="EVENTBUS_BACKEND")
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")

    # AI Orchestrator Integration
    AI_ORCHESTRATOR_URL: str = Field(
        default="http://localhost:8000",
        env="AI_ORCHESTRATOR_URL"
    )
    AI_ORCHESTRATOR_TIMEOUT: int = Field(default=30, env="AI_ORCHESTRATOR_TIMEOUT")

    # Docker Configuration
    DOCKER_COMPOSE_FILE: str = Field(
        default="docker-compose.yml",
        env="DOCKER_COMPOSE_FILE"
    )

    # Service Configuration
    SERVICE_ORDER: list = Field(
        default=[
            "postgres", "redis", "rabbitmq",  # Infrastructure
            "ai_orchestrator", "github_app",   # AI services
            "odoo",                           # Core
            "web_portal", "admin_panel"       # Frontend
        ]
    )
    CRITICAL_SERVICES: list = Field(
        default=["postgres", "redis"]
    )

    # Monitoring Configuration
    HEALTH_CHECK_INTERVAL: int = Field(default=60, env="HEALTH_CHECK_INTERVAL")
    HEALTH_CHECK_TIMEOUT: int = Field(default=30, env="HEALTH_CHECK_TIMEOUT")
    SERVICE_START_TIMEOUT: int = Field(default=300, env="SERVICE_START_TIMEOUT")

    # Prometheus Metrics
    METRICS_ENABLED: bool = Field(default=True, env="METRICS_ENABLED")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")

    # Multi-tenancy
    DEFAULT_TENANT_ID: str = Field(default="system", env="DEFAULT_TENANT_ID")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # Graceful Shutdown
    SHUTDOWN_TIMEOUT: int = Field(default=30, env="SHUTDOWN_TIMEOUT")

    class Config:
        env_file = ".env"
        case_sensitive = True

    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()

    @validator("EVENTBUS_BACKEND")
    def validate_eventbus_backend(cls, v):
        """Validate EventBus backend"""
        valid_backends = ["memory", "redis", "rabbitmq"]
        if v.lower() not in valid_backends:
            raise ValueError(f"EVENTBUS_BACKEND must be one of {valid_backends}")
        return v.lower()


# Global config instance
config = DeploymentConfig()
