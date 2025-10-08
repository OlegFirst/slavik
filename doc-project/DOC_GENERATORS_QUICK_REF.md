# 📚 Doc Generators - Быстрый справочник

**⚡ Для быстрого использования**

---

## 🎯 Что запускать

| Задача | Команда | Результат |
|--------|---------|-----------|
| **AI Документация** | `python3 infrastructure/tools/doc-generators/ai_documentation_generator.py --full --ai` | README.md с AI описаниями |
| **Обычная документация** | `python3 infrastructure/tools/doc-generators/documentation_generator.py --full` | README.md + API.md + ARCHITECTURE.md |
| **Event Catalog** | `python3 infrastructure/tools/doc-generators/event_catalog_generator.py` | EVENTS.md + EVENT_FLOW.md |
| **Prometheus Config** | `python3 infrastructure/tools/doc-generators/prometheus_config_generator.py` | prometheus-auto.yml |
| **Tests** | `python3 infrastructure/tools/doc-generators/test_generator.py` | test_*.py + tavern_test_*.yaml |
| **UI Blueprints** | `python3 infrastructure/tools/doc-generators/ui_blueprint_gen.py` | *_blueprint.html + *_spec.json |

---

## 🤖 AI Colleagues

| AI Коллега | Может запускать | Приоритет |
|------------|-----------------|-----------|
| **Living Docs** | ai_docs, events, api_docs | 🔴 ВЫСОКИЙ |
| **Documents Specialist** | Все 7 инструментов | 🟡 СРЕДНИЙ |
| **MIO Manager** | prometheus, events | 🟡 СРЕДНИЙ |
| **AI Office Orchestrator** | Координация всех | 🟢 НИЗКИЙ |

---

## 📂 Выходные файлы

```
{module}/
├── README.md          ← ai_documentation_generator / documentation_generator
├── API.md             ← documentation_generator / api_docs_generator
└── ARCHITECTURE.md    ← documentation_generator (layer level)

infrastructure/events/
├── EVENTS.md          ← event_catalog_generator
├── events_catalog.json
└── EVENT_FLOW.md

infrastructure/observability/config/prometheus/
├── prometheus-auto.yml        ← prometheus_config_generator
└── sd_configs/services.json

tests/generated/
├── test_*_api.py       ← test_generator
├── test_*_unit.py
└── tavern_test_*.yaml

docs/ui/
├── *_blueprint.html    ← ui_blueprint_gen
├── *_spec.json
└── index.html

docs/api/
├── {service}.md        ← api_docs_generator
├── README.md
└── postman_collection.json
```

---

## 🔑 Environment Variables

```bash
# Для AI-генерации
export ANTHROPIC_API_KEY="sk-ant-..."

# Для Prometheus генератора (hardcoded в коде)
# PROJECT_ROOT = "/Users/MD/AI-Platform-ISO"
```

---

## ⚠️ Зависимости (не найдены!)

- ❌ `module_scanner.py` - Нужен для ai_docs и docs генераторов
- ❌ `ast_analyzer.py` - Нужен для test и ui генераторов
- ❌ `api_map.json` - Нужен для prometheus генератора

**Рекомендация**: Создать эти инструменты или найти их в других директориях.

---

## 🚀 Automation Ideas

### Вариант 1: Git Hooks
```bash
# .git/hooks/post-commit
python3 infrastructure/tools/doc-generators/event_catalog_generator.py
```

### Вариант 2: Cron Jobs
```bash
# Ежедневно в 2:00
0 2 * * * python3 infrastructure/tools/doc-generators/ai_documentation_generator.py --full --ai
```

### Вариант 3: API Endpoint
```python
POST /api/v1/docs/generate
{"module": "ai-foundation", "use_ai": true}
```

---

## 📊 Статус

- ✅ **7 инструментов** готовы к использованию
- ❌ **Не автоматизировано** (запуск вручную)
- ❌ **Не интегрировано** с AI коллегами
- ⚠️  **3 зависимости** отсутствуют

---

## 📖 Полная документация

- [ИНСТРУМЕНТЫ_ДОКУМЕНТАЦИИ_АНАЛИЗ.md](ИНСТРУМЕНТЫ_ДОКУМЕНТАЦИИ_АНАЛИЗ.md) - Детальный анализ (24KB)
- [DOC_GENERATORS_SUMMARY.md](DOC_GENERATORS_SUMMARY.md) - Сводка

---

**Обновлено**: 2025-10-08
