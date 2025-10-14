"""
Analytics Specialist - Configuration
=====================================

Environment configuration for Analytics Specialist AI Colleague.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Analytics Specialist Configuration

    Environment variables:
    - ANALYTICS_PORT: Service port (default: 8056)
    - ANALYTICS_HOST: Service host (default: 0.0.0.0)
    - MIO_MANAGER_URL: MIO Manager base URL
    - AI_ORCHESTRATOR_URL: AI Orchestrator base URL
    - PROCESS_ANALYTICS_URL: Process Analytics service URL
    - PREDICTIVE_URL: Predictive service URL
    - WORKFLOW_OPTIMIZER_URL: AI Workflow Optimizer URL
    - DEBUG: Debug mode (default: False)
    """

    # Service configuration
    SERVICE_NAME: str = "Analytics Specialist"
    PORT: int = int(os.getenv("ANALYTICS_PORT", "8056"))
    HOST: str = os.getenv("ANALYTICS_HOST", "0.0.0.0")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # AI Office Infrastructure
    MIO_MANAGER_URL: str = os.getenv("MIO_MANAGER_URL", "http://localhost:8046")
    AI_ORCHESTRATOR_URL: str = os.getenv("AI_ORCHESTRATOR_URL", "http://localhost:8004")

    # Analytics Services
    PROCESS_ANALYTICS_URL: str = os.getenv("PROCESS_ANALYTICS_URL", "http://localhost:8780")
    PREDICTIVE_SERVICE_URL: str = os.getenv("PREDICTIVE_SERVICE_URL", "http://localhost:8033")
    PREDICTIVE_URL: str = os.getenv("PREDICTIVE_URL", "http://localhost:8033")  # Legacy support
    WORKFLOW_OPTIMIZER_URL: str = os.getenv("WORKFLOW_OPTIMIZER_URL", "http://localhost:8006")
    COMMUNITY_INTELLIGENCE_URL: str = os.getenv("COMMUNITY_INTELLIGENCE_URL", "http://localhost:8031")
    COLLECTIVE_URL: str = os.getenv("COLLECTIVE_URL", "http://localhost:8032")
    WORKFLOW_INTELLIGENCE_URL: str = os.getenv("WORKFLOW_INTELLIGENCE_URL", "http://localhost:8030")

    # AI Foundation
    AI_FOUNDATION_URL: str = os.getenv("AI_FOUNDATION_URL", "http://localhost:8050")
    LEARNING_KNOWLEDGE_URL: str = os.getenv("LEARNING_KNOWLEDGE_URL", "http://localhost:8052")

    # Tools Configuration
    PROJECT_ROOT: str = os.getenv("PROJECT_ROOT", "/Users/MD/AI-Platform-ISO")
    TOOLS_ANALYZERS_PATH: str = os.path.join(PROJECT_ROOT, "infrastructure/tools/analyzers")

    # Competency Level (grows over time)
    COMPETENCY_LEVEL: str = os.getenv("COMPETENCY_LEVEL", "junior")  # junior, middle, senior, expert

    # Workflows Configuration
    DAILY_HEALTH_CHECK_ENABLED: bool = os.getenv("DAILY_HEALTH_CHECK_ENABLED", "true").lower() == "true"
    DAILY_HEALTH_CHECK_TIME: str = os.getenv("DAILY_HEALTH_CHECK_TIME", "09:00")

    CONTINUOUS_IMPROVEMENT_ENABLED: bool = os.getenv("CONTINUOUS_IMPROVEMENT_ENABLED", "true").lower() == "true"
    CONTINUOUS_IMPROVEMENT_INTERVAL: int = int(os.getenv("CONTINUOUS_IMPROVEMENT_INTERVAL", "3600"))  # 1 hour

    # Database
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # Caching
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
