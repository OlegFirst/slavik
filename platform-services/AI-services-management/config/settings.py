"""
KQM Configuration Settings
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """KQM Settings"""

    # Service
    SERVICE_NAME: str = "knowledge-quality-manager"
    SERVICE_PORT: int = 8090
    SERVICE_VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres.tpdkhddtbhpoqzzgxfni:K%40x3ta9V8GK5rnW@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"
    )

    # Redis
    REDIS_URL: str = os.getenv(
        "REDIS_URL",
        "redis://:tldJWwUq7lAwOHuCa9pSD7sVfjQFYPYN@redis-10023.c8.us-east-1-4.ec2.redns.redis-cloud.com:10023"
    )

    # AI
    ANTHROPIC_API_KEY: str = os.getenv(
        "ANTHROPIC_API_KEY",
        "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"
    )

    # Paths
    SCENARIOS_PATH: str = "/Users/MD/AI-Platform-ISO/platform-services/docs/business-scenarios"
    GENERATED_PATH: str = "/Users/MD/AI-Platform-ISO/platform-services/docs/business-scenarios/generated"
    STANDARDS_PATH: str = "/Users/MD/AI-Platform-ISO/doc/ISO-22301-Library"

    # Generation Settings
    MIN_CONFIDENCE: float = 0.7
    MAX_SCENARIOS_PER_CYCLE: int = 10
    CYCLE_INTERVAL_HOURS: int = 24

    # Quality Thresholds
    COVERAGE_TARGET: float = 0.85  # 85% coverage target
    VALIDATION_PASS_RATE: float = 0.90  # 90% validation pass rate
    USAGE_RATE_TARGET: float = 0.65  # 65% scenario usage target

    # Component URLs
    AI_FOUNDATION_URL: str = "http://localhost:8002"
    EXPERTISE_CENTER_URL: str = "http://localhost:8003"
    PREDICTIVE_URL: str = "http://localhost:8004"
    COMMUNITY_INTEL_URL: str = "http://localhost:8005"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
