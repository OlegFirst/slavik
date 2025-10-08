# Shared Library

**Type**: Shared Utilities Library
**Domain**: Cross-Platform Utilities
**Status**: Active
**Version**: 2.0.0

## Overview

The Shared Library provides common utilities, interfaces, and base classes used across all platform components. It implements reusable patterns for authentication, database access, caching, event handling, audit logging, and middleware functionality. This library ensures consistency and reduces code duplication across Intelligent Core, Platform Services, and Infrastructure layers.

## Components

### Authentication & Authorization

| Component | Description | Location |
|-----------|-------------|----------|
| Auth Module | JWT handling, token validation, user context | `shared/auth/` |
| Middleware | Authentication middleware for FastAPI | `shared/middleware/` |

### Data Access

| Component | Description | Location |
|-----------|-------------|----------|
| Database | Connection pooling, query builders, ORM helpers | `shared/database/` |
| Cache | Redis integration, caching decorators | `shared/cache/` |

### Event Handling

| Component | Description | Location |
|-----------|-------------|----------|
| Event Bus | Event publishing/subscription interfaces | `shared/eventbus/` |
| History | Event history tracking and replay | `shared/history/` |

### Cross-Cutting Concerns

| Component | Description | Location |
|-----------|-------------|----------|
| Audit | Audit logging, compliance tracking | `shared/audit/` |
| Exceptions | Custom exception classes | `shared/exceptions/` |
| Config | Configuration management | `shared/config.py` |

## Installation

### As a Dependency

```python
# requirements.txt
-e ./shared
```

### Direct Import

```python
from shared.auth import get_current_user
from shared.database import get_db_session
from shared.cache import cache_result
from shared.eventbus import publish_event
```

## Usage

### Authentication

```python
from fastapi import Depends
from shared.auth import get_current_user
from shared.auth.models import User

@app.get("/api/protected")
async def protected_route(user: User = Depends(get_current_user)):
    return {"user_id": user.id, "email": user.email}
```

### Database Access

```python
from shared.database import get_db_session, execute_query

async with get_db_session() as session:
    result = await execute_query(
        session,
        "SELECT * FROM users WHERE active = true"
    )
```

### Caching

```python
from shared.cache import cache_result

@cache_result(ttl=300)  # 5 minutes
async def get_expensive_data(param: str):
    # Expensive operation
    return result
```

### Event Publishing

```python
from shared.eventbus import publish_event

await publish_event(
    event_type="user.created",
    payload={
        "user_id": user.id,
        "email": user.email
    }
)
```

### Audit Logging

```python
from shared.audit import log_audit_event

await log_audit_event(
    action="document.updated",
    user_id=current_user.id,
    resource_id=document_id,
    metadata={"changes": changes}
)
```

## Architecture

```mermaid
graph TB
    subgraph "Intelligent Core"
        IC[Core Modules]
    end
    
    subgraph "Platform Services"
        PS[Services]
    end
    
    subgraph "Infrastructure"
        Infra[Infrastructure]
    end
    
    subgraph "Shared Library"
        Auth[Authentication]
        DB[Database]
        Cache[Cache]
        Event[Event Bus]
        Audit[Audit]
    end
    
    IC --> Auth
    IC --> DB
    IC --> Cache
    IC --> Event
    
    PS --> Auth
    PS --> DB
    PS --> Event
    PS --> Audit
    
    Infra --> Auth
    Infra --> DB
```

## Testing

```bash
# Run shared library tests
pytest shared/tests/ -v

# Run with coverage
pytest shared/tests/ --cov=shared --cov-report=html
```

## Configuration

The shared library uses environment variables for configuration:

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/db

# Redis
REDIS_URL=redis://localhost:6379/0

# Authentication
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Event Bus
EVENTBUS_URL=amqp://localhost:5672/
```

## Standards Compliance

This library adheres to:

- **ISO/IEC/IEEE 26514:2022** - Software documentation
- **PEP 8** - Python code style
- **Type Hints** - Full type annotation coverage
- **Clean Architecture** - Dependency inversion principles

## Related Components

- [Intelligent Core](../intelligent-core/README.md) - Core AI modules
- [Platform Services](../platform-services/README.md) - Business services
- [Infrastructure](../infrastructure/README.md) - Infrastructure layer

## License

Proprietary - AI-Platform-ISO

---

**Last Updated**: 2025-10-08
**Maintainer**: Platform Team
