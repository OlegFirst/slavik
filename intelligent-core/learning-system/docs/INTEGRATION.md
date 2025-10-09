# Learning System - Integration Guide

**Version**: 1.0.0
**Last Updated**: 2025-10-09

## Integration Overview

Integration patterns and dependencies for learning-system.

## Internal Dependencies

### Database Integration

```python
from shared.database import get_db

db = await get_db()
```

### EventBus Integration

```python
from shared.eventbus import get_eventbus_client

eventbus = get_eventbus_client()
await eventbus.publish('event.type', {'data': 'value'})
```

## External Integrations

- Supabase PostgreSQL
- Redis EventBus
- Prometheus metrics

## Event Patterns

### Published Events

List of events published by this module.

### Subscribed Events

List of events this module subscribes to.

## Integration Testing

```python
import pytest

@pytest.mark.asyncio
async def test_integration():
    # Test integration
    pass
```

---

**Document Control**
- Version: 1.0.0
- Author: AI Platform Team
