# 🧪 Карта Всех Тестов в Проекте (ОБНОВЛЕНО)

**Дата обновления:** 11 октября 2025
**Статус:** ✅ Тесты централизованы в `/tests`

---

## 🎉 ОБНОВЛЕНИЕ: Централизация Тестов

Все тесты были перенесены в `/tests` для лучшей организации и удобства запуска.

### Новая Структура:
```
/Users/MD/AI-Platform-ISO/tests/
├── unit/                          # Юнит-тесты (быстрые, изолированные)
│   ├── platform-services/         # 9 сервисов
│   ├── intelligent-core/          # 8 компонентов
│   └── infrastructure/            # 5 компонентов
├── integration/                   # Интеграционные тесты
├── e2e/                          # End-to-end тесты
├── performance/                   # Performance тесты
├── conftest.py                   # Глобальные фикстуры
├── pytest.ini                    # Pytest конфигурация
└── run_tests.sh                  # Скрипт для запуска тестов
```

---

## 🚀 Быстрый Старт

### Запуск Всех Тестов
```bash
cd /Users/MD/AI-Platform-ISO

# Используя bash скрипт (рекомендуется)
./tests/run_tests.sh all

# Или используя pytest напрямую
pytest tests/
```

### Запуск По Категориям
```bash
# Только unit тесты
./tests/run_tests.sh unit

# Только integration тесты
./tests/run_tests.sh integration

# Только e2e тесты
./tests/run_tests.sh e2e

# Platform services
./tests/run_tests.sh platform

# Intelligent core
./tests/run_tests.sh intelligent

# Infrastructure
./tests/run_tests.sh infrastructure
```

### Запуск Конкретного Сервиса
```bash
# BIA Service
./tests/run_tests.sh bia

# Risk Service
./tests/run_tests.sh risk

# Workflow Intelligence
./tests/run_tests.sh workflow

# AI Orchestration
./tests/run_tests.sh orchestration
```

---

## 📊 Статистика Тестов

### Platform Services (9 сервисов с тестами)
| Сервис | Директория | Статус |
|--------|------------|--------|
| BIA Service | `tests/unit/platform-services/bia-service/` | ✅ |
| Risk Service | `tests/unit/platform-services/risk-service/` | ✅ |
| Compliance Service | `tests/unit/platform-services/compliance-service/` | ✅ |
| Governance Service | `tests/unit/platform-services/governance-service/` | ✅ |
| Learning Service | `tests/unit/platform-services/learning-service/` | ✅ |
| Planning Service | `tests/unit/platform-services/planning-service/` | ✅ |
| Plans Service | `tests/unit/platform-services/plans-service/` | ✅ |
| Response Service | `tests/unit/platform-services/response-service/` | ✅ |
| Digital Twin | `tests/unit/platform-services/digital-twin/` | ✅ |

### Intelligent Core (8 компонентов с тестами)
| Компонент | Директория | Количество Тестов |
|-----------|------------|-------------------|
| Workflow Intelligence | `tests/unit/intelligent-core/workflow-intelligence/` | 12+ файлов |
| AI Orchestration | `tests/unit/intelligent-core/ai-orchestration/` | 10 файлов |
| Expertise Center | `tests/unit/intelligent-core/expertise-center/` | 3 поддиректории |
| System BCM | `tests/unit/intelligent-core/system-bcm/` | ✅ |
| Coordination Center | `tests/unit/intelligent-core/coordination-center/` | ✅ |
| AI Foundation | `tests/unit/intelligent-core/ai-foundation/` | 2 поддиректории |
| Community Intelligence | `tests/unit/intelligent-core/community-intelligence/` | ✅ |
| Workflow Engine | `tests/unit/intelligent-core/workflow-engine/` | ✅ |

### Infrastructure (5 компонентов с тестами)
| Компонент | Директория | Статус |
|-----------|------------|--------|
| EventBus | `tests/unit/infrastructure/eventbus/` | ✅ |
| Balancer Service | `tests/unit/infrastructure/balancer-service/` | ✅ |
| API Gateway | `tests/unit/infrastructure/api-gateway/` | ✅ |
| MIO Manager | `tests/unit/infrastructure/mio-manager/` | ✅ |
| Project Agent | `tests/unit/infrastructure/project-agent/` | ✅ |

---

## 🏷️ Маркеры Тестов

### По Типу
```python
@pytest.mark.unit           # Юнит-тесты (быстрые)
@pytest.mark.integration    # Интеграционные тесты
@pytest.mark.e2e           # End-to-end тесты
@pytest.mark.slow          # Медленные тесты
@pytest.mark.security      # Security тесты
@pytest.mark.performance   # Performance тесты
```

### По Категории
```python
@pytest.mark.platform_services   # Platform services
@pytest.mark.intelligent_core    # Intelligent core
@pytest.mark.infrastructure      # Infrastructure
```

### По Требованиям
```python
@pytest.mark.requires_db        # Требуется БД
@pytest.mark.requires_redis     # Требуется Redis
@pytest.mark.requires_temporal  # Требуется Temporal
@pytest.mark.requires_llm       # Требуется LLM API
```

### Примеры Использования
```bash
# Запустить только unit тесты
pytest tests/ -m "unit"

# Запустить быстрые тесты (исключить медленные)
pytest tests/ -m "not slow"

# Запустить security тесты
pytest tests/ -m "security"

# Запустить тесты platform-services без медленных
pytest tests/ -m "platform_services and not slow"
```

---

## 📂 Детальная Структура

### Unit Tests

#### Platform Services
```
tests/unit/platform-services/
├── bia-service/tests/
├── risk-service/tests/
├── compliance-service/tests/
├── governance-service/tests/
├── learning-service/tests/
├── planning-service/tests/
├── plans-service/tests/
├── response-service/tests/
└── digital-twin/tests/
```

#### Intelligent Core
```
tests/unit/intelligent-core/
├── workflow-intelligence/tests/
│   ├── test_temporal_connection.py
│   ├── test_case_collector.py
│   ├── test_case_library.py
│   ├── test_rls.py
│   ├── test_sql_injection.py
│   └── api_tests/
│       ├── test_analysis.py
│       ├── test_health.py
│       └── test_cases.py
│
├── ai-orchestration/tests/
│   ├── test_orchestrator.py
│   ├── test_decision_center.py
│   ├── test_safety.py
│   ├── test_memory.py
│   ├── test_e2e.py
│   └── load_test.py
│
├── expertise-center/
│   ├── ai-office/tests/
│   ├── ai-experts/tests/
│   └── service/tests/
│
└── ... (другие компоненты)
```

#### Infrastructure
```
tests/unit/infrastructure/
├── eventbus/tests/
├── balancer-service/tests/
├── api-gateway/tests/
├── mio-manager/tests/
└── project-agent/tests/
```

### Integration Tests
```
tests/integration/
├── test_platform_services_integration.py
│   ├── TestPlatformServicesIntegration
│   ├── TestDatabaseIntegration
│   └── TestEventBusIntegration
│
└── test_intelligent_core_integration.py
    ├── TestIntelligentCoreIntegration
    ├── TestTemporalIntegration
    └── TestAIIntegration
```

### E2E Tests
```
tests/e2e/
└── test_full_bcm_workflow.py
    ├── TestBCMWorkflowE2E
    │   ├── test_complete_bia_workflow
    │   ├── test_incident_response_workflow
    │   └── test_compliance_audit_workflow
    │
    └── TestUserJourneys
        ├── test_bcm_manager_daily_workflow
        ├── test_auditor_review_workflow
        └── test_executive_dashboard_view
```

---

## 🔧 Конфигурация

### pytest.ini
```ini
[pytest]
testpaths = tests
python_files = test_*.py
asyncio_mode = auto

markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow tests
    security: Security tests
    performance: Performance tests
    # ... и другие
```

### conftest.py

Глобальные фикстуры доступные всем тестам:

**Database:**
- `db_session` - Database session с автоматическим rollback
- `database_url` - Test database URL

**Cache/Redis:**
- `redis_client` - Fake Redis (in-memory)
- `mock_cache` - Mock cache client

**EventBus:**
- `mock_eventbus` - Mock EventBus client

**AI Foundation:**
- `mock_llm_client` - Mock LLM client
- `mock_rag_pipeline` - Mock RAG pipeline
- `mock_ml_predictor` - Mock ML predictor
- `mock_qdrant` - Mock Qdrant vector store

**Temporal:**
- `mock_temporal_client` - Mock Temporal client

**Test Data:**
- `sample_workflow_context` - Sample workflow data
- `sample_organization` - Sample org data
- `sample_case_data` - Sample case data
- `sample_user` - Sample user data

**Security:**
- `sql_injection_patterns` - SQL injection patterns
- `xss_patterns` - XSS attack patterns

---

## 📈 Coverage Reports

### Генерация Coverage Report
```bash
# HTML report
./tests/run_tests.sh coverage

# Открыть HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Terminal report
pytest tests/ --cov=platform-services --cov=intelligent-core --cov=infrastructure --cov-report=term-missing
```

### Текущее Coverage
- **Platform Services:** ~53% (9/17 сервисов с тестами)
- **Intelligent Core:** ~100% (8/8 компонентов с тестами)
- **Infrastructure:** ~45% (5/11 компонентов с тестами)

---

## 🎯 Команды Для Разработчиков

### Запуск Тестов

```bash
# Все тесты
pytest tests/

# Только unit
pytest tests/unit/ -m "unit"

# Только integration
pytest tests/integration/ -m "integration"

# Только e2e
pytest tests/e2e/ -m "e2e"

# Быстрые тесты
pytest tests/ -m "not slow"

# Security тесты
pytest tests/ -m "security"

# Конкретный сервис
pytest tests/unit/platform-services/bia-service/ -v

# Конкретный тест
pytest tests/unit/platform-services/bia-service/test_main.py::test_specific_function -v

# С покрытием
pytest tests/ --cov=platform-services --cov=intelligent-core --cov=infrastructure --cov-report=html

# Остановиться на первой ошибке
pytest tests/ -x

# Перезапустить только failed тесты
pytest tests/ --lf

# Параллельный запуск (требует pytest-xdist)
pytest tests/ -n auto

# С выводом print
pytest tests/ -s

# С debugger
pytest tests/ --pdb
```

### Используя Test Runner

```bash
# Bash скрипт
./tests/run_tests.sh all
./tests/run_tests.sh unit
./tests/run_tests.sh platform
./tests/run_tests.sh bia
./tests/run_tests.sh coverage
./tests/run_tests.sh help

# Python скрипт
python tests/run_tests.py all
python tests/run_tests.py unit
python tests/run_tests.py platform
python tests/run_tests.py coverage
python tests/run_tests.py specific tests/unit/platform-services/bia-service/
```

---

## ✅ Чек-лист Миграции

- [x] Platform Services тесты перенесены (9 сервисов)
- [x] Intelligent Core тесты перенесены (8 компонентов)
- [x] Infrastructure тесты перенесены (5 компонентов)
- [x] Integration тесты созданы
- [x] E2E тесты созданы
- [x] pytest.ini обновлен
- [x] conftest.py настроен
- [x] Test runners созданы (Bash + Python)
- [x] Документация создана (README_STRUCTURE.md)
- [x] TESTS_MAP.md обновлен

---

## 📚 Дополнительная Документация

### Основные Документы
- **`/tests/README_STRUCTURE.md`** - Полная документация по структуре тестов
- **`/tests/conftest.py`** - Глобальные фикстуры и конфигурация
- **`/tests/pytest.ini`** - Pytest настройки
- **`/tests/run_tests.sh`** - Bash test runner
- **`/tests/run_tests.py`** - Python test runner

### Примеры Тестов
- **Unit:** `tests/unit/platform-services/bia-service/`
- **Integration:** `tests/integration/test_platform_services_integration.py`
- **E2E:** `tests/e2e/test_full_bcm_workflow.py`

---

## 🚨 Важные Заметки

### Миграция
1. **Оригинальные тесты:** Скопированы (не перемещены) для обратной совместимости
2. **Старые директории:** Можно удалить старые `tests/` в сервисах после проверки
3. **Import paths:** Некоторые импорты могут требовать обновления

### CI/CD
Обновите CI/CD pipeline для использования новой структуры:

```yaml
# .github/workflows/tests.yml
- name: Run tests
  run: ./tests/run_tests.sh all

# Или для coverage
- name: Run tests with coverage
  run: ./tests/run_tests.sh coverage
```

### Новые Тесты
При создании новых тестов используйте централизованную структуру:

```bash
# Platform service test
tests/unit/platform-services/my-service/test_my_feature.py

# Intelligent core test
tests/unit/intelligent-core/my-component/test_my_feature.py

# Integration test
tests/integration/test_my_integration.py
```

---

## 🎓 Best Practices

### 1. Используйте Маркеры
```python
@pytest.mark.unit
@pytest.mark.platform_services
def test_something():
    pass
```

### 2. Используйте Фикстуры
```python
async def test_workflow(db_session, mock_eventbus):
    # Используйте глобальные фикстуры
    pass
```

### 3. Тестируйте Одну Вещь
```python
def test_bia_calculates_rto():  # Good
    pass

def test_everything():  # Bad
    pass
```

### 4. Используйте Async для Async Кода
```python
async def test_async_function():
    result = await some_async_function()
    assert result == expected
```

### 5. Группируйте Связанные Тесты
```python
class TestBIACalculation:
    def test_rto_calculation(self):
        pass

    def test_rpo_calculation(self):
        pass
```

---

## 🔍 Debugging

### Запустить Конкретный Тест
```bash
pytest tests/unit/platform-services/bia-service/test_main.py::test_specific -v
```

### С Выводом Print
```bash
pytest tests/ -s
```

### С Debugger
```bash
pytest tests/ --pdb
```

### Verbose Mode
```bash
pytest tests/ -vv
```

---

## 📞 Помощь

### Показать Список Всех Маркеров
```bash
pytest --markers
```

### Показать Все Фикстуры
```bash
pytest --fixtures
```

### Показать Помощь Test Runner
```bash
./tests/run_tests.sh help
```

---

**Последнее обновление:** 11 октября 2025
**Версия:** 2.0 (Централизованная структура)
**Статус:** ✅ Готово к использованию

Все тесты теперь в `/tests` - наслаждайтесь централизованным тестированием! 🎉
