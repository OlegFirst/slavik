# Centralized Test Structure

All tests have been consolidated into `/tests` directory for better organization and easier test execution.

## 📁 Directory Structure

```
tests/
├── conftest.py                    # Global fixtures and pytest configuration
├── pytest.ini                      # Pytest settings and markers
├── requirements-test.txt           # Test dependencies
├── run_tests.sh                    # Bash test runner
├── run_tests.py                    # Python test runner
│
├── unit/                           # Unit tests (fast, isolated)
│   ├── platform-services/
│   │   ├── bia-service/
│   │   ├── risk-service/
│   │   ├── compliance-service/
│   │   ├── governance-service/
│   │   ├── learning-service/
│   │   ├── planning-service/
│   │   ├── plans-service/
│   │   ├── response-service/
│   │   └── digital-twin/
│   │
│   ├── intelligent-core/
│   │   ├── workflow-intelligence/
│   │   ├── ai-orchestration/
│   │   ├── expertise-center/
│   │   ├── system-bcm/
│   │   ├── coordination-center/
│   │   ├── ai-foundation/
│   │   ├── community-intelligence/
│   │   └── workflow-engine/
│   │
│   └── infrastructure/
│       ├── eventbus/
│       ├── balancer-service/
│       ├── api-gateway/
│       ├── mio-manager/
│       └── project-agent/
│
├── integration/                    # Integration tests (multiple components)
│   ├── test_platform_services_integration.py
│   └── test_intelligent_core_integration.py
│
├── e2e/                           # End-to-end tests (full workflows)
│   └── test_full_bcm_workflow.py
│
├── performance/                   # Performance and load tests
│
└── fixtures/                      # Shared test data and fixtures
```

## 🚀 Running Tests

### Using Bash Script (Recommended)

```bash
# Make executable (first time only)
chmod +x tests/run_tests.sh

# Run all tests
./tests/run_tests.sh all

# Run unit tests only
./tests/run_tests.sh unit

# Run integration tests
./tests/run_tests.sh integration

# Run e2e tests
./tests/run_tests.sh e2e

# Run platform services tests
./tests/run_tests.sh platform

# Run intelligent core tests
./tests/run_tests.sh intelligent

# Run infrastructure tests
./tests/run_tests.sh infrastructure

# Run fast tests (exclude slow)
./tests/run_tests.sh fast

# Run with coverage
./tests/run_tests.sh coverage

# Run specific service
./tests/run_tests.sh bia
./tests/run_tests.sh risk
./tests/run_tests.sh workflow

# Run specific path
./tests/run_tests.sh specific tests/unit/platform-services/bia-service/

# Show help
./tests/run_tests.sh help
```

### Using Python Script

```bash
# Run all tests
python tests/run_tests.py all

# Run unit tests
python tests/run_tests.py unit

# Run specific category
python tests/run_tests.py platform
python tests/run_tests.py intelligent
python tests/run_tests.py infrastructure

# Run with coverage
python tests/run_tests.py coverage

# Run specific path
python tests/run_tests.py specific tests/unit/platform-services/bia-service/
```

### Using pytest directly

```bash
# Run all tests
pytest tests/

# Run unit tests only
pytest tests/unit/ -m "unit"

# Run integration tests
pytest tests/integration/ -m "integration"

# Run e2e tests
pytest tests/e2e/ -m "e2e"

# Run fast tests (exclude slow)
pytest tests/ -m "not slow"

# Run specific service
pytest tests/unit/platform-services/bia-service/ -v

# Run with coverage
pytest tests/ --cov=platform-services --cov=intelligent-core --cov=infrastructure --cov-report=html

# Run and stop on first failure
pytest tests/ -x

# Run last failed tests
pytest tests/ --lf

# Run in parallel (requires pytest-xdist)
pytest tests/ -n auto
```

## 🏷️ Test Markers

Tests are categorized using pytest markers:

### By Type
- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (multiple components)
- `@pytest.mark.e2e` - End-to-end tests (full workflows)
- `@pytest.mark.slow` - Slow tests
- `@pytest.mark.security` - Security tests
- `@pytest.mark.performance` - Performance tests

### By Category
- `@pytest.mark.platform_services` - Platform services tests
- `@pytest.mark.intelligent_core` - Intelligent core tests
- `@pytest.mark.infrastructure` - Infrastructure tests

### By Requirements
- `@pytest.mark.requires_db` - Requires database
- `@pytest.mark.requires_redis` - Requires Redis
- `@pytest.mark.requires_temporal` - Requires Temporal
- `@pytest.mark.requires_llm` - Requires LLM API

### Examples

```python
import pytest

@pytest.mark.unit
@pytest.mark.platform_services
def test_bia_calculation():
    """Unit test for BIA calculation logic"""
    pass

@pytest.mark.integration
@pytest.mark.requires_db
async def test_bia_to_risk_workflow(db_session):
    """Integration test for BIA -> Risk workflow"""
    pass

@pytest.mark.e2e
@pytest.mark.slow
async def test_complete_bcm_workflow():
    """End-to-end test for complete BCM workflow"""
    pass
```

## 🔧 Configuration

### pytest.ini

Main pytest configuration file with:
- Test discovery patterns
- Marker definitions
- Output options
- Coverage settings
- Timeout configuration

### conftest.py

Global fixtures available to all tests:
- `db_session` - Database session with automatic rollback
- `redis_client` - Fake Redis client (in-memory)
- `mock_eventbus` - Mock EventBus client
- `mock_llm_client` - Mock LLM client
- `mock_rag_pipeline` - Mock RAG pipeline
- `mock_temporal_client` - Mock Temporal client
- `sample_workflow_context` - Sample workflow data
- `sql_injection_patterns` - Security test patterns
- And many more...

## 📊 Coverage Reports

Generate coverage reports:

```bash
# HTML coverage report
pytest tests/ --cov=platform-services --cov=intelligent-core --cov=infrastructure --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Terminal coverage report
pytest tests/ --cov=platform-services --cov=intelligent-core --cov=infrastructure --cov-report=term-missing
```

## 🎯 Best Practices

### Writing Tests

1. **Use descriptive names**
   ```python
   def test_bia_calculates_rto_correctly():  # Good
   def test_calc():  # Bad
   ```

2. **Use markers**
   ```python
   @pytest.mark.unit
   @pytest.mark.platform_services
   def test_something():
       pass
   ```

3. **Use fixtures**
   ```python
   async def test_workflow(db_session, mock_eventbus):
       # Use fixtures instead of setup/teardown
       pass
   ```

4. **Test one thing**
   ```python
   def test_bia_calculates_rto():  # Good - tests one thing
       pass

   def test_bia_everything():  # Bad - tests too much
       pass
   ```

5. **Use async for async code**
   ```python
   async def test_async_function():  # Use async def for async tests
       result = await some_async_function()
       assert result == expected
   ```

### Organizing Tests

1. **Mirror source structure**
   ```
   platform-services/bia-service/main.py
   tests/unit/platform-services/bia-service/test_main.py
   ```

2. **Group related tests**
   ```python
   class TestBIACalculation:
       def test_rto_calculation(self):
           pass

       def test_rpo_calculation(self):
           pass
   ```

3. **Use integration tests for cross-service tests**
   ```python
   # tests/integration/test_bia_to_risk.py
   async def test_bia_triggers_risk_assessment():
       pass
   ```

## 🔍 Debugging Tests

### Run specific test
```bash
pytest tests/unit/platform-services/bia-service/test_main.py::test_specific_function -v
```

### Run with print statements
```bash
pytest tests/ -s  # -s shows print output
```

### Run with pdb debugger
```bash
pytest tests/ --pdb  # Drop into debugger on failure
```

### Run in verbose mode
```bash
pytest tests/ -vv  # Extra verbose
```

## 📚 Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest markers](https://docs.pytest.org/en/stable/how-to/mark.html)
- [pytest fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)

## ✅ Migration Checklist

Tests have been migrated from individual service directories to centralized `/tests`:

- [x] Platform Services (9 services)
- [x] Intelligent Core (8 components)
- [x] Infrastructure (5 components)
- [x] Integration tests created
- [x] E2E tests created
- [x] Test runners created (Bash + Python)
- [x] pytest.ini updated
- [x] conftest.py configured
- [x] Documentation created

## 🚨 Important Notes

1. **Original test directories**: Tests have been COPIED (not moved) from service directories to maintain backward compatibility. You can delete the original `tests/` directories in services if needed.

2. **Import paths**: Some tests may need import path updates to work from the centralized location.

3. **Fixtures**: All tests now have access to global fixtures from `/tests/conftest.py`.

4. **CI/CD**: Update CI/CD pipelines to use the new test structure:
   ```yaml
   # .github/workflows/tests.yml
   - name: Run tests
     run: ./tests/run_tests.sh all
   ```

---

**Created:** 2025-10-11
**Version:** 1.0
