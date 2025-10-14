# Project Agent - Test Management Guide
## Управление Тестовой Инфраструктурой

**Service:** Project Agent
**Port:** 8060
**Version:** 2.0.0
**Responsibility:** Test Coverage, Generation, Quality Analysis

---

## 🎯 Обзор

Project Agent теперь является **центральным менеджером** всей тестовой инфраструктуры платформы. Он отвечает за:

- ✅ **Test Coverage Analysis** - Анализ покрытия кода тестами
- ✅ **Test Generation** - Автоматическая генерация недостающих тестов
- ✅ **Code Quality Analysis** - Анализ качества кода
- ✅ **Compliance Checking** - Проверка соответствия стандартам
- ✅ **Test Reporting** - Отчётность по тестированию

---

## 📁 Тестовая Инфраструктура

### Централизованная Структура

```
/tests/
├── unit/                          # Unit тесты (80%+ coverage)
│   ├── platform-services/         # 9 сервисов
│   ├── intelligent-core/          # 12 компонентов
│   └── infrastructure/            # 4 компонента
├── integration/                   # Интеграционные тесты
│   ├── services/                  # Межсервисные тесты
│   ├── database/                  # DB интеграция
│   └── eventbus/                  # EventBus workflows
├── e2e/                          # End-to-end тесты
│   ├── workflows/                 # User journeys
│   └── api/                       # API endpoints
├── load/                         # Load & performance тесты
│   ├── performance/
│   └── stress/
├── fixtures/                     # Тестовые данные
├── conftest.py                   # 30+ глобальных фикстур
├── pytest.ini                    # 12 маркеров
├── run_tests.sh                  # Bash runner
├── run_tests.py                  # Python runner
└── TEST_INFRASTRUCTURE_CONFIG.yaml  # Конфигурация
```

### Компоненты под управлением

#### Platform Services (9):
1. **bia-service** (8012) - BIA workflows
2. **compliance-service** (8014) - Compliance validation
3. **governance-service** (8025) - Governance policies
4. **learning-service** (8021) - Learning & training
5. **planning_service** (8011) - BC planning
6. **plans_service** (8023) - Plan management
7. **response-service** (8027) - Incident response
8. **risk-service** (8026) - Risk assessment
9. **digital-twin** (8035) - Digital twin simulation

#### Intelligent Core (12):
1. **ai-foundation** - Learning & Knowledge base
2. **ai-orchestration** (8002) - The Brain
3. **community_intelligence** (8030) - Peer knowledge
4. **coordination-center** (8033) - Multi-agent coordination
5. **expertise-center** (8029) - 14 AI Specialists
6. **workflow-engine** (8030) - BPMN 2.0 engine
7. **workflow_intelligence** (8028) - Workflow design
8. **system-bcm-service** (8050) - Platform self-application
9. **collective** (8034) - Privacy-preserving knowledge sharing
10. **ai_workflow_optimizer** (8038) - ML workflow optimization
11. **predictive** (8031) - AI forecasting
12. **event_intelligence** (8032) - Event analysis

#### Infrastructure (4):
1. **api-gateway** - API Gateway
2. **eventbus** (8001) - Event-driven choreography
3. **mio-manager** (8057) - AI Office manager
4. **balancer-service** - Load balancing

---

## 🔌 API Endpoints для Управления Тестами

### 1. Run Tests
```bash
POST /api/tests/run
```

**Request:**
```json
{
  "suite": "unit",                    // unit | integration | e2e | load | all
  "component": "bia-service",         // optional: specific component
  "markers": ["fast", "critical"],    // optional: pytest markers
  "parallel": true,                   // optional: parallel execution
  "coverage": true                    // optional: enable coverage
}
```

**Response:**
```json
{
  "execution_id": "exec-001",
  "status": "running",
  "suite": "unit",
  "component": "bia-service",
  "started_at": "2025-10-11T10:00:00Z"
}
```

### 2. Get Coverage Report
```bash
GET /api/tests/coverage
GET /api/tests/coverage?component=bia-service
```

**Response:**
```json
{
  "total_coverage": 82.5,
  "by_category": {
    "platform_services": 80.2,
    "intelligent_core": 85.1,
    "infrastructure": 75.8
  },
  "by_component": {
    "bia-service": {
      "coverage": 85.0,
      "lines_covered": 850,
      "lines_total": 1000,
      "missing_coverage": [
        "bia_service.py:145-150",
        "workflows.py:230-240"
      ]
    }
  },
  "quality_gates": {
    "meets_minimum": true,
    "target": 80,
    "actual": 82.5
  }
}
```

### 3. Generate Missing Tests
```bash
POST /api/tests/generate
```

**Request:**
```json
{
  "component": "bia-service",
  "coverage_threshold": 85,
  "test_types": ["unit", "integration"]
}
```

**Response:**
```json
{
  "generation_id": "gen-001",
  "component": "bia-service",
  "tests_generated": 15,
  "files_created": [
    "/tests/unit/platform-services/test_bia_service_new.py",
    "/tests/integration/services/test_bia_workflow.py"
  ],
  "coverage_improvement": {
    "before": 75.0,
    "after": 85.2,
    "improvement": 10.2
  }
}
```

### 4. Get Test Report
```bash
GET /api/tests/report
GET /api/tests/report?execution_id=exec-001
```

**Response:**
```json
{
  "execution_id": "exec-001",
  "suite": "unit",
  "status": "completed",
  "duration": "125.3s",
  "results": {
    "total_tests": 458,
    "passed": 452,
    "failed": 4,
    "skipped": 2,
    "errors": 0
  },
  "failures": [
    {
      "test": "test_bia_workflow_validation",
      "file": "test_bia_service.py:145",
      "error": "AssertionError: Expected 200, got 500"
    }
  ],
  "coverage": 82.5,
  "quality_score": 95.2
}
```

### 5. Analyze Test Quality
```bash
GET /api/tests/quality
```

**Response:**
```json
{
  "overall_quality": 92.5,
  "metrics": {
    "test_maintainability": 90.0,
    "assertion_quality": 95.0,
    "fixture_reusability": 88.0,
    "test_isolation": 94.0
  },
  "recommendations": [
    "Add more edge case tests for bia-service",
    "Improve fixture documentation in conftest.py",
    "Consider parametrizing test_risk_assessment"
  ]
}
```

---

## 🔄 Workflow с DevOps Agent

Project Agent и DevOps Agent работают совместно:

### CI/CD Pipeline:

```
1. Developer pushes code
   ↓
2. DevOps Agent (8058) triggered
   ↓
3. DevOps calls Project Agent → POST /api/tests/run
   ↓
4. Project Agent executes tests
   ↓
5. Project Agent analyzes coverage → POST /api/tests/coverage
   ↓
6. If coverage < threshold → POST /api/tests/generate
   ↓
7. Re-run tests with new tests
   ↓
8. Project Agent reports results → GET /api/tests/report
   ↓
9. DevOps Agent proceeds with deployment (if tests pass)
```

### Event-Driven Communication:

```yaml
# DevOps publishes event
event: "deployment.requested"
payload:
  service: "bia-service"
  environment: "production"

# Project Agent subscribes and responds
event: "tests.run.requested"
handler: run_test_suite()

# Project Agent publishes results
event: "tests.completed"
payload:
  execution_id: "exec-001"
  status: "passed"
  coverage: 85.2

# DevOps listens and deploys
event: "deployment.approved"
```

---

## 📊 Coverage Requirements

### Minimum Coverage Targets:

| Component Type | Target | Critical Paths |
|----------------|--------|----------------|
| Platform Services | 80% | 95% |
| Intelligent Core | 85% | 95% |
| Infrastructure | 75% | 90% |
| Shared Library | 85% | 95% |

### Critical Paths (95% coverage required):
- BIA workflow
- Risk assessment
- Compliance validation
- AI orchestration
- EventBus choreography

---

## 🛠️ Test Generation Strategy

### Automated Test Generation:

1. **Coverage Analysis:**
   - Identify untested code paths
   - Prioritize by criticality
   - Calculate coverage gaps

2. **Test Template Selection:**
   - Unit test templates for business logic
   - Integration test templates for API endpoints
   - E2E test templates for user workflows

3. **Code Generation:**
   - Generate pytest fixtures
   - Create test assertions
   - Add docstrings and comments

4. **Validation:**
   - Run generated tests
   - Verify coverage improvement
   - Check test quality

### Example Generated Test:

```python
# Auto-generated by Project Agent
# Generation ID: gen-001
# Component: bia-service
# Coverage Target: 85%

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
@pytest.mark.unit
async def test_bia_service_start_workflow(test_client, auth_user):
    """
    Test BIA service workflow initiation.

    Generated to cover: bia_service.py:145-150
    Coverage improvement: +5.2%
    """
    # Arrange
    org_id = "test_org_001"

    # Act
    response = await test_client.post(
        "/api/v1/bia/start",
        json={"organization_id": org_id},
        headers={"Authorization": f"Bearer {auth_user.token}"}
    )

    # Assert
    assert response.status_code == 200
    assert "bia_id" in response.json()
    assert response.json()["organization_id"] == org_id
```

---

## 🎨 Test Markers

### Available Markers:

```python
@pytest.mark.fast         # Fast tests (<1s)
@pytest.mark.slow         # Slow tests (>5s)
@pytest.mark.integration  # Integration tests
@pytest.mark.e2e          # End-to-end tests
@pytest.mark.critical     # Critical path tests
@pytest.mark.skip_ci      # Skip in CI
@pytest.mark.require_db   # Requires database
@pytest.mark.require_redis  # Requires Redis
@pytest.mark.require_eventbus  # Requires EventBus
```

### Usage in API:

```bash
# Run only fast, critical tests
POST /api/tests/run
{
  "suite": "unit",
  "markers": ["fast", "critical"]
}

# Skip CI-only tests
POST /api/tests/run
{
  "suite": "all",
  "markers": ["not skip_ci"]
}
```

---

## 📈 Monitoring & Metrics

### Prometheus Metrics:

```yaml
# Test Coverage
test_coverage_percentage{component="bia-service", category="unit"} 85.2

# Test Execution Duration
test_execution_duration_seconds{suite="unit", test_type="fast"} 45.3

# Test Failures
test_failures_total{component="bia-service", test_name="test_workflow"} 2

# Tests Generated
tests_generated_total{component="bia-service", generator="project-agent"} 15
```

### Grafana Dashboards:
- **Test Coverage Dashboard** - Real-time coverage по компонентам
- **Test Execution Performance** - Время выполнения тестов
- **Test Failure Trends** - Тренды провалов тестов

---

## 🔍 Quality Gates

### Pre-Deployment Checks:

1. **Minimum Coverage:** 80% overall
2. **Critical Path Coverage:** 95%
3. **No Failing Tests:** 0 failures
4. **Performance Regression:** <10% degradation

### Automated Actions:

```yaml
# Block merge if coverage < 80%
quality_gate:
  name: "minimum_coverage"
  threshold: 80
  action: "block_merge"

# Block merge if tests fail
quality_gate:
  name: "no_failing_tests"
  action: "block_merge"

# Warn if performance degrades
quality_gate:
  name: "performance_regression"
  threshold: "10%"
  action: "warn"
```

---

## 📝 Test Fixtures

### Global Fixtures (conftest.py):

```python
@pytest.fixture
async def db_session():
    """Provides test database session"""
    # Create test DB session
    yield session
    # Cleanup

@pytest.fixture
async def event_bus():
    """Provides test event bus"""
    # Connect to test EventBus
    yield bus
    # Disconnect

@pytest.fixture
async def auth_user():
    """Provides authenticated test user"""
    # Create test user with token
    yield user
    # Cleanup

@pytest.fixture
async def test_client():
    """Provides async HTTP test client"""
    async with AsyncClient(base_url="http://test") as client:
        yield client
```

### Test Data Fixtures (/tests/fixtures/):

- **users.json** - Test user data (20 users)
- **organizations.json** - Test organizations (10 orgs)
- **workflows.json** - Test workflow definitions (15 workflows)
- **documents.json** - Test documents (50 documents)

---

## 🚀 Quick Start Commands

### Run All Tests:
```bash
# Via Project Agent API
curl -X POST http://localhost:8060/api/tests/run \
  -H "Content-Type: application/json" \
  -d '{"suite": "all", "coverage": true}'

# Via bash script
cd /tests
./run_tests.sh all
```

### Check Coverage:
```bash
# Via Project Agent API
curl http://localhost:8060/api/tests/coverage | jq

# Via pytest
cd /tests
pytest --cov=. --cov-report=html
```

### Generate Tests:
```bash
# Via Project Agent API
curl -X POST http://localhost:8060/api/tests/generate \
  -H "Content-Type: application/json" \
  -d '{
    "component": "bia-service",
    "coverage_threshold": 85
  }'
```

---

## 📚 Related Documentation

- **Config:** `/tests/TEST_INFRASTRUCTURE_CONFIG.yaml`
- **Main README:** `/tests/README.md`
- **Structure:** `/tests/README_STRUCTURE.md`
- **pytest.ini:** `/tests/pytest.ini`
- **conftest.py:** `/tests/conftest.py`

---

## 🔗 Integration Points

### With DevOps Agent (8058):
- CI/CD pipeline execution
- Automated deployment triggers
- Environment management

### With EventBus (8001):
- Event-driven test triggers
- Test result broadcasting
- Coverage alerts

### With Monitoring (Prometheus/Grafana):
- Real-time metrics
- Coverage dashboards
- Performance tracking

---

## ✅ Checklist для Project Agent

### Daily:
- [ ] Monitor test coverage across all components
- [ ] Generate missing tests for coverage gaps
- [ ] Analyze test execution performance
- [ ] Report test failures to team

### Weekly:
- [ ] Review test quality metrics
- [ ] Update test fixtures with new scenarios
- [ ] Optimize slow-running tests
- [ ] Generate test quality report

### Monthly:
- [ ] Audit test effectiveness
- [ ] Update testing standards
- [ ] Optimize test infrastructure
- [ ] Review and archive obsolete tests

---

**Maintained by:** Project Agent (Port 8060)
**Last Updated:** 2025-10-11
**Version:** 1.0.0
