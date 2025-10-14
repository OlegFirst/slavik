# Archive: Original Test Directories

**Date:** 11 октября 2025
**Reason:** Test centralization to `/tests` directory

---

## Summary

This archive contains the original `tests/` directories from individual services and components before centralization.

**Total directories archived:** 25

All tests have been **copied** to the centralized `/tests` structure and are now available at:
- `/tests/unit/platform-services/`
- `/tests/unit/intelligent-core/`
- `/tests/unit/infrastructure/`

---

## Archived Components

### Platform Services (9 directories)
1. `bia-service/tests`
2. `compliance-service/tests`
3. `digital-twin/tests`
4. `governance-service/tests`
5. `learning-service/tests`
6. `planning_service/tests`
7. `plans_service/tests`
8. `response-service/tests`
9. `risk-service/tests`

### Intelligent Core (12 directories)
1. `ai-foundation/tests`
2. `ai-office/tests` (from expertise-center)
3. `ai-orchestration/tests`
4. `ai_experts/tests` (from expertise-center)
5. `community_intelligence/tests`
6. `coordination-center/tests`
7. `expertise-service/tests` (from expertise-center/service)
8. `learning-knowledge/tests`
9. `system-bcm-service/tests`
10. `temporal-sample/tests`
11. `workflow-engine/tests`
12. `workflow_intelligence/tests`

### Infrastructure (4 directories)
1. `api-gateway/tests`
2. `balancer-service/tests`
3. `eventbus/tests`
4. `mio-manager/tests`

---

## Migration Details

### Original Locations

**Platform Services:**
```
platform-services/bia-service/tests
platform-services/compliance-service/tests
platform-services/governance-service/tests
platform-services/learning-service/tests
platform-services/planning_service/tests
platform-services/plans_service/tests
platform-services/response-service/tests
platform-services/risk-service/tests
platform-services/simulation/digital-twin/tests
```

**Intelligent Core:**
```
intelligent-core/workflow-engine/workflow/tests
intelligent-core/expertise-center/ai-office/tests
intelligent-core/expertise-center/ai_experts/tests
intelligent-core/expertise-center/service/tests
intelligent-core/workflow_intelligence/tests
intelligent-core/workflow_intelligence/temporal-sample/tests
intelligent-core/ai-foundation/tests
intelligent-core/ai-foundation/learning-knowledge/tests
intelligent-core/community_intelligence/tests
intelligent-core/orchestration/ai-orchestration/tests
intelligent-core/orchestration/coordination-center/tests
intelligent-core/system-bcm-service/tests
```

**Infrastructure:**
```
infrastructure/eventbus/tests
infrastructure/balancer-service/tests
infrastructure/gateway/api-gateway/tests
infrastructure/AI-office-infrastructure/mio-manager/tests
```

### New Centralized Locations

All tests are now organized in `/tests` with the following structure:

```
/tests/
├── unit/
│   ├── platform-services/
│   │   ├── bia-service/tests/
│   │   ├── risk-service/tests/
│   │   ├── compliance-service/tests/
│   │   ├── governance-service/tests/
│   │   ├── learning-service/tests/
│   │   ├── planning-service/tests/
│   │   ├── plans-service/tests/
│   │   ├── response-service/tests/
│   │   └── digital-twin/tests/
│   │
│   ├── intelligent-core/
│   │   ├── workflow-intelligence/tests/
│   │   ├── ai-orchestration/tests/
│   │   ├── expertise-center/
│   │   │   ├── ai-office/tests/
│   │   │   ├── ai-experts/tests/
│   │   │   └── service/tests/
│   │   ├── system-bcm/tests/
│   │   ├── coordination-center/tests/
│   │   ├── ai-foundation/
│   │   │   ├── core/tests/
│   │   │   └── learning-knowledge/tests/
│   │   ├── community-intelligence/tests/
│   │   └── workflow-engine/tests/
│   │
│   └── infrastructure/
│       ├── eventbus/tests/
│       ├── balancer-service/tests/
│       ├── api-gateway/tests/
│       ├── mio-manager/tests/
│       └── project-agent/tests/
│
├── integration/
│   ├── test_platform_services_integration.py
│   └── test_intelligent_core_integration.py
│
└── e2e/
    └── test_full_bcm_workflow.py
```

---

## Running Tests

Tests should now be run from the centralized location:

```bash
# Run all tests
./tests/run_tests.sh all

# Run unit tests
./tests/run_tests.sh unit

# Run platform services tests
./tests/run_tests.sh platform

# Run specific service
./tests/run_tests.sh bia

# Run with coverage
./tests/run_tests.sh coverage
```

Or using pytest directly:

```bash
pytest tests/
pytest tests/unit/platform-services/
pytest tests/unit/intelligent-core/
```

---

## Restoration

If you need to restore the original test structure:

```bash
# For a specific service
cp -r _archive/tests-original-2025-10-11/platform-services/bia-service/tests platform-services/bia-service/

# For all services (not recommended)
# Manually copy each directory back to its original location
```

---

## Notes

1. **Tests are now centralized**: All future test development should happen in `/tests`
2. **This archive is for reference only**: Don't modify these files
3. **Import paths**: Some tests may have been updated with new import paths
4. **Fixtures**: Tests now use global fixtures from `/tests/conftest.py`
5. **CI/CD**: CI/CD pipelines should use the new test structure

---

## Related Documentation

- `/tests/README_STRUCTURE.md` - Complete test structure documentation
- `/TESTS_MAP.md` - Map of all tests
- `/TESTS_CENTRALIZATION_COMPLETE.md` - Migration summary

---

**Archive Created:** 11 октября 2025
**Status:** ✅ Complete
**Test Files:** 96 test files preserved
**Directories:** 25 test directories archived
