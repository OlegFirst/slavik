"""
Collective Agent Networks Configuration

Settings for:
- Agent creation and lifecycle
- Stuck detection thresholds
- Privacy parameters
- Anonymization
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os

class CollectiveConfig(BaseSettings):
    """Configuration for Collective Agent Networks"""

    # Agent Lifecycle
    AGENT_EXPIRATION_DAYS: int = Field(default=7, description="Days until agent expires")
    MIN_ORGS_FOR_COLLECTIVE: int = Field(default=5, description="Minimum orgs to create agent")
    AGENT_TEMPERATURE: float = Field(default=0.3, description="LLM temperature for agent responses")
    AGENT_MAX_TOKENS: int = Field(default=2000, description="Max tokens for agent response")

    # Stuck Detection
    STUCK_THRESHOLD: int = Field(default=4, description="Score threshold for 'stuck' classification")
    DAYS_NO_PROGRESS_WARNING: int = Field(default=7, description="Days without progress = warning")
    VALIDATION_FAILURE_THRESHOLD: int = Field(default=5, description="Failures = stuck signal")
    LOW_CONFIDENCE_THRESHOLD: float = Field(default=0.6, description="Low AI confidence threshold")

    # Privacy & Anonymization
    K_ANONYMITY: int = Field(default=5, description="K-anonymity parameter")
    MAX_RISK_SCORE: float = Field(default=0.7, description="Maximum acceptable re-identification risk")

    # Service settings
    PORT: int = Field(default=8032, description="Service port")
    DEBUG: bool = Field(default=False, description="Debug mode")
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        description="CORS origins"
    )

    # Database
    DATABASE_URL: str = Field(default="", env="DATABASE_URL")
    REDIS_URL: str = Field(default="", env="REDIS_URL")

    # EventBus
    EVENTBUS_URL: str = Field(default="http://localhost:8001", env="EVENTBUS_URL")

    # AI
    ANTHROPIC_API_KEY: str = Field(default="", env="ANTHROPIC_API_KEY")

    class Config:
        env_prefix = "COLLECTIVE_"
        env_file = ".env"

# Global config instance
settings = CollectiveConfig()
