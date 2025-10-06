"""
Community Intelligence Configuration

Settings for:
- Peer review process
- Reputation system
- AI synthesis
- Predictive models
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Dict, List
import os

class CommunityIntelligenceConfig(BaseSettings):
    """Configuration for Community Intelligence module"""

    # Peer Review Settings
    REVIEWERS_PER_CONTRIBUTION: int = Field(default=3, description="Number of peer reviewers")
    REVIEW_DEADLINE_DAYS: int = Field(default=7, description="Days to complete review")
    MIN_REPUTATION_TO_REVIEW: int = Field(default=100, description="Minimum reputation to be reviewer")
    MIN_EXPERTISE_TO_REVIEW: int = Field(default=50, description="Module expertise threshold")
    APPROVAL_THRESHOLD: int = Field(default=2, description="Approvals needed (out of 3)")

    # Reputation System
    POINTS_PEER_REVIEW: int = Field(default=5, description="Points for completing review")
    POINTS_CASE_APPROVED_BASE: int = Field(default=50, description="Max points for approved case")
    POINTS_HELPFUL_ANSWER: int = Field(default=2, description="Points for helpful answer")

    LEVEL_THRESHOLDS: Dict[str, int] = {
        'newcomer': 0,
        'contributor': 100,
        'expert': 500,
        'master': 2000
    }

    # Anonymization
    K_ANONYMITY: int = Field(default=5, description="K-anonymity parameter")
    MAX_RISK_SCORE: float = Field(default=0.7, description="Maximum acceptable risk")

    # AI Synthesis
    SYNTHESIS_TEMPERATURE: float = Field(default=0.3, description="LLM temperature for synthesis")
    SYNTHESIS_MAX_TOKENS: int = Field(default=2000, description="Max tokens for synthesis")
    MAX_INTERPRETATIONS: int = Field(default=10, description="Max interpretations to include")
    MAX_CASE_EXAMPLES: int = Field(default=5, description="Max case examples to include")

    # Predictive Timeline
    DEFAULT_HORIZON_MONTHS: int = Field(default=12, description="Default prediction horizon")
    MIN_SIMILAR_ORGS: int = Field(default=3, description="Minimum similar orgs for prediction")
    CONFIDENCE_THRESHOLD: float = Field(default=0.6, description="Minimum confidence for predictions")

    # Rate Limiting
    MAX_CONTRIBUTIONS_PER_MONTH: int = Field(default=10, description="Max contributions per user/month")
    MAX_REVIEWS_PENDING: int = Field(default=5, description="Max pending reviews per user")

    # Service settings
    PORT: int = Field(default=8030, description="Service port")
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

    # Integration with Workflow Intelligence
    WORKFLOW_INTELLIGENCE_URL: str = Field(
        default="http://localhost:8020",
        env="WORKFLOW_INTELLIGENCE_URL",
        description="Workflow Intelligence service URL"
    )

    # ML Predictor Settings
    ML_ENABLED: bool = Field(default=True, description="Enable ML predictions")
    ML_MODEL_PATH: str = Field(default="./models", description="Path to ML models")
    ML_MIN_TRAINING_CASES: int = Field(default=50, description="Minimum cases for training")
    ML_RETRAIN_INTERVAL_HOURS: int = Field(default=24, description="Model retraining interval")

    # Proactive Monitoring
    PROACTIVE_MONITORING_ENABLED: bool = Field(default=True, description="Enable proactive monitoring")
    STUCK_THRESHOLD_HOURS: int = Field(default=48, description="Hours before workflow considered stuck")
    INACTIVE_THRESHOLD_HOURS: int = Field(default=24, description="Hours before user considered inactive")
    MONITORING_CHECK_INTERVAL_SECONDS: int = Field(default=3600, description="Monitoring check frequency")

    class Config:
        env_prefix = "COMMUNITY_"
        env_file = ".env"

# Global config instance
settings = CommunityIntelligenceConfig()
