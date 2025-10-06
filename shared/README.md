# BCM Platform Shared Library

Shared modules and utilities for all BCM Platform services.

## Overview

This library provides common functionality used across all BCM Platform microservices:

- **Database**: Async connection pooling and session management
- **Cache**: Redis caching with decorators
- **Auth**: JWT authentication and RBAC
- **EventBus**: RabbitMQ event publishing and subscription
- **Exceptions**: Custom exception hierarchy
- **Utils**: Logging, metrics, validators
- **Models**: Common Pydantic models
- **Config**: Shared configuration

## Installation

```bash
# Install shared library
cd /Users/MD/AI-Platform-ISO/shared
pip install -r requirements.txt

# Add to Python path or install in editable mode
pip install -e .
```

## Quick Start

### 1. Database

```python
from shared.database import init_database, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

# Initialize at startup
@app.on_event("startup")
async def startup():
    init_database(
        database_url="postgresql+asyncpg://user:pass@localhost/bcm",
        pool_size=20
    )

# Use in endpoints
@app.get("/users")
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
```

### 2. Cache

```python
from shared.cache import init_cache, cached

# Initialize at startup
@app.on_event("startup")
async def startup():
    init_cache("redis://localhost:6379/0")

# Use decorator for automatic caching
@cached(ttl=3600, key_prefix="exercises")
async def get_exercise_scenarios(tenant_id: str):
    # Expensive calculation
    return await expensive_calculation(tenant_id)

# Use directly
from shared.cache import get_cache

cache = get_cache()
await cache.set("user:123", user_data, ttl=7200)
user = await cache.get("user:123")
```

### 3. Authentication & Authorization

```python
from shared.auth import init_jwt, get_current_user, require_permission, Permission

# Initialize at startup
@app.on_event("startup")
async def startup():
    init_jwt(secret_key="your-secret-key")

# Require authentication
@app.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    return {
        "user_id": current_user["user_id"],
        "role": current_user["role"]
    }

# Require specific permission
@app.post("/exercises")
@require_permission(Permission.EXERCISE_CREATE)
async def create_exercise(
    exercise: ExerciseCreate,
    current_user: dict = Depends(get_current_user)
):
    return await exercise_service.create(exercise)
```

### 4. EventBus

```python
from shared.eventbus import init_eventbus, EventPublisher, EventSubscriber

# Initialize at startup
@app.on_event("startup")
async def startup():
    eventbus = init_eventbus("amqp://guest:guest@localhost/")
    await eventbus.connect()

# Publish events
publisher = EventPublisher(service_name="validation")

await publisher.publish_created(
    "exercise",
    exercise.id,
    {"exercise_type": exercise.exercise_type},
    tenant_id=exercise.tenant_id
)

# Subscribe to events
subscriber = EventSubscriber(service_name="documents")

@subscriber.on("exercise.created")
async def handle_exercise_created(event_data: dict, tenant_id: str):
    exercise_id = event_data["exercise_id"]
    print(f"Processing exercise {exercise_id}")

@app.on_event("startup")
async def startup():
    await subscriber.start()
```

### 5. Exceptions

```python
from shared.exceptions import (
    ValidationException,
    ResourceNotFoundException,
    PermissionDeniedException
)

# Raise custom exceptions
if not exercise:
    raise ResourceNotFoundException(
        f"Exercise {exercise_id} not found",
        details={"exercise_id": exercise_id}
    )

if planned_date < datetime.now():
    raise ValidationException(
        "Planned date cannot be in the past",
        details={"planned_date": planned_date}
    )

# Global exception handler
from fastapi import Request
from fastapi.responses import JSONResponse
from shared.exceptions import BCMException

@app.exception_handler(BCMException)
async def bcm_exception_handler(request: Request, exc: BCMException):
    return JSONResponse(
        status_code=400,
        content=exc.to_response().dict()
    )
```

### 6. Logging

```python
from shared.utils import get_logger

logger = get_logger("validation-service")

# Structured logging
logger.info("Exercise created", extra={
    "exercise_id": exercise.id,
    "tenant_id": exercise.tenant_id,
    "exercise_type": exercise.exercise_type,
    "duration_ms": 234
})

# Context-aware logging
request_logger = logger.with_context(
    request_id="req_123",
    user_id="user_456"
)
request_logger.info("Processing request")
```

### 7. Metrics

```python
from shared.utils import MetricsCollector

metrics = MetricsCollector("validation")

# Track request duration
with metrics.track_request("POST", "/exercises", status=201):
    result = await create_exercise(data)

# Track database queries
with metrics.track_query("insert", "exercises"):
    await db.execute(insert_query)

# Expose metrics endpoint
from prometheus_client import generate_latest
from fastapi import Response

@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

### 8. Validators

```python
from shared.utils import (
    validate_email,
    validate_tenant_id,
    validate_date_range,
    validate_kpi_threshold
)

# Email validation
if not validate_email(user_email):
    raise ValidationException("Invalid email format")

# Tenant ID validation
if not validate_tenant_id(tenant_id):
    raise ValidationException("Invalid tenant ID")

# KPI threshold validation
valid, error = validate_kpi_threshold(
    performance_direction="higher_better",
    target=95.0,
    warning=90.0,
    critical=85.0
)
if not valid:
    raise ValidationException(error)
```

### 9. Configuration

```python
from shared.config import SharedSettings

# Create service-specific settings
class ValidationSettings(SharedSettings):
    SERVICE_NAME: str = "validation"
    
    # Add service-specific settings
    MAX_EXERCISE_DURATION_HOURS: int = 24
    AUTO_CREATE_CAPA_FOR_HIGH_FINDINGS: bool = True

# Use settings
settings = ValidationSettings()

# Initialize shared components
init_database(
    database_url=settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE
)
init_cache(settings.REDIS_URL)
init_jwt(settings.JWT_SECRET_KEY)
```

## Module Reference

### Database (`shared.database`)

#### Classes
- **DatabaseManager**: Async connection pool manager
  - `get_session()`: Get database session
  - `dispose()`: Close all connections
  - `get_pool_status()`: Get pool statistics

#### Functions
- `init_database(database_url, pool_size=20)`: Initialize global database
- `get_db()`: FastAPI dependency for database session
- `get_or_404(db, model, id)`: Get object or raise 404

### Cache (`shared.cache`)

#### Classes
- **RedisCache**: Async Redis cache manager
  - `get(key)`: Get value from cache
  - `set(key, value, ttl)`: Set value in cache
  - `delete(key)`: Delete key from cache
  - `exists(key)`: Check if key exists
  - `clear_pattern(pattern)`: Delete keys matching pattern

#### Functions
- `init_cache(redis_url)`: Initialize global cache
- `@cached(ttl, key_prefix)`: Decorator for caching function results

### Auth (`shared.auth`)

#### Classes
- **JWTManager**: JWT token manager
  - `create_token(user_id, tenant_id, role)`: Create JWT token
  - `verify_token(token)`: Verify and decode token

- **Role**: User role enum
  - `SYSTEM_ADMIN`, `BCM_MANAGER`, `EXERCISE_COORDINATOR`, etc.

- **Permission**: Permission enum
  - `EXERCISE_CREATE`, `KPI_VIEW`, `DOCUMENT_APPROVE`, etc.

#### Functions
- `init_jwt(secret_key)`: Initialize JWT manager
- `get_current_user()`: FastAPI dependency for current user
- `@require_permission(permission)`: Decorator for permission checking
- `has_permission(role, permission)`: Check if role has permission

### EventBus (`shared.eventbus`)

#### Classes
- **EventBusClient**: RabbitMQ client
  - `connect()`: Connect to RabbitMQ
  - `publish(event_type, data, tenant_id)`: Publish event
  - `subscribe(event_type, handler)`: Subscribe to events

- **EventPublisher**: Event publishing helper
  - `publish_created(entity, id, data)`: Publish created event
  - `publish_updated(entity, id, changes)`: Publish updated event
  - `publish_deleted(entity, id)`: Publish deleted event

- **EventSubscriber**: Event subscription helper
  - `@on(event_type)`: Register event handler
  - `start()`: Start all subscriptions

#### Functions
- `init_eventbus(rabbitmq_url)`: Initialize EventBus client

### Exceptions (`shared.exceptions`)

#### Classes
All exceptions inherit from `BCMException`:

- **ValidationException**: Business validation failed
- **ResourceNotFoundException**: Resource not found
- **DuplicateResourceException**: Resource already exists
- **WorkflowException**: Invalid workflow transition
- **SecurityException**: Security violation
- **PermissionDeniedException**: Insufficient permissions
- **ExternalServiceException**: External service failed

#### Models
- **ErrorResponse**: Standard error response format

### Utils (`shared.utils`)

#### Logging
- **StructuredLogger**: JSON structured logger
  - `info(message, **kwargs)`
  - `error(message, **kwargs)`
  - `warning(message, **kwargs)`
  - `debug(message, **kwargs)`
- `get_logger(service_name)`: Get logger instance

#### Metrics
- **MetricsCollector**: Prometheus metrics collector
  - `track_request(method, endpoint, status)`
  - `track_query(operation, table)`

#### Validators
- `validate_email(email)`: Validate email format
- `validate_url(url)`: Validate URL format
- `validate_tenant_id(tenant_id)`: Validate tenant ID
- `validate_date_range(start, end, max_days)`: Validate date range
- `validate_kpi_threshold(direction, target, warning, critical)`: Validate KPI thresholds
- `sanitize_filename(filename)`: Sanitize uploaded filenames

### Models (`shared.models`)

#### Pydantic Models
- **User**: User model
- **Tenant**: Tenant model
- **HealthCheck**: Health check response
- **PaginationParams**: Pagination parameters
- **PaginatedResponse[T]**: Generic paginated response
- **AuditLog**: Audit log entry

## Integration Example

Complete example of using shared library in a service:

```python
# main.py
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import init_database, get_db
from shared.cache import init_cache
from shared.auth import init_jwt, get_current_user, require_permission, Permission
from shared.eventbus import init_eventbus, EventPublisher
from shared.exceptions import BCMException, ResourceNotFoundException
from shared.utils import get_logger
from shared.config import SharedSettings
from shared.models import HealthCheck

# Configuration
class ValidationSettings(SharedSettings):
    SERVICE_NAME: str = "validation"
    SERVICE_VERSION: str = "1.0.0"

settings = ValidationSettings()
logger = get_logger(settings.SERVICE_NAME)

# FastAPI app
app = FastAPI(title="Validation Service")

# Startup
@app.on_event("startup")
async def startup():
    # Initialize database
    init_database(
        database_url=settings.DATABASE_URL,
        pool_size=settings.DB_POOL_SIZE
    )
    logger.info("Database initialized")
    
    # Initialize cache
    init_cache(settings.REDIS_URL)
    logger.info("Cache initialized")
    
    # Initialize JWT
    init_jwt(settings.JWT_SECRET_KEY)
    logger.info("JWT initialized")
    
    # Initialize EventBus
    eventbus = init_eventbus(settings.RABBITMQ_URL)
    await eventbus.connect()
    logger.info("EventBus connected")

# Exception handler
@app.exception_handler(BCMException)
async def bcm_exception_handler(request, exc: BCMException):
    return JSONResponse(
        status_code=400,
        content=exc.to_response().dict()
    )

# Health check
@app.get("/health", response_model=HealthCheck)
async def health_check():
    return HealthCheck(
        status="healthy",
        service=settings.SERVICE_NAME,
        version=settings.SERVICE_VERSION
    )

# Protected endpoint
@app.post("/exercises")
@require_permission(Permission.EXERCISE_CREATE)
async def create_exercise(
    exercise: ExerciseCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    logger.info("Creating exercise", 
                user_id=current_user["user_id"],
                tenant_id=exercise.tenant_id)
    
    # Create exercise
    db_exercise = await exercise_service.create(db, exercise)
    
    # Publish event
    publisher = EventPublisher(settings.SERVICE_NAME)
    await publisher.publish_created(
        "exercise",
        db_exercise.id,
        {"exercise_type": db_exercise.exercise_type},
        tenant_id=exercise.tenant_id
    )
    
    return db_exercise
```

## Environment Variables

Create a `.env` file for configuration:

```bash
# Environment
ENVIRONMENT=development

# Service
SERVICE_NAME=validation-service
SERVICE_VERSION=1.0.0

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/bcm
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379/0
CACHE_DEFAULT_TTL=3600

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@localhost/
EVENTBUS_EXCHANGE=bcm_events

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_EXPIRATION_HOURS=24

# Security
ENCRYPTION_KEY=your-encryption-key
ENABLE_VIRUS_SCAN=true

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Metrics
METRICS_ENABLED=true
METRICS_PORT=9090
```

## Testing

```python
import pytest
from shared.database import init_database
from shared.cache import init_cache
from shared.auth import init_jwt

@pytest.fixture
async def db_session():
    init_database("sqlite+aiosqlite:///:memory:")
    # Yield session for tests
    
@pytest.fixture
async def cache():
    init_cache("redis://localhost:6379/1")  # Test database
    # Yield cache for tests

@pytest.fixture
def jwt_manager():
    return init_jwt("test-secret-key")

async def test_exercise_creation(db_session):
    exercise = await create_exercise(db_session, exercise_data)
    assert exercise.id is not None
```

## License

Proprietary - BCM Platform

## Support

For questions or issues, contact the BCM Platform development team.
