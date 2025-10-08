"""Expertise Center Service Configuration"""

import os
from typing import Optional

# Service Configuration
SERVICE_NAME = "expertise-center-service"
VERSION = "1.0.0"
PORT = int(os.getenv("EXPERTISE_CENTER_PORT", "8035"))
HOST = os.getenv("EXPERTISE_CENTER_HOST", "0.0.0.0")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Dependencies
AI_FOUNDATION_URL = os.getenv("AI_FOUNDATION_URL", "http://localhost:8040")
KNOWLEDGE_BASE_URL = os.getenv("KNOWLEDGE_BASE_URL", "http://localhost:8040")

# Database (if needed)
DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

# EventBus (if needed)
EVENTBUS_ENABLED = os.getenv("EVENTBUS_ENABLED", "false").lower() == "true"
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5673"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "bcm_platform")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "bcm_secure_2024")

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Performance
WORKERS = int(os.getenv("WORKERS", "1"))
