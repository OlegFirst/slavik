"""
Learning Service Configuration
"""

import sys
from pathlib import Path

# Add shared to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))

from shared.config import SharedSettings


class LearningServiceSettings(SharedSettings):
    """Learning Service specific settings"""

    SERVICE_NAME: str = "learning"
    SERVICE_PORT: int = 8021

    # Override required fields with defaults for testing
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/bcm_platform"
    JWT_SECRET_KEY: str = "dev-secret-CHANGE-IN-PRODUCTION-learning"

    # Learning specific
    DEFAULT_PASSING_SCORE: int = 70
    POINTS_PER_TRAINING: int = 100
    POINTS_PER_CERTIFICATION: int = 200
    STREAK_BONUS_DAYS: int = 7
    LEADERBOARD_SIZE: int = 50

    class Config:
        env_file = ".env"
        env_prefix = "LEARNING_"


# Initialize settings
settings = LearningServiceSettings()
