# Shared Utilities Module

**Type**: Library Module
**Domain**: Intelligent-Core
**Status**: Active
**Version**: 1.0.0

## Overview

The Shared module provides common utilities, clients, and helper functions used across all intelligent-core services. It ensures consistency, reduces code duplication, and provides standardized interfaces for cross-cutting concerns.

## Components

### EventBus Client

Unified event publishing and subscription interface.

```python
from shared.eventbus import get_eventbus_client, init_eventbus

# Initialize
await init_eventbus(service_name="my-service")

# Get client
eventbus = get_eventbus_client()

# Publish
await eventbus.publish('event.type', {'data': 'value'})

# Subscribe
@eventbus.subscribe('event.type')
async def handler(data):
    print(f"Received: {data}")
```

### Database Clients

Standardized database connection pooling and query interfaces.

```python
from shared.database import get_db, get_supabase_client

# PostgreSQL (via Supabase)
db = await get_db()
result = await db.table('users').select('*').execute()

# Direct Supabase client
supabase = get_supabase_client()
```

### Authentication Utilities

JWT token validation and user context management.

```python
from shared.auth import verify_token, get_current_user

# Verify token
payload = await verify_token(token)

# Get user from request
user = await get_current_user(request)
```

### Logging Framework

Structured logging with correlation IDs.

```python
from shared.logging import get_logger

logger = get_logger(__name__)
logger.info("Service started", extra={'service': 'my-service'})
```

### Configuration Management

Environment variable loading and validation.

```python
from shared.config import get_config

config = get_config()
database_url = config.DATABASE_URL
```

## Features

- **EventBus Client**: Redis-based pub/sub messaging
- **Database Clients**: Supabase PostgreSQL, connection pooling
- **Authentication**: JWT validation, user context
- **Logging**: Structured JSON logging, correlation IDs
- **Configuration**: Environment variable management
- **Metrics**: Prometheus client utilities
- **Error Handling**: Standardized exception classes

## Installation

```bash
cd intelligent-core/shared

# Install dependencies
pip install -r requirements.txt
```

## Usage

Import shared utilities in your service:

```python
# Event publishing
from shared.eventbus import get_eventbus_client

# Database access
from shared.database import get_db

# Authentication
from shared.auth import verify_token

# Logging
from shared.logging import get_logger

# Configuration
from shared.config import get_config
```

## Dependencies

### External Dependencies

- `redis` - EventBus messaging
- `supabase` - Database client
- `python-jose` - JWT handling
- `prometheus-client` - Metrics
- `python-dotenv` - Configuration

## Configuration

### Environment Variables

```bash
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Messaging
REDIS_URL=redis://localhost:6379

# Authentication
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## Development

### Running Tests

```bash
pytest tests/
pytest --cov=shared
```

### Adding New Utilities

1. Create module in `shared/`
2. Add exports to `__init__.py`
3. Update documentation
4. Add tests

## Best Practices

- Use async/await for I/O operations
- Always handle exceptions gracefully
- Log with appropriate levels
- Use correlation IDs for request tracing
- Follow type hints

## License

Proprietary - AI-Platform-ISO

---

**Last Updated**: 2025-10-09
**Maintainer**: AI Platform Team
