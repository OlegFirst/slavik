# Shared Library - Quick Start Guide

## 1-Minute Setup

### Step 1: Install Dependencies

```bash
cd /Users/MD/AI-Platform-ISO/shared
pip install -r requirements.txt
```

### Step 2: Create .env File

```bash
cat > .env << 'ENVEOF'
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/bcm
DB_POOL_SIZE=20

# Redis
REDIS_URL=redis://localhost:6379/0

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@localhost/

# JWT
JWT_SECRET_KEY=your-secret-key-here

# Service
SERVICE_NAME=validation-service
ENVIRONMENT=development
ENVEOF
```

### Step 3: Initialize in Your Service

```python
from fastapi import FastAPI
from shared.database import init_database
from shared.cache import init_cache
from shared.auth import init_jwt
from shared.eventbus import init_eventbus
from shared.config import SharedSettings

settings = SharedSettings()
app = FastAPI()

@app.on_event("startup")
async def startup():
    init_database(settings.DATABASE_URL, pool_size=20)
    init_cache(settings.REDIS_URL)
    init_jwt(settings.JWT_SECRET_KEY)
    eventbus = init_eventbus(settings.RABBITMQ_URL)
    await eventbus.connect()
```

## Common Usage Patterns

### Database

```python
from shared.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

@app.get("/items")
async def get_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item))
    return result.scalars().all()
```

### Cache

```python
from shared.cache import cached

@cached(ttl=300, key_prefix="dashboard")
async def get_dashboard(tenant_id: str):
    # Expensive operation - cached for 5 minutes
    return await calculate_dashboard(tenant_id)
```

### Authentication

```python
from shared.auth import get_current_user, require_permission, Permission
from fastapi import Depends

@app.post("/exercises")
@require_permission(Permission.EXERCISE_CREATE)
async def create_exercise(
    exercise: ExerciseCreate,
    current_user: dict = Depends(get_current_user)
):
    return await create_exercise_logic(exercise)
```

### Events

```python
from shared.eventbus import EventPublisher

publisher = EventPublisher("validation")
await publisher.publish_created(
    "exercise", 
    exercise_id, 
    {"type": "tabletop"}, 
    tenant_id
)
```

### Exceptions

```python
from shared.exceptions import ResourceNotFoundException

if not exercise:
    raise ResourceNotFoundException(
        f"Exercise {id} not found",
        details={"exercise_id": id}
    )
```

### Logging

```python
from shared.utils import get_logger

logger = get_logger("validation")
logger.info("Exercise created", exercise_id=123, tenant_id="abc")
```

## Done!

Your service now has:
- Database connection pooling
- Redis caching
- JWT authentication
- Event publishing
- Structured logging
- Error handling

See README.md for full documentation.
