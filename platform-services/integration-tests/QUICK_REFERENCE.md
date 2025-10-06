# Integration Tests - Quick Reference

## Quick Start (5 Minutes)

```bash
# 1. Setup
cd integration-tests
pip install -r requirements.txt

# 2. Run all tests
./run_integration_tests.sh

# 3. View results
# Tests will run and show pass/fail status
```

## Common Commands

### Run All Tests
```bash
./run_integration_tests.sh
```

### Run by Category
```bash
# Workflow tests only
./run_integration_tests.sh -k workflow

# API tests only
./run_integration_tests.sh -k api

# Fast tests only (exclude slow)
./run_integration_tests.sh -m "integration and not slow"
```

### Run Specific Test File
```bash
./run_integration_tests.sh test_bia_to_planning_workflow.py
```

### Run with Verbose Output
```bash
./run_integration_tests.sh -v -s
```

## Test Categories

| Category | Count | Marker | Command |
|----------|-------|--------|---------|
| All Tests | 65 | `integration` | `./run_integration_tests.sh` |
| Workflow | 17 | `workflow` | `-k workflow` |
| API | 9 | `api` | `-k api` |
| EventBus | 9 | `eventbus` | `-k eventbus` |
| Auth | 8 | `auth` | `-k auth` |
| Resilience | 9 | `resilience` | `-k resilience` |
| Performance | 7 | `performance` | `-k performance` |
| Data | 6 | `data_consistency` | `-k data_consistency` |

## Service URLs (Local)

| Service | URL | Health Check |
|---------|-----|--------------|
| BIA | http://localhost:8012 | http://localhost:8012/health |
| Planning | http://localhost:8011 | http://localhost:8011/health |
| Plans | http://localhost:8023 | http://localhost:8023/health |
| Compliance | http://localhost:8014 | http://localhost:8014/health |

## Manual Service Management

### Start Services
```bash
docker-compose -f docker-compose.test.yml up -d
```

### Check Service Status
```bash
docker-compose -f docker-compose.test.yml ps
```

### View Logs
```bash
# All services
docker-compose -f docker-compose.test.yml logs -f

# Specific service
docker-compose -f docker-compose.test.yml logs -f bia-service-test
```

### Stop Services
```bash
docker-compose -f docker-compose.test.yml down -v
```

### Restart Single Service
```bash
docker-compose -f docker-compose.test.yml restart bia-service-test
```

## Troubleshooting

### Services Won't Start
```bash
# Check Docker
docker info

# View startup logs
docker-compose -f docker-compose.test.yml logs

# Hard reset
docker-compose -f docker-compose.test.yml down -v
docker-compose -f docker-compose.test.yml up -d
```

### Tests Timing Out
```bash
# Edit .env.test
TEST_TIMEOUT=180
HEALTH_CHECK_TIMEOUT=90
```

### Port Conflicts
```bash
# Check what's using ports
lsof -i :8012
lsof -i :8011

# Kill process or change ports in docker-compose.test.yml
```

### Database Issues
```bash
# Reset database
docker-compose -f docker-compose.test.yml down -v
docker volume prune -f
```

## Test File Overview

| File | Tests | What It Tests |
|------|-------|---------------|
| `test_bia_to_planning_workflow.py` | 5 | BIA → Planning integration |
| `test_planning_to_plans_workflow.py` | 6 | Planning → Plans integration |
| `test_compliance_audit_workflow.py` | 6 | Compliance workflows |
| `test_api_integration.py` | 9 | Cross-service APIs |
| `test_eventbus_integration.py` | 9 | Event publishing/consuming |
| `test_auth_integration.py` | 8 | JWT auth & multi-tenancy |
| `test_resilience_integration.py` | 9 | Error handling & retries |
| `test_performance_integration.py` | 7 | Response times & throughput |
| `test_data_consistency.py` | 6 | Data integrity |

## Key Fixtures

| Fixture | Purpose |
|---------|---------|
| `http_client` | Async HTTP client |
| `auth_headers` | Default auth headers |
| `service_urls` | All service URLs |
| `cleanup_test_data` | Auto cleanup after test |
| `wait_for_services` | Wait for healthy services |

## Expected Execution Times

| Test Suite | Duration |
|------------|----------|
| All tests | 5-10 min |
| Workflow only | 2-3 min |
| API only | 1-2 min |
| Fast tests only | ~2 min |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All tests passed |
| 1 | Some tests failed |
| 2 | Test collection error |
| 3 | Internal error |

## Useful Pytest Options

```bash
# Stop on first failure
./run_integration_tests.sh -x

# Capture print statements
./run_integration_tests.sh -s

# Show local variables on failure
./run_integration_tests.sh -l

# Show 10 slowest tests
./run_integration_tests.sh --durations=10

# Parallel execution (install pytest-xdist)
pytest -n 4
```

## Environment Variables

Edit `.env.test` to configure:

```bash
# Increase timeouts
TEST_TIMEOUT=180
HEALTH_CHECK_TIMEOUT=90

# Change service URLs
BIA_SERVICE_URL=http://bia-service-test:8012

# JWT configuration
JWT_SECRET=your-test-secret
```

## CI/CD Integration

### GitHub Actions
See `README.md` for complete GitHub Actions example.

### GitLab CI
```yaml
test:
  script:
    - cd integration-tests
    - pip install -r requirements.txt
    - ./run_integration_tests.sh
```

## Getting Help

1. **Check README.md** - Comprehensive documentation
2. **Check INTEGRATION_TESTS_SUMMARY.md** - Detailed coverage info
3. **View service logs** - `docker-compose logs`
4. **Run with verbose output** - `-v -s` flags

## Quick Validation

```bash
# Verify syntax
python3 -m py_compile test_*.py

# Check service health
curl http://localhost:8012/health
curl http://localhost:8011/health
curl http://localhost:8023/health
curl http://localhost:8014/health

# Run smoke test
./run_integration_tests.sh test_api_integration.py::test_health_endpoints_all_services
```
