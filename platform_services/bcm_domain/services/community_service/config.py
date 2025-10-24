"""
Community Service Configuration
ISO 22301 Clause 10.2 - Continual Improvement & Knowledge Sharing

Inherits from shared SharedSettings with Community-specific settings.
"""

import sys
from pathlib import Path
from typing import List

# Add shared to path
sys.path.insert(0, str(Path(__file__).parent.parent / "_shared"))

from shared.config import SharedSettings


class CommunitySettings(SharedSettings):
    """Community Service Settings"""

    # Service Identity (override defaults)
    SERVICE_NAME: str = "community"
    SERVICE_TITLE: str = "Community Service - BCM Specialists & Knowledge Sharing"
    SERVICE_PORT: int = 8022
    API_PREFIX: str = "/api/community"

    # Development defaults (override in production via env vars)
    DATABASE_URL: str = "sqlite+aiosqlite:///./community_dev.db"
    JWT_SECRET_KEY: str = "dev-secret-CHANGE-IN-PRODUCTION-community"

    # Community-Specific Settings
    MARKETPLACE_ENABLED: bool = True
    PORTAL_ENABLED: bool = True
    KNOWLEDGE_SHARING_ENABLED: bool = True

    # Gamification
    ENABLE_GAMIFICATION: bool = True
    POINTS_PER_CONTRIBUTION: int = 50
    POINTS_PER_KNOWLEDGE_SHARE: int = 100

    # Marketplace
    MAX_LISTINGS_PER_SPECIALIST: int = 10
    LISTING_REVIEW_REQUIRED: bool = True

    # EventBus Topics (Community subscribes to these)
    SUBSCRIBE_TOPICS: List[str] = [
        "learning.training.completed",       # Award points
        "validation.exercise.completed",     # Share learnings
        "planning.plan.created",            # Knowledge contribution
    ]

    class Config:
        env_prefix = "COMMUNITY_"  # Environment variables: COMMUNITY_SERVICE_PORT, etc.


# Global settings instance
settings = CommunitySettings()
