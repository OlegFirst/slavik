# Planning Service - Test Suite

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
export PYTHONPATH="$(pwd):$PYTHONPATH"
python3 -m pytest tests/ -v

# Or use the script
chmod +x run_tests.sh
./run_tests.sh
```

## Test Files

| File | Tests | Purpose |
|------|-------|---------|
| `test_cost_benefit.py` | 25 | NPV, payback, recommendations |
| `test_validation.py` | 50 | Pydantic model validators |
| `test_repository.py` | 15 | Database operations |
| `test_auth_deps.py` | 24 | JWT authentication |
| **Total** | **114** | **Complete coverage** |

## Run Specific Tests

```bash
# Cost-benefit calculations only
python3 -m pytest tests/test_cost_benefit.py -v

# Validation tests only
python3 -m pytest tests/test_validation.py -v

# Repository tests only
python3 -m pytest tests/test_repository.py -v

# Authentication tests only
python3 -m pytest tests/test_auth_deps.py -v

# Run with coverage
python3 -m pytest tests/ --cov=. --cov-report=html
```

## Test Markers

```bash
# Run only unit tests
python3 -m pytest -m unit

# Run only integration tests
python3 -m pytest -m integration

# Skip slow tests
python3 -m pytest -m "not slow"
```

## Fixtures Available

From `conftest.py`:

- `db_engine` - Test database engine (SQLite in-memory)
- `db_session` - Async database session
- `mock_settings` - Mock configuration
- `sample_cost_breakdown` - Cost data fixture
- `sample_benefits` - Benefits data fixture
- `mock_user_context` - Authenticated user fixture

## Coverage Report

After running tests with coverage:

```bash
# View HTML report
open htmlcov/index.html
```

## Important Notes

1. **PYTHONPATH Required**: Tests need parent directory in path
2. **Async Tests**: Use `pytest-asyncio` for async test support
3. **In-Memory DB**: Each test gets fresh database
4. **No External Dependencies**: Tests are fully isolated

## Test Categories

### Critical Business Logic ✅
- NPV calculations with known values
- Payback period edge cases
- Recommendation decision logic
- Confidence assessment

### Data Validation ✅
- Implementation years: 1-30
- Discount rate: 0-50%
- Currency codes
- Benefit requirements
- Resource constraints

### Database Operations ✅
- CRUD operations
- Multi-tenancy filtering
- Soft deletes
- Pagination
- JSON field updates

### Authentication ✅
- JWT validation
- Token expiry
- Development mode
- Optional auth
- Role handling

## CI/CD Integration

```yaml
# Example GitHub Actions
- name: Run Tests
  run: |
    pip install -r requirements.txt
    export PYTHONPATH=$PWD
    pytest tests/ --cov=. --cov-report=xml

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Troubleshooting

### Import Errors
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH="/path/to/planning_service:$PYTHONPATH"
```

### Async Test Issues
```bash
# Check pytest-asyncio is installed
pip install pytest-asyncio==0.21.1
```

### Database Errors
```bash
# Install aiosqlite for async SQLite
pip install aiosqlite==0.19.0
```

## For More Details

See [TEST_REPORT.md](../TEST_REPORT.md) for comprehensive test documentation.
