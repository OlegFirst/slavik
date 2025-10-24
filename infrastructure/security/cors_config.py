"""
CORS Configuration - Production-Safe Defaults
Centralized CORS settings for all services
"""

import os
from typing import List


class CORSConfig:
    """CORS configuration with environment-specific defaults"""

    @staticmethod
    def get_allowed_origins() -> List[str]:
        """Get allowed origins based on environment"""
        env = os.getenv("ENVIRONMENT", "development")

        if env == "production":
            # Production: Only specific allowed origins
            return [
                "https://platform.bcm.ai",  # Main platform frontend
                "https://app.bcm.ai",       # App frontend
                "https://admin.bcm.ai",     # Admin panel
                # Add production domains from environment
                *_parse_cors_env("CORS_ALLOWED_ORIGINS"),
            ]
        elif env == "staging":
            # Staging: Staging domains
            return [
                "https://staging.bcm.ai",
                "https://staging-app.bcm.ai",
                "https://staging-admin.bcm.ai",
                *_parse_cors_env("CORS_ALLOWED_ORIGINS"),
            ]
        else:
            # Development: localhost variants
            return [
                "http://localhost:3000",     # Next.js default
                "http://localhost:3001",     # Alternative frontend
                "http://localhost:8080",     # Alternative port
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8080",
                *_parse_cors_env("CORS_ALLOWED_ORIGINS"),
            ]

    @staticmethod
    def get_cors_config() -> dict:
        """Get complete CORS configuration"""
        return {
            "allow_origins": CORSConfig.get_allowed_origins(),
            "allow_credentials": True,
            "allow_methods": [
                "GET",
                "POST",
                "PUT",
                "PATCH",
                "DELETE",
                "OPTIONS",
            ],
            "allow_headers": [
                "Authorization",
                "Content-Type",
                "X-Request-ID",
                "X-Organization-ID",
                "X-User-ID",
                "Accept",
                "Origin",
                "User-Agent",
                "DNT",
                "Cache-Control",
                "X-Requested-With",
            ],
            "expose_headers": [
                "X-Request-ID",
                "X-RateLimit-Limit",
                "X-RateLimit-Remaining",
                "X-RateLimit-Reset",
            ],
            "max_age": 600,  # 10 minutes
        }

    @staticmethod
    def validate_origin(origin: str) -> bool:
        """Validate if origin is allowed"""
        allowed = CORSConfig.get_allowed_origins()

        # Never allow wildcard in production
        if "*" in allowed:
            env = os.getenv("ENVIRONMENT", "development")
            if env == "production":
                raise ValueError(
                    "Wildcard CORS origins (*) are not allowed in production"
                )

        return origin in allowed


def _parse_cors_env(env_var: str) -> List[str]:
    """Parse CORS origins from environment variable"""
    origins_str = os.getenv(env_var, "")
    if not origins_str:
        return []

    # Split by comma and strip whitespace
    origins = [origin.strip() for origin in origins_str.split(",")]
    return [origin for origin in origins if origin]  # Filter empty strings


# Pre-configured CORS middleware settings for FastAPI
def get_fastapi_cors_middleware_params() -> dict:
    """Get parameters for FastAPI CORSMiddleware"""
    config = CORSConfig.get_cors_config()
    return config


# Example usage for FastAPI:
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from infrastructure.security.cors_config import get_fastapi_cors_middleware_params

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    **get_fastapi_cors_middleware_params()
)
"""
