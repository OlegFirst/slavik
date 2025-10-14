# Quick Start - Security Tests

## TL;DR

```bash
# 1. Install dependencies
pip install pytest pytest-asyncio pytest-cov

# 2. Set database URL
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/test_bcm"

# 3. Run all security tests
cd tests
./run_security_tests.sh all

# OR using pytest directly
pytest test_sql_injection.py test_validation.py test_rls.py test_integration_security.py -v
```

## What Was Created

**4 NEW test files** with **60 security tests**:

1. `test_sql_injection.py` - 15 tests for SQL injection prevention
2. `test_validation.py` - 22 tests for Pydantic validation
3. `test_rls.py` - 10 tests for tenant isolation (RLS)
4. `test_integration_security.py` - 13 tests for end-to-end security

## Quick Commands

```bash
# Run all security tests
./run_security_tests.sh all

# Run specific test suite
./run_security_tests.sh sql          # SQL injection tests only
./run_security_tests.sh validation   # Validation tests only
./run_security_tests.sh rls          # RLS tests only
./run_security_tests.sh integration  # Integration tests only

# Run with coverage
./run_security_tests.sh coverage

# Quick smoke test (4 tests)
./run_security_tests.sh quick
```

## Expected Output

```
========================================
  Workflow Intelligence Security Tests
========================================

Running ALL security tests...

test_sql_injection.py::test_sql_injection_in_workflow_id PASSED
test_sql_injection.py::test_sql_injection_in_tenant_id PASSED
test_sql_injection.py::test_sql_injection_in_module PASSED
... (57 more tests)

✅ All security tests PASSED!

========================================
  Test run complete
========================================
```

## Test Count Summary

| File | Tests | Type |
|------|-------|------|
| `test_sql_injection.py` | 15 | async |
| `test_validation.py` | 22 | sync |
| `test_rls.py` | 10 | async |
| `test_integration_security.py` | 13 | async |
| **TOTAL** | **60** | **mixed** |

## What's Tested

### SQL Injection (15 tests)
- All input parameters (workflow_id, tenant_id, module, case_id, etc.)
- UNION attacks, stacked queries, encoding tricks
- Parameterized query verification

### Validation (22 tests)
- String lengths, numeric ranges, boolean types
- Required fields, nested objects, lists
- Special characters, unicode support

### Tenant Isolation (10 tests)
- Workflow context isolation
- Cross-tenant access prevention
- Data leakage prevention

### Integration (13 tests)
- Complete workflows with isolation
- Concurrent operations
- Large-scale testing (100 tenants)

## Troubleshooting

### Database connection failed
```bash
# Check PostgreSQL is running
psql -U postgres -d test_bcm -c "SELECT 1"

# Install pgvector extension
psql -U postgres -d test_bcm -c "CREATE EXTENSION IF NOT EXISTS vector"
```

### Import errors
```bash
# Install dependencies
pip install -r ../requirements.txt
pip install pytest pytest-asyncio pytest-cov
```

### Tests fail
```bash
# Run with verbose output
pytest test_sql_injection.py -v -s

# Run single test
pytest test_sql_injection.py::test_sql_injection_in_workflow_id -v
```

## More Information

- Full documentation: `README_SECURITY_TESTS.md`
- Summary: `SECURITY_TEST_SUMMARY.md`
- Configuration: `../pytest.ini`

## Success Criteria

All 60 tests should **PASS** if:
- ✓ PostgreSQL is running with pgvector
- ✓ All queries use parameterization ($1, $2, etc.)
- ✓ Pydantic models have proper validation
- ✓ Tenant isolation is implemented correctly
