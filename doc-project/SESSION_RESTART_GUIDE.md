# 🔄 Session Restart Guide - Перезагрузка Команды

**Дата**: 2025-10-06
**Цель**: Перезапустить все 5 Claude с чистым контекстом
**Причина**: Сессии работают 2+ суток, контекст раздут (119K tokens)

---

## ✅ Что Сделано (Текущая Сессия)

### Achievements:

1. **ai-foundation** ✅
   - Создан и закоммичен (коммит `699f3eb`)
   - RAG, ML, Learning, Context, LLM
   - Qdrant подключен (коммит `ad46b46`)
   - README.md готов

2. **shared/** ✅
   - Полностью готов
   - Auth, Database, Cache, EventBus, Utils

3. **infrastructure/** ✅
   - PostgreSQL (Supabase) работает
   - Redis (Upstash) работает
   - Qdrant настроен

4. **Sprint 1 Plan** ✅
   - Команда из 5 Claude распределена
   - Задачи назначены
   - Координация через SPRINT_STATUS.md

5. **Orchestration Analysis** ✅ (ВАЖНО!)
   - Проанализирован весь orchestration/
   - Определена стратегия очистки
   - План реорганизации готов

### Commits:
```
699f3eb - ai-foundation создан
ad46b46 - Qdrant integration + Sprint docs
47a208b - Orchestration strategy + RAG/LLM plan
```

---

## 📚 Ключевые Документы (ОБЯЗАТЕЛЬНО ЧИТАТЬ)

### Для Всех:

1. **FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md** (v8.2)
   - Полная архитектура платформы
   - V7 Improved с ai-foundation

2. **SPRINT_1_ASSEMBLY_PLAN.md**
   - Роли и задачи для 5 Claude
   - Timeline, метрики, правила

3. **SPRINT_STATUS.md**
   - Live статус команды
   - Обновлять каждый час

### Специализированные:

4. **ORCHESTRATION_STRATEGY.md** ⭐ КРИТИЧНО
   - Анализ ai-orchestration (928K, 87 файлов)
   - Что удалять, что оставлять
   - План чистки и интеграции

5. **RAG_LLM_INTEGRATION_PLAN.md**
   - План интеграции RAG + LLM (~1 час)
   - Уже есть Qdrant, осталось подключить

6. **PARALLEL_TASK_SPECIFICATION.md**
   - ТЗ для expertise-center (Claude #4)

---

## 🎯 Стартовые Команды (Новые Сессии)

### 🤖 Claude #1 (Координатор + RAG/LLM)

```
Я Claude #1 - Координатор команды.

Контекст:
- Читай: doc-project/SPRINT_1_ASSEMBLY_PLAN.md (моя секция)
- Читай: doc-project/RAG_LLM_INTEGRATION_PLAN.md

Моя задача:
1. Закончить RAG + LLM интеграцию (~1 час)
   - Обновить RAGPipeline (использовать QdrantVectorStore)
   - Настроить LLMRouter (Claude + OpenAI)
   - Создать Qdrant collections
2. Координировать команду через SPRINT_STATUS.md

Статус: ai-foundation готов ✅, Qdrant подключен ✅
Осталось: интегрировать RAG pipeline + LLM routing

Последний коммит: 47a208b

Начинаю!
```

---

### 🤖 Claude #2 (workflow_intelligence)

```
Я Claude #2 - Workflow Engine Specialist.

Контекст:
- Читай: doc-project/SPRINT_1_ASSEMBLY_PLAN.md (моя секция)
- Важно: Всё на SQLAlchemy, НЕ asyncpg!

Моя задача:
1. Переписать storage/postgres_adapter.py на SQLAlchemy
   - Использовать shared.database.DatabaseManager
   - Сохранить RLS (Row Level Security)
2. Интегрировать ai-foundation (RAG, ML, LLM)
3. Интегрировать shared (database, cache, eventbus)
4. Убрать все моки (InMemoryStorageAdapter, DemoCaseLibrary)
5. Integration tests с реальной БД

Файлы:
- intelligent-core/workflow_intelligence/
- Приоритет: storage/postgres_adapter.py

Жду готовности ai-foundation от Claude #1.

Начинаю!
```

---

### 🤖 Claude #3 (Infrastructure + Temporal)

```
Я Claude #3 - Infrastructure Specialist.

Контекст:
- Читай: doc-project/SPRINT_1_ASSEMBLY_PLAN.md (моя секция)

Моя задача:
1. Завершить настройку Temporal.io
   - Cloud: https://cloud.temporal.io
   - Workflow definitions для BCM
2. RabbitMQ eventbus топики
3. Qdrant collections (координация с Claude #1)
4. Prometheus + Grafana базовые дашборды

Передать конфиг Temporal → Claude #2 (workflow_intelligence)
Передать Qdrant setup → Claude #1 (ai-foundation)

Начинаю с Temporal!
```

---

### 🤖 Claude #4 (expertise-center + orchestration cleanup)

```
Я Claude #4 - Expertise & Orchestration Specialist.

Контекст:
- Читай: doc-project/PARALLEL_TASK_SPECIFICATION.md
- Читай: doc-project/ORCHESTRATION_STRATEGY.md ⭐ КРИТИЧНО

Моя задача (2 части):

ЧАСТЬ 1: expertise-center (4-5 часов)
1. Реорганизация структуры (core/, shared/, domains/bcm/)
2. Разобрать ai_experts → specialists (3) + tools + knowledge
3. Разобрать ai-office → colleagues (7) + analyzers (10)
4. ПОЛУЧИТЬ analyzers из orchestration/ai-orchestration/muscles/ai_organs/
5. Core файлы (chief_executive, domain_loader, expert_registry)
6. Интеграция с ai-foundation + shared

ЧАСТЬ 2: orchestration cleanup (2-3 часа)
1. Переместить 11 organs → expertise-center/analyzers
2. Удалить дубликаты (agent_router, llm_clients, brain/)
3. Очистить ai-orchestration до ~400K
4. Интегрировать с ai-foundation + shared

Стратегия в ORCHESTRATION_STRATEGY.md!

Начинаю!
```

---

### 🤖 Claude #5 (Community + Integration)

```
Я Claude #5 - Community AI & Integration Specialist.

Контекст:
- Читай: doc-project/SPRINT_1_ASSEMBLY_PLAN.md (моя секция)

Моя задача:
1. community_intelligence - интеграция с ai-foundation + shared
2. collective - интеграция
3. predictive - использовать ai-foundation.ml (НЕ свой ML!)
4. learning-system - интеграция с ai-foundation.learning
5. living-docs - интеграция
6. Integration tests (tests/integration/)

Жду готовности ai-foundation от Claude #1.

Начинаю!
```

---

## 📊 Приоритеты и Зависимости

### Критический путь:

```
Claude #1 (RAG/LLM) → готов первым → все остальные могут интегрировать
    ↓
Claude #3 (Temporal) → готов → Claude #2 интегрирует
    ↓
Claude #2, #4, #5 → работают параллельно
```

### Время:

- **Claude #1**: 1 час (RAG/LLM) → ПРИОРИТЕТ!
- **Claude #3**: 2-3 часа (Temporal + infrastructure)
- **Claude #4**: 6-8 часов (expertise-center + orchestration)
- **Claude #2**: 4-5 часов (workflow_intelligence)
- **Claude #5**: 3-4 часа (community modules)

**Итого**: 1 день активной работы

---

## 🚨 Важные Правила

### Git:
1. Коммитить часто (каждая готовая фича)
2. Формат: `feat(module): description`
3. Всегда добавлять `Co-Authored-By: Claude`

### Код:
1. **НЕТ МОКОВ!** Только реальные подключения
2. **Всё через shared/** (database, cache, eventbus)
3. **Всё через ai-foundation** (RAG, ML, LLM)
4. Документация в модуле, НЕ в корне

### Координация:
1. Обновлять SPRINT_STATUS.md каждый час
2. Блокеры сразу писать в файл
3. Координатор - Claude #1

---

## ✅ Готово к Перезагрузке!

1. MD закрывает все текущие Claude терминалы
2. Открывает 5 новых терминалов
3. Запускает каждого Claude командой выше
4. Команда работает синхронно через SPRINT_STATUS.md

**Время старта**: Когда MD готов
**Ожидаемый результат**: Полная интеграция intelligent-core + infrastructure за 1 день

---

**Удачи команде!** 🚀
