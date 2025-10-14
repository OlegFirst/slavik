"""
AI-Powered API Gateway - Main Application
Production-grade gateway with intelligent management

This gateway protects 15 microservices with:
- JWT Authentication
- Redis-based rate limiting
- PostgreSQL audit logging
- Circuit breaker protection
- AI-powered management
- Auto-discovery of services
- Self-healing capabilities
"""

import asyncio
import logging
import sys
import uuid
from contextlib import asynccontextmanager
from typing import Optional

import httpx
import structlog
import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.base import BaseHTTPMiddleware

# Configuration
from config import settings, validate_settings

# Middleware
from middleware.auth import AuthenticationMiddleware
from middleware.rate_limit import RateLimitMiddleware
from middleware.audit import AuditLogMiddleware

# Routing
from routing.router import ServiceRouter, get_service_router
from routing.health_checker import HealthChecker, get_health_checker

# Utils
from utils.redis_client import get_redis_client

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer() if settings.log_format == "json"
        else structlog.dev.ConsoleRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown
    Handles initialization and cleanup of resources
    """
    logger.info("=� Starting AI-Powered API Gateway...")

    # Validate configuration
    try:
        validate_settings()
        logger.info(" Configuration validated")
    except ValueError as e:
        logger.error(f"L Configuration validation failed: {e}")
        sys.exit(1)

    # Initialize Redis client
    try:
        redis_client = get_redis_client()
        await redis_client.connect()
        logger.info(" Redis connection established")
    except Exception as e:
        logger.error(f"L Redis connection failed: {e}")
        if settings.environment == "production":
            sys.exit(1)

    # Initialize audit logger
    try:
        audit_logger = get_audit_logger()
        await audit_logger.initialize()
        logger.info(" Audit logger initialized")
    except Exception as e:
        logger.error(f"L Audit logger initialization failed: {e}")
        if settings.environment == "production":
            sys.exit(1)

    # Initialize HTTP client pool for proxying
    app.state.http_client = httpx.AsyncClient(
        limits=httpx.Limits(
            max_connections=settings.max_connections,
            max_keepalive_connections=settings.max_keepalive_connections,
            keepalive_expiry=settings.keepalive_expiry,
        ),
        timeout=httpx.Timeout(settings.default_timeout),
        follow_redirects=False,
    )
    logger.info(" HTTP client pool initialized")

    # Initialize service router
    service_router = get_service_router()
    await service_router.initialize()
    logger.info(" Service router initialized")

    # Initialize health checker
    if settings.health_check_enabled:
        health_checker = get_health_checker()
        asyncio.create_task(health_checker.start_monitoring())
        logger.info(" Health checker started")

    # Start AI Gateway Manager integration
    if settings.ai_manager_enabled:
        asyncio.create_task(start_ai_manager_integration())
        logger.info(" AI Gateway Manager integration started")

    logger.info(
        f"<� API Gateway running on port {settings.port}",
        environment=settings.environment,
        rate_limit=f"{settings.rate_limit_requests} req/{settings.rate_limit_window}s",
        circuit_breaker="enabled" if settings.circuit_breaker_enabled else "disabled",
    )

    yield  # Application is running

    # Shutdown
    logger.info("=� Shutting down API Gateway...")

    # Close HTTP client
    await app.state.http_client.aclose()
    logger.info(" HTTP client closed")

    # Close Redis connection
    await redis_client.close()
    logger.info(" Redis connection closed")

    # Close audit logger
    await audit_logger.close()
    logger.info(" Audit logger closed")

    # Stop health checker
    if settings.health_check_enabled:
        health_checker = get_health_checker()
        health_checker.stop_monitoring()
        logger.info(" Health checker stopped")

    logger.info("=K API Gateway shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-Powered API Gateway for BCM Platform - Intelligent, Secure, Self-Healing",
    version=settings.version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)


# Security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Add security headers
        for header, value in settings.security_headers.items():
            response.headers[header] = value

        return response


app.add_middleware(SecurityHeadersMiddleware)


# Request ID middleware
class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to every request"""

    async def dispatch(self, request: Request, call_next):
        # Generate or extract request ID
        request_id = request.headers.get(settings.request_id_header)
        if not request_id:
            request_id = str(uuid.uuid4())

        # Attach to request state
        request.state.request_id = request_id

        # Call next middleware
        response = await call_next(request)

        # Add request ID to response headers
        response.headers[settings.request_id_header] = request_id

        return response


app.add_middleware(RequestIDMiddleware)


# Add authentication middleware
if settings.audit_enabled:
    app.middleware("http")(audit_middleware)

if settings.rate_limit_enabled:
    app.middleware("http")(rate_limit_middleware)

app.middleware("http")(auth_middleware)


# Prometheus metrics
if settings.metrics_enabled:
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
    logger.info(f" Prometheus metrics exposed at /metrics")


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    Returns gateway health status and backend service health
    """
    health_checker = get_health_checker()

    # Check Redis
    redis_healthy = False
    try:
        redis_client = get_redis_client()
        redis_healthy = await redis_client.health_check()
    except Exception:
        pass

    # Get backend services health
    services_health = {}
    if settings.health_check_enabled:
        services_health = health_checker.get_all_health_status()

    # Determine overall health
    all_services_healthy = all(
        status.get("healthy", False)
        for status in services_health.values()
    )

    overall_healthy = redis_healthy and all_services_healthy

    return {
        "status": "healthy" if overall_healthy else "degraded",
        "service": "api-gateway",
        "version": settings.version,
        "timestamp": structlog.get_logger().bind().info("health_check"),
        "components": {
            "redis": "healthy" if redis_healthy else "unhealthy",
            "backend_services": "healthy" if all_services_healthy else "degraded",
        },
        "services": services_health,
    }


# AI Gateway Manager endpoints
@app.post("/api/v1/gateway/ai/analyze", tags=["AI Management"])
async def ai_analyze_gateway(request: Request):
    """
    Trigger AI analysis of gateway performance
    Requires authentication
    """
    if not settings.ai_manager_enabled:
        raise HTTPException(status_code=503, detail="AI Gateway Manager not enabled")

    try:
        # Get user context
        tenant_id = getattr(request.state, "tenant_id", "default")

        # Call AI Gateway Manager
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.ai_manager_url}/analyze",
                json={
                    "tenant_id": tenant_id,
                    "time_range": request.query_params.get("time_range", "5m"),
                },
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")


@app.post("/api/v1/gateway/ai/optimize", tags=["AI Management"])
async def ai_optimize_gateway(request: Request):
    """
    Get AI optimization suggestions for gateway
    Requires authentication and admin role
    """
    if not settings.ai_manager_enabled:
        raise HTTPException(status_code=503, detail="AI Gateway Manager not enabled")

    # Check admin role
    roles = getattr(request.state, "roles", [])
    if "admin" not in roles and "gateway_admin" not in roles:
        raise HTTPException(status_code=403, detail="Admin role required")

    try:
        tenant_id = getattr(request.state, "tenant_id", "default")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.ai_manager_url}/suggest",
                json={
                    "tenant_id": tenant_id,
                    "focus_area": request.query_params.get("focus", "performance"),
                },
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    except Exception as e:
        logger.error(f"AI optimization failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI optimization failed: {str(e)}")


@app.get("/api/v1/gateway/services", tags=["Service Discovery"])
async def list_services():
    """
    List all discovered backend services
    """
    service_router = get_service_router()
    services = service_router.get_all_services()

    health_checker = get_health_checker()
    health_status = health_checker.get_all_health_status()

    return {
        "services": [
            {
                "name": name,
                "url": info["url"],
                "path_prefix": info["path_prefix"],
                "healthy": health_status.get(name, {}).get("healthy", False),
                "response_time_ms": health_status.get(name, {}).get("response_time_ms"),
                "last_check": health_status.get(name, {}).get("last_check"),
            }
            for name, info in services.items()
        ],
        "total": len(services),
    }


# Main proxy endpoint - routes to backend services
@app.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    tags=["Proxy"],
)
async def proxy_request(request: Request, path: str):
    """
    Main proxy endpoint - routes requests to backend services

    This endpoint:
    1. Receives authenticated request (auth middleware already ran)
    2. Routes to appropriate backend service
    3. Adds user context headers
    4. Forwards request and returns response
    """
    service_router = get_service_router()

    try:
        # Route request to backend
        backend_url = await service_router.route_request(f"/{path}")

        if not backend_url:
            raise HTTPException(
                status_code=404,
                detail=f"No service found for path: /{path}"
            )

        # Build full URL
        full_url = f"{backend_url}/{path}"
        if request.url.query:
            full_url += f"?{request.url.query}"

        # Prepare headers
        headers = dict(request.headers)

        # Add user context headers (from auth middleware)
        headers["X-User-Id"] = getattr(request.state, "user_id", "")
        headers["X-Tenant-Id"] = getattr(request.state, "tenant_id", "")
        headers["X-User-Roles"] = ",".join(getattr(request.state, "roles", []))
        headers["X-Request-ID"] = getattr(request.state, "request_id", "")

        # Remove host header (will be set by httpx)
        headers.pop("host", None)

        # Forward request
        try:
            response = await app.state.http_client.request(
                method=request.method,
                url=full_url,
                headers=headers,
                content=await request.body(),
                timeout=settings.default_timeout,
            )

            # Return response
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type"),
            )

        except httpx.TimeoutException:
            logger.error(f"Timeout calling {backend_url}")
            raise HTTPException(
                status_code=504,
                detail=f"Gateway timeout calling backend service"
            )

        except httpx.RequestError as e:
            logger.error(f"Error calling {backend_url}: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Backend service unavailable: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in proxy: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal gateway error: {str(e)}"
        )


# AI Gateway Manager background integration
async def start_ai_manager_integration():
    """
    Background task to integrate with AI Gateway Manager
    Periodically sends gateway metrics for AI analysis
    """
    logger.info("Starting AI Gateway Manager integration loop")

    while True:
        try:
            await asyncio.sleep(settings.ai_manager_check_interval)

            # Send health check to AI manager
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.ai_manager_url}/analyze",
                    json={
                        "tenant_id": "system",
                        "time_range": "5m",
                    },
                    timeout=10.0,
                )

                if response.status_code == 200:
                    result = response.json()
                    status = result.get("health_status", "UNKNOWN")

                    if status == "CRITICAL":
                        logger.warning(
                            "=� AI Gateway Manager detected CRITICAL issues",
                            recommendations=result.get("recommendations", [])
                        )
                    elif status == "DEGRADED":
                        logger.info(
                            "� AI Gateway Manager detected performance degradation",
                            recommendations=result.get("recommendations", [])
                        )
                    else:
                        logger.debug(" AI Gateway Manager: system healthy")

        except Exception as e:
            logger.error(f"AI Gateway Manager integration error: {e}")
            # Continue loop even on errors


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "request_id": getattr(request.state, "request_id", None),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler for unexpected errors"""
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "request_id": getattr(request.state, "request_id", None),
        },
    )


# Main entry point
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        log_level=settings.log_level.lower(),
        access_log=True,
        reload=settings.environment == "development",
    )
