# Service Wrappers Module

**Type**: Integration Module
**Domain**: Intelligent-Core
**Status**: Active
**Version**: 1.0.0

## Overview

The Wrappers module provides service adapters and integration wrappers for external systems and platform-services. It abstracts external dependencies, provides protocol translation, and implements resilience patterns (circuit breakers, retries, rate limiting).

## Components

### Notification Service Wrapper

Interface for notification-service integration.

```python
from wrappers.notification_client import NotificationClient

client = NotificationClient(base_url="http://notification-service:8020")

await client.send_email(
    to="user@example.com",
    template="daily_digest",
    data={"recommendations": [...]}
)
```

### Monitoring Service Wrapper

Interface for monitoring service integration.

```python
from wrappers.monitoring_client import MonitoringClient

client = MonitoringClient(base_url="http://monitoring:8025")

await client.log_metric(
    name="predictions_total",
    value=1,
    labels={"service": "predictive"}
)
```

### Case Library Wrapper

Interface for workflow_intelligence case library.

```python
from wrappers.case_library_client import CaseLibraryClient

client = CaseLibraryClient()

similar_cases = await client.find_similar_cases(
    organization_context={...},
    limit=50
)
```

### AI Foundation Wrapper

Interface for ai-foundation services.

```python
from wrappers.ai_foundation_client import AIFoundationClient

client = AIFoundationClient()

response = await client.generate_text(
    prompt="Analyze this workflow...",
    model="claude-3-sonnet"
)
```

## Features

- **Circuit Breaker**: Automatic failure detection and recovery
- **Retry Logic**: Exponential backoff with jitter
- **Rate Limiting**: Token bucket implementation
- **Protocol Translation**: REST, gRPC, WebSocket adapters
- **Connection Pooling**: Efficient resource management
- **Timeout Management**: Configurable timeouts per service
- **Error Handling**: Standardized exception mapping

## Installation

```bash
cd intelligent-core/wrappers

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from wrappers.notification_client import NotificationClient

# Create client with resilience patterns
client = NotificationClient(
    base_url="http://notification-service:8020",
    timeout=10.0,
    max_retries=3,
    circuit_breaker_threshold=5
)

# Use client
try:
    result = await client.send_email(...)
except ServiceUnavailable:
    # Handle service unavailability
    pass
```

### Circuit Breaker Pattern

```python
from wrappers.resilience import CircuitBreaker

breaker = CircuitBreaker(
    failure_threshold=5,
    timeout=60
)

@breaker
async def call_external_service():
    # Service call
    pass
```

### Retry Pattern

```python
from wrappers.resilience import retry

@retry(max_attempts=3, backoff_base=2)
async def call_external_service():
    # Service call with automatic retries
    pass
```

## Configuration

### Environment Variables

```bash
# Service URLs
NOTIFICATION_SERVICE_URL=http://notification-service:8020
MONITORING_SERVICE_URL=http://monitoring:8025
CASE_LIBRARY_URL=http://workflow-intelligence:8030

# Resilience Configuration
CIRCUIT_BREAKER_THRESHOLD=5
MAX_RETRIES=3
TIMEOUT_SECONDS=10
RATE_LIMIT_PER_SECOND=100
```

## Resilience Patterns

### Circuit Breaker States

- **CLOSED**: Normal operation
- **OPEN**: Failures exceeded threshold, blocking requests
- **HALF_OPEN**: Testing if service recovered

### Retry Strategy

```python
# Exponential backoff with jitter
retry_delay = min(base ** attempt + random.uniform(0, 1), max_delay)
```

### Rate Limiting

```python
# Token bucket algorithm
tokens_per_second = 100
max_burst = 200
```

## Development

### Running Tests

```bash
pytest tests/
pytest --cov=wrappers
```

### Adding New Wrapper

1. Create client class in `wrappers/`
2. Implement base interface
3. Add resilience patterns
4. Add tests
5. Update documentation

## Best Practices

- Always use timeout values
- Implement circuit breakers for external calls
- Log all external service interactions
- Use connection pooling
- Handle partial failures gracefully

## License

Proprietary - AI-Platform-ISO

---

**Last Updated**: 2025-10-09
**Maintainer**: AI Platform Team
