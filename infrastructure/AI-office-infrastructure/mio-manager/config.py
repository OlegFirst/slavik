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
    SERVICE_VERSION: str = "2.0.0"

    # Legacy integrations
    ORCHESTRATOR_URL: str = "http://localhost:8001"
    GATEWAY_URL: str = "http://localhost:8000"

    # v2.0 Critical Integrations
    WORKFLOW_INTELLIGENCE_URL: str = "http://localhost:8050"  # Мозг
    PREDICTIVE_URL: str = "http://localhost:8052"  # Predictive Service
    OPTIMIZER_URL: str = "http://localhost:8051"  # Workflow Optimizer
    COORDINATION_CENTER_URL: str = "http://localhost:8053"  # Coordination Center
    COMPLIANCE_MONITORING_URL: str = "http://localhost:8779"  # Compliance Monitoring
    AI_EVENT_MANAGER_URL: str = "http://localhost:8055"  # AI Event Manager
    DEVOPS_AGENT_URL: str = "http://localhost:8060"  # DevOps Agent

    # EventBus
    REDIS_URL: str = "redis://localhost:6379"  # For EventBus

    # Monitoring
    PROMETHEUS_URL: str = "http://localhost:9090"
    GRAFANA_URL: str = "http://localhost:3000"

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
