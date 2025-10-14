# Integration Tests — Real Infrastructure

**Тесты с реальной runtime инфраструктурой**

---

## 🎯 Назначение

Интеграционные тесты проверяют работу модулей с **реальной инфраструктурой**:
- EventBus (Memory/Redis backends)
- RabbitMQ message queue
- PostgreSQL database
- Service Discovery
- WebSocket connections

---

## 📋 Требования

### Минимальные (Memory backend):
```bash
# Только Python зависимости
pip install -r requirements-test.txt
```

### Полные (все сервисы):
```bash
# PostgreSQL
brew install postgresql@14
brew services start postgresql@14

# Redis
brew install redis
brew services start redis

# RabbitMQ
brew install rabbitmq
brew services start rabbitmq
```

---

## 🚀 Запуск тестов

### 1. Только unit тесты (без инфраструктуры):
```bash
pytest tests/unit/ -v
```

### 2. Integration тесты (минимальные, Memory backend):
```bash
# Используют in-memory EventBus, не требуют сервисов
pytest tests/integration/ -v -m "integration and not requires_redis and not requires_rabbitmq"
```

### 3. Full integration (все сервисы):
```bash
# Требуют запущенные Redis, RabbitMQ, PostgreSQL
pytest tests/integration/ -v -m integration
```

### 4. Конкретные тесты:
```bash
# EventBus integration
pytest tests/integration/test_workflow_with_eventbus.py -v

# With coverage
pytest tests/integration/test_workflow_with_eventbus.py --cov=intelligent_core --cov-report=html
```

---

## 🔧 Настройка окружения

### Environment Variables:

```bash
# Test database (создайте отдельную БД для тестов!)
export TEST_DATABASE_URL="postgresql+asyncpg://localhost/test_ai_platform"

# Redis
export REDIS_URL="redis://localhost:6379"

# RabbitMQ
export RABBITMQ_URL="amqp://guest:guest@localhost:5672/"

# Optional: LLM API keys (для полных E2E тестов)
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
```

### Создание тестовой БД:

```bash
# PostgreSQL
createdb test_ai_platform

# Применить миграции к тестовой БД
export DATABASE_URL="postgresql://localhost/test_ai_platform"
python infrastructure/database/apply_migrations_simple.py
```

---

## 📊 Структура тестов

### Уровни тестирования:

```
tests/
├── unit/                           # Unit тесты (изолированные, моки)
│   ├── workflow_intelligence/
│   ├── ai-foundation/
│   └── orchestration/
│
├── integration/                    # Integration тесты (реальная инфра)
│   ├── conftest.py                    # Fixtures с реальными сервисами
│   ├── test_workflow_with_eventbus.py # EventBus integration
│   ├── test_bia_with_database.py      # PostgreSQL integration
│   ├── test_rabbitmq_workflows.py     # RabbitMQ integration
│   └── test_service_discovery.py      # Service Discovery
│
└── e2e/                            # End-to-end тесты (полные сценарии)
    ├── test_complete_bia_workflow.py
    └── test_risk_assessment_flow.py
```

---

## 🧪 Примеры тестов

### 1. Unit Test (mock/fixtures):
```python
@pytest.mark.asyncio
async def test_workflow_engine_start(mock_eventbus, mock_storage):
    """Unit test with mocks"""
    engine = WorkflowEngine(storage=mock_storage, event_bus=mock_eventbus)
    context = WorkflowContext(workflow_id="test")

    result = await engine.start_workflow(context)

    assert result is not None
    mock_eventbus.publish.assert_called_once()
```

### 2. Integration Test (real EventBus):
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_workflow_with_real_eventbus(real_eventbus):
    """Integration test with real EventBus"""
    events = []

    async def handler(event):
        events.append(event)

    await real_eventbus.subscribe("workflow.*", handler)

    # Use real workflow engine
    engine = WorkflowEngine(storage=..., event_bus=real_eventbus)
    await engine.start_workflow(context)

    await asyncio.sleep(0.1)
    assert len(events) > 0  # Real events received!
```

### 3. E2E Test (complete scenario):
```python
@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.asyncio
async def test_complete_bia_workflow(
    real_eventbus,
    test_db_session,
    real_llm_client  # Real Claude API
):
    """Complete BIA workflow end-to-end"""
    # 1. Start workflow
    # 2. Run all BIA activities
    # 3. Verify results in database
    # 4. Check events published
    # 5. Validate final report
```

---

## 🎯 Что тестируем

### Интеграционные тесты проверяют:

**1. EventBus Integration:**
- ✅ Events публикуются корректно
- ✅ Subscriptions работают
- ✅ Wildcard patterns работают
- ✅ Redis backend корректен (если запущен)

**2. Database Integration:**
- ✅ Workflow context сохраняется
- ✅ State transitions записываются
- ✅ RLS policies работают
- ✅ Transactions корректны

**3. Message Queue Integration:**
- ✅ Tasks публикуются в RabbitMQ
- ✅ Consumers получают задачи
- ✅ DLQ обрабатывает ошибки
- ✅ Priority queues работают

**4. Service Discovery:**
- ✅ Services регистрируются
- ✅ Health checks выполняются
- ✅ ISO mapping корректен
- ✅ Service lookup работает

---

## ⚠️ Важно!

### DO:
✅ Используйте **отдельную тестовую БД** (не production!)
✅ Очищайте данные после тестов (transactions + rollback)
✅ Используйте fixtures для setup/teardown
✅ Изолируйте тесты (один тест = один сценарий)

### DON'T:
❌ НЕ запускайте на production БД
❌ НЕ оставляйте мусор в БД
❌ НЕ делайте тесты зависимыми друг от друга
❌ НЕ используйте production API ключи

---

## 🏃 Continuous Integration

### GitHub Actions workflow:

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  integration:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_DB: test_ai_platform
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      rabbitmq:
        image: rabbitmq:3.12
        options: >-
          --health-cmd "rabbitmq-diagnostics -q ping"
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
          pip install -r requirements-test.txt

      - name: Run integration tests
        env:
          TEST_DATABASE_URL: postgresql+asyncpg://postgres:test@localhost/test_ai_platform
          REDIS_URL: redis://localhost:6379
          RABBITMQ_URL: amqp://guest:guest@localhost:5672/
        run: |
          pytest tests/integration/ -v -m integration --cov=intelligent_core --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 📈 Прогресс

### Current Status:
- ✅ Integration test infrastructure ready
- ✅ Fixtures для всех сервисов
- ✅ EventBus integration tests
- 🔄 Database integration tests (in progress)
- 🔄 RabbitMQ integration tests (in progress)
- ⏳ Service Discovery tests (planned)
- ⏳ Full E2E tests (planned)

### Next Steps:
1. Создать тесты для каждого модуля с реальной БД
2. Добавить RabbitMQ integration tests
3. Создать E2E тесты для полных сценариев
4. Настроить CI/CD с integration tests

---

## 🔍 Debugging

### Run with verbose output:
```bash
pytest tests/integration/ -vv -s
```

### Run specific test:
```bash
pytest tests/integration/test_workflow_with_eventbus.py::TestWorkflowEngineWithEventBus::test_workflow_publishes_events_to_eventbus -vv
```

### With pdb debugger:
```bash
pytest tests/integration/ --pdb
```

### Check infrastructure:
```bash
# Redis
redis-cli ping

# RabbitMQ
rabbitmqctl status

# PostgreSQL
psql test_ai_platform -c "SELECT version();"
```

---

## 📚 Resources

- [Unit Tests](../unit/README.md)
- [Test Automation Guide](../../docs/TEST_AUTOMATION_GUIDE.md)
- [EventBus Documentation](../../infrastructure/runtime/eventbus/README.md)
- [Service Discovery](../../infrastructure/runtime/service-discovery/README.md)

---

*Integration tests bring us closer to production reality! 🚀*
