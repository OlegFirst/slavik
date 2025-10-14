# 🧪 MIO Manager Tests

## Запуск тестов

### Все тесты
```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/mio-manager
pytest tests/ -v
```

### Конкретный файл
```bash
pytest tests/test_database.py -v
```

### С coverage
```bash
pytest --cov=. --cov-report=html tests/
open htmlcov/index.html
```

## Структура тестов

- `test_database.py` - Database operations
- `test_api.py` - API endpoints (TODO)
- `test_automation_toolkit.py` - Automation Toolkit (TODO)
- `test_response_engine.py` - Response Engine (TODO)
- `test_workflows.py` - Workflows (TODO)

## Требования

```bash
pip install pytest pytest-asyncio pytest-cov
```
