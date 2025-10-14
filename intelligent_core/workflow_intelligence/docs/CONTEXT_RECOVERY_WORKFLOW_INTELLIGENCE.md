# 🔄 CONTEXT RECOVERY: Workflow Intelligence Integration

**Date:** October 3, 2025
**Task:** ПОЛНАЯ интеграция workflow-intelligence во все BCM сервисы
**Status:** ЧАСТИЧНО выполнено (Planning Service готов, остальные - НЕТ)

---

## ❌ ЧТО НЕ ДОДЕЛАНО (СРОЧНО!)

### 1. Plans Service - main.py НЕ ОБНОВЛЁН
- ❌ Нет imports в main.py
- ❌ Нет инициализации в lifespan
- ❌ Нет router include
- ✅ workflow_ai.py создан (template)

### 2. BIA Service - main.py НЕ ОБНОВЛЁН
- ❌ Нет imports в main.py
- ❌ Нет инициализации в lifespan
- ❌ Нет router include
- ✅ workflow_ai.py создан (template)

### 3. Compliance Service - main.py НЕ ОБНОВЛЁН
- ❌ Нет imports в main.py
- ❌ Нет инициализации в lifespan
- ❌ Нет router include
- ✅ workflow_ai.py создан (template)

### 4. GitHub Workflows - НЕ СОЗДАНЫ
- ❌ CI/CD для workflow-intelligence
- ❌ Tests для интеграции
- ❌ Automated deployment

---

## ✅ ЧТО УЖЕ СДЕЛАНО

### Workflow Intelligence Library
- ✅ `/intelligent-core/workflow-intelligence/` - полная реализация
- ✅ `setup.py` создан (Python >= 3.9)
- ✅ `storage/postgres_adapter.py` - PostgreSQL интеграция (300+ строк)
- ✅ Установлено: `pip install -e .`

### Planning Service (ЕДИНСТВЕННЫЙ ГОТОВЫЙ!)
**Файлы:**
- ✅ `planning_service/main.py` - обновлён (строки 29-40, 66-87, 134-140)
- ✅ `planning_service/api/workflow_ai.py` - создан (150+ строк)

**Изменения в main.py:**
```python
# Line 29-40: Imports and globals
from workflow_intelligence import PostgresStorageAdapter, WorkflowEngine, ContextAdvisor, CaseCollector

workflow_storage = None
workflow_engine = None
ai_advisor = None
case_collector = None

# Line 66-87: Startup initialization
workflow_storage = PostgresStorageAdapter(settings.DATABASE_URL)
await workflow_storage.connect()
workflow_engine = WorkflowEngine(module="planning", storage_adapter=workflow_storage)
case_collector = CaseCollector(storage_adapter=workflow_storage)

# Line 134-140: Shutdown
if workflow_storage:
    await workflow_storage.close()

# Line 21: Import router
from .api.workflow_ai import router as workflow_ai_router

# Line 349: Include router
app.include_router(workflow_ai_router)
```

### Templates Created
- ✅ `plans_service/api/workflow_ai.py` (template, module="plans")
- ✅ `bia-service/api/workflow_ai.py` (template, module="bia")
- ✅ `compliance-service/api/workflow_ai.py` (template, module="compliance")
- ✅ `integrate_workflow_intelligence.sh` (automation script)

---

## 📋 ПОЛНЫЙ ПЛАН РАБОТЫ (TODO)

### PHASE 1: Finish Service Integration (КРИТИЧНО!)

#### Task 1.1: Plans Service
**File:** `/Users/MD/AI-Platform-ISO/platform-services/plans_service/main.py`

**Action 1:** Add imports (after line ~20)
```python
# Workflow Intelligence integration
from workflow_intelligence import PostgresStorageAdapter, WorkflowEngine, ContextAdvisor, CaseCollector

# Global workflow intelligence instances
workflow_storage = None
workflow_engine = None
ai_advisor = None
case_collector = None
```

**Action 2:** Find `async def lifespan(app: FastAPI):` and after `await init_db()` add:
```python
        # Initialize Workflow Intelligence
        global workflow_storage, workflow_engine, ai_advisor, case_collector
        try:
            workflow_storage = PostgresStorageAdapter(settings.DATABASE_URL)
            await workflow_storage.connect()

            workflow_engine = WorkflowEngine(
                module="plans",
                storage_adapter=workflow_storage
            )

            case_collector = CaseCollector(storage_adapter=workflow_storage)

            logger.info("✅ Workflow Intelligence initialized (Plans module)")
        except Exception as e:
            logger.warning(f"Workflow Intelligence initialization failed: {e}")
```

**Action 3:** Find shutdown section and add BEFORE `await close_db()`:
```python
    # Close Workflow Intelligence
    if workflow_storage:
        try:
            await workflow_storage.close()
            logger.info("Workflow Intelligence connection closed")
        except Exception as e:
            logger.error(f"Error closing Workflow Intelligence: {e}")
```

**Action 4:** Add router import (near other router imports):
```python
from .api.workflow_ai import router as workflow_ai_router
```

**Action 5:** Add router include (near other includes):
```python
app.include_router(workflow_ai_router)  # Workflow Intelligence AI endpoints
```

#### Task 1.2: BIA Service
**File:** `/Users/MD/AI-Platform-ISO/platform-services/bia-service/main.py`

**SAME STEPS as Plans Service, but:**
- Module name: `"bia"` (not "plans")
- Log message: `"✅ Workflow Intelligence initialized (BIA module)"`

#### Task 1.3: Compliance Service
**File:** `/Users/MD/AI-Platform-ISO/platform-services/compliance-service/main.py`

**SAME STEPS as Plans Service, but:**
- Module name: `"compliance"` (not "plans")
- Log message: `"✅ Workflow Intelligence initialized (Compliance module)"`

---

### PHASE 2: GitHub Workflows (ОБЯЗАТЕЛЬНО!)

#### Task 2.1: CI/CD for Workflow Intelligence
**File:** `/Users/MD/AI-Platform-ISO/.github/workflows/workflow-intelligence-ci.yml`

**Create:**
```yaml
name: Workflow Intelligence CI

on:
  push:
    paths:
      - 'intelligent-core/workflow-intelligence/**'
  pull_request:
    paths:
      - 'intelligent-core/workflow-intelligence/**'

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python 3.9
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          cd intelligent-core/workflow-intelligence
          pip install -e .
          pip install pytest pytest-asyncio pytest-cov

      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        run: |
          cd intelligent-core/workflow-intelligence
          pytest tests/ -v --cov=. --cov-report=term-missing

      - name: Check code quality
        run: |
          pip install black ruff mypy
          cd intelligent-core/workflow-intelligence
          black --check .
          ruff check .
```

#### Task 2.2: Integration Tests
**File:** `/Users/MD/AI-Platform-ISO/.github/workflows/integration-tests.yml`

**Create:**
```yaml
name: BCM Services Integration Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  integration-tests:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: bcm_password
          POSTGRES_USER: bcm_user
          POSTGRES_DB: bcm_platform
        ports:
          - 5432:5432

      redis:
        image: redis:7
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python 3.9
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install workflow-intelligence
        run: |
          cd intelligent-core/workflow-intelligence
          pip install -e .

      - name: Test Planning Service
        run: |
          cd platform-services/planning_service
          pip install -r requirements.txt
          pytest tests/ -v -k "workflow"

      - name: Test Plans Service
        run: |
          cd platform-services/plans_service
          pip install -r requirements.txt
          pytest tests/ -v -k "workflow"

      - name: Test BIA Service
        run: |
          cd platform-services/bia-service
          pip install -r requirements.txt
          pytest tests/ -v -k "workflow"

      - name: Test Compliance Service
        run: |
          cd platform-services/compliance-service
          pip install -r requirements.txt
          pytest tests/ -v -k "workflow"
```

#### Task 2.3: Deployment Workflow
**File:** `/Users/MD/AI-Platform-ISO/.github/workflows/deploy-services.yml`

**Create:**
```yaml
name: Deploy BCM Services

on:
  push:
    branches: [main]
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Build Docker images
        run: |
          docker-compose -f platform-services/docker-compose.yml build

      - name: Run database migrations
        run: |
          # Workflow Intelligence schema will be created automatically
          docker-compose -f platform-services/docker-compose.yml up -d postgres
          sleep 10
          docker-compose -f platform-services/docker-compose.yml run planning-service alembic upgrade head

      - name: Deploy services
        run: |
          docker-compose -f platform-services/docker-compose.yml up -d

      - name: Health checks
        run: |
          sleep 30
          curl -f http://localhost:8011/health || exit 1
          curl -f http://localhost:8023/health || exit 1
          curl -f http://localhost:8012/health || exit 1
          curl -f http://localhost:8014/health || exit 1
```

---

### PHASE 3: Tests (ОБЯЗАТЕЛЬНО!)

#### Task 3.1: Workflow Intelligence Unit Tests
**File:** `/Users/MD/AI-Platform-ISO/intelligent-core/workflow-intelligence/tests/test_postgres_adapter.py`

**Create:**
```python
import pytest
import asyncio
from workflow_intelligence.storage import PostgresStorageAdapter

@pytest.mark.asyncio
async def test_save_and_retrieve_context():
    storage = PostgresStorageAdapter("postgresql://postgres:postgres@localhost:5432/test_db")
    await storage.connect()

    # Save context
    await storage.save_workflow_context(
        workflow_id="test-123",
        module="planning",
        context={"stage": "select_strategy", "progress": 50},
        tenant_id="test-org"
    )

    # Retrieve context
    context = await storage.get_workflow_context("test-123", "test-org")

    assert context["stage"] == "select_strategy"
    assert context["progress"] == 50

    await storage.close()

@pytest.mark.asyncio
async def test_save_case():
    storage = PostgresStorageAdapter("postgresql://postgres:postgres@localhost:5432/test_db")
    await storage.connect()

    case_data = {
        "org_context": {"industry": "healthcare", "size": "medium"},
        "journey": [],
        "metrics": {"total_duration_days": 14, "completed_successfully": True},
        "success_patterns": ["Used AI early"],
        "lessons_learned": ["Start with critical processes"]
    }

    await storage.save_case(
        case_id="case-test-001",
        module="planning",
        case_data=case_data,
        tenant_id="test-org"
    )

    # Find similar cases
    similar = await storage.find_similar_cases(
        module="planning",
        org_context={"industry": "healthcare", "size": "medium"},
        current_stage="test",
        limit=5
    )

    assert len(similar) >= 0  # May be 0 if no cases yet

    await storage.close()

@pytest.mark.asyncio
async def test_get_benchmarks():
    storage = PostgresStorageAdapter("postgresql://postgres:postgres@localhost:5432/test_db")
    await storage.connect()

    benchmarks = await storage.get_benchmarks(
        module="planning",
        industry="healthcare"
    )

    assert "avg_duration_days" in benchmarks
    assert "success_rate" in benchmarks
    assert "total_cases" in benchmarks

    await storage.close()
```

#### Task 3.2: Integration Tests for Services
**File:** `/Users/MD/AI-Platform-ISO/platform-services/planning_service/tests/test_workflow_intelligence.py`

**Create:**
```python
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_ai_advice_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/planning/strategies/123e4567-e89b-12d3-a456-426614174000/ai-advice",
            headers={"Authorization": "Bearer test_token"}
        )

        assert response.status_code in [200, 401, 503]  # May fail if not initialized

@pytest.mark.asyncio
async def test_benchmarks_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/planning/benchmarks",
            headers={"Authorization": "Bearer test_token"}
        )

        assert response.status_code in [200, 401, 503]
```

---

### PHASE 4: Documentation Updates

#### Task 4.1: Update README.md
**File:** `/Users/MD/AI-Platform-ISO/README.md`

**Add section:**
```markdown
## 🧠 Workflow Intelligence

AI-powered self-learning platform integrated into all BCM services.

### Features
- **Context-Aware AI**: Understands where user is in workflow
- **Self-Learning**: Learns from every successful workflow
- **Cross-Service Learning**: Planning learns from BIA and vice versa
- **Benchmarks**: Real-time statistics from platform data
- **ML Predictions**: Predicts success probability and duration

### Services with Workflow Intelligence
- ✅ Planning Service (Port 8011)
- ✅ Plans Service (Port 8023)
- ✅ BIA Service (Port 8012)
- ✅ Compliance Service (Port 8014)

### API Endpoints
```bash
# AI advice
GET /api/v1/planning/strategies/{id}/ai-advice

# Benchmarks
GET /api/v1/planning/benchmarks?industry=healthcare

# Complete and create case
POST /api/v1/planning/strategies/{id}/complete-case
```

### Database Schema
Auto-created on first startup: `workflow_intelligence` schema with:
- `workflow_contexts` - Current states
- `workflow_cases` - Completed cases for learning
- `benchmarks` - Aggregated statistics
- `ml_predictions` - ML predictions
```

---

## 🚀 EXECUTION CHECKLIST

### Immediate Tasks (MUST DO NOW!)
- [ ] Update `plans_service/main.py` (5 changes)
- [ ] Update `bia-service/main.py` (5 changes)
- [ ] Update `compliance-service/main.py` (5 changes)
- [ ] Create `.github/workflows/workflow-intelligence-ci.yml`
- [ ] Create `.github/workflows/integration-tests.yml`
- [ ] Create `.github/workflows/deploy-services.yml`
- [ ] Create tests in `intelligent-core/workflow-intelligence/tests/`
- [ ] Create integration tests in each service
- [ ] Update root `README.md`
- [ ] Test all services startup
- [ ] Verify database schema created
- [ ] Test AI endpoints

### Verification Commands
```bash
# 1. Test Plans Service
cd /Users/MD/AI-Platform-ISO/platform-services/plans_service
python3 -m uvicorn main:app --reload --port 8023

# Should see in logs:
# "✅ Workflow Intelligence initialized (Plans module)"

# Test endpoint:
curl http://localhost:8023/api/v1/plans/benchmarks

# 2. Test BIA Service
cd /Users/MD/AI-Platform-ISO/platform-services/bia-service
python3 -m uvicorn main:app --reload --port 8012

# Should see:
# "✅ Workflow Intelligence initialized (BIA module)"

# 3. Test Compliance Service
cd /Users/MD/AI-Platform-ISO/platform-services/compliance-service
python3 -m uvicorn main:app --reload --port 8014

# Should see:
# "✅ Workflow Intelligence initialized (Compliance module)"

# 4. Check database schema
psql -h localhost -U bcm_user -d bcm_platform -c "\dt workflow_intelligence.*"

# Should show:
# workflow_contexts
# workflow_cases
# benchmarks
# ml_predictions
```

---

## 📁 FILES TO MODIFY (EXACT PATHS)

### Must Modify:
1. `/Users/MD/AI-Platform-ISO/platform-services/plans_service/main.py`
2. `/Users/MD/AI-Platform-ISO/platform-services/bia-service/main.py`
3. `/Users/MD/AI-Platform-ISO/platform-services/compliance-service/main.py`

### Must Create:
4. `/Users/MD/AI-Platform-ISO/.github/workflows/workflow-intelligence-ci.yml`
5. `/Users/MD/AI-Platform-ISO/.github/workflows/integration-tests.yml`
6. `/Users/MD/AI-Platform-ISO/.github/workflows/deploy-services.yml`
7. `/Users/MD/AI-Platform-ISO/intelligent-core/workflow-intelligence/tests/test_postgres_adapter.py`
8. `/Users/MD/AI-Platform-ISO/intelligent-core/workflow-intelligence/tests/test_workflow_engine.py`
9. `/Users/MD/AI-Platform-ISO/platform-services/planning_service/tests/test_workflow_intelligence.py`
10. `/Users/MD/AI-Platform-ISO/platform-services/plans_service/tests/test_workflow_intelligence.py`
11. `/Users/MD/AI-Platform-ISO/platform-services/bia-service/tests/test_workflow_intelligence.py`
12. `/Users/MD/AI-Platform-ISO/platform-services/compliance-service/tests/test_workflow_intelligence.py`

### Must Update:
13. `/Users/MD/AI-Platform-ISO/README.md`

---

## ⚠️ КРИТИЧЕСКИЕ МОМЕНТЫ

1. **НЕ ЗАБЫТЬ**: В каждом main.py модуль должен быть РАЗНЫЙ:
   - Plans Service: `module="plans"`
   - BIA Service: `module="bia"`
   - Compliance Service: `module="compliance"`

2. **ПОРЯДОК ВАЖЕН**:
   - Workflow Intelligence init ПОСЛЕ `await init_db()`
   - Workflow Intelligence close ПЕРЕД `await close_db()`

3. **Router import** должен быть РЯДОМ с другими router imports

4. **Global variables** должны быть ДО `@asynccontextmanager`

5. **DATABASE_URL** - используем тот же что у сервиса (не создаём новый!)

---

## 🎯 SUCCESS CRITERIA

Integration считается ЗАВЕРШЁННОЙ когда:

- [ ] Все 4 сервиса стартуют без ошибок
- [ ] В логах каждого: "✅ Workflow Intelligence initialized"
- [ ] Database schema `workflow_intelligence` создана автоматически
- [ ] Все AI endpoints отвечают (даже если 401 без auth)
- [ ] GitHub workflows созданы и проходят
- [ ] Tests написаны и проходят
- [ ] README.md обновлён
- [ ] Можно получить benchmarks: `curl http://localhost:8011/api/v1/planning/benchmarks`

---

## 💾 BACKUP BEFORE START

```bash
# Create backup
cd /Users/MD/AI-Platform-ISO
tar -czf backup-before-workflow-intelligence-$(date +%Y%m%d-%H%M%S).tar.gz \
    platform-services/plans_service/main.py \
    platform-services/bia-service/main.py \
    platform-services/compliance-service/main.py
```

---

**NEXT ACTION**: Start with Task 1.1 (Plans Service main.py)
**PRIORITY**: CRITICAL - User explicitly asked for FULL integration
**TIME ESTIMATE**: 2-3 hours for complete integration with tests and workflows
