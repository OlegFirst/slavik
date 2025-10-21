"""
Secrets Manager - Alias for Secrets Management Service

This service is deprecated in favor of secrets-management.
Kept for backwards compatibility.

Port: 8063
"""

import os
import logging
import uvicorn
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Secrets Manager (Deprecated)", version="1.0.0")

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "secrets-manager",
        "deprecated": True,
        "use_instead": "secrets-management (port 8062)"
    }

if __name__ == "__main__":
    PORT = int(os.getenv("SECRETS_MANAGER_PORT", "8063"))
    logger.warning("️  This service is deprecated. Use secrets-management instead.")
    uvicorn.run("main:app", host="0.0.0.0", port=PORT)
