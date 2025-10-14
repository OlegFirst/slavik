"""
Rate Limiting Middleware
Production-grade Redis-based sliding window rate limiter
"""

import logging
import time
from typing import Callable, Optional, Tuple
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config import settings
from utils.redis_client import redis_client

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Redis-based sliding window rate limiter

    Features:
    - Sliding window algorithm for accurate rate limiting
    - Different limits for VIP/premium users
    - Rate limit headers (X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset)
    - 429 response with Retry-After header
    - Per-user and per-IP rate limiting
    - Graceful degradation if Redis is unavailable
    """

    def __init__(self, app):
        """Initialize rate limiting middleware"""
        super().__init__(app)
        self.enabled = settings.rate_limit_enabled
        self.default_limit = settings.rate_limit_requests
        self.default_window = settings.rate_limit_window
        self.vip_limit = settings.vip_rate_limit_requests
        self.vip_window = settings.vip_rate_limit_window
        self.burst_allowance = settings.rate_limit_burst

        logger.info(
            f"Rate limit middleware initialized: "
            f"default={self.default_limit}/{self.default_window}s, "
            f"vip={self.vip_limit}/{self.vip_window}s, "
            f"enabled={self.enabled}"
        )

    def _is_vip_user(self, request: Request) -> bool:
        """
        Check if user has VIP/premium status

        Args:
            request: FastAPI request object

        Returns:
            True if user is VIP
        """
        # Check if user is authenticated and has VIP role
        if hasattr(request.state, "roles"):
            roles = request.state.roles or []
            return "vip" in roles or "premium" in roles or "admin" in roles

        return False

    def _get_rate_limit_config(self, request: Request) -> Tuple[int, int]:
        """
        Get rate limit configuration for request

        Args:
            request: FastAPI request object

        Returns:
            Tuple of (limit, window_seconds)
        """
        if self._is_vip_user(request):
            return (self.vip_limit, self.vip_window)
        else:
            return (self.default_limit, self.default_window)

    def _get_identifier(self, request: Request) -> str:
        """
        Get unique identifier for rate limiting

        Uses user_id if authenticated, otherwise falls back to IP address

        Args:
            request: FastAPI request object

        Returns:
            Unique identifier string
        """
        # Prefer user_id if authenticated
        if hasattr(request.state, "user_id") and request.state.user_id:
            return f"user:{request.state.user_id}"

        # Fallback to IP address
        # Check for X-Forwarded-For header (proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take first IP in chain
            ip = forwarded_for.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"

        return f"ip:{ip}"

    async def _check_rate_limit(
        self,
        identifier: str,
        limit: int,
        window: int
    ) -> Tuple[bool, int, int, int]:
        """
        Check rate limit using sliding window algorithm

        Args:
            identifier: Unique identifier (user_id or IP)
            limit: Maximum requests allowed
            window: Time window in seconds

        Returns:
            Tuple of (allowed, remaining, reset_time, retry_after)
        """
        current_time = time.time()
        window_start = current_time - window

        # Redis key for this rate limit window
        key = f"ratelimit:{identifier}"

        try:
            # Use sorted set to track requests in sliding window
            # Score is timestamp, value is request ID

            # Remove old requests outside the window
            await redis_client.zremrangebyscore(key, 0, window_start)

            # Count requests in current window
            request_count = await redis_client.zcard(key)

            # Check if limit exceeded
            if request_count >= limit:
                # Get oldest request in window to calculate retry_after
                oldest_requests = await redis_client._client.zrange(
                    key, 0, 0, withscores=True
                )

                if oldest_requests:
                    oldest_timestamp = oldest_requests[0][1]
                    retry_after = int(oldest_timestamp + window - current_time) + 1
                else:
                    retry_after = window

                reset_time = int(current_time + retry_after)

                logger.warning(
                    f"Rate limit exceeded for {identifier}: "
                    f"{request_count}/{limit} in {window}s window"
                )

                return (False, 0, reset_time, retry_after)

            # Add current request to sorted set
            request_id = f"{current_time}:{id(object())}"
            await redis_client.zadd(key, {request_id: current_time})

            # Set expiration on key (cleanup)
            await redis_client.expire(key, window + 60)

            # Calculate remaining requests and reset time
            remaining = limit - (request_count + 1)
            reset_time = int(current_time + window)

            logger.debug(
                f"Rate limit check passed for {identifier}: "
                f"{request_count + 1}/{limit} (remaining: {remaining})"
            )

            return (True, remaining, reset_time, 0)

        except Exception as e:
            logger.error(f"Rate limit check error for {identifier}: {str(e)}")

            # Graceful degradation: allow request if Redis fails
            # In production, you might want different behavior
            logger.warning("Rate limit check failed, allowing request (graceful degradation)")
            return (True, limit - 1, int(current_time + window), 0)

    def _add_rate_limit_headers(
        self,
        response: Response,
        limit: int,
        remaining: int,
        reset_time: int
    ) -> None:
        """
        Add rate limit headers to response

        Args:
            response: Response object
            limit: Rate limit
            remaining: Remaining requests
            reset_time: Reset timestamp
        """
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)

    def _create_rate_limit_response(self, retry_after: int, reset_time: int) -> JSONResponse:
        """
        Create 429 Too Many Requests response

        Args:
            retry_after: Seconds until retry is allowed
            reset_time: Timestamp when limit resets

        Returns:
            JSONResponse with 429 status
        """
        return JSONResponse(
            status_code=429,
            content={
                "error": "rate_limit_exceeded",
                "message": f"Rate limit exceeded. Please retry after {retry_after} seconds.",
                "retry_after": retry_after,
                "reset_at": reset_time,
            },
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(self.default_limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_time),
            },
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request through rate limiting middleware

        Args:
            request: FastAPI request
            call_next: Next middleware/handler in chain

        Returns:
            Response from downstream handlers or 429 if rate limited
        """
        # Skip if rate limiting is disabled
        if not self.enabled:
            return await call_next(request)

        # Skip rate limiting for health checks and metrics
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)

        # Get identifier and rate limit config
        identifier = self._get_identifier(request)
        limit, window = self._get_rate_limit_config(request)

        # Check rate limit
        allowed, remaining, reset_time, retry_after = await self._check_rate_limit(
            identifier, limit, window
        )

        # If rate limit exceeded, return 429
        if not allowed:
            logger.warning(
                f"Rate limit exceeded: {identifier} - "
                f"{request.method} {request.url.path}"
            )
            return self._create_rate_limit_response(retry_after, reset_time)

        # Continue to next middleware/handler
        response = await call_next(request)

        # Add rate limit headers to response
        self._add_rate_limit_headers(response, limit, remaining, reset_time)

        return response


class AdaptiveRateLimiter(BaseHTTPMiddleware):
    """
    Adaptive rate limiter that adjusts limits based on system load

    This is an advanced rate limiter that can increase/decrease limits
    based on backend service health and performance metrics.
    """

    def __init__(self, app):
        """Initialize adaptive rate limiter"""
        super().__init__(app)
        self.base_limit = settings.rate_limit_requests
        self.window = settings.rate_limit_window
        self.multiplier = 1.0  # Starts at 1.0, adjusts based on system health

    async def _calculate_adaptive_limit(self, request: Request) -> int:
        """
        Calculate adaptive rate limit based on system health

        Args:
            request: FastAPI request

        Returns:
            Adjusted rate limit
        """
        try:
            # Check Redis health
            health = await redis_client.health_check()

            # Adjust multiplier based on Redis latency
            if health["status"] == "healthy":
                latency_ms = health.get("latency_ms", 0)

                if latency_ms < 10:
                    # Excellent performance - allow higher limits
                    self.multiplier = 1.2
                elif latency_ms < 50:
                    # Good performance - normal limits
                    self.multiplier = 1.0
                elif latency_ms < 100:
                    # Degraded performance - reduce limits
                    self.multiplier = 0.8
                else:
                    # Poor performance - significantly reduce limits
                    self.multiplier = 0.5
            else:
                # Redis unhealthy - very conservative limits
                self.multiplier = 0.3

            # Calculate adjusted limit
            adjusted_limit = int(self.base_limit * self.multiplier)

            logger.debug(
                f"Adaptive rate limit: {adjusted_limit} "
                f"(base: {self.base_limit}, multiplier: {self.multiplier})"
            )

            return adjusted_limit

        except Exception as e:
            logger.error(f"Error calculating adaptive limit: {str(e)}")
            return self.base_limit

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with adaptive rate limiting"""
        # Get adaptive limit
        limit = await self._calculate_adaptive_limit(request)

        # Store in request state for use by standard rate limiter
        request.state.adaptive_limit = limit

        return await call_next(request)


async def get_rate_limit_status(identifier: str) -> dict:
    """
    Get current rate limit status for identifier

    Args:
        identifier: User ID or IP address

    Returns:
        Dict with rate limit status
    """
    key = f"ratelimit:{identifier}"
    window = settings.rate_limit_window
    current_time = time.time()
    window_start = current_time - window

    try:
        # Clean old requests
        await redis_client.zremrangebyscore(key, 0, window_start)

        # Get current count
        request_count = await redis_client.zcard(key)

        # Get TTL
        ttl = await redis_client.ttl(key)

        return {
            "identifier": identifier,
            "current_usage": request_count,
            "limit": settings.rate_limit_requests,
            "window_seconds": window,
            "remaining": max(0, settings.rate_limit_requests - request_count),
            "reset_in_seconds": ttl if ttl > 0 else window,
        }

    except Exception as e:
        logger.error(f"Error getting rate limit status: {str(e)}")
        return {
            "identifier": identifier,
            "error": str(e),
        }


async def reset_rate_limit(identifier: str) -> bool:
    """
    Reset rate limit for identifier (admin function)

    Args:
        identifier: User ID or IP address

    Returns:
        True if reset successful
    """
    try:
        key = f"ratelimit:{identifier}"
        await redis_client.delete(key)
        logger.info(f"Rate limit reset for {identifier}")
        return True
    except Exception as e:
        logger.error(f"Error resetting rate limit: {str(e)}")
        return False
