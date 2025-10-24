# AI-Platform-ISO Testing Guide

**Version**: 3.0.0
**Last Updated**: 2025-10-21
**Status**: Production Ready

## Table of Contents

1. [Overview](#overview)
2. [Test Infrastructure](#test-infrastructure)
3. [Running Tests](#running-tests)
4. [Writing Tests](#writing-tests)
5. [Test Categories](#test-categories)
6. [Coverage Requirements](#coverage-requirements)
7. [CI/CD Integration](#cicd-integration)
8. [Best Practices](#best-practices)

---

## Overview

This guide provides comprehensive instructions for testing the AI-Platform-ISO system. Our testing strategy ensures:

- **High Quality**: 80%+ code coverage across all components
- **Reliability**: Automated testing in CI/CD pipelines
- **Security**: OWASP Top 10 coverage and security testing
- **Performance**: Load and stress testing for scalability
- **Compliance**: ISO 22301, ISO 27001 compliance testing

### Testing Philosophy

We follow a **test pyramid approach**:

```
        /\
       /  \      E2E Tests (10%)
      /    \     - Complete user journeys
     /------\    - Cross-system workflows
    /        \
   /          \  Integration Tests (30%)
  /            \ - Service-to-service communication
 /--------------\ - Database integration
/                \ - EventBus workflows
/------------------\
   Unit Tests (60%)
   - Individual functions
   - Class methods
   - Business logic
```

---

## Test Infrastructure

### Directory Structure

```
tests/
├── conftest.py                           # Global fixtures (40+ fixtures)
├── pytest.ini                            # pytest configuration
├── requirements-test.txt                 # Test dependencies
├── run_tests.sh                          # Test execution script
├── TESTING_GUIDE.md                      # This file
│
├── unit/                                 # Unit tests (fast, isolated)
│   ├── infrastructure/                   # Infrastructure tests
│   │   ├── eventbus/                     # EventBus tests
│   │   ├── saga-engine/                  # Saga pattern tests
│   │   └── cqrs/                         # CQRS tests
│   ├── intelligent-core/                 # Intelligent core tests
│   │   ├── ai-foundation/                # AI foundation tests
│   │   ├── expertise-center/             # AI experts tests
│   │   └── workflow-intelligence/        # Workflow tests
│   └── platform-services/                # Platform services tests
│       ├── bia-service/                  # BIA service tests
│       ├── risk-service/                 # Risk service tests
│       ├── planning-service/             # Planning tests
│       └── response-service/             # Response tests
│
├── integration/                          # Integration tests
│   ├── test_platform_integration_comprehensive.py
│   ├── test_service_workflows.py
│   ├── test_eventbus_choreography.py
│   └── test_database_integration.py
│
├── e2e/                                  # End-to-end tests
│   ├── test_bcm_workflows.py             # Complete BCM workflows
│   └── test_incident_response.py         # Incident response flows
│
├── performance/                          # Performance tests
│   └── test_load_scenarios.py
│
├── security/                             # Security tests
│   ├── test_security_suite.py            # General security
│   └── owasp/                            # OWASP Top 10
│       └── test_owasp_top10.py
│
└── fixtures/                             # Test data
    ├── sample_data.py                    # Sample data generators
    └── mock_services.py                  # Mock service implementations
```

### Key Files

**conftest.py**: Provides 40+ shared fixtures including:
- Database fixtures (db_session, test_db_engine)
- Cache fixtures (redis_client, mock_cache)
- EventBus fixtures (mock_eventbus)
- AI Foundation mocks (mock_llm_client, mock_rag_pipeline)
- Security fixtures (auth_user, mock_jwt_manager, mock_rbac_manager)
- Test data generators (sample_workflow_context, sample_organization)

**pytest.ini**: Configuration for:
- Test discovery patterns
- Async test support
- Test markers (unit, integration, e2e, slow, security)
- Coverage configuration
- Timeout settings

---

## Running Tests

### Quick Start

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov --cov-report=html --cov-report=term

# Run specific test category
pytest tests/unit/ -v                    # Unit tests only
pytest tests/integration/ -v             # Integration tests only
pytest tests/e2e/ -v                     # E2E tests only

# Run tests by marker
pytest tests/ -m unit                    # Fast unit tests
pytest tests/ -m integration             # Integration tests
pytest tests/ -m "not slow"              # Skip slow tests
pytest tests/ -m security                # Security tests only

# Run specific test file
pytest tests/integration/test_platform_integration_comprehensive.py -v

# Run specific test function
pytest tests/unit/infrastructure/eventbus/test_intelligent_router.py::test_event_routing -v
```

### Coverage Reports

```bash
# Generate HTML coverage report
pytest tests/ --cov --cov-report=html

# View in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Generate terminal coverage report
pytest tests/ --cov --cov-report=term-missing

# Generate XML coverage report (for CI/CD)
pytest tests/ --cov --cov-report=xml
```

### Parallel Test Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest tests/ -n 4 -v

# Auto-detect CPU count
pytest tests/ -n auto -v
```

### Continuous Testing

```bash
# Install pytest-watch
pip install pytest-watch

# Watch for changes and re-run tests
ptw tests/ -- -v
```

---

## Writing Tests

### Unit Test Example

```python
import pytest
from platform_services.bia_service.business_logic import BIAAnalyzer


@pytest.mark.unit
@pytest.mark.asyncio
async def test_bia_analyzer_initialization():
    """Test BIA analyzer initializes correctly"""
    analyzer = BIAAnalyzer()
    assert analyzer is not None
    assert analyzer.default_rto_hours == 24


@pytest.mark.unit
@pytest.mark.asyncio
async def test_bia_analyzer_calculates_impact(mock_llm_client):
    """Test BIA analyzer calculates business impact"""
    analyzer = BIAAnalyzer(llm_client=mock_llm_client)

    process = {
        "name": "Payment Processing",
        "revenue_per_hour": 10000,
        "employees_affected": 50
    }

    impact = await analyzer.calculate_impact(process)

    assert impact["financial_impact"] > 0
    assert impact["operational_impact"] is not None
    assert "recommendation" in impact
```

### Integration Test Example

```python
import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.requires_db
async def test_bia_creation_workflow(db_session, auth_user, mock_eventbus):
    """Test complete BIA creation workflow"""

    # Step 1: Create BIA via API
    async with AsyncClient(base_url="http://test") as client:
        response = await client.post(
            "/api/v1/bia/create",
            headers={"Authorization": f"Bearer {auth_user['token']}"},
            json={
                "organization_id": "org-001",
                "scope": "IT Operations"
            }
        )

    assert response.status_code == 201
    bia_id = response.json()["bia_id"]

    # Step 2: Verify database record
    from platform_services.bia_service.models import BIA
    bia = await db_session.get(BIA, bia_id)
    assert bia is not None
    assert bia.scope == "IT Operations"

    # Step 3: Verify event published
    mock_eventbus.publish.assert_called_with(
        "bia.created",
        {"bia_id": bia_id, "organization_id": "org-001"}
    )
```

### E2E Test Example

```python
import pytest


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.slow
async def test_complete_bcm_program_creation(
    db_session,
    auth_user,
    mock_eventbus,
    mock_temporal_client
):
    """Test complete BCM program creation from start to finish"""

    # Step 1: Initiate BCM program
    program_id = await create_bcm_program(auth_user)

    # Step 2: Complete BIA
    bia_id = await create_and_complete_bia(program_id, auth_user)
    assert bia_id is not None

    # Step 3: Assess risks
    risk_ids = await assess_program_risks(program_id, auth_user)
    assert len(risk_ids) > 0

    # Step 4: Create plans
    plan_ids = await create_continuity_plans(program_id, risk_ids, auth_user)
    assert len(plan_ids) > 0

    # Step 5: Submit for governance approval
    approval_status = await submit_for_approval(program_id, auth_user)
    assert approval_status == "approved"

    # Step 6: Activate program
    activation_result = await activate_program(program_id, auth_user)
    assert activation_result["status"] == "active"
```

### Security Test Example

```python
import pytest


@pytest.mark.security
@pytest.mark.asyncio
async def test_sql_injection_prevention(db_session, sql_injection_patterns):
    """Test SQL injection prevention in search queries"""

    from platform_services.bia_service.repository import BIARepository
    repo = BIARepository(db_session)

    for pattern in sql_injection_patterns:
        # Attempt injection via search
        try:
            results = await repo.search_bia(search_term=pattern)
            # Should return safely, not execute injection
            assert isinstance(results, list)
        except Exception as e:
            # Should raise safe error, not SQL error
            assert "SQL syntax" not in str(e)
            assert "DROP TABLE" not in str(e)


@pytest.mark.security
@pytest.mark.asyncio
async def test_authorization_enforcement(auth_user, mock_rbac_manager):
    """Test RBAC authorization is enforced"""

    # User with limited permissions
    limited_user = {"role": "auditor"}

    # Should be able to read
    assert mock_rbac_manager.can_user_perform("auditor", "workflows.read")

    # Should NOT be able to delete
    assert not mock_rbac_manager.can_user_perform("auditor", "workflows.delete")
```

---

## Test Categories

### Unit Tests (60% of test suite)

**Purpose**: Test individual functions, classes, and methods in isolation

**Characteristics**:
- Fast execution (< 100ms per test)
- No external dependencies
- Mock all I/O operations
- High coverage (85%+)

**Markers**: `@pytest.mark.unit`

**Example Coverage**:
- Business logic functions
- Data transformations
- Validation logic
- Utility functions

### Integration Tests (30% of test suite)

**Purpose**: Test interaction between components

**Characteristics**:
- Moderate execution time (< 5s per test)
- Uses real database (test DB)
- Tests EventBus communication
- Tests API endpoints

**Markers**: `@pytest.mark.integration`

**Example Coverage**:
- Service-to-service communication
- Database operations
- EventBus choreography
- CQRS patterns
- API endpoint integration

### E2E Tests (10% of test suite)

**Purpose**: Test complete user journeys

**Characteristics**:
- Slower execution (5-30s per test)
- Tests full workflows
- Multiple services involved
- Simulates real user scenarios

**Markers**: `@pytest.mark.e2e`

**Example Coverage**:
- BCM program creation
- Incident response workflow
- Plan approval process
- Compliance audit workflow

### Security Tests

**Purpose**: Ensure system security

**Markers**: `@pytest.mark.security`

**Coverage**:
- OWASP Top 10 (2021)
- SQL injection prevention
- XSS prevention
- Authentication & Authorization
- Session management
- Rate limiting
- Input validation

### Performance Tests

**Purpose**: Ensure system scalability

**Markers**: `@pytest.mark.performance`, `@pytest.mark.slow`

**Coverage**:
- Load testing
- Stress testing
- Concurrency testing
- Cache performance

---

## Coverage Requirements

| Component | Minimum Coverage | Target Coverage | Current Status |
|-----------|-----------------|-----------------|----------------|
| Infrastructure | 75% | 85% | ✅ 78% |
| Intelligent Core | 80% | 90% | ✅ 82% |
| Platform Services | 80% | 90% | ✅ 85% |
| Security Components | 90% | 95% | ✅ 92% |
| Overall Platform | 80% | 88% | ✅ 83% |

### Coverage Goals by Service

**BIA Service**: 85%+
**Risk Service**: 85%+
**Planning Service**: 85%+
**Response Service**: 80%+
**Governance Service**: 80%+
**EventBus**: 90%+
**Saga Engine**: 85%+

---

## CI/CD Integration

### GitHub Actions Integration

Tests run automatically on:
- Pull requests
- Commits to main branch
- Nightly builds
- Release tags

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Required Checks

Before merging:
- [ ] All tests pass
- [ ] Coverage ≥ 80%
- [ ] No security vulnerabilities
- [ ] No linting errors

---

## Best Practices

### 1. Test Naming

```python
# Good - descriptive test names
def test_bia_creation_publishes_event_to_eventbus():
    pass

def test_risk_assessment_fails_with_invalid_severity():
    pass

# Bad - vague test names
def test_bia():
    pass

def test_feature():
    pass
```

### 2. Arrange-Act-Assert Pattern

```python
async def test_bia_analyzer_calculates_impact():
    # Arrange - set up test data
    analyzer = BIAAnalyzer()
    process = {"name": "Payment Processing", "revenue": 10000}

    # Act - perform the action
    result = await analyzer.calculate_impact(process)

    # Assert - verify the result
    assert result["impact_level"] == "high"
    assert result["estimated_loss"] > 0
```

### 3. Use Fixtures for Common Setup

```python
# Instead of repeating setup
async def test_create_bia():
    db = await create_db_session()
    user = await create_test_user(db)
    # ... test code
    await cleanup_db(db)

# Use fixtures
@pytest.mark.asyncio
async def test_create_bia(db_session, auth_user):
    # Test code - setup handled by fixtures
    pass
```

### 4. Test One Thing Per Test

```python
# Good - focused test
async def test_bia_creation_returns_valid_id():
    bia_id = await create_bia()
    assert bia_id is not None
    assert isinstance(bia_id, str)

# Bad - testing multiple things
async def test_bia_workflow():
    bia_id = await create_bia()
    assert bia_id is not None

    risks = await assess_risks(bia_id)
    assert len(risks) > 0

    plan = await create_plan(bia_id)
    assert plan is not None
```

### 5. Mock External Dependencies

```python
@pytest.mark.asyncio
async def test_llm_analysis(mock_llm_client):
    """Test LLM analysis without calling real API"""
    analyzer = BIAAnalyzer(llm_client=mock_llm_client)

    result = await analyzer.analyze_with_ai("Test data")

    # Verify mock was called
    mock_llm_client.generate.assert_called_once()
```

### 6. Test Error Cases

```python
async def test_bia_creation_fails_with_invalid_data():
    """Test BIA creation handles invalid data gracefully"""
    with pytest.raises(ValidationError) as exc:
        await create_bia(organization_id=None)

    assert "organization_id is required" in str(exc.value)
```

### 7. Use Parametrize for Multiple Cases

```python
@pytest.mark.parametrize("severity,expected_priority", [
    ("critical", "urgent"),
    ("high", "high"),
    ("medium", "normal"),
    ("low", "low")
])
async def test_risk_priority_mapping(severity, expected_priority):
    priority = map_severity_to_priority(severity)
    assert priority == expected_priority
```

### 8. Clean Test Data

```python
@pytest.fixture
async def clean_database(db_session):
    """Ensure clean state for each test"""
    yield
    # Cleanup after test
    await db_session.rollback()
```

---

## Troubleshooting

### Tests Fail Locally But Pass in CI

1. Check environment variables
2. Verify database state
3. Check for hardcoded paths
4. Ensure consistent dependencies

### Flaky Tests

1. Add explicit waits for async operations
2. Mock time-dependent code
3. Avoid shared state between tests
4. Use database transactions with rollback

### Slow Test Suite

1. Run only changed tests: `pytest --lf`
2. Use parallel execution: `pytest -n auto`
3. Profile slow tests: `pytest --durations=10`
4. Move slow tests to `@pytest.mark.slow`

---

## Resources

- **pytest Documentation**: https://docs.pytest.org/
- **pytest-asyncio**: https://github.com/pytest-dev/pytest-asyncio
- **Coverage.py**: https://coverage.readthedocs.io/
- **OWASP Testing Guide**: https://owasp.org/www-project-web-security-testing-guide/

---

## Support

For testing questions or issues:

1. Check this guide
2. Review existing tests for examples
3. Consult team testing standards
4. Create issue in project tracker

---

**Last Updated**: 2025-10-21
**Version**: 3.0.0
**Maintained By**: Platform Team
