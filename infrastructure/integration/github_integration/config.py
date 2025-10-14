"""
GitHub Integration Service Configuration
========================================

Configuration management for GitHub App integration.
"""

import os
from typing import Optional
from pydantic import BaseSettings, Field, validator


class GitHubConfig(BaseSettings):
    """GitHub Integration Service Configuration"""

    # Service Identity
    SERVICE_NAME: str = "github-integration"
    SERVICE_VERSION: str = "2.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8001

    # GitHub App Configuration
    GITHUB_APP_ID: str = Field(..., env="GITHUB_APP_ID")
    GITHUB_APP_PRIVATE_KEY_PATH: Optional[str] = Field(
        default=None,
        env="GITHUB_APP_PRIVATE_KEY_PATH"
    )
    GITHUB_APP_PRIVATE_KEY: Optional[str] = Field(
        default=None,
        env="GITHUB_APP_PRIVATE_KEY"
    )
    GITHUB_WEBHOOK_SECRET: str = Field(..., env="GITHUB_WEBHOOK_SECRET")
    GITHUB_CLIENT_ID: Optional[str] = Field(default=None, env="GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET: Optional[str] = Field(default=None, env="GITHUB_CLIENT_SECRET")

    # GitHub API
    GITHUB_API_URL: str = Field(
        default="https://api.github.com",
        env="GITHUB_API_URL"
    )
    GITHUB_API_VERSION: str = Field(default="2022-11-28", env="GITHUB_API_VERSION")

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

    # Rate Limiting (GitHub API limits)
    RATE_LIMIT_REQUESTS: int = Field(default=5000, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1 hour

    # Retry Configuration
    MAX_RETRIES: int = Field(default=3, env="MAX_RETRIES")
    RETRY_BACKOFF_FACTOR: float = Field(default=2.0, env="RETRY_BACKOFF_FACTOR")
    RETRY_MAX_DELAY: int = Field(default=60, env="RETRY_MAX_DELAY")

    # Token Configuration
    INSTALLATION_TOKEN_TTL: int = Field(
        default=3600,
        env="INSTALLATION_TOKEN_TTL"
    )  # 1 hour
    JWT_TOKEN_TTL: int = Field(default=600, env="JWT_TOKEN_TTL")  # 10 minutes

    # Webhook Processing
    WEBHOOK_QUEUE_SIZE: int = Field(default=1000, env="WEBHOOK_QUEUE_SIZE")
    WEBHOOK_WORKERS: int = Field(default=4, env="WEBHOOK_WORKERS")

    # Prometheus Metrics
    METRICS_ENABLED: bool = Field(default=True, env="METRICS_ENABLED")
    METRICS_PORT: int = Field(default=9091, env="METRICS_PORT")

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

    @validator("GITHUB_APP_PRIVATE_KEY", always=True)
    def validate_private_key(cls, v, values):
        """Validate private key - either direct key or path must be provided"""
        if not v and not values.get("GITHUB_APP_PRIVATE_KEY_PATH"):
            raise ValueError(
                "Either GITHUB_APP_PRIVATE_KEY or GITHUB_APP_PRIVATE_KEY_PATH must be set"
            )
        return v

    def get_private_key(self) -> str:
        """Get private key content"""
        if self.GITHUB_APP_PRIVATE_KEY:
            return self.GITHUB_APP_PRIVATE_KEY

        if self.GITHUB_APP_PRIVATE_KEY_PATH:
            with open(self.GITHUB_APP_PRIVATE_KEY_PATH, 'r') as f:
                return f.read()

        raise ValueError("No private key configured")


# Global config instance
config = GitHubConfig()
