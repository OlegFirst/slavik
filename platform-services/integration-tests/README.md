# BCM Platform Integration Tests

Comprehensive integration tests for inter-service communication in the BCM platform.

## Overview

This directory contains end-to-end integration tests that verify:
- Cross-service workflows (BIA → Planning → Plans → Compliance)
- API integration and data flow
- EventBus event publishing and consumption
- Authentication and authorization across services
- Data consistency and referential integrity
- Performance benchmarks
- Error handling and resilience

## Directory Structure

```
integration-tests/
├── README.md                           # This file
├── pytest.ini                          # Pytest configuration
├── requirements.txt                    # Test dependencies
├── conftest.py                         # Shared fixtures
├── .env.test                           # Test environment variables
├── docker-compose.test.yml             # Test service configuration
├── run_integration_tests.sh            # Main test runner script
├── wait-for-services.sh                # Health check script
│
├── test_bia_to_planning_workflow.py    # BIA → Planning workflow tests
├── test_planning_to_plans_workflow.py  # Planning → Plans workflow tests
├── test_compliance_audit_workflow.py   # Compliance workflow tests
├── test_api_integration.py             # Cross-service API tests
├── test_eventbus_integration.py        # EventBus integration tests
├── test_auth_integration.py            # Auth/authz tests
├── test_resilience_integration.py      # Resilience & error handling tests
├── test_performance_integration.py     # Performance benchmarks
└── test_data_consistency.py            # Data consistency tests
```

## Prerequisites

1. **Docker & Docker Compose** - For running test services
2. **Python 3.11+** - For running tests
3. **Virtual Environment** (recommended)

## Quick Start

### 1. Setup

```bash
cd integration-tests

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run All Tests

```bash
# Make scripts executable
chmod +x run_integration_tests.sh wait-for-services.sh

# Run all integration tests
./run_integration_tests.sh
```

The script will:
1. Start all services via Docker Compose
2. Wait for services to become healthy
3. Run all integration tests
4. Provide cleanup option

### 3. Run Specific Tests

```bash
# Run only workflow tests
./run_integration_tests.sh -k workflow

# Run only API tests
./run_integration_tests.sh -k api

# Run specific test file
./run_integration_tests.sh test_bia_to_planning_workflow.py

# Run with verbose output
./run_integration_tests.sh -v -s

# Run marked tests
./run_integration_tests.sh -m "integration and not slow"
```

## Test Categories

### 1. Workflow Tests

**test_bia_to_planning_workflow.py**
- BIA completion triggers planning strategy creation
- RTO/RPO mapping from BIA to Planning
- Critical processes require higher-tier strategies
- Dependency analysis influences strategy design

**test_planning_to_plans_workflow.py**
- Strategy approval triggers plan creation
- Plans inherit strategy recovery objectives
- Resource requirements flow from strategy to plans
- Rejected strategies block plan creation

**test_compliance_audit_workflow.py**
- Audit → Gap → NC → CAPA → Improvement lifecycle
- BIA triggers compliance audits
- Plan testing through compliance
- Continuous improvement cycle

### 2. API Integration Tests

**test_api_integration.py**
- Cross-service API interactions
- Bulk operations
- Pagination consistency
- Filtering and search
- Error handling
- Health endpoints

### 3. EventBus Tests

**test_eventbus_integration.py**
- Event publishing and consuming
- Event payload structure
- Event idempotency
- Event ordering
- Cross-service subscriptions
- Tenant isolation in events

### 4. Auth/Authz Tests

**test_auth_integration.py**
- JWT token validation
- Tenant isolation (multi-tenancy)
- Role-based access control (RBAC)
- Admin privileges
- Token expiration
- Invalid token rejection

### 5. Resilience Tests

**test_resilience_integration.py**
- Graceful degradation (cache failure)
- Timeout handling
- Retry logic
- Concurrent request handling
- Rate limiting
- Database connection pooling

### 6. Performance Tests

**test_performance_integration.py**
- API response time benchmarks (< 200ms p95)
- Bulk operation performance (100+ items)
- Concurrent user simulation (50 users)
- Cache hit rate (> 80%)
- Dashboard load performance

### 7. Data Consistency Tests

**test_data_consistency.py**
- Referential integrity
- Data validation consistency
- Status workflow consistency
- Timestamp management
- Unique constraint enforcement
- Cascade update propagation

## Test Markers

Tests are marked for selective execution:

- `@pytest.mark.integration` - All integration tests
- `@pytest.mark.workflow` - End-to-end workflow tests
- `@pytest.mark.api` - API integration tests
- `@pytest.mark.eventbus` - EventBus tests
- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.resilience` - Resilience tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.slow` - Slow-running tests (> 5s)
- `@pytest.mark.requires_docker` - Requires Docker

### Run by Marker

```bash
# Run only workflow tests
pytest -m workflow

# Run all except slow tests
pytest -m "integration and not slow"

# Run auth and api tests
pytest -m "auth or api"
```

## Environment Configuration

Edit `.env.test` to customize:

```bash
# Database
POSTGRES_DB=bcm_test
POSTGRES_USER=bcm_test_user
POSTGRES_PASSWORD=bcm_test_password

# JWT
JWT_SECRET=test-secret-DO-NOT-USE-IN-PRODUCTION
JWT_ALGORITHM=HS256

# Service URLs (Docker network)
BIA_SERVICE_URL=http://bia-service-test:8012
PLANNING_SERVICE_URL=http://planning-service-test:8011
PLANS_SERVICE_URL=http://plans-service-test:8023
COMPLIANCE_SERVICE_URL=http://compliance-service-test:8014

# Timeouts
TEST_TIMEOUT=120
HEALTH_CHECK_TIMEOUT=60
```

## Manual Service Management

### Start services only

```bash
docker-compose -f docker-compose.test.yml up -d
```

### Check service health

```bash
./wait-for-services.sh
```

### View service logs

```bash
docker-compose -f docker-compose.test.yml logs -f
```

### Stop services

```bash
docker-compose -f docker-compose.test.yml down -v
```

## Expected Test Execution Time

- **All tests**: ~5-10 minutes
- **Workflow tests**: ~2-3 minutes
- **API tests**: ~1-2 minutes
- **Performance tests**: ~3-5 minutes (marked as slow)

## Troubleshooting

### Services won't start

```bash
# Check Docker status
docker info

# View service logs
docker-compose -f docker-compose.test.yml logs

# Restart services
docker-compose -f docker-compose.test.yml restart
```

### Tests failing due to timeouts

Increase timeout in `.env.test`:
```bash
TEST_TIMEOUT=180
HEALTH_CHECK_TIMEOUT=90
```

### Port conflicts

If default ports are in use, modify `docker-compose.test.yml` to use different ports.

### Database connection issues

```bash
# Reset database
docker-compose -f docker-compose.test.yml down -v
docker-compose -f docker-compose.test.yml up -d postgres-test
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  integration-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd integration-tests
          pip install -r requirements.txt

      - name: Run integration tests
        run: |
          cd integration-tests
          chmod +x run_integration_tests.sh
          ./run_integration_tests.sh -v --tb=short

      - name: Cleanup
        if: always()
        run: |
          cd integration-tests
          docker-compose -f docker-compose.test.yml down -v
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Use `cleanup_test_data` fixture for automatic cleanup
3. **Assertions**: Use descriptive assertion messages
4. **Markers**: Tag tests appropriately for selective execution
5. **Performance**: Mark slow tests with `@pytest.mark.slow`
6. **Retries**: Use `retry_async` fixture for flaky operations

## Contributing

When adding new integration tests:

1. Use existing fixtures from `conftest.py`
2. Add appropriate markers
3. Include cleanup via `cleanup_test_data` fixture
4. Document test purpose in docstring
5. Keep tests focused and independent
6. Update this README with new test categories

## Test Coverage

Current coverage by service:

| Service     | Workflows | API | Events | Auth | Perf | Total Tests |
|-------------|-----------|-----|--------|------|------|-------------|
| BIA         | ✅ 5      | ✅ 6 | ✅ 4   | ✅ 3 | ✅ 4 | ~22         |
| Planning    | ✅ 7      | ✅ 5 | ✅ 3   | ✅ 3 | ✅ 3 | ~21         |
| Plans       | ✅ 7      | ✅ 4 | ✅ 2   | ✅ 2 | ✅ 2 | ~17         |
| Compliance  | ✅ 6      | ✅ 4 | ✅ 2   | ✅ 2 | ✅ 1 | ~15         |

**Total Integration Tests**: ~75+

## Support

For issues or questions:
1. Check service logs: `docker-compose -f docker-compose.test.yml logs`
2. Verify service health: `curl http://localhost:8012/health`
3. Review test output with `-v -s` flags
4. Check `.env.test` configuration
