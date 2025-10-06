"""
API Gateway Configuration
Production-grade settings with environment variable support
"""

from pydantic_settings import BaseSettings
from typing import List, Dict
import os


class Settings(BaseSettings):
    """API Gateway Settings"""

    # Service Info
    app_name: str = "AI-Powered API Gateway"
    version: str = "1.0.0"
    port: int = 8000
    environment: str = "production"

    # Security
    jwt_secret: str = os.getenv("JWT_SECRET", "")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # Auth Service
    auth_service_url: str = "http://localhost:8001"

    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_password: str = os.getenv("REDIS_PASSWORD", "")

    # PostgreSQL (for audit logs)
    database_url: str = os.getenv("DATABASE_URL", "")

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100  # requests per window
    rate_limit_window: int = 60  # seconds
    rate_limit_burst: int = 20  # burst allowance

    # VIP Rate Limits (higher limits)
    vip_rate_limit_requests: int = 500
    vip_rate_limit_window: int = 60

    # Circuit Breaker
    circuit_breaker_enabled: bool = True
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout: int = 30  # seconds
    circuit_breaker_expected_exception: str = "httpx.HTTPError"

    # Timeouts
    default_timeout: float = 30.0
    auth_timeout: float = 5.0
    health_check_timeout: float = 3.0

    # Connection Pooling
    max_connections: int = 100
    max_keepalive_connections: int = 20
    keepalive_expiry: float = 30.0

    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
    ]
    cors_credentials: bool = True
    cors_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    cors_headers: List[str] = ["Authorization", "Content-Type", "X-Request-ID"]

    # Service Discovery & Routing
    enable_service_discovery: bool = True
    service_discovery_interval: int = 30  # seconds

    # Backend Services (will be auto-discovered + manual fallback)
    backend_services: Dict[str, str] = {
        "/coordination": "http://localhost:8004",
        "/eventbus": "http://localhost:8001",
        "/ai-orchestration": "http://localhost:8002",
        "/bpmn": "http://localhost:8003",
        "/ai-intelligence": "http://localhost:8032",
        "/project-intelligence": "http://localhost:8025",
        "/notification": "http://localhost:8035",
        "/process-mining": "http://localhost:8040",
        "/monitoring": "http://localhost:8045",
        "/realtime": "http://localhost:8050",
    }

    # AI Gateway Manager Integration
    ai_manager_enabled: bool = True
    ai_manager_url: str = "http://localhost:8032/colleagues/gateway-manager"
    ai_manager_check_interval: int = 60  # seconds

    # Health Checks
    health_check_enabled: bool = True
    health_check_interval: int = 30  # seconds
    unhealthy_threshold: int = 3  # failures before marking unhealthy

    # Audit Logging
    audit_enabled: bool = True
    audit_log_requests: bool = True
    audit_log_responses: bool = False  # Can be verbose
    audit_retention_days: int = 90

    # Metrics
    metrics_enabled: bool = True
    prometheus_port: int = 9090

    # Caching
    cache_enabled: bool = True
    cache_ttl_default: int = 300  # 5 minutes
    cache_ttl_short: int = 60  # 1 minute
    cache_ttl_long: int = 3600  # 1 hour

    # Security Headers
    security_headers: Dict[str, str] = {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    }

    # Request ID
    request_id_header: str = "X-Request-ID"

    # Public Endpoints (no auth required)
    public_endpoints: List[str] = [
        "/health",
        "/metrics",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
    ]

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Validate critical settings on startup
def validate_settings():
    """Validate critical settings"""
    errors = []

    if not settings.jwt_secret:
        errors.append("JWT_SECRET environment variable is required")

    if not settings.database_url:
        errors.append("DATABASE_URL environment variable is required for audit logs")

    if settings.environment == "production":
        if "localhost" in str(settings.cors_origins):
            errors.append("CORS origins should not include localhost in production")

        if settings.jwt_secret == "changeme":
            errors.append("JWT_SECRET must be changed in production")

    if errors:
        raise ValueError(
            f"Configuration validation failed:\\n" +
            "\\n".join(f"  - {err}" for err in errors)
        )

    return True


if __name__ == "__main__":
    # Test configuration
    try:
        validate_settings()
        print(" Configuration valid")
        print(f"=Ý Environment: {settings.environment}")
        print(f"= JWT Algorithm: {settings.jwt_algorithm}")
        print(f"=¦ Rate Limit: {settings.rate_limit_requests} req/{settings.rate_limit_window}s")
        print(f"= Circuit Breaker: {'Enabled' if settings.circuit_breaker_enabled else 'Disabled'}")
        print(f"> AI Manager: {'Enabled' if settings.ai_manager_enabled else 'Disabled'}")
    except ValueError as e:
        print(f"L Configuration error: {e}")
