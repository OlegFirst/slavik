"""
Rate Limiting Middleware for API Gateway
Protection against API abuse and DDoS
"""

import logging
from fastapi import Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379"
)


# Tiered rate limits
RATE_LIMITS = {
    "free": "100/minute",
    "basic": "500/minute",
    "premium": "2000/minute",
    "enterprise": "10000/minute"
}


async def get_user_tier(request: Request) -> str:
    """Get user tier from JWT or API key"""
    # TODO: Extract from JWT token
    return "free"


async def rate_limit_by_tier(request: Request):
    """Apply rate limit based on user tier"""
    tier = await get_user_tier(request)
    limit = RATE_LIMITS.get(tier, "100/minute")

    # Check rate limit
    # Implementation depends on your rate limiting library


async def rate_limit_middleware(request: Request, call_next):
    """Middleware for rate limiting"""
    try:
        await rate_limit_by_tier(request)
        response = await call_next(request)
        return response
    except RateLimitExceeded:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )


# Apply to FastAPI app:
# app.middleware("http")(rate_limit_middleware)
