"""
Living Documentation Configuration
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List

class LivingDocsConfig(BaseSettings):
    """Configuration for Living Documentation Service"""

    # Service
    PORT: int = Field(default=8034, description="Service port")
    DEBUG: bool = Field(default=False, description="Debug mode")
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        description="CORS origins"
    )

    # AI
    ANTHROPIC_API_KEY: str = Field(default="", env="ANTHROPIC_API_KEY")
    AI_TEMPERATURE: float = Field(default=0.4, description="AI temperature for content generation")
    AI_MAX_TOKENS: int = Field(default=2500, description="Max tokens for AI generation")

    # Evolution
    AUTO_IMPROVEMENT_ENABLED: bool = Field(default=True, description="Enable auto-improvement")
    IMPROVEMENT_INTERVAL_HOURS: int = Field(default=1, description="Hours between improvement runs")
    MIN_INTERACTIONS_FOR_ANALYSIS: int = Field(default=10, description="Min interactions before analysis")

    # Personalization
    PERSONALIZATION_ENABLED: bool = Field(default=True, description="Enable personalization")
    CACHE_PERSONALIZED_CONTENT: bool = Field(default=True, description="Cache personalized versions")
    CACHE_TTL_HOURS: int = Field(default=24, description="Cache TTL in hours")

    # Examples
    EXAMPLE_GENERATION_ENABLED: bool = Field(default=True, description="Enable AI example generation")
    MIN_SOURCES_FOR_EXAMPLE: int = Field(default=3, description="Min sources for example generation")
    CACHE_EXAMPLES: bool = Field(default=True, description="Cache generated examples")

    # Quality thresholds
    MIN_HELPFUL_RATE: float = Field(default=0.6, description="Minimum helpful vote rate")
    MAX_BOUNCE_RATE: float = Field(default=0.7, description="Maximum acceptable bounce rate")
    MIN_TIME_ON_PAGE: int = Field(default=30, description="Minimum seconds on page")

    # Database
    DATABASE_URL: str = Field(default="", env="DATABASE_URL")
    REDIS_URL: str = Field(default="", env="REDIS_URL")

    # Integration
    COLLECTIVE_INTELLIGENCE_URL: str = Field(
        default="http://localhost:8032",
        env="COLLECTIVE_INTELLIGENCE_URL"
    )

    class Config:
        env_prefix = "LIVING_DOCS_"
        env_file = ".env"

# Global config instance
settings = LivingDocsConfig()
