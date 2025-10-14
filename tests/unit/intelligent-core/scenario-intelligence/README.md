# Scenario Intelligence - Unit Tests

## Overview

Unit tests for Scenario Intelligence system components.

## Test Structure

```
tests/unit/intelligent-core/scenario-intelligence/
├── __init__.py
├── README.md                 # This file
├── test_config.py            # Configuration tests
├── test_database.py          # Database tests
├── test_monitoring.py        # Monitoring tests
└── pytest.ini                # Pytest configuration
```

## Running Tests

### All tests
```bash
cd /Users/MD/AI-Platform-ISO
pytest tests/unit/intelligent-core/scenario-intelligence/ -v
```

### Specific test file
```bash
pytest tests/unit/intelligent-core/scenario-intelligence/test_config.py -v
```

### With coverage
```bash
pytest tests/unit/intelligent-core/scenario-intelligence/ --cov=intelligent-core/scenario-intelligence --cov-report=html
```

## Test Categories

### Configuration Tests (`test_config.py`)
- Config loading
- Validation
- Storage configuration
- Feature flags
- Monitoring configuration

### Database Tests (`test_database.py`)
- PostgreSQL connection
- Schema verification
- Statistics retrieval
- Storage operations

### Monitoring Tests (`test_monitoring.py`)
- Prometheus metrics
- Context managers
- MIO Manager integration
- Metric recording functions

## Environment Requirements

For database tests, set:
```bash
export DATABASE_URL="postgresql://user:pass@host:port/db"
```

## Dependencies

```bash
pip install pytest pytest-asyncio pytest-cov
```

## Coverage Target

**Target**: 80% code coverage

## Test Status

- ✅ Configuration: Implemented
- ✅ Monitoring: Implemented
- ✅ Database: Implemented
- 🔄 Execution Engine: Covered by integration tests
- 🔄 Generators: Covered by integration tests

## Related Tests

- **Integration Tests**: `/intelligent-core/scenario-intelligence/tests/integration/`
- **E2E Tests**: `/intelligent-core/scenario-intelligence/tests/e2e/`
- **Full System Test**: `/intelligent-core/scenario-intelligence/test_full_system.py`
