# 🚀 План работы для 4 Claude

**Дата**: 2025-10-06
**Команда**: 4 Claude разработчика
**Статус**: `doc-project/SPRINT_STATUS.md`

---

## 👤 Claude #1 (Я) - Координатор + Оркестратор

**Роль**: Tech Lead & Orchestration
**Статус**: ✅ RAG/LLM готов → Оркестратор

### Задачи:

1. ✅ **ai-foundation** - ГОТОВО
   - RAG + LLM интеграция завершена
   - Qdrant + Claude + OpenAI настроены
   - Коммиты: a5b4d4c, 68a512f

2. ⏳ **Оркестратор** (моя текущая работа):
   - Анализировать `intelligent-core/coordination-center/` (236K, готов)
   - Чистить `intelligent-core/ai-orchestration/` (928K → 400K)
   - Переместить 11 "органов" → `expertise-center/analyzers/`
   - Удалить дубликаты (agent_router, llm_clients, brain/)
   - **Принцип**: Оркестратор настраивается ПОД архитектуру!

3. **Координация команды**:
   - Обновлять `SPRINT_STATUS.md`
   - Синхронизировать работу между Claude
   - Решать конфликты и зависимости

### Документы:
- `doc-project/ORCHESTRATION_STRATEGY.md` - моя стратегия

---

## 👤 Claude #2 - workflow_intelligence + SQLAlchemy

**Роль**: Workflow Engine Specialist
**Фокус**: Миграция на SQLAlchemy

### КРИТИЧЕСКАЯ ЗАДАЧА:

**Переписать на SQLAlchemy** (вместо asyncpg):
- `intelligent-core/workflow_intelligence/storage/postgres_adapter.py`
- Использовать `shared.database.DatabaseManager`
- Сохранить RLS (Row Level Security)
- Убрать все прямые asyncpg вызовы

### Остальные задачи:

1. **Интеграция с ai-foundation**:
```python
from ai_foundation import RAGPipeline, LLMRouter, ContextBuilder
```

2. **Интеграция с shared**:
```python
from shared.database import get_db
from shared.cache import cached
from shared.auth import get_current_user
from shared.eventbus import EventPublisher
```

3. **Убрать моки**:
   - `InMemoryStorageAdapter` → PostgresStorageAdapter
   - `DemoCaseLibrary` → настоящий
   - Пустые папки удалить

4. **Тесты**:
   - Integration tests с реальной БД
   - Проверить RLS работает

### Координация:
- Ждать Temporal config от Claude #3
- Использовать ai-foundation от Claude #1

### Отчётность:
Обновлять в `doc-project/SPRINT_STATUS.md`:
```yaml
Claude #2:
  task: workflow_intelligence SQLAlchemy migration
  status: in_progress
  progress: "postgres_adapter.py - 40%"
  blockers: []
```

---

## 👤 Claude #3 - Infrastructure + Temporal

**Роль**: Infrastructure Specialist
**Фокус**: Temporal.io + RabbitMQ + Qdrant

### Задачи:

1. **Temporal.io** (https://cloud.temporal.io):
   - Настроить Temporal Cloud подключение
   - Создать workflow definitions для BCM
   - Интеграция с workflow_intelligence
   - Документация: `infrastructure/temporal/README.md`

2. **RabbitMQ (EventBus)**:
   - Проверить `shared.eventbus`
   - Создать топики для workflow events
   - Тесты pub/sub

3. **Qdrant (Vector DB)**:
   - Создать collections (уже есть скрипт в ai-foundation):
     - `bcm_knowledge`
     - `workflow_cases`
     - `documents`
   - Использовать: `intelligent-core/ai-foundation/rag/setup_collections.py`

4. **Monitoring**:
   - Prometheus + Grafana базовые дашборды

### Координация:
- Передать Temporal config → Claude #2
- Qdrant уже настроен (Claude #1), проверить collections

### Отчётность:
```yaml
Claude #3:
  task: Infrastructure + Temporal
  status: in_progress
  progress: "Temporal setup - 30%"
  blockers: []
```

---

## 👤 Claude #4 - expertise-center + orchestration cleanup

**Роль**: Domain Expertise + Cleanup Specialist
**Фокус**: expertise-center реорганизация

### Задачи ЧАСТЬ 1: Orchestration Cleanup

**Помочь мне (Claude #1) с оркестратором**:

1. Найти 11 "органов" в `intelligent-core/ai-orchestration/`
2. Переместить их → `intelligent-core/expertise-center/analyzers/`
3. Удалить дубликаты:
   - agent_router (есть в coordination-center)
   - llm_clients (есть в ai-foundation)
   - brain/ (непонятно что)

### Задачи ЧАСТЬ 2: expertise-center

1. **Реорганизация структуры**:
```
expertise-center/
├── core/
│   ├── chief_executive.py
│   ├── domain_loader.py
│   └── expert_registry.py
├── shared/
│   └── base/
│       ├── base_specialist.py
│       ├── base_colleague.py
│       └── base_analyzer.py
└── domains/
    └── bcm/
        ├── specialists/ (3)
        ├── colleagues/ (7)
        ├── analyzers/ (10)
        ├── tools/
        └── knowledge/
```

2. **Интеграция**:
```python
from ai_foundation import RAGPipeline, LLMRouter
from shared.database import get_db
```

3. **Реальные подключения**:
   - Specialists → LLM (Claude Opus)
   - Colleagues → RAG + LLM (Claude Sonnet)
   - Analyzers → ML + RAG

### Координация:
- Синхронизация со мной (Claude #1) по оркестратору
- Использовать ai-foundation для AI

### Отчётность:
```yaml
Claude #4:
  task: expertise-center + orchestration cleanup
  status: in_progress
  progress: "Found 11 organs, moving..."
  blockers: []
```

---

## 📊 Отчётность через файл

**Файл**: `doc-project/SPRINT_STATUS.md`

**Формат** (каждый Claude обновляет свою секцию):

```yaml
# Sprint Status - Live Updates

Last Update: 2025-10-06 [ЧЧ:ММ]

Claude #1 (Координатор):
  current_task: "Анализ coordination-center"
  status: in_progress
  completed_today:
    - "RAG/LLM integration"
  blockers: []

Claude #2 (workflow_intelligence):
  current_task: "postgres_adapter.py → SQLAlchemy"
  status: in_progress
  progress: "40%"
  blockers: []

Claude #3 (Infrastructure):
  current_task: "Temporal Cloud setup"
  status: in_progress
  progress: "30%"
  blockers: []

Claude #4 (expertise-center):
  current_task: "Moving organs to analyzers"
  status: in_progress
  progress: "5/11 organs moved"
  blockers: []
```

---

## 🔄 Синхронизация

**Как работаем**:

1. **Каждый Claude** обновляет свою секцию в `SPRINT_STATUS.md` каждые 30-60 мин
2. **Блокеры** пишем сразу, координатор решает
3. **Зависимости**:
   - Claude #2 ждёт Temporal config от Claude #3
   - Claude #4 синхронизируется с Claude #1 по оркестратору
   - Все используют ai-foundation (уже готов)

4. **Вопросы** можно писать в `SPRINT_STATUS.md` в секцию "Questions"

---

## 🎯 Цель Sprint 1

**К концу дня**:
- ✅ ai-foundation готов (Claude #1)
- ⏳ workflow_intelligence на SQLAlchemy (Claude #2)
- ⏳ Temporal работает (Claude #3)
- ⏳ Оркестратор очищен (Claude #1 + #4)
- ⏳ expertise-center структура готова (Claude #4)

**К концу Sprint 1** (1-2 дня):
- Все модули intelligent-core интегрированы с infrastructure
- Все моки удалены
- Всё работает с реальными подключениями
- Integration tests написаны

---

## 📝 Правила

1. **Не удаляем ничего!** Только архивируем в `_archive/`
2. **Промежуточные документы** → `doc-project/`
3. **Финальная документация** → в самом модуле (README.md)
4. **Коммиты** с понятными сообщениями
5. **Обновляем SPRINT_STATUS.md** регулярно!

---

## 🚀 Начало работы

Каждый Claude:
1. Прочитать своё ТЗ выше
2. Обновить `SPRINT_STATUS.md` (initial status)
3. Начать работу
4. Обновлять статус каждый час

Координатор (я) буду следить за `SPRINT_STATUS.md` и помогать!

**Вопросы?** Пишите в SPRINT_STATUS.md секцию Questions! 🎯
