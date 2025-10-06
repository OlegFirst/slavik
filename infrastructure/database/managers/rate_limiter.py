"""
Advanced Rate Limiter
Token bucket, sliding window, and adaptive rate limiting
"""

import time
from typing import Optional, Dict, Tuple
from enum import Enum
import logging
from .redis_client import redis_manager

logger = logging.getLogger(__name__)


class RateLimitStrategy(Enum):
    """Rate limiting strategies"""
    FIXED_WINDOW = "fixed_window"  # Simple counter per time window
    SLIDING_WINDOW = "sliding_window"  # More accurate, uses timestamps
    TOKEN_BUCKET = "token_bucket"  # Allows bursts


class RateLimiter:
    """
    Advanced rate limiter with multiple strategies:
    - Fixed Window: Simple, efficient
    - Sliding Window: Accurate, fair
    - Token Bucket: Burst-friendly
    """

    def __init__(self, redis_client=None):
        self.redis = redis_client or redis_manager
        self.prefix = "ratelimit"

    def _key(self, identifier: str, resource: str) -> str:
        """Generate rate limit key"""
        return f"{self.prefix}:{resource}:{identifier}"

    async def check_rate_limit_fixed(
        self,
        identifier: str,
        resource: str,
        max_requests: int,
        window_seconds: int
    ) -> Tuple[bool, Dict[str, int]]:
        """
        Fixed window rate limiting

        Args:
            identifier: User ID, IP, or other identifier
            resource: Resource being accessed (e.g., 'api', 'login', 'upload')
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds

        Returns:
            (is_allowed, info_dict)
            info_dict contains: {remaining, reset_at, total}
        """
        key = self._key(identifier, resource)

        try:
            # Increment counter
            count = await self.redis.client.incr(key)

            # Set expiry on first request
            if count == 1:
                await self.redis.client.expire(key, window_seconds)

            # Get TTL
            ttl = await self.redis.ttl(key)
            reset_at = int(time.time()) + ttl

            remaining = max(0, max_requests - count)
            allowed = count <= max_requests

            info = {
                "remaining": remaining,
                "reset_at": reset_at,
                "total": max_requests,
                "current": count
            }

            return allowed, info

        except Exception as e:
            logger.error(f"Rate limit error: {e}")
            # On error, allow request (fail open)
            return True, {"remaining": max_requests, "reset_at": 0, "total": max_requests, "current": 0}

    async def check_rate_limit_sliding(
        self,
        identifier: str,
        resource: str,
        max_requests: int,
        window_seconds: int
    ) -> Tuple[bool, Dict[str, int]]:
        """
        Sliding window rate limiting using sorted sets

        More accurate than fixed window, prevents boundary issues
        """
        key = self._key(identifier, f"{resource}:sliding")

        try:
            now = time.time()
            window_start = now - window_seconds

            # Remove old entries
            await self.redis.client.zremrangebyscore(key, 0, window_start)

            # Count requests in current window
            count = await self.redis.client.zcard(key)

            allowed = count < max_requests

            if allowed:
                # Add current request with timestamp as score
                await self.redis.client.zadd(key, {str(now): now})
                # Set expiry
                await self.redis.client.expire(key, window_seconds)

            remaining = max(0, max_requests - count - (1 if allowed else 0))
            reset_at = int(now + window_seconds)

            info = {
                "remaining": remaining,
                "reset_at": reset_at,
                "total": max_requests,
                "current": count + (1 if allowed else 0)
            }

            return allowed, info

        except Exception as e:
            logger.error(f"Sliding window rate limit error: {e}")
            return True, {"remaining": max_requests, "reset_at": 0, "total": max_requests, "current": 0}

    async def check_rate_limit_token_bucket(
        self,
        identifier: str,
        resource: str,
        max_tokens: int,
        refill_rate: float,  # tokens per second
        cost: int = 1  # tokens consumed per request
    ) -> Tuple[bool, Dict[str, any]]:
        """
        Token bucket rate limiting

        Allows burst traffic up to max_tokens, then refills at steady rate

        Args:
            identifier: User/IP identifier
            resource: Resource name
            max_tokens: Bucket capacity
            refill_rate: Tokens added per second
            cost: Tokens consumed by this request

        Returns:
            (is_allowed, info_dict)
        """
        key = self._key(identifier, f"{resource}:bucket")

        try:
            # Get current bucket state
            bucket = await self.redis.hgetall(key)

            now = time.time()

            if bucket:
                tokens = float(bucket.get("tokens", max_tokens))
                last_refill = float(bucket.get("last_refill", now))
            else:
                tokens = max_tokens
                last_refill = now

            # Calculate tokens to add based on time elapsed
            time_passed = now - last_refill
            tokens_to_add = time_passed * refill_rate
            tokens = min(max_tokens, tokens + tokens_to_add)

            # Check if enough tokens
            allowed = tokens >= cost

            if allowed:
                tokens -= cost

            # Update bucket
            await self.redis.client.hset(key, "tokens", tokens)
            await self.redis.client.hset(key, "last_refill", now)
            await self.redis.client.expire(key, 3600)  # 1 hour expiry

            info = {
                "tokens_remaining": int(tokens),
                "max_tokens": max_tokens,
                "refill_rate": refill_rate,
                "cost": cost
            }

            return allowed, info

        except Exception as e:
            logger.error(f"Token bucket rate limit error: {e}")
            return True, {"tokens_remaining": max_tokens, "max_tokens": max_tokens}

    async def check_rate_limit(
        self,
        identifier: str,
        resource: str,
        max_requests: int,
        window_seconds: int,
        strategy: RateLimitStrategy = RateLimitStrategy.FIXED_WINDOW
    ) -> Tuple[bool, Dict]:
        """
        Check rate limit with specified strategy

        Returns:
            (is_allowed, info_dict)
        """
        if strategy == RateLimitStrategy.SLIDING_WINDOW:
            return await self.check_rate_limit_sliding(
                identifier, resource, max_requests, window_seconds
            )
        elif strategy == RateLimitStrategy.TOKEN_BUCKET:
            # Convert to token bucket parameters
            refill_rate = max_requests / window_seconds
            return await self.check_rate_limit_token_bucket(
                identifier, resource, max_tokens=max_requests, refill_rate=refill_rate
            )
        else:  # FIXED_WINDOW
            return await self.check_rate_limit_fixed(
                identifier, resource, max_requests, window_seconds
            )

    async def reset_rate_limit(self, identifier: str, resource: str):
        """Reset rate limit for identifier"""
        key = self._key(identifier, resource)
        await self.redis.delete(key)
        logger.info(f"Rate limit reset for {identifier}:{resource}")


# Global instance
rate_limiter = RateLimiter()


# Common rate limit profiles

class RateLimitProfiles:
    """Pre-defined rate limit configurations"""

    # API endpoints: 100 requests per minute
    API_DEFAULT = {"max_requests": 100, "window_seconds": 60}

    # Login attempts: 5 per 15 minutes
    LOGIN = {"max_requests": 5, "window_seconds": 900}

    # Password reset: 3 per hour
    PASSWORD_RESET = {"max_requests": 3, "window_seconds": 3600}

    # File uploads: 10 per hour
    FILE_UPLOAD = {"max_requests": 10, "window_seconds": 3600}

    # AI requests: 20 per minute
    AI_REQUESTS = {"max_requests": 20, "window_seconds": 60}

    # Heavy queries: 10 per minute
    HEAVY_QUERY = {"max_requests": 10, "window_seconds": 60}

    # Burst allowed: 1000 per hour, but burst to 100
    BURST_ALLOWED = {"max_tokens": 100, "refill_rate": 1000/3600}  # For token bucket


# Decorator for rate limiting

def rate_limit(
    resource: str,
    max_requests: int = 100,
    window_seconds: int = 60,
    strategy: RateLimitStrategy = RateLimitStrategy.FIXED_WINDOW,
    identifier_func: Optional[callable] = None
):
    """
    Decorator for rate limiting functions/endpoints

    Args:
        resource: Resource name
        max_requests: Max requests allowed
        window_seconds: Time window
        strategy: Rate limiting strategy
        identifier_func: Function to extract identifier from args (default: first arg)

    Example:
        @rate_limit("api:users", max_requests=100, window_seconds=60)
        async def get_users(user_id: str):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract identifier
            if identifier_func:
                identifier = identifier_func(*args, **kwargs)
            elif args:
                identifier = str(args[0])
            else:
                identifier = "default"

            # Check rate limit
            allowed, info = await rate_limiter.check_rate_limit(
                identifier, resource, max_requests, window_seconds, strategy
            )

            if not allowed:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Try again in {info.get('reset_at', 0) - int(time.time())} seconds"
                )

            # Execute function
            return await func(*args, **kwargs)

        return wrapper
    return decorator
