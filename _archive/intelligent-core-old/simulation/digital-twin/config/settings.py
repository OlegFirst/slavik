"""
Configuration Settings for Digital Twin Universal Service
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = "Digital Twin Universal Service"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8001
    api_prefix: str = "/api/v1"

    # Database - Supabase
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    supabase_service_key: Optional[str] = None

    # Database - PostgreSQL (alternative)
    postgres_url: Optional[str] = None
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_db: str = "digital_twin"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0
    redis_password: Optional[str] = None

    # Security
    secret_key: str = "change-me-in-production-super-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8069",
    ]

    # Collectors - Odoo
    odoo_url: Optional[str] = None
    odoo_db: Optional[str] = None
    odoo_username: Optional[str] = None
    odoo_password: Optional[str] = None

    # Collectors - Salesforce
    salesforce_instance_url: Optional[str] = None
    salesforce_username: Optional[str] = None
    salesforce_password: Optional[str] = None
    salesforce_security_token: Optional[str] = None

    # Collectors - HubSpot
    hubspot_api_key: Optional[str] = None

    # Collectors - QuickBooks
    quickbooks_client_id: Optional[str] = None
    quickbooks_client_secret: Optional[str] = None

    # Collectors - Slack
    slack_bot_token: Optional[str] = None

    # Collectors - Jira
    jira_url: Optional[str] = None
    jira_username: Optional[str] = None
    jira_api_token: Optional[str] = None

    # Enrichment APIs
    clearbit_api_key: Optional[str] = None
    google_maps_api_key: Optional[str] = None

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Monitoring
    prometheus_enabled: bool = True
    prometheus_port: int = 9090

    # Cache
    cache_ttl: int = 3600  # 1 hour
    cache_max_size: int = 1000

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds

    @property
    def database_url(self) -> str:
        """Get database URL"""
        if self.postgres_url:
            return self.postgres_url
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


# Global settings instance
settings = Settings()
