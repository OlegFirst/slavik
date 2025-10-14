# 🌐 API Gateway Implementation Plan

**Status:** Not Started
**Priority:** CRITICAL
**Estimated Time:** 3 days

---

## 📋 OVERVIEW

Implement centralized API Gateway to secure all 15 microservices.

**Current State:** All services exposed directly on ports 8000-8050 (INSECURE!)
**Target State:** Single gateway on port 8000, all traffic authenticated

---

## 🎯 REQUIREMENTS

### Functional Requirements
1. **Authentication:** JWT token validation
2. **Authorization:** Role-based access control (RBAC)
3. **Rate Limiting:** 100 requests/minute per user
4. **Routing:** Smart routing to backend services
5. **Logging:** All requests logged to audit trail
6. **CORS:** Whitelist allowed origins
7. **Health Checks:** Monitor backend service health

### Non-Functional Requirements
1. **Performance:** < 10ms latency overhead
2. **Availability:** 99.9% uptime
3. **Scalability:** Handle 1000+ req/s
4. **Security:** OWASP Top 10 protection

---

## 🏗️ ARCHITECTURE

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT                               │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│              API GATEWAY (Port 8000)                    │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  1. Authentication Middleware                    │  │
│  │     - Validate JWT token                         │  │
│  │     - Extract user_id, tenant_id, roles          │  │
│  └──────────────────────────────────────────────────┘  │
│                     ↓                                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │  2. Rate Limiting Middleware                     │  │
│  │     - Check Redis for request count              │  │
│  │     - Increment counter                          │  │
│  │     - Return 429 if exceeded                     │  │
│  └──────────────────────────────────────────────────┘  │
│                     ↓                                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │  3. Authorization Middleware                     │  │
│  │     - Check user roles/permissions               │  │
│  │     - Return 403 if not allowed                  │  │
│  └──────────────────────────────────────────────────┘  │
│                     ↓                                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │  4. Routing Middleware                           │  │
│  │     - Match path to backend service              │  │
│  │     - Check service health                       │  │
│  │     - Load balance if multiple instances         │  │
│  └──────────────────────────────────────────────────┘  │
│                     ↓                                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │  5. Request Forwarding                           │  │
│  │     - Add X-User-Id, X-Tenant-Id headers         │  │
│  │     - Forward to backend                         │  │
│  │     - Return response                            │  │
│  └──────────────────────────────────────────────────┘  │
│                     ↓                                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │  6. Audit Logging                                │  │
│  │     - Log request/response to PostgreSQL         │  │
│  │     - Include user, action, status               │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│              BACKEND SERVICES                           │
│  8001, 8002, 8003, 8004, ... 8050                      │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 FILE STRUCTURE

```
security/api-gateway/
├── main.py                    # FastAPI application
├── config.py                  # Configuration
├── middleware/
│   ├── __init__.py
│   ├── auth.py               # JWT authentication
│   ├── rate_limit.py         # Rate limiting
│   ├── authorization.py      # RBAC
│   └── audit.py              # Audit logging
├── routing/
│   ├── __init__.py
│   ├── router.py             # Service routing
│   ├── health_checker.py     # Backend health checks
│   └── load_balancer.py      # Load balancing
├── models/
│   ├── __init__.py
│   └── schemas.py            # Pydantic models
├── utils/
│   ├── __init__.py
│   ├── jwt_handler.py        # JWT utilities
│   └── redis_client.py       # Redis connection
├── tests/
│   ├── test_auth.py
│   ├── test_rate_limit.py
│   └── test_routing.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🔨 IMPLEMENTATION STEPS

### Step 1: Project Setup (2 hours)
```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/security/api-gateway

# Create structure
mkdir -p middleware routing models utils tests

# Create files
touch main.py config.py
touch middleware/{__init__,auth,rate_limit,authorization,audit}.py
touch routing/{__init__,router,health_checker,load_balancer}.py
touch models/{__init__,schemas}.py
touch utils/{__init__,jwt_handler,redis_client}.py
touch tests/{test_auth,test_rate_limit,test_routing}.py
touch requirements.txt Dockerfile docker-compose.yml README.md
```

---

### Step 2: Dependencies (requirements.txt)
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-jose[cryptography]==3.3.0  # JWT
redis==5.0.1
httpx==0.25.0  # For proxying requests
prometheus-fastapi-instrumentator==6.1.0
pydantic-settings==2.0.3
```

---

### Step 3: Configuration (config.py)
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Service
    app_name: str = "API Gateway"
    port: int = 8000

    # Auth
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    auth_service_url: str = "http://localhost:8001"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds

    # Backend Services
    coordination_center_url: str = "http://localhost:8004"
    eventbus_url: str = "http://localhost:8001"
    ai_orchestration_url: str = "http://localhost:8002"
    # ... etc

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()
```

---

### Step 4: JWT Authentication Middleware
**File:** `middleware/auth.py`

```python
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()

# Public endpoints that don't require auth
PUBLIC_ENDPOINTS = [
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json"
]

async def verify_jwt_token(credentials: HTTPAuthorizationCredentials) -> dict:
    """Verify JWT token and return payload."""
    token = credentials.credentials

    try:
        from config import settings
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError as e:
        logger.error(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def auth_middleware(request: Request, call_next):
    """Authentication middleware."""

    # Skip auth for public endpoints
    if request.url.path in PUBLIC_ENDPOINTS:
        return await call_next(request)

    # Get Authorization header
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract and verify token
    token = auth_header.split(" ")[1]
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    try:
        payload = await verify_jwt_token(credentials)

        # Add user info to request state
        request.state.user_id = payload.get("sub")
        request.state.tenant_id = payload.get("tenant_id")
        request.state.roles = payload.get("roles", [])
        request.state.email = payload.get("email")

        logger.info(f"Authenticated user: {request.state.user_id}")

    except HTTPException as e:
        logger.warning(f"Authentication failed for {request.url.path}: {e.detail}")
        raise

    response = await call_next(request)
    return response
```

---

### Step 5: Rate Limiting Middleware
**File:** `middleware/rate_limit.py`

```python
from fastapi import Request, HTTPException, status
from utils.redis_client import get_redis
import time
import logging

logger = logging.getLogger(__name__)

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware using Redis sliding window."""

    # Skip for public endpoints
    if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)

    # Get user ID (set by auth middleware)
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        # If no auth, use IP address
        user_id = request.client.host

    from config import settings
    redis = await get_redis()

    now = time.time()
    window_start = now - settings.rate_limit_window
    key = f"rate_limit:{user_id}"

    try:
        # Remove old entries
        await redis.zremrangebyscore(key, 0, window_start)

        # Count current requests
        count = await redis.zcard(key)

        if count >= settings.rate_limit_requests:
            # Rate limit exceeded
            retry_after = int(settings.rate_limit_window - (now - float(await redis.zrange(key, 0, 0)[0])))

            logger.warning(f"Rate limit exceeded for user {user_id}")

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
                headers={
                    "X-RateLimit-Limit": str(settings.rate_limit_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(now + retry_after)),
                    "Retry-After": str(retry_after)
                }
            )

        # Add current request
        await redis.zadd(key, {str(now): now})
        await redis.expire(key, settings.rate_limit_window)

        # Add rate limit headers to response
        response = await call_next(request)

        remaining = settings.rate_limit_requests - count - 1
        response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(now + settings.rate_limit_window))

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rate limiting error: {e}")
        # Don't block requests if rate limiting fails
        return await call_next(request)
```

---

### Step 6: Service Routing
**File:** `routing/router.py`

```python
import httpx
from fastapi import Request, HTTPException
from config import settings
import logging

logger = logging.getLogger(__name__)

# Service routing map
SERVICE_ROUTES = {
    "/coordination": settings.coordination_center_url,
    "/eventbus": settings.eventbus_url,
    "/ai-orchestration": settings.ai_orchestration_url,
    # ... add all services
}

async def route_request(request: Request) -> httpx.Response:
    """Route request to appropriate backend service."""

    path = request.url.path

    # Find matching service
    backend_url = None
    for prefix, url in SERVICE_ROUTES.items():
        if path.startswith(prefix):
            backend_url = url
            # Remove prefix from path
            backend_path = path[len(prefix):]
            break

    if not backend_url:
        raise HTTPException(
            status_code=404,
            detail=f"No service found for path: {path}"
        )

    # Build full URL
    full_url = f"{backend_url}{backend_path}"
    if request.url.query:
        full_url += f"?{request.url.query}"

    # Forward request
    async with httpx.AsyncClient() as client:
        try:
            # Add user context headers
            headers = dict(request.headers)
            headers["X-User-Id"] = getattr(request.state, "user_id", "")
            headers["X-Tenant-Id"] = getattr(request.state, "tenant_id", "")
            headers["X-User-Roles"] = ",".join(getattr(request.state, "roles", []))

            # Remove host header (will be set by httpx)
            headers.pop("host", None)

            response = await client.request(
                method=request.method,
                url=full_url,
                headers=headers,
                content=await request.body(),
                timeout=30.0
            )

            return response

        except httpx.RequestError as e:
            logger.error(f"Error routing request to {full_url}: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Service unavailable: {backend_url}"
            )
```

---

### Step 7: Main Application
**File:** `main.py`

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from prometheus_fastapi_instrumentator import Instrumentator
from middleware.auth import auth_middleware
from middleware.rate_limit import rate_limit_middleware
from routing.router import route_request
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="API Gateway for BCM Platform",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Middlewares (order matters!)
app.middleware("http")(auth_middleware)
app.middleware("http")(rate_limit_middleware)

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "api-gateway"}

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(request: Request, path: str):
    """Proxy all requests to backend services."""
    response = await route_request(request)

    # Return response from backend
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.headers.get("content-type")
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.port)
```

---

## 🧪 TESTING

```bash
# Unit tests
pytest tests/

# Integration tests
# 1. Start all services
# 2. Test authenticated requests
curl -H "Authorization: Bearer <token>" http://localhost:8000/coordination/health

# 3. Test rate limiting
for i in {1..101}; do
    curl -H "Authorization: Bearer <token>" http://localhost:8000/coordination/health
done
# Should get 429 on 101st request

# 4. Test unauthenticated request
curl http://localhost:8000/coordination/health
# Should get 401
```

---

## 📊 SUCCESS CRITERIA

- [ ] All requests authenticated
- [ ] Rate limiting working
- [ ] Requests routed correctly
- [ ] < 10ms latency overhead
- [ ] 99.9% success rate under load
- [ ] All tests passing

---

## 🚀 DEPLOYMENT

```yaml
# docker-compose.yml
version: '3.8'

services:
  api-gateway:
    build: .
    ports:
      - "8000:8000"
    environment:
      JWT_SECRET: ${JWT_SECRET}
      REDIS_URL: redis://redis:6379
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

---

**Next Steps:**
1. Review this plan
2. Start implementation
3. Test thoroughly
4. Deploy to staging
5. Deploy to production
