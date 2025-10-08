# Shared Library - Quick Reference Guide

**Fast lookup for common patterns and usage**
**Version:** 1.0.0 | **Last Updated:** 2025-10-07

---

## Table of Contents

1. [Quick Setup](#quick-setup)
2. [Authentication Patterns](#authentication-patterns)
3. [Database Patterns](#database-patterns)
4. [Cache Patterns](#cache-patterns)
5. [EventBus Patterns](#eventbus-patterns)
6. [Error Handling](#error-handling)
7. [Monitoring & Logging](#monitoring--logging)
8. [Common Tasks](#common-tasks)
9. [Environment Variables](#environment-variables)
10. [Troubleshooting](#troubleshooting)

---

## Quick Setup

### Minimal Service Setup

```python
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from shared.config import SharedSettings
from shared.database import init_database, get_db, close_db
from shared.cache import init_cache
from shared.auth import init_jwt, get_current_user
from shared.eventbus import init_eventbus, get_eventbus
from shared.middleware import ErrorHandlerMiddleware
from shared.monitoring import PrometheusMiddleware, get_metrics_endpoint

# Configuration
settings = SharedSettings()

# FastAPI app
app = FastAPI(title=settings.SERVICE_NAME, version=settings.SERVICE_VERSION)

# Middleware
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", get_metrics_endpoint)

# Startup
@app.on_event("startup")
async def startup():
    # Database
    init_database(settings.DATABASE_URL, pool_size=20)

    # Cache
    init_cache(settings.REDIS_URL)

    # JWT
    init_jwt(settings.JWT_SECRET_KEY)

    # EventBus
    eventbus = init_eventbus(settings.RABBITMQ_URL)
    await eventbus.connect()

# Shutdown
@app.on_event("shutdown")
async def shutdown():
    await close_db()
    await get_eventbus().disconnect()

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "service": settings.SERVICE_NAME}
```

---

## Authentication Patterns

### Protect Endpoint with Authentication

```python
from shared.auth import get_current_user

@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {
        "user_id": current_user["user_id"],
        "tenant_id": current_user["tenant_id"],
        "role": current_user["role"]
    }
```

### Require Specific Permission

```python
from shared.auth import require_permission, Permission

@router.post("/exercises")
@require_permission(Permission.EXERCISE_CREATE)
async def create_exercise(
    exercise: ExerciseCreate,
    current_user: dict = Depends(get_current_user)
):
    # User has EXERCISE_CREATE permission
    return await create_exercise_logic(exercise)
```

### Require Specific Role

```python
from shared.auth import require_role

@router.delete("/exercises/{id}")
async def delete_exercise(
    id: int,
    current_user: dict = Depends(require_role("admin", "bcm_manager"))
):
    # Only admins and bcm_managers can access
    return await delete_exercise_logic(id)
```

### Require Admin Access

```python
from shared.auth import require_admin

@router.post("/tenants")
async def create_tenant(
    tenant: TenantCreate,
    current_user: dict = Depends(require_admin())
):
    # Only admins
    return await create_tenant_logic(tenant)
```

### Optional Authentication

```python
from shared.auth import get_optional_user

@router.get("/public-data")
async def get_data(user: dict | None = Depends(get_optional_user)):
    if user:
        # Authenticated - return personalized data
        return await get_user_data(user["user_id"])
    else:
        # Public - return general data
        return await get_public_data()
```

### Create JWT Token (for login endpoints)

```python
from shared.auth import get_jwt_manager

@router.post("/login")
async def login(credentials: LoginRequest):
    # Validate credentials
    user = await authenticate(credentials)

    # Create token
    jwt_manager = get_jwt_manager()
    token = jwt_manager.create_token(
        user_id=user.id,
        tenant_id=user.tenant_id,
        role=user.role,
        expires_hours=24,
        additional_claims={"email": user.email}
    )

    return {"access_token": token, "token_type": "bearer"}
```

### Check Permission in Code

```python
from shared.auth import has_permission, Permission

if has_permission(current_user["role"], Permission.DOCUMENT_APPROVE):
    # User can approve documents
    await approve_document(doc_id)
else:
    # User cannot approve
    raise PermissionDeniedException("Cannot approve documents")
```

---

## Database Patterns

### Basic Query

```python
from sqlalchemy import select
from shared.database import get_db

@router.get("/users")
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users
```

### Filter by Tenant

```python
@router.get("/exercises")
async def list_exercises(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Exercise).where(
        Exercise.tenant_id == current_user["tenant_id"]
    )
    result = await db.execute(stmt)
    return result.scalars().all()
```

### Get by ID or 404

```python
from shared.database.session import get_or_404

@router.get("/exercises/{id}")
async def get_exercise(
    id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    exercise = await get_or_404(db, Exercise, id)

    # Validate tenant access
    if exercise.tenant_id != current_user["tenant_id"]:
        raise TenantMismatchError(
            user_tenant=current_user["tenant_id"],
            resource_tenant=exercise.tenant_id
        )

    return exercise
```

### Create Record

```python
@router.post("/exercises")
async def create_exercise(
    exercise: ExerciseCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Create model
    db_exercise = Exercise(
        tenant_id=current_user["tenant_id"],
        created_by=current_user["user_id"],
        **exercise.dict()
    )

    # Add and commit
    db.add(db_exercise)
    await db.commit()
    await db.refresh(db_exercise)

    return db_exercise
```

### Update Record

```python
@router.put("/exercises/{id}")
async def update_exercise(
    id: int,
    updates: ExerciseUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    exercise = await get_or_404(db, Exercise, id)

    # Update fields
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(exercise, field, value)

    exercise.updated_by = current_user["user_id"]
    exercise.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(exercise)

    return exercise
```

### Delete Record

```python
@router.delete("/exercises/{id}")
async def delete_exercise(
    id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    exercise = await get_or_404(db, Exercise, id)

    await db.delete(exercise)
    await db.commit()

    return {"message": "Exercise deleted"}
```

### Transaction Handling

```python
from shared.database.session import commit_or_rollback

@router.post("/complex-operation")
async def complex_operation(
    data: ComplexData,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Multiple operations
        db.add(record1)
        db.add(record2)

        # Commit or rollback
        await commit_or_rollback(db)

        return {"status": "success"}
    except Exception as e:
        # Rollback already handled
        raise DatabaseError("complex-operation", str(e))
```

### Pagination (Offset-based)

```python
from shared.database.pagination import paginate_offset

@router.get("/exercises")
async def list_exercises(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Exercise).order_by(Exercise.created_at.desc())

    result = await paginate_offset(
        db,
        stmt,
        page=page,
        page_size=page_size
    )

    return result
```

### Check Pool Status

```python
from shared.database import get_db_manager

@router.get("/admin/pool-status")
async def get_pool_status(current_user: dict = Depends(require_admin())):
    manager = get_db_manager()
    status = manager.get_pool_status()

    return {
        "pool_size": status["pool_size"],
        "active": status["checked_out"],
        "available": status["checked_in"],
        "overflow": status["overflow"]
    }
```

---

## Cache Patterns

### Direct Cache Usage

```python
from shared.cache import get_cache

@router.get("/dashboard/{tenant_id}")
async def get_dashboard(tenant_id: str):
    cache = get_cache()

    # Try cache first
    cached = await cache.get("dashboard", tenant_id=tenant_id)
    if cached:
        return cached

    # Compute if not cached
    dashboard = await compute_dashboard(tenant_id)

    # Cache for 5 minutes
    await cache.set("dashboard", dashboard, ttl=300, tenant_id=tenant_id)

    return dashboard
```

### Decorator Caching (Recommended)

```python
from shared.cache import cached

@cached(ttl=300, key_prefix="kpi:dashboard")
async def get_kpi_dashboard(tenant_id: str):
    # This function is automatically cached
    # Cache key: "tenant:{tenant_id}:kpi:dashboard:{tenant_id}"
    return await expensive_kpi_calculation(tenant_id)

# Use it
dashboard = await get_kpi_dashboard("tenant123")
```

### Cache with Custom Key

```python
@cached(ttl=3600, key_prefix="user:profile", use_tenant=False)
async def get_user_profile(user_id: str):
    # Cache key: "user:profile:{user_id}"
    return await fetch_user_profile(user_id)
```

### Invalidate Cache on Update

```python
@router.put("/kpi/{id}")
async def update_kpi(
    id: int,
    updates: KPIUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Update database
    kpi = await update_kpi_in_db(id, updates, db)

    # Invalidate related caches
    cache = get_cache()
    await cache.clear_pattern(
        "kpi:dashboard*",
        tenant_id=current_user["tenant_id"]
    )

    return kpi
```

### Pattern-based Invalidation

```python
# Clear all user caches for a tenant
await cache.clear_pattern("user:*", tenant_id="tenant123")

# Clear all KPI caches
await cache.clear_pattern("kpi:*", tenant_id="tenant123")

# Clear specific prefix
await cache.clear_pattern("dashboard:*", tenant_id="tenant123")
```

### Check Cache Metrics

```python
@router.get("/admin/cache-metrics")
async def cache_metrics(current_user: dict = Depends(require_admin())):
    cache = get_cache()
    metrics = cache.get_metrics()

    return {
        "hits": metrics["hits"],
        "misses": metrics["misses"],
        "hit_rate": f"{metrics['hit_rate']:.2%}",
        "total_requests": metrics["total_requests"],
        "errors": metrics["errors"]
    }
```

### Health Check Cache

```python
@router.get("/health/cache")
async def cache_health():
    cache = get_cache()
    healthy = await cache.ping()

    return {
        "status": "healthy" if healthy else "unhealthy",
        "service": "redis"
    }
```

---

## EventBus Patterns

### Publish Event (Simple)

```python
from shared.eventbus import get_eventbus

@router.post("/exercises")
async def create_exercise(
    exercise: ExerciseCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Create exercise
    db_exercise = await create_exercise_in_db(exercise, db)

    # Publish event
    eventbus = get_eventbus()
    await eventbus.publish(
        "exercise.created",
        {
            "exercise_id": db_exercise.id,
            "exercise_type": db_exercise.exercise_type,
            "tenant_id": db_exercise.tenant_id
        },
        tenant_id=db_exercise.tenant_id
    )

    return db_exercise
```

### Publish with EventPublisher Helper

```python
from shared.eventbus import EventPublisher

# Initialize once
publisher = EventPublisher(service_name="validation")

@router.post("/exercises")
async def create_exercise(...):
    db_exercise = await create_exercise_in_db(exercise, db)

    # Publish created event
    await publisher.publish_created(
        "exercise",
        db_exercise.id,
        {
            "exercise_type": db_exercise.exercise_type,
            "planned_date": db_exercise.planned_date
        },
        tenant_id=db_exercise.tenant_id
    )

    return db_exercise
```

### Publish Status Change

```python
await publisher.publish_status_changed(
    "exercise",
    exercise_id=123,
    old_status="PLANNED",
    new_status="IN_PROGRESS",
    tenant_id="tenant456"
)
```

### Subscribe to Events

```python
from shared.eventbus import EventSubscriber

# Initialize subscriber
subscriber = EventSubscriber(service_name="notifications")

# Register handler
@subscriber.on("exercise.created")
async def handle_exercise_created(event_data: dict, tenant_id: str):
    exercise_id = event_data["exercise_id"]
    print(f"[{tenant_id}] New exercise created: {exercise_id}")

    # Send notification
    await send_notification(tenant_id, exercise_id)

# Start subscriber (in startup event)
@app.on_event("startup")
async def startup():
    # ... other initialization
    await subscriber.start()
```

### Subscribe to Multiple Event Types

```python
# Exact match
@subscriber.on("exercise.created")
async def handle_created(event_data, tenant_id):
    ...

# Wildcard - all exercise events
@subscriber.on("exercise.*")
async def handle_all_exercise(event_data, tenant_id):
    ...

# All events
@subscriber.on("#")
async def handle_all_events(event_data, tenant_id):
    ...
```

### Error Handling in Subscribers

```python
@subscriber.on("exercise.created")
async def handle_exercise_created(event_data: dict, tenant_id: str):
    try:
        exercise_id = event_data["exercise_id"]
        await process_exercise(exercise_id)
    except Exception as e:
        logger.error(
            "Failed to process exercise event",
            exercise_id=exercise_id,
            error=str(e)
        )
        # Event will be acknowledged anyway
        # Consider implementing dead letter queue
```

---

## Error Handling

### Raise Specific Exceptions

```python
from shared.exceptions import (
    ResourceNotFoundException,
    ValidationException,
    PermissionDeniedException,
    WorkflowException
)

# Resource not found
if not exercise:
    raise ResourceNotFoundException(
        f"Exercise {id} not found",
        details={"exercise_id": id, "tenant_id": tenant_id}
    )

# Validation error
if rto_hours > 168:
    raise ValidationException(
        "RTO cannot exceed 168 hours (7 days)",
        details={"rto_hours": rto_hours, "max": 168}
    )

# Permission denied
if not has_permission(user.role, Permission.EXERCISE_DELETE):
    raise PermissionDeniedException(
        "User cannot delete exercises",
        details={"user_id": user.id, "role": user.role}
    )

# Workflow error
if exercise.status == "COMPLETED":
    raise WorkflowException(
        "Cannot start completed exercise",
        details={
            "exercise_id": exercise.id,
            "current_status": "COMPLETED"
        }
    )
```

### Custom Exception Handler (if needed)

```python
from fastapi import Request
from fastapi.responses import JSONResponse
from shared.exceptions import BCMException

@app.exception_handler(BCMException)
async def bcm_exception_handler(request: Request, exc: BCMException):
    # Middleware already handles this, but you can customize
    error_response = exc.to_response()

    # Map error code to HTTP status
    status_codes = {
        "RESOURCE_NOT_FOUND": 404,
        "VALIDATION": 400,
        "PERMISSION_DENIED": 403,
        "WORKFLOW": 400,
    }

    status_code = status_codes.get(exc.code, 500)

    return JSONResponse(
        status_code=status_code,
        content=error_response.dict()
    )
```

### Tenant Mismatch Check

```python
from shared.exceptions import TenantMismatchError

exercise = await get_or_404(db, Exercise, id)

if exercise.tenant_id != current_user["tenant_id"]:
    raise TenantMismatchError(
        user_tenant=current_user["tenant_id"],
        resource_tenant=exercise.tenant_id
    )
```

---

## Monitoring & Logging

### Structured Logging

```python
from shared.utils import get_logger

logger = get_logger(__name__)

# Info with context
logger.info(
    "Exercise created",
    exercise_id=123,
    tenant_id="tenant456",
    created_by="user789",
    exercise_type="tabletop"
)

# Warning
logger.warning(
    "Exercise deadline approaching",
    exercise_id=123,
    days_remaining=2
)

# Error with exception
try:
    await risky_operation()
except Exception as e:
    logger.error(
        "Operation failed",
        operation="risky_operation",
        error=str(e),
        exercise_id=123
    )
```

### Track Business Metrics

```python
from shared.monitoring import track_business_metric

# Track exercise completion
track_business_metric(
    "exercises_completed",
    1,
    labels={
        "tenant_id": "tenant456",
        "exercise_type": "tabletop",
        "duration_hours": 4
    }
)

# Track KPI measurement
track_business_metric(
    "kpi_measured",
    kpi_value,
    labels={
        "tenant_id": tenant_id,
        "kpi_name": kpi.name,
        "status": "on_target"
    }
)
```

### Track Database Queries

```python
from shared.monitoring import track_db_query
import time

start = time.time()
result = await db.execute(complex_query)
duration = time.time() - start

track_db_query(
    query_name="get_kpi_dashboard",
    duration=duration,
    tenant_id=tenant_id
)
```

### Track EventBus Events

```python
from shared.monitoring import track_event_published, track_event_consumed

# When publishing
await eventbus.publish("exercise.created", data, tenant_id)
track_event_published("exercise.created", tenant_id)

# When consuming
@subscriber.on("exercise.created")
async def handle_event(event_data, tenant_id):
    try:
        await process(event_data)
        track_event_consumed("exercise.created", tenant_id, success=True)
    except Exception:
        track_event_consumed("exercise.created", tenant_id, success=False)
        raise
```

---

## Common Tasks

### Multi-Tenant Data Access

```python
# ALWAYS filter by tenant_id
@router.get("/exercises")
async def list_exercises(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Exercise).where(
        Exercise.tenant_id == current_user["tenant_id"]
    )
    result = await db.execute(stmt)
    return result.scalars().all()

# ALWAYS validate tenant access
exercise = await get_or_404(db, Exercise, id)
if exercise.tenant_id != current_user["tenant_id"]:
    raise TenantMismatchError(
        user_tenant=current_user["tenant_id"],
        resource_tenant=exercise.tenant_id
    )
```

### Audit Logging

```python
from shared.audit import AuditLogger

audit = AuditLogger()

# Log creation
await audit.log_create(
    user_id=current_user["user_id"],
    tenant_id=current_user["tenant_id"],
    entity_type="exercise",
    entity_id=exercise.id,
    data=exercise.dict()
)

# Log update
await audit.log_update(
    user_id=current_user["user_id"],
    tenant_id=current_user["tenant_id"],
    entity_type="exercise",
    entity_id=exercise.id,
    changes={"status": {"old": "PLANNED", "new": "IN_PROGRESS"}}
)

# Log deletion
await audit.log_delete(
    user_id=current_user["user_id"],
    tenant_id=current_user["tenant_id"],
    entity_type="exercise",
    entity_id=exercise.id
)
```

### Change Tracking (History)

```python
from shared.history import ChangeTracker

tracker = ChangeTracker()

# Track field change
await tracker.track_change(
    entity_type="exercise",
    entity_id=exercise.id,
    field="status",
    old_value="PLANNED",
    new_value="IN_PROGRESS",
    user_id=current_user["user_id"]
)

# Get change history
history = await tracker.get_history("exercise", exercise.id)

# Rollback to previous version
await tracker.rollback("exercise", exercise.id, version=5)
```

### Parallel Processing

```python
from shared.utils import parallel_map, batched_process

# Process items in parallel
async def process_exercise(exercise):
    # Heavy processing
    return await analyze_exercise(exercise)

# Process up to 10 concurrently
results = await parallel_map(
    process_exercise,
    exercises,
    max_concurrency=10
)

# Batch processing
async def process_batch(batch):
    # Process batch
    return await bulk_insert(batch)

results = await batched_process(
    items=large_dataset,
    batch_size=100,
    processor_func=process_batch
)
```

### Validation

```python
from shared.validators import (
    validate_email,
    validate_tenant_id,
    validate_date_range,
    validate_url
)

# Email validation
if not validate_email(email):
    raise ValidationException("Invalid email format")

# Tenant ID validation
if not validate_tenant_id(tenant_id):
    raise ValidationException("Invalid tenant ID format")

# Date range validation
if not validate_date_range(start_date, end_date):
    raise ValidationException("Start date must be before end date")

# URL validation
if not validate_url(callback_url):
    raise ValidationException("Invalid URL format")
```

---

## Environment Variables

### Required Variables

```bash
# Database (REQUIRED)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/bcm_db

# Redis (REQUIRED)
REDIS_URL=redis://localhost:6379/0

# RabbitMQ (REQUIRED)
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# JWT (REQUIRED)
JWT_SECRET_KEY=your-super-secret-key-minimum-32-characters-long
```

### Optional Variables

```bash
# Environment
ENVIRONMENT=development  # development, staging, production
SERVICE_NAME=my-service
SERVICE_VERSION=1.0.0

# Database Pool
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_RECYCLE=3600
DB_ECHO=false

# Cache
CACHE_DEFAULT_TTL=3600

# EventBus
EVENTBUS_EXCHANGE=bcm_events

# JWT
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
CORS_ALLOW_CREDENTIALS=true

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json  # json, text

# Metrics
METRICS_ENABLED=true
METRICS_PORT=9090

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60

# File Upload
MAX_UPLOAD_SIZE_MB=100
ALLOWED_FILE_TYPES=[".pdf",".docx",".xlsx",".jpg",".png"]

# Email (if using notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@example.com
SMTP_PASSWORD=your-smtp-password
SMTP_FROM_EMAIL=noreply@example.com
```

### .env File Template

```bash
# Copy this to .env and fill in values

# === REQUIRED ===
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/bcm
REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
JWT_SECRET_KEY=change-this-to-a-secure-random-key-minimum-32-chars

# === SERVICE INFO ===
ENVIRONMENT=development
SERVICE_NAME=my-service
SERVICE_VERSION=1.0.0

# === DATABASE ===
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_RECYCLE=3600

# === LOGGING ===
LOG_LEVEL=INFO
LOG_FORMAT=json

# === CORS (for frontend) ===
CORS_ORIGINS=["http://localhost:3000"]
```

---

## Troubleshooting

### Database Connection Issues

**Problem:** `RuntimeError: Database not initialized`

```python
# Solution: Call init_database() in startup event
@app.on_event("startup")
async def startup():
    init_database(settings.DATABASE_URL, pool_size=20)
```

**Problem:** Connection pool exhausted

```python
# Check pool status
manager = get_db_manager()
status = manager.get_pool_status()
print(f"Pool size: {status['pool_size']}")
print(f"Active: {status['checked_out']}")
print(f"Available: {status['checked_in']}")

# Solution: Increase pool size
DATABASE_URL=...
DB_POOL_SIZE=50  # Increase from default 20
DB_MAX_OVERFLOW=20  # Increase from default 10
```

**Problem:** Stale connections

```python
# Solution: Already handled by pool_pre_ping=True
# But you can also reduce recycle time:
DB_POOL_RECYCLE=1800  # 30 minutes instead of 1 hour
```

### Cache Connection Issues

**Problem:** `RuntimeError: Cache not initialized`

```python
# Solution: Call init_cache() in startup
@app.on_event("startup")
async def startup():
    init_cache(settings.REDIS_URL)
```

**Problem:** Cache not invalidating

```python
# Check cache status
cache = get_cache()
healthy = await cache.ping()
print(f"Redis healthy: {healthy}")

# Force invalidation
await cache.clear_pattern("*", tenant_id="tenant123")
```

**Problem:** Cache hit rate low

```python
# Check metrics
metrics = cache.get_metrics()
print(f"Hit rate: {metrics['hit_rate']:.2%}")

# Solutions:
# 1. Increase TTL
@cached(ttl=3600)  # 1 hour instead of 5 minutes

# 2. Use more specific cache keys
@cached(ttl=300, key_prefix="specific:prefix")
```

### EventBus Issues

**Problem:** `RuntimeError: EventBus not initialized`

```python
# Solution: Initialize and connect in startup
@app.on_event("startup")
async def startup():
    eventbus = init_eventbus(settings.RABBITMQ_URL)
    await eventbus.connect()
```

**Problem:** Events not being received

```python
# Check connection
eventbus = get_eventbus()
connected = eventbus.is_connected()
print(f"EventBus connected: {connected}")

# Verify subscription
@subscriber.on("exercise.created")  # Exact match
async def handler(event_data, tenant_id):
    print(f"Received: {event_data}")

await subscriber.start()  # Don't forget to start!
```

**Problem:** Events publishing but not consumed

```python
# Check routing key
# Publisher uses: "exercise.created"
# Subscriber must use exact match or wildcard:
@subscriber.on("exercise.created")  # ✅ Exact
@subscriber.on("exercise.*")        # ✅ Wildcard
@subscriber.on("exercises.created") # ❌ Wrong!
```

### Authentication Issues

**Problem:** `401 Unauthorized` on protected endpoints

```python
# Check token format
# Must be: Authorization: Bearer <token>

# Verify token
jwt_manager = get_jwt_manager()
try:
    payload = jwt_manager.verify_token(token)
    print(f"Token valid for user: {payload['user_id']}")
except Exception as e:
    print(f"Token invalid: {e}")
```

**Problem:** `403 Permission Denied`

```python
# Check user permissions
from shared.auth import get_user_permissions

permissions = get_user_permissions(user_role)
print(f"User has {len(permissions)} permissions")

# Check specific permission
from shared.auth import has_permission
can_create = has_permission(user_role, Permission.EXERCISE_CREATE)
print(f"Can create exercises: {can_create}")
```

### Performance Issues

**Problem:** Slow database queries

```python
# Enable query profiling
from shared.database import enable_profiling, get_global_profiler

enable_profiling()

# Run queries...

# Get profile
profiler = get_global_profiler()
stats = profiler.get_stats()
for query_name, info in stats.items():
    print(f"{query_name}: {info['avg_time']:.3f}s avg")
```

**Problem:** High memory usage

```python
# Check pool status
manager = get_db_manager()
status = manager.get_pool_status()

# Reduce pool size if needed
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=5
```

**Problem:** Slow cache lookups

```python
# Check Redis latency
cache = get_cache()
healthy = await cache.ping()

# Use connection pooling for Redis
REDIS_URL=redis://localhost:6379/0?encoding=utf-8&decode_responses=True
```

### Logging Issues

**Problem:** Logs not appearing

```python
# Setup logging in main.py
from shared.utils import setup_logging

setup_logging(level="INFO", format="json")

# Use logger
logger = get_logger(__name__)
logger.info("Test message", key="value")
```

**Problem:** Too many logs

```python
# Reduce log level
LOG_LEVEL=WARNING  # or ERROR

# Or filter in code
import logging
logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
```

### Multi-Tenant Issues

**Problem:** Seeing other tenant's data

```python
# ALWAYS filter by tenant_id
stmt = select(Exercise).where(
    Exercise.tenant_id == current_user["tenant_id"]  # ✅ Required!
)

# ALWAYS validate access
if exercise.tenant_id != current_user["tenant_id"]:
    raise TenantMismatchError(...)
```

**Problem:** Cache bleeding between tenants

```python
# ALWAYS include tenant_id in cache operations
await cache.set(key, value, tenant_id=tenant_id)  # ✅
await cache.get(key, tenant_id=tenant_id)         # ✅

await cache.set(key, value)  # ❌ Global cache!
```

---

## Quick Commands

### Start Dependencies (Docker)

```bash
# PostgreSQL
docker run -d --name bcm-postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=bcm \
  -p 5432:5432 \
  postgres:15

# Redis
docker run -d --name bcm-redis \
  -p 6379:6379 \
  redis:7

# RabbitMQ
docker run -d --name bcm-rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:3-management
```

### Run Service

```bash
# Install dependencies
pip install -r requirements.txt

# Run with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or with environment
ENV=production uvicorn main:app --host 0.0.0.0 --port 8000
```

### Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Metrics
curl http://localhost:8000/metrics

# Login (get token)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# Protected endpoint
curl http://localhost:8000/exercises \
  -H "Authorization: Bearer <token>"
```

---

## Additional Resources

- **Full Analysis:** `/shared/SHARED_LIBRARY_ANALYSIS.md`
- **Source Code:** `/shared/`
- **Examples:** Check `platform-services/` for real usage
- **Tests:** `/shared/*/test_*.py`

---

**For more help, see SHARED_LIBRARY_ANALYSIS.md or check module-specific docstrings.**
