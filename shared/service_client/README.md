# Service Client Library

Unified API client for microservices communication across the AI-Powered BCM Platform.

## Features

- **Service Discovery**: Automatic service registry with configuration
- **Health Monitoring**: Track service availability and health status
- **Unified Interface**: Single client for all microservice communication
- **Error Handling**: Built-in error handling and retry logic
- **Authentication**: Automatic API key handling
- **Multi-method**: Support for GET, POST, PUT, DELETE
- **File Upload**: Built-in file upload support

## Architecture

```
shared/service_client/
├── __init__.py         # Public API
├── config.py           # ServiceConfig dataclass
├── health.py           # ServiceHealthMonitor
├── registry.py         # ServiceRegistry (service discovery)
├── client.py           # ServiceClient (main client)
└── README.md          # This file
```

## Installation

```bash
# Add to requirements.txt
httpx>=0.25.0

# Or install directly
pip install httpx
```

## Quick Start

### Basic Usage

```python
from shared.service_client import ServiceRegistry, ServiceClient

# Initialize
registry = ServiceRegistry()  # Loads from environment or defaults
client = ServiceClient(registry)

# Make requests
result = await client.request(
    service_type='predictive',
    endpoint='/api/v1/predictions/journey/org_123',
    method='GET'
)
```

### Health Monitoring

```python
# Check health of all services
health_status = await client.check_all_services_health()
print(health_status)
# {'predictive': True, 'collective': True, 'community_intelligence': False}

# Get detailed health status
detailed_status = client.get_health_status()
# {
#   'predictive': {
#       'status': 'healthy',
#       'last_check': '2025-10-06T12:00:00',
#       'response_code': 200
#   }
# }

# Get unhealthy services
unhealthy = client.get_unhealthy_services()
# ['community_intelligence']
```

### Custom Service Configuration

```python
from shared.service_client import ServiceConfig, ServiceRegistry, ServiceClient

# Define custom services
custom_configs = [
    ServiceConfig(
        name='My Custom Service',
        service_type='my_service',
        base_url='http://my-service.com',
        port=9000,
        api_key='secret_key',
        timeout=60
    )
]

registry = ServiceRegistry(custom_configs=custom_configs)
client = ServiceClient(registry)

# Use custom service
result = await client.request('my_service', '/api/data')
```

## Environment Variables

Configure services via environment variables:

```bash
# Predictive Service
PREDICTIVE_URL=http://localhost
PREDICTIVE_PORT=8031

# Collective Agents
COLLECTIVE_URL=http://localhost
COLLECTIVE_PORT=8032

# Community Intelligence
COMMUNITY_URL=http://localhost
COMMUNITY_PORT=8030

# Living Documentation
LIVING_DOCS_URL=http://localhost
LIVING_DOCS_PORT=8034

# Simulation Service
SIMULATION_URL=http://localhost
SIMULATION_PORT=8031
```

## Available Services

Default registered services:

| Service Type | Name | Default Port |
|-------------|------|--------------|
| `predictive` | Predictive Journey | 8031 |
| `collective` | Collective Agents | 8032 |
| `community_intelligence` | Community Intelligence | 8030 |
| `living_docs` | Living Documentation | 8034 |
| `simulation` | Simulation Service | 8031 |

## Advanced Usage

### Custom Headers

```python
result = await client.request(
    'predictive',
    '/api/v1/predictions',
    headers={'X-Custom-Header': 'value'}
)
```

### Query Parameters

```python
result = await client.request(
    'predictive',
    '/api/v1/search',
    params={'query': 'ISO 22301', 'limit': '10'}
)
```

### File Upload

```python
with open('document.pdf', 'rb') as f:
    result = await client.request(
        'living_docs',
        '/api/v1/documents/upload',
        method='POST',
        files={'file': ('document.pdf', f, 'application/pdf')},
        data={'category': 'compliance'}
    )
```

### Error Handling

```python
import httpx

try:
    result = await client.request('predictive', '/api/endpoint')
except ValueError as e:
    # Service not registered
    print(f"Service not found: {e}")
except httpx.HTTPError as e:
    # HTTP error (4xx, 5xx)
    print(f"Request failed: {e}")
```

## Convenience Methods

Pre-built methods for common operations:

```python
# Journey prediction
prediction = await client.get_journey_prediction(org_id='org_123')

# Create collective agent
agent = await client.create_collective_agent(
    problem="Stuck on BIA supply chain analysis",
    context={'industry': 'healthcare', 'size': 200}
)

# Submit case contribution
case = await client.submit_case_contribution({
    'module': 'bia',
    'success_story': '...',
    'metrics': {...}
})
```

## Integration Examples

### In Workflow Intelligence

```python
# workflow_intelligence/ai/context_advisor.py
from shared.service_client import ServiceRegistry, ServiceClient

class ContextAdvisor:
    def __init__(self):
        registry = ServiceRegistry()
        self.client = ServiceClient(registry)

    async def get_journey_context(self, org_id: str):
        # Get predictions from Predictive service
        predictions = await self.client.get_journey_prediction(org_id)

        # Use predictions for context building
        return self._build_context(predictions)
```

### In Expertise Center

```python
# expertise-center/domains/bcm/specialists/bcm_advisor.py
from shared.service_client import ServiceRegistry, ServiceClient

class BCMAdvisor:
    def __init__(self):
        registry = ServiceRegistry()
        self.client = ServiceClient(registry)

    async def analyze_with_collective_wisdom(self, problem: str):
        # Create collective agent for stuck problems
        agent = await self.client.create_collective_agent(
            problem=problem,
            context=self.context
        )

        return agent['insights']
```

## Testing

```python
# tests/test_service_client.py
import pytest
from shared.service_client import ServiceRegistry, ServiceClient, ServiceConfig

@pytest.mark.asyncio
async def test_service_health():
    registry = ServiceRegistry()
    client = ServiceClient(registry)

    health = await client.check_all_services_health()
    assert isinstance(health, dict)
    assert 'predictive' in health

@pytest.mark.asyncio
async def test_custom_service():
    config = ServiceConfig(
        name='Test Service',
        service_type='test',
        base_url='http://localhost',
        port=9999
    )

    registry = ServiceRegistry(custom_configs=[config])
    client = ServiceClient(registry)

    assert client.registry.get_service('test') == config
```

## Original Source

Extracted and adapted from:
- **Source**: Odoo `bcm_ai_control/bcm_base/models/bcm_ai_service.py`
- **Extracted**: 2025-10-05
- **Adapted for**: AI-Powered BCM Platform v2.0

## License

Part of the AI-Powered BCM Platform
