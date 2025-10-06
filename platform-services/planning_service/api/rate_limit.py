"""
Rate Limiting for Planning Service
Prevents API abuse and DDoS attacks
"""

from fastapi import Request, HTTPException, status
from typing import Dict
import time
import logging

logger = logging.getLogger(__name__)

# Simple in-memory rate limiter (use Redis in production)
request_counts: Dict[str, list] = {}

# Configuration
RATE_LIMIT_REQUESTS = 100  # requests
RATE_LIMIT_WINDOW = 60  # seconds (1 minute)


async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware
    Limits requests per IP address
    """
    client_ip = request.client.host if request.client else "unknown"
    current_time = time.time()

    # Initialize or clean old requests
    if client_ip not in request_counts:
        request_counts[client_ip] = []

    # Remove requests outside the window
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip]
        if current_time - req_time < RATE_LIMIT_WINDOW
    ]

    # Check rate limit
    if len(request_counts[client_ip]) >= RATE_LIMIT_REQUESTS:
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds.",
            headers={"Retry-After": str(RATE_LIMIT_WINDOW)}
        )

    # Add current request
    request_counts[client_ip].append(current_time)

    # Continue processing
    response = await call_next(request)

    # Add rate limit headers
    remaining = RATE_LIMIT_REQUESTS - len(request_counts[client_ip])
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_REQUESTS)
    response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
    response.headers["X-RateLimit-Reset"] = str(int(current_time + RATE_LIMIT_WINDOW))

    return response
