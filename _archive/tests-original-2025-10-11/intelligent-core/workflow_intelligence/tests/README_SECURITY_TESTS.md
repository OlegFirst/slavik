# Security Test Suite

Comprehensive security tests for Workflow Intelligence service.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                      # Pytest fixtures and configuration
├── test_sql_injection.py            # SQL injection protection tests (15 tests)
├── test_validation.py               # Pydantic validation tests (20 tests)
├── test_rls.py                      # Row-Level Security tests (12 tests)
├── test_integration_security.py     # Integration security tests (13 tests)
└── README_SECURITY_TESTS.md         # This file
```

## Test Categories

### 1. SQL Injection Protection (`test_sql_injection.py`)

Tests that verify SQL injection is IMPOSSIBLE:

- ✓ SQL injection in `workflow_id`
- ✓ SQL injection in `tenant_id`
- ✓ SQL injection in `module` parameter
- ✓ SQL injection in `case_id`
- ✓ SQL injection in filter parameters (industry, org_size)
- ✓ SQL injection in benchmark queries
- ✓ SQL injection in JSON context data
- ✓ UNION-based SQL injection attacks
- ✓ Stacked query attacks
- ✓ Encoding tricks (URL encoding, Unicode)
- ✓ Verification that all queries use parameterization ($1, $2, etc)

**Total: 15 tests**

### 2. Pydantic Validation (`test_validation.py`)

Tests that verify input validation works correctly:

- ✓ String length limits
- ✓ Type validation (numeric, boolean, datetime)
- ✓ Range validation (ratings, probabilities)
- ✓ Required fields validation
- ✓ Nested object validation
- ✓ List/array validation
- ✓ Query parameter validation
- ✓ Embedding dimension validation
- ✓ Large context handling
- ✓ Special characters handling

**Total: 20 tests**

### 3. Row-Level Security (`test_rls.py`)

Tests that verify tenant isolation:

- ✓ Workflow context isolation
- ✓ Case isolation
- ✓ Prediction isolation
- ✓ NULL/empty tenant_id handling
- ✓ Update operations preserve isolation
- ✓ Multiple tenants in same module
- ✓ Benchmark aggregation (cross-tenant, anonymized)
- ✓ Similar cases privacy
- ✓ Tenant_id cannot be overridden
- ✓ Raw SQL query isolation
- ⏳ Database-level RLS policies (future)

**Total: 12 tests (2 skipped, 10 active)**

### 4. Integration Security (`test_integration_security.py`)

End-to-end security tests:

- ✓ Complete workflow lifecycle with tenant isolation
- ✓ Concurrent tenant operations
- ✓ Cross-tenant data leakage prevention
- ✓ Case submission with privacy
- ✓ Prediction isolation
- ✓ Malicious tenant enumeration prevention
- ✓ Benchmark aggregation safety
- ✓ Similar cases data leak prevention
- ✓ Parameterized queries in all operations
- ✓ Large-scale tenant isolation (100 tenants)
- ✓ Transaction isolation
- ✓ Error messages don't leak data

**Total: 13 tests**

## Running Tests

### All Security Tests

```bash
# Run all security tests
pytest tests/test_sql_injection.py tests/test_validation.py tests/test_rls.py tests/test_integration_security.py -v

# Or use pattern matching
pytest tests/test_*security*.py tests/test_sql*.py tests/test_validation.py tests/test_rls.py -v
```

### Individual Test Files

```bash
# SQL injection tests only
pytest tests/test_sql_injection.py -v

# Validation tests only
pytest tests/test_validation.py -v

# RLS tests only
pytest tests/test_rls.py -v

# Integration security tests only
pytest tests/test_integration_security.py -v
```

### Specific Test

```bash
# Run specific test by name
pytest tests/test_sql_injection.py::test_sql_injection_in_workflow_id -v

# Run tests matching pattern
pytest tests/ -k "sql_injection" -v
pytest tests/ -k "tenant_isolation" -v
```

### With Coverage

```bash
# Run with coverage report
pytest tests/test_sql_injection.py tests/test_validation.py tests/test_rls.py tests/test_integration_security.py --cov=workflow_intelligence --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Async Tests

All tests are async (using `@pytest.mark.asyncio`):

```bash
# Install pytest-asyncio if not installed
pip install pytest-asyncio

# Run async tests
pytest tests/test_sql_injection.py -v
```

## Prerequisites

### Dependencies

```bash
pip install pytest pytest-asyncio pytest-cov asyncpg pydantic
```

### Database Setup

Tests require a PostgreSQL database with pgvector extension:

```bash
# Set database URL
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/test_bcm"

# Or create .env file
echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/test_bcm" > .env
```

### Docker Setup (Recommended)

```bash
# Start test database with docker-compose
docker-compose -f docker-compose.test.yml up -d

# Run tests
pytest tests/test_sql_injection.py -v

# Clean up
docker-compose -f docker-compose.test.yml down -v
```

## Test Summary

| Test File                        | Tests | Focus Area                |
|----------------------------------|-------|---------------------------|
| `test_sql_injection.py`          | 15    | SQL injection prevention  |
| `test_validation.py`             | 20    | Input validation          |
| `test_rls.py`                    | 10    | Tenant isolation          |
| `test_integration_security.py`   | 13    | End-to-end security       |
| **TOTAL**                        | **58**| **Comprehensive security**|

## CI/CD Integration

### GitHub Actions

```yaml
name: Security Tests

on: [push, pull_request]

jobs:
  security-tests:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: pgvector/pgvector:pg16
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_bcm
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov

      - name: Run security tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_bcm
        run: |
          pytest tests/test_sql_injection.py tests/test_validation.py tests/test_rls.py tests/test_integration_security.py -v --cov=workflow_intelligence

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Security Test Checklist

- [x] SQL injection protection (all entry points)
- [x] Parameterized queries verification
- [x] Input validation (Pydantic models)
- [x] Tenant isolation (application-level)
- [x] Cross-tenant data leakage prevention
- [x] Concurrent operations safety
- [x] Error message sanitization
- [ ] Database-level RLS policies (future)
- [ ] Rate limiting tests (future)
- [ ] Authentication/Authorization tests (future)

## Known Issues & Future Work

### Current Implementation

- ✓ Application-level tenant isolation (WHERE tenant_id = $X)
- ✓ Parameterized queries for all operations
- ✓ Pydantic validation for models

### Future Improvements

1. **Database-Level RLS**
   - Implement PostgreSQL RLS policies
   - Add tests for database-level enforcement
   - Migration from application-level to DB-level

2. **Rate Limiting**
   - Add rate limiting per tenant
   - Tests for rate limit enforcement
   - DDoS protection

3. **Additional Security**
   - API authentication tests
   - Authorization/RBAC tests
   - Audit logging tests
   - Encryption at rest tests

## Contributing

When adding new features:

1. **Add security tests FIRST**
2. Write tests for:
   - SQL injection vectors
   - Input validation
   - Tenant isolation
   - Data leakage scenarios
3. Run full security suite before PR
4. Update this README

## References

- [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [PostgreSQL Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Pydantic Validation](https://docs.pydantic.dev/latest/concepts/validators/)
- [Multi-tenancy Best Practices](https://aws.amazon.com/blogs/apn/multi-tenant-database-architectures/)
