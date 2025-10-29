#!/usr/bin/env python3
"""
Centralized Configuration Service для всей платформы
Единое место для всех конфигураций, секретов и настроек
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import json
import os
import yaml
from datetime import datetime
import logging
from pathlib import Path
import asyncio
import aioredis
from cryptography.fernet import Fernet
import hashlib

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("config_service")

app = FastAPI(
    title="BCM Configuration Service",
    description="Centralized configuration management for BCM platform",
    version="1.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration models
class ServiceConfig(BaseModel):
    """Configuration for a single service"""
    service_name: str
    environment: str = "development"
    config: Dict[str, Any]
    secrets: Optional[Dict[str, str]] = {}
    version: str = "1.0.0"
    updated_at: Optional[datetime] = None

class ConfigUpdate(BaseModel):
    """Configuration update request"""
    config: Dict[str, Any]
    reason: str = "Manual update"
    updated_by: str = "admin"

class SecretUpdate(BaseModel):
    """Secret update request"""
    secrets: Dict[str, str]
    reason: str = "Secret rotation"

# Configuration storage
class ConfigManager:
    def __init__(self):
        self.configs: Dict[str, ServiceConfig] = {}
        self.redis_client = None
        self.config_dir = Path(os.getenv("CONFIG_DIR", "/tmp/bcm_configs"))
        self.config_dir.mkdir(exist_ok=True)

        # Encryption for secrets
        self.cipher_key = os.getenv("CONFIG_CIPHER_KEY", Fernet.generate_key())
        self.cipher = Fernet(self.cipher_key)

        # Load default configurations
        self._load_default_configs()

    def _load_default_configs(self):
        """Load default configurations for all services"""
        defaults = {
            "event-bus": {
                "redis_url": os.getenv("REDIS_URL", "redis://redis:6379"),
                "postgres_url": os.getenv("POSTGRES_URL", "postgresql://bcm:bcm@postgres:5432/bcm_events"),
                "retention_days": 30,
                "batch_size": 100
            },
            "api-gateway": {
                "port": 8000,
                "rate_limit": {
                    "requests_per_minute": 100,
                    "burst": 10
                },
                "cors_origins": ["*"],
                "timeout": 30
            },
            "auth-service": {
                "jwt_secret": os.getenv("JWT_SECRET", "change_me_in_production"),
                "jwt_algorithm": "HS256",
                "access_token_expire_minutes": 30,
                "refresh_token_expire_days": 7,
                "keycloak_url": os.getenv("KEYCLOAK_URL", "http://keycloak:8080"),
                "keycloak_realm": "bcm"
            },
            "notification-service": {
                "smtp_host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
                "smtp_port": 587,
                "smtp_user": os.getenv("SMTP_USER", ""),
                "smtp_password": os.getenv("SMTP_PASSWORD", ""),
                "sms_provider": "twilio",
                "push_provider": "firebase"
            },
            "monitoring": {
                "prometheus_url": "http://prometheus:9090",
                "grafana_url": "http://grafana:3000",
                "loki_url": "http://loki:3100",
                "alert_webhook": os.getenv("ALERT_WEBHOOK_URL", ""),
                "metrics_retention_hours": 168
            },
            "orchestrator": {
                "workflow_timeout": 3600,
                "max_concurrent_workflows": 10,
                "retry_policy": {
                    "max_retries": 3,
                    "backoff_multiplier": 2
                },
                "event_bus_url": "http://event-bus:8001"
            },
            "service-registry": {
                "discovery_interval": 30,
                "health_check_interval": 60,
                "failure_threshold": 3,
                "success_threshold": 2
            }
        }

        # Load configurations
        for service_name, config in defaults.items():
            self.configs[service_name] = ServiceConfig(
                service_name=service_name,
                environment=os.getenv("ENVIRONMENT", "development"),
                config=config,
                updated_at=datetime.utcnow()
            )

    async def connect_redis(self):
        """Connect to Redis for config caching"""
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            self.redis_client = await aioredis.create_redis_pool(redis_url)
            logger.info("Connected to Redis for config caching")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")

    def encrypt_secret(self, value: str) -> str:
        """Encrypt a secret value"""
        return self.cipher.encrypt(value.encode()).decode()

    def decrypt_secret(self, encrypted: str) -> str:
        """Decrypt a secret value"""
        return self.cipher.decrypt(encrypted.encode()).decode()

    async def get_config(self, service_name: str) -> Optional[ServiceConfig]:
        """Get configuration for a service"""
        # Try cache first
        if self.redis_client:
            cached = await self.redis_client.get(f"config:{service_name}")
            if cached:
                return ServiceConfig(**json.loads(cached))

        # Get from memory
        config = self.configs.get(service_name)

        # Cache it
        if config and self.redis_client:
            await self.redis_client.setex(
                f"config:{service_name}",
                300,  # 5 minutes TTL
                json.dumps(config.dict(), default=str)
            )

        return config

    async def update_config(self, service_name: str, update: ConfigUpdate) -> ServiceConfig:
        """Update configuration for a service"""
        if service_name not in self.configs:
            self.configs[service_name] = ServiceConfig(
                service_name=service_name,
                environment=os.getenv("ENVIRONMENT", "development"),
                config={}
            )

        # Update config
        self.configs[service_name].config.update(update.config)
        self.configs[service_name].updated_at = datetime.utcnow()

        # Persist to file
        config_file = self.config_dir / f"{service_name}.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(self.configs[service_name].dict(), f)

        # Invalidate cache
        if self.redis_client:
            await self.redis_client.delete(f"config:{service_name}")

        # Notify subscribers (via event bus)
        await self._notify_config_change(service_name, update.reason)

        return self.configs[service_name]

    async def _notify_config_change(self, service_name: str, reason: str):
        """Notify services about config change via event bus"""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                await client.post(
                    "http://event-bus:8001/publish",
                    json={
                        "type": "config_changed",
                        "payload": {
                            "service": service_name,
                            "reason": reason,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    }
                )
        except Exception as e:
            logger.error(f"Failed to notify config change: {e}")

# Initialize manager
config_manager = ConfigManager()

@app.on_event("startup")
async def startup():
    """Initialize connections on startup"""
    await config_manager.connect_redis()
    logger.info("Config Service started")

# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "config-service",
        "configs_loaded": len(config_manager.configs)
    }

@app.get("/configs")
async def list_configs():
    """List all available configurations"""
    return {
        "configs": list(config_manager.configs.keys()),
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/config/{service_name}")
async def get_config(service_name: str):
    """Get configuration for a specific service"""
    config = await config_manager.get_config(service_name)
    if not config:
        raise HTTPException(status_code=404, detail=f"Configuration for {service_name} not found")
    return config

@app.put("/config/{service_name}")
async def update_config(service_name: str, update: ConfigUpdate):
    """Update configuration for a service"""
    config = await config_manager.update_config(service_name, update)
    return {
        "status": "updated",
        "service": service_name,
        "config": config
    }

@app.post("/config/{service_name}/secrets")
async def update_secrets(service_name: str, secret_update: SecretUpdate):
    """Update secrets for a service"""
    if service_name not in config_manager.configs:
        raise HTTPException(status_code=404, detail=f"Service {service_name} not found")

    # Encrypt and store secrets
    encrypted_secrets = {
        key: config_manager.encrypt_secret(value)
        for key, value in secret_update.secrets.items()
    }

    config_manager.configs[service_name].secrets = encrypted_secrets
    config_manager.configs[service_name].updated_at = datetime.utcnow()

    return {"status": "secrets updated", "service": service_name}

@app.get("/config/{service_name}/secrets/{secret_key}")
async def get_secret(service_name: str, secret_key: str):
    """Get a specific secret (decrypted)"""
    if service_name not in config_manager.configs:
        raise HTTPException(status_code=404, detail=f"Service {service_name} not found")

    secrets = config_manager.configs[service_name].secrets or {}
    if secret_key not in secrets:
        raise HTTPException(status_code=404, detail=f"Secret {secret_key} not found")

    # Return decrypted secret
    return {
        "service": service_name,
        "key": secret_key,
        "value": config_manager.decrypt_secret(secrets[secret_key])
    }

@app.post("/config/reload")
async def reload_configs():
    """Reload all configurations from disk"""
    config_manager._load_default_configs()

    # Load from disk
    for config_file in config_manager.config_dir.glob("*.yaml"):
        with open(config_file) as f:
            data = yaml.safe_load(f)
            service_name = config_file.stem
            config_manager.configs[service_name] = ServiceConfig(**data)

    return {
        "status": "reloaded",
        "configs": len(config_manager.configs)
    }

@app.get("/config/{service_name}/export")
async def export_config(service_name: str, format: str = "yaml"):
    """Export configuration in different formats"""
    config = await config_manager.get_config(service_name)
    if not config:
        raise HTTPException(status_code=404, detail=f"Configuration for {service_name} not found")

    if format == "yaml":
        return yaml.dump(config.dict())
    elif format == "json":
        return config.dict()
    elif format == "env":
        # Convert to environment variables format
        env_vars = []
        for key, value in config.config.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    env_vars.append(f"{service_name.upper()}_{key.upper()}_{sub_key.upper()}={sub_value}")
            else:
                env_vars.append(f"{service_name.upper()}_{key.upper()}={value}")
        return "\n".join(env_vars)
    else:
        raise HTTPException(status_code=400, detail="Format must be yaml, json, or env")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)