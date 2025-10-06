# AI Intelligence Layer - Test Suite

**Version:** 1.0.0
**Coverage:** ~65% (core components)
**Tests:** 36 unit tests

---

## Quick Start

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage report
pytest --cov

# Run specific test file
pytest tests/test_meta_learning.py -v
```

---

## Test Files

### 1. test_meta_learning.py (12 tests)

Tests for Meta-Learning Engine:
- ✅ Interaction recording
- ✅ Routing accuracy calculation
- ✅ User feedback recording
- ✅ ML-based routing recommendations
- ✅ Performance insights
- ✅ Learning insights
- ✅ Intent pattern tracking
- ✅ Colleague performance tracking
- ✅ Statistics retrieval

**Run:**
```bash
pytest tests/test_meta_learning.py -v
```

### 2. test_predictive_analytics.py (13 tests)

Tests for Predictive Analytics:
- ✅ Metric recording
- ✅ Trend analysis (increasing/decreasing/stable)
- ✅ Anomaly detection
- ✅ Future state prediction
- ✅ Weekly pattern detection
- ✅ Risk predictions
- ✅ Analytics insights
- ✅ Trend calculation
- ✅ Insufficient data handling

**Run:**
```bash
pytest tests/test_predictive_analytics.py -v
```

### 3. test_coordinator.py (11 tests)

Tests for Colleague Coordinator:
- ✅ Manual routing
- ✅ Auto-routing
- ✅ Workflow execution
- ✅ Statistics retrieval
- ✅ Colleague listing
- ✅ Intent mapping
- ✅ Context determination
- ✅ Stats update
- ✅ Error handling

**Run:**
```bash
pytest tests/test_coordinator.py -v
```

### 4. test_api_integration.py (Placeholder)

Integration tests for API endpoints (to be implemented).

---

## Test Coverage

**Current Coverage:** ~65%

| Component | Coverage | Status |
|-----------|----------|--------|
| Meta-Learning | ~85% | ✅ Good |
| Predictive Analytics | ~85% | ✅ Good |
| Coordinator | ~70% | ✅ OK |
| Colleagues | ~20% | ⚠️ Low |
| RAG Pipeline | ~10% | ⚠️ Low |
| EventBus | ~10% | ⚠️ Low |

**Target:** 80% overall coverage

---

## Running Tests

### All Tests
```bash
pytest
```

### With Verbose Output
```bash
pytest -v
```

### With Coverage
```bash
pytest --cov --cov-report=html
open htmlcov/index.html
```

### Specific Test
```bash
pytest tests/test_meta_learning.py::test_record_interaction
```

### Tests Matching Pattern
```bash
pytest -k "routing"
```

---

## Test Configuration

**pytest.ini:**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
asyncio_mode = auto

addopts = 
    -v
    --cov=core
    --cov=coordinator
    --cov=colleagues
    --cov-report=html
```

---

## Adding New Tests

### Test Template

```python
import pytest
from your_module import YourClass

@pytest.fixture
def your_fixture():
    """Fixture description"""
    return YourClass()

@pytest.mark.asyncio
async def test_your_feature(your_fixture):
    """Test that your feature works correctly"""
    # Arrange
    input_data = "test"
    
    # Act
    result = await your_fixture.process(input_data)
    
    # Assert
    assert result == expected_value
```

### Test Naming

- `test_<component>_<scenario>_<expected_result>`
- Clear, descriptive names
- One assert per test (generally)

---

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements-test.txt
      - run: pytest --cov
```

---

## Troubleshooting

### Import Errors
```bash
# Install in development mode
pip install -e .
```

### Async Test Failures
```bash
# Ensure pytest-asyncio is installed
pip install pytest-asyncio
```

### Coverage Not Generated
```bash
# Install coverage tools
pip install pytest-cov coverage
```

---

## Next Steps

1. **Increase Coverage:** Add tests for colleagues, RAG pipeline
2. **Integration Tests:** Test API endpoints with live server
3. **Load Tests:** Performance testing with locust/ab
4. **E2E Tests:** Full system testing

---

**For Full Documentation:** See `/ISO-22301-Library/TESTING_GUIDE.md`

