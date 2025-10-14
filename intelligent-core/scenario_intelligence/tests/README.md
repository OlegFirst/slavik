# Scenario Intelligence Tests

Комплексное тестирование Системы Сценарного Интеллекта.

## 📁 Структура

```
tests/
├─ unit/                      # Модульные тесты
│  ├─ test_engines.py        # Тесты всех движков
│  ├─ test_registry.py       # Тесты Registry
│  └─ test_learner.py        # Тесты Learner
│
├─ integration/               # Интеграционные тесты
│  ├─ test_db_integration.py # PostgreSQL integration [TODO]
│  ├─ test_rag_integration.py # Qdrant integration [TODO]
│  └─ test_eventbus.py       # EventBus integration [TODO]
│
└─ e2e/                       # End-to-end тесты
   └─ test_full_system.py    # Полный системный тест

## 🚀 Запуск тестов

### Все тесты:
```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/scenario-intelligence
pytest tests/ -v
```

### Unit тесты:
```bash
pytest tests/unit/ -v
```

### Integration тесты:
```bash
pytest tests/integration/ -v
```

### E2E тесты:
```bash
pytest tests/e2e/ -v
```

### Конкретный тест:
```bash
pytest tests/unit/test_engines.py -v
```

### С coverage:
```bash
pytest tests/ --cov=. --cov-report=html
```

## 📊 Текущий статус

### ✅ Реализовано:
- **Unit Tests**:
  - `test_engines.py` - тесты всех 5 движков (13 тестов)
  - `test_registry.py` - тесты Registry (7 тестов)
  - `test_learner.py` - тесты Learner (6 тестов)
- **E2E Tests**:
  - `test_full_system.py` - полный системный тест

### 🔄 TODO:
- **Integration Tests**:
  - PostgreSQL integration
  - Qdrant RAG integration
  - EventBus integration
  - Service Discovery integration

## 📝 Соглашения

### Именование тестов:
- `test_<component>_<action>` - для unit тестов
- `test_<integration>_<scenario>` - для integration тестов
- `test_<workflow>` - для e2e тестов

### Структура теста:
```python
class TestComponent:
    """Tests for Component"""

    @pytest.mark.asyncio
    async def test_something(self):
        """Test that something works correctly"""
        # Arrange
        ...

        # Act
        ...

        # Assert
        ...
```

### Маркеры:
- `@pytest.mark.asyncio` - для async тестов
- `@pytest.mark.integration` - для интеграционных тестов
- `@pytest.mark.slow` - для медленных тестов
- `@pytest.mark.skip` - для пропуска тестов

## 🎯 Coverage Target

**Целевой coverage**: 80%

**Текущий coverage**: ~60% (только unit + e2e)

## 🔧 Требования

```bash
pip install pytest pytest-asyncio pytest-cov
```

## 📚 Примеры

### Запустить один тест:
```bash
pytest tests/unit/test_engines.py::TestScenarioEngine::test_scenario_engine_initialization -v
```

### Запустить с выводом print:
```bash
pytest tests/ -v -s
```

### Запустить только быстрые тесты:
```bash
pytest tests/ -v -m "not slow"
```

## 🐛 Debugging

### С pdb:
```bash
pytest tests/ --pdb
```

### С подробным traceback:
```bash
pytest tests/ -v --tb=long
```

### С логами:
```bash
pytest tests/ -v --log-cli-level=DEBUG
```
