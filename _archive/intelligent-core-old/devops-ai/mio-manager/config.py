#!/usr/bin/env python3
"""
MIO Manager Configuration
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Service config
    SERVICE_NAME: str = "mio-manager"
    SERVICE_PORT: int = 8046
    SERVICE_VERSION: str = "1.0.0"

    # Orchestrator
    ORCHESTRATOR_URL: str = "http://localhost:8001"

    # Gateway
    GATEWAY_URL: str = "http://localhost:8000"

    # Prometheus
    PROMETHEUS_URL: str = "http://localhost:9090"

    # Grafana
    GRAFANA_URL: str = "http://localhost:3000"

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
