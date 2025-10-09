# 📚 Doc Generators - Краткая сводка

**Местоположение**: `/infrastructure/tools/doc-generators/`
**Инструментов**: 7
**Размер**: ~100KB кода
**Статус**: ✅ Готовы к использованию, ❌ Не автоматизированы

---

## 🎯 Быстрый обзор

### 7 инструментов генерации документации:

| # | Инструмент | Размер | Тип | AI | Статус |
|---|-----------|--------|-----|----|----|
| 1 | `ai_documentation_generator.py` | 21KB | AI-powered | ✅ Claude 3.5 | ✅ |
| 2 | `documentation_generator.py` | 24KB | Template | ❌ | ✅ |
| 3 | `event_catalog_generator.py` | 13KB | Static analysis | ❌ | ✅ |
| 4 | `api_docs_generator.py` | 10KB | Runtime | ❌ | ✅ |
| 5 | `prometheus_config_generator.py` | 11KB | Config | ❌ | ✅ |
| 6 | `test_generator.py` | 10KB | Code gen | ❌ | ✅ |
| 7 | `ui_blueprint_gen.py` | 14KB | UI specs | ❌ | ✅ |

---

## 🚀 Быстрый старт

### 1. AI Documentation (лучший выбор)

```bash
# С AI (требует Claude API key)
export ANTHROPIC_API_KEY="your-key"
python3 infrastructure/tools/doc-generators/ai_documentation_generator.py --full --ai

# Без AI (шаблоны)
python3 infrastructure/tools/doc-generators/documentation_generator.py --full
```

**Результат**: README.md + API.md для всех модулей ✅

---

### 2. Event Catalog

```bash
python3 infrastructure/tools/doc-generators/event_catalog_generator.py
```

**Результат**:
- `infrastructure/events/EVENTS.md`
- `infrastructure/events/events_catalog.json`
- `infrastructure/events/EVENT_FLOW.md` (Mermaid)

---

### 3. Prometheus Config

```bash
python3 infrastructure/tools/doc-generators/prometheus_config_generator.py
```

**Результат**: `infrastructure/observability/config/prometheus/prometheus-auto.yml`

---

## 🤖 Интеграция с AI коллегами

### Текущий статус: ❌ **НЕ ИНТЕГРИРОВАНО**

Инструменты работают **standalone** (вручную).

### Кто может запускать:

#### 1️⃣ **Living Docs Service** (Приоритет: ВЫСОКИЙ)
**Местоположение**: `intelligent-core/living-docs/`

**Может интегрировать**:
- ✅ `ai_documentation_generator` - AI docs
- ✅ `event_catalog_generator` - Event docs
- ✅ `api_docs_generator` - API docs

**Зачем**: Living Docs = эволюция документации (уже существует!)

---

#### 2️⃣ **Documents Specialist** (Приоритет: СРЕДНИЙ)
**Местоположение**: `expertise-center/domains/bcm/tactical_assistants/documents_specialist.py`

**Может вызывать**:
- Все 7 инструментов как toolkit

**Зачем**: По запросу пользователя
- "Обнови документацию для ai-foundation"
- "Сгенерируй event catalog"
- "Создай тесты для validation-service"

---

#### 3️⃣ **MIO Manager** (Приоритет: СРЕДНИЙ)
**Местоположение**: `devops-ai/mio-manager/`

**Может автоматизировать**:
- ✅ `prometheus_config_generator` - при деплое новых сервисов
- ✅ `event_catalog_generator` - при изменении eventbus

**Зачем**: Автоматизация DevOps задач

---

#### 4️⃣ **AI Office Orchestrator** (Приоритет: НИЗКИЙ)
**Местоположение**: `infrastructure/AI-office-infrastructure/orchestrator/`

**Может координировать**:
- Запуск всех генераторов как workflow
- Приоритизация задач генерации

**Зачем**: Координация сложных workflow

---

## 📊 Что генерируют

### Документация:
- ✅ `README.md` (с AI описаниями или шаблонами)
- ✅ `API.md` (группировка по ресурсам, curl примеры)
- ✅ `ARCHITECTURE.md` (для слоёв: intelligent-core, platform-services)
- ✅ `EVENTS.md` (каталог событий с publishers/subscribers)

### Конфигурация:
- ✅ `prometheus.yml` (авто-генерация scrape configs)
- ✅ `sd_configs/services.json` (service discovery)

### Тесты:
- ✅ `test_{service}_api.py` (pytest integration tests)
- ✅ `test_{service}_unit.py` (pytest unit tests)
- ✅ `tavern_test_{service}.yaml` (Tavern API scenarios)
- ✅ `pytest.ini` + `conftest.py`

### UI Specs:
- ✅ `{service}_blueprint.html` (визуальные схемы)
- ✅ `{service}_spec.json` (JSON спецификации для фронтенда)

### API Docs:
- ✅ `docs/api/{service}.md` (Markdown docs)
- ✅ `postman_collection.json` (Postman import)

---

## 🔨 Рекомендации

### Что сделать сейчас:

1. **Интегрировать с Living Docs** (1-2 дня)
   ```python
   # living-docs/services/documentation_evolution_engine.py
   async def auto_update_docs(self):
       # Вызывать ai_documentation_generator
       # Вызывать event_catalog_generator
       # Вызывать api_docs_generator
   ```

2. **Создать API endpoint** (1 день)
   ```python
   POST /api/v1/documentation/generate
   {
       "module": "ai-foundation",
       "use_ai": true,
       "generators": ["ai_docs", "events", "tests"]
   }
   ```

3. **Настроить CI/CD** (1 день)
   ```yaml
   # .github/workflows/auto-docs.yml
   on: [push]
   jobs:
     generate-docs:
       runs-on: ubuntu-latest
       steps:
         - name: Generate AI Docs
           run: python3 infrastructure/tools/doc-generators/ai_documentation_generator.py --full --ai
   ```

---

## 📁 Файлы

### Документация:
- **[ИНСТРУМЕНТЫ_ДОКУМЕНТАЦИИ_АНАЛИЗ.md](ИНСТРУМЕНТЫ_ДОКУМЕНТАЦИИ_АНАЛИЗ.md)** - Полный анализ (24KB)
- **[DOC_GENERATORS_SUMMARY.md](DOC_GENERATORS_SUMMARY.md)** - Эта сводка

### Сами инструменты:
- `infrastructure/tools/doc-generators/` - 7 Python скриптов

---

## 🎓 Примеры использования

### Сценарий 1: Создать документацию для нового модуля

```bash
# 1. Сканировать модуль (требует module_scanner.py)
python3 tools/analyzers/module_scanner.py --module ai-foundation

# 2. Генерировать AI docs
export ANTHROPIC_API_KEY="sk-..."
python3 infrastructure/tools/doc-generators/ai_documentation_generator.py --module ai-foundation --ai

# Результат:
# ✅ intelligent-core/ai-foundation/README.md (с AI описаниями)
```

### Сценарий 2: Обновить event catalog

```bash
python3 infrastructure/tools/doc-generators/event_catalog_generator.py

# Результат:
# ✅ infrastructure/events/EVENTS.md
# ✅ infrastructure/events/events_catalog.json
# ✅ infrastructure/events/EVENT_FLOW.md
```

### Сценарий 3: Генерация тестов для нового сервиса

```bash
# 1. Сканировать API (требует AST analyzer)
python3 tools/analyzers/ast_analyzer.py --service validation-service

# 2. Генерировать тесты
python3 infrastructure/tools/doc-generators/test_generator.py

# Результат:
# ✅ tests/generated/test_validation_api.py
# ✅ tests/generated/test_validation_unit.py
# ✅ tests/generated/tavern_test_validation.yaml
```

---

## 🔗 Связанные документы

- [МЕТРИКИ_INDEX.md](МЕТРИКИ_INDEX.md) - Система метрик (другой инструмент)
- [FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md](FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md) - Архитектура платформы

---

**Версия**: 1.0
**Дата**: 2025-10-08
**Статус**: ✅ READY TO INTEGRATE
