# Tests

**Type**: Testing Suite
**Domain**: Quality Assurance
**Status**: Active
**Version**: 2.0.0

## Overview

The Tests directory provides comprehensive testing infrastructure for the AI-Platform-ISO system. It implements unit tests, integration tests, end-to-end tests, load tests, and test fixtures. This suite ensures platform quality, reliability, and compliance with functional requirements.

## Test Structure

```
tests/
├── unit/              # Unit tests for individual components
├── integration/       # Integration tests across services
│   └── eventbus/      # EventBus choreography tests
├── e2e/              # End-to-end user workflow tests
├── load/             # Performance and load tests
├── security/         # Security and vulnerability tests
│   └── owasp/        # OWASP Top 10 2021 coverage
├── fixtures/         # Test data and fixtures
├── generated/        # Auto-generated test artifacts
├── conftest.py       # pytest configuration and fixtures (30+ fixtures)
└── pytest.ini        # pytest settings
```

## Test Categories

### Unit Tests

| Category | Description | Location |
|----------|-------------|----------|
| Core Modules | Tests for intelligent-core modules | `unit/intelligent-core/` |
| Services | Tests for platform-services | `unit/platform-services/` |
| Infrastructure | Tests for infrastructure components | `unit/infrastructure/` |
| Shared Library | Tests for shared utilities | `unit/shared/` |

### Integration Tests

| Category | Description | Location |
|----------|-------------|----------|
| Service-to-Service | Cross-service communication tests | `integration/services/` |
| Database | Database integration tests | `integration/database/` |
| Event Bus | Event-driven workflow tests | `integration/eventbus/` |

### End-to-End Tests

| Category | Description | Location |
|----------|-------------|----------|
| User Workflows | Complete user journey tests | `e2e/workflows/` |
| API Tests | Full API endpoint tests | `e2e/api/` |

### Load Tests

| Category | Description | Location |
|----------|-------------|----------|
| Performance | Performance benchmarking | `load/performance/` |
| Stress Tests | System stress testing | `load/stress/` |

### Security Tests

| Category | Description | Location |
|----------|-------------|----------|
| General Security | JWT, RBAC, sessions, rate limiting | `security/` |
| OWASP Top 10 | OWASP Top 10 2021 coverage (25+ tests) | `security/owasp/` |
| EventBus Security | Event-driven choreography & security | `integration/eventbus/` |

## Running Tests

### All Tests

```bash
# Run entire test suite
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=. --cov-report=html --cov-report=term
```

### Category-Specific Tests

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# E2E tests only
pytest tests/e2e/ -v

# Load tests only
pytest tests/load/ -v

# Security tests only
pytest tests/security/ -v

# OWASP Top 10 only
pytest tests/security/owasp/ -v
```

### Specific Module Tests

```bash
# Test specific module
pytest tests/unit/intelligent-core/test_ai_foundation.py -v

# Test specific service
pytest tests/unit/platform-services/test_bia_service.py -v
```

### Test Markers

```bash
# Run only fast tests
pytest tests/ -m fast

# Run only slow tests
pytest tests/ -m slow

# Skip integration tests
pytest tests/ -m "not integration"

# Run only critical tests
pytest tests/ -m critical
```

## Test Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    fast: Fast-running tests
    slow: Slow-running tests
    integration: Integration tests
    e2e: End-to-end tests
    critical: Critical path tests
    security: Security-focused tests
    owasp: OWASP Top 10 coverage tests
    require_eventbus: Requires EventBus connection
```

### conftest.py

Provides 40+ shared fixtures including:

**Database & Infrastructure:**
```python
@pytest.fixture
async def db_session():
    """Test database session with auto-rollback"""

@pytest.fixture
async def event_bus():
    """Mock EventBus for testing"""

@pytest.fixture
async def redis_client():
    """Fake Redis client (in-memory)"""
```

**Security Fixtures:**
```python
@pytest.fixture
def auth_user():
    """Authenticated user with JWT token"""

@pytest.fixture
def mock_jwt_manager():
    """JWT token manager for testing"""

@pytest.fixture
def mock_rbac_manager():
    """RBAC authorization manager"""

@pytest.fixture
def password_validator():
    """Password complexity validator"""

@pytest.fixture
def ssrf_validator():
    """SSRF prevention validator"""

@pytest.fixture
def rate_limiter():
    """API rate limiter"""

@pytest.fixture
def security_logger():
    """Security event logger"""
```

**AI Foundation Mocks:**
```python
@pytest.fixture
def mock_llm_client():
    """Mock LLM client with deterministic responses"""

@pytest.fixture
def mock_rag_pipeline():
    """Mock RAG pipeline with sample documents"""
```

## Test Coverage Requirements

| Component Type | Minimum Coverage | Current Status |
|----------------|------------------|----------------|
| Core Modules | 80% | ✅ |
| Platform Services | 80% | ✅ |
| Infrastructure | 75% | ✅ |
| Shared Library | 85% | ✅ |
| Security Tests | 90% | ✅ |
| OWASP Top 10 | 95% | ✅ |

## CI/CD Integration

Tests run automatically on:

- Pull requests
- Commits to main branch
- Nightly builds
- Release candidates

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: pytest tests/ --cov --cov-report=xml
```

## Test Data Management

### Fixtures

Test fixtures are stored in `tests/fixtures/`:

```
fixtures/
├── users.json          # Test user data
├── organizations.json  # Test organization data
├── workflows.json      # Test workflow definitions
└── documents.json      # Test documents
```

### Generated Artifacts

Auto-generated test artifacts are stored in `tests/generated/`:

- Test reports
- Coverage reports
- Performance metrics
- Screenshot captures (E2E tests)

## Writing Tests

### Unit Test Example

```python
import pytest
from intelligent-core.ai_foundation import LLMRouter

@pytest.mark.asyncio
async def test_llm_router_initialization():
    """Test LLM router initializes correctly"""
    router = LLMRouter()
    assert router is not None
    assert router.strategy == "least_latency"

@pytest.mark.asyncio
async def test_llm_router_routes_request():
    """Test LLM router routes requests"""
    router = LLMRouter()
    response = await router.route(
        prompt="Test prompt",
        strategy="least_latency"
    )
    assert response is not None
```

### Integration Test Example

```python
import pytest
from httpx import AsyncClient

@pytest.mark.integration
@pytest.mark.asyncio
async def test_bia_service_workflow(db_session, auth_user):
    """Test complete BIA workflow"""
    async with AsyncClient(base_url="http://test") as client:
        # Start BIA
        response = await client.post(
            "/api/v1/bia/start",
            headers={"Authorization": f"Bearer {auth_user.token}"}
        )
        assert response.status_code == 200
        
        # Verify workflow created
        bia_id = response.json()["bia_id"]
        assert bia_id is not None
```

## Performance Testing

### Load Test Example

```python
from locust import HttpUser, task, between

class BIAServiceUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def create_bia(self):
        self.client.post("/api/v1/bia/start", json={
            "organization_id": "test_org"
        })
```

## Test Reports

Test reports are generated in:

- `tests/generated/reports/` - HTML coverage reports
- `tests/generated/junit/` - JUnit XML reports
- `tests/generated/allure/` - Allure reports (if enabled)

## Standards Compliance

This testing suite adheres to:

- **ISO/IEC/IEEE 29119** - Software testing standards
- **ISO/IEC 25010** - Software quality model
- **OWASP Top 10 2021** - Security vulnerability coverage (100%)
- **ISO 27001** - Information security (partial: A.9, A.10, A.12)
- **pytest best practices** - Modern Python testing

## Related Components

- [Intelligent Core](../intelligent-core/README.md) - Core modules under test
- [Platform Services](../platform-services/README.md) - Services under test
- [Infrastructure](../infrastructure/README.md) - Infrastructure under test
- [Shared Library](../shared/README.md) - Shared utilities under test

## License

Proprietary - AI-Platform-ISO

## Documentation

- **Main Config:** `/tests/TEST_INFRASTRUCTURE_CONFIG.yaml`
- **Security Tests Report:** `/tests/SECURITY_TESTS_COMPLETE.md`
- **Test Management:** `/tests/PROJECT_AGENT_TEST_MANAGEMENT.md`
- **Security Suite:** `/tests/security/README.md`
- **OWASP Coverage:** `/tests/security/owasp/README.md`

## API Management

Tests managed by **Project Agent (Port 8060)**:

```bash
# Run tests via API
curl -X POST http://localhost:8060/api/tests/run \
  -H "Content-Type: application/json" \
  -d '{"suite": "security", "coverage": true}'

# Get coverage report
curl http://localhost:8060/api/tests/coverage | jq

# Generate missing tests
curl -X POST http://localhost:8060/api/tests/generate \
  -d '{"component": "bia-service", "coverage_threshold": 85}'
```

---

**Last Updated**: 2025-10-11
**Maintainer**: Project Agent (Port 8060)
**Version**: 2.0.0
