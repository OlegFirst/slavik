"""
Secrets Management Service - Secure secrets storage and retrieval via Supabase Vault

Provides secure storage for API keys, passwords, certificates, and other secrets.
Integrated with Supabase Vault for persistence.

Port: 8062
"""

import logging
import os
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Optional
import uvicorn

from vault_client import get_vault_client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PORT = int(os.getenv("SECRETS_MANAGEMENT_PORT", "8062"))
HOST = os.getenv("SECRETS_MANAGEMENT_HOST", "0.0.0.0")
MASTER_KEY = os.getenv("SECRETS_MASTER_KEY", "dev-master-key-change-in-production")

app = FastAPI(
    title="Secrets Management Service",
    description="Secure secrets storage and retrieval via Supabase Vault",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

class SecretCreate(BaseModel):
    name: str
    value: str
    description: Optional[str] = ""

class SecretRotate(BaseModel):
    new_value: str

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key for authentication"""
    if api_key != MASTER_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

@app.get("/health")
async def health():
    try:
        vault = get_vault_client()
        secrets = vault.list_secrets()
        return {
            "status": "healthy",
            "service": "secrets-management",
            "version": "2.0.0",
            "storage": "Supabase Vault",
            "total_secrets": len(secrets)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/secrets/{name}")
async def get_secret(
    name: str,
    _api_key: str = Depends(verify_api_key)
):
    """Retrieve a secret from Vault"""
    try:
        vault = get_vault_client()
        value = vault.get_secret(name)

        logger.info(f"Secret retrieved: {name}")

        return {
            "name": name,
            "value": value
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get secret {name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/secrets/{name}/rotate")
async def rotate_secret(
    name: str,
    rotation: SecretRotate,
    _api_key: str = Depends(verify_api_key)
):
    """Rotate a secret (update its value)"""
    try:
        vault = get_vault_client()
        success = vault.rotate_secret(name, rotation.new_value)

        if success:
            logger.warning(f"Secret rotated: {name}")
            return {
                "status": "rotated",
                "name": name
            }
        else:
            raise HTTPException(status_code=500, detail="Rotation failed")

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to rotate secret {name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/secrets")
async def list_secrets(
    _api_key: str = Depends(verify_api_key)
):
    """List all secret keys (without values)"""
    try:
        vault = get_vault_client()
        secrets = vault.list_secrets()

        return {
            "secrets": secrets,
            "count": len(secrets)
        }
    except Exception as e:
        logger.error(f"Failed to list secrets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info(f"🔐 Starting Secrets Management Service on {HOST}:{PORT}")
    logger.info(f"📦 Using Supabase Vault for secure storage")

    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level="info"
    )
