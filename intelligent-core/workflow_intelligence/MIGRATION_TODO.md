# workflow_intelligence Migration TODO

## ✅ COMPLETED:

1. ✅ **storage/postgres_adapter.py** - МИГРИРОВАН на SQLAlchemy
2. ✅ **storage/rls_context.py** - МИГРИРОВАН на SQLAlchemy
3. ✅ **__init__.py** - Добавлен `initialize()` с PostgresStorageAdapter + CaseRepository

## ⏳ СЛЕДУЮЩИЕ ШАГИ:

4. **Интеграция с ai-foundation** (RAG, LLM, ML) - 2-3h
5. **Integration tests** - 1-2h

## 📝 NOTES:

- `InMemoryStorageAdapter` сохранён для тестов (в core/workflow_engine.py)
- `quick_start()` deprecated, использует моки только для dev/testing
- Production код должен использовать `initialize(module, state_machine, db_manager)`

## ✅ Что сделано:

### 1. ✅ Переписать storage на SQLAlchemy (DONE)

**Файлы:**
- ✅ `storage/postgres_adapter.py` - мигрирован
- ✅ `storage/rls_context.py` - мигрирован

**Что сделано:**
- Заменили `asyncpg.Pool` на `DatabaseManager` из `shared.database`
- Все SQL запросы используют `text()` и named parameters (`:param`)
- RLS context теперь работает с `AsyncSession`
- Добавлен helper `set_rls_context(session, tenant_id)`
- Обновлены `verify_rls_enabled` и `test_rls_isolation`
- Все методы используют `async for session in db_manager.get_session()`

**Изменения:**
```python
# БЫЛО:
import asyncpg
self.pool = await asyncpg.create_pool(...)
await conn.execute("INSERT ... VALUES ($1, $2)", val1, val2)

# СТАЛО:
from shared.database import DatabaseManager
self.db_manager = DatabaseManager()
await session.execute(
    text("INSERT ... VALUES (:val1, :val2)"),
    {"val1": val1, "val2": val2}
)
```

### 2. ✅ Добавить production инициализацию (DONE)

**Файлы:**
- ✅ `__init__.py` - добавлен `initialize()` function

**Что сделано:**
```python
# Новый production helper
async def initialize(module, state_machine, db_manager, vector_db_client=None):
    storage = PostgresStorageAdapter(db_manager)  # Real storage
    case_repository = CaseRepository(session, vector_db_client)  # Real case library
    advisor = ContextAdvisor(workflow, case_repository)  # Real advisor
    return workflow, advisor
```

**Для production:**
```python
from workflow_intelligence import initialize
from shared.database import get_db_manager

db_manager = get_db_manager()
workflow, advisor = await initialize("bia", state_machine, db_manager)
```

**Для тестов:**
- `quick_start()` остаётся (deprecated) - использует InMemoryStorageAdapter
- `InMemoryStorageAdapter` сохранён в workflow_engine.py для тестов

### 3. Интегрировать с ai-foundation (2-3h)

**Добавить в workflow_engine.py:**
```python
from ai_foundation import RAGPipeline, LLMRouter, ContextBuilder

class WorkflowEngine:
    def __init__(self):
        self.rag = RAGPipeline()
        self.llm = LLMRouter()
        self.context_builder = ContextBuilder()
```

**Использовать в:**
- `ai/context_advisor.py` - использовать ai-foundation.ContextBuilder
- `ai/journey_predictor.py` - использовать ai-foundation.ml
- `case_library/repository.py` - использовать ai-foundation.RAGPipeline

### 4. Убрать внутренние ml/ (если есть) (1h)

Проверить есть ли `workflow_intelligence/ml/` - если есть, использовать вместо этого `ai-foundation.ml`.

### 5. Интегрировать с shared/ (1-2h)

**Заменить:**
- Все database connections → `shared.database`
- Все cache → `shared.cache`
- Все eventbus → `shared.eventbus`
- Все auth → `shared.auth`

### 6. Создать requirements.txt (30min)

Добавить зависимости:
```
# Core
temporalio>=1.18.1
sqlalchemy[asyncio]>=2.0.0
asyncpg>=0.29.0

# Shared (from parent)
# Uses: shared.database, shared.cache, shared.eventbus

# AI Foundation
# Uses: ai_foundation (RAG, LLM, ML)
```

### 7. Тесты обновить (2h)

- Обновить тесты использовать реальную БД (не моки)
- Integration tests с PostgreSQL
- Integration tests с Temporal

## 📊 Timeline

| Задача | Время | Приоритет |
|--------|-------|-----------|
| SQLAlchemy migration | 3-4h | 🔴 HIGH |
| Убрать моки | 1h | 🔴 HIGH |
| Интеграция ai-foundation | 2-3h | 🟡 MEDIUM |
| Убрать внутренние ml/ | 1h | 🟡 MEDIUM |
| Интеграция shared/ | 1-2h | 🟡 MEDIUM |
| requirements.txt | 30min | 🟢 LOW |
| Тесты | 2h | 🟢 LOW |
| **TOTAL** | **10-13h** | |

## 🎯 Начать с:

**PRIORITY 1**: SQLAlchemy migration (storage/postgres_adapter.py + rls_context.py)
