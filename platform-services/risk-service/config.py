"""
Risk Module Configuration
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Risk module settings"""

    # Database
    DATABASE_URL: str = Field(
        ...,
        env="DATABASE_URL",
        description="Database connection URL - MUST be set via environment variable"
    )

    # Service
    SERVICE_NAME: str = "Risk Management"
    SERVICE_VERSION: str = "1.0.0"
    PORT: int = 8040

    # API
    API_PREFIX: str = "/api/v1/risk"

    # FAIR Analysis Defaults
    FAIR_CONFIDENCE_INTERVAL: float = 0.2  # ±20%

    # Monte Carlo Defaults
    MONTE_CARLO_DEFAULT_ITERATIONS: int = 10000
    MONTE_CARLO_MIN_ITERATIONS: int = 1000
    MONTE_CARLO_MAX_ITERATIONS: int = 100000

    # Risk Scoring
    CRITICAL_THRESHOLD: int = 20  # Inherent risk score >= 20
    HIGH_THRESHOLD: int = 15      # Inherent risk score 15-19
    MEDIUM_THRESHOLD: int = 8     # Inherent risk score 8-14
    # LOW: score < 8

    # Review Intervals (days)
    CRITICAL_RISK_REVIEW_DAYS: int = 30
    HIGH_RISK_REVIEW_DAYS: int = 60
    MEDIUM_RISK_REVIEW_DAYS: int = 90
    LOW_RISK_REVIEW_DAYS: int = 180

    # JWT Authentication
    JWT_AUTH_ENABLED: bool = Field(
        default=False,
        env="JWT_AUTH_ENABLED",
        description="Enable JWT authentication (set to false for development)"
    )
    JWT_SECRET_KEY: Optional[str] = Field(
        default=None,
        env="JWT_SECRET_KEY",
        description="JWT secret key for token signing/verification"
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        env="JWT_ALGORITHM",
        description="JWT signing algorithm"
    )
    JWT_EXPIRATION_MINUTES: int = Field(
        default=30,
        env="JWT_EXPIRATION_MINUTES",
        description="JWT token expiration time in minutes"
    )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
