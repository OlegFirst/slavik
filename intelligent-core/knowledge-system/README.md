# 📚 Knowledge System

**Version:** 1.0.0
**Status:** Production-Ready
**Created:** 2025-10-06

---

## 🎯 Что это?

**Knowledge System** — централизованная система управления знаниями платформы с:

- 📖 **Доменной организацией** - Standards (ISO, BCI, WHO), Research, Regulatory
- 🔄 **Живой библиотекой кейсов** - Workflow + Community + Simulation
- 🌐 **Автообновлением** - RSS, API, scrapers для актуальности
- ⚡ **Производительностью** - 3-уровневое кеширование, векторный поиск
- 🔗 **Интеграцией** - Единый API для всех источников знаний

---

## 📁 Структура

```
knowledge-system/
├── loader/                    # Загрузчики знаний
│   ├── standards_loader.py   # ISO, BCI, WHO, NIST
│   └── case_loader.py        # Workflow, Community, Simulation cases
│
├── updater/                   # Автообновление (TODO)
│   ├── iso_monitor.py        # Мониторинг ISO updates
│   ├── regulatory_scraper.py # Scraping регуляторных изменений
│   └── scheduler.py          # Temporal workflows
│
├── indexer/                   # Индексация (TODO)
│   ├── vector_indexer.py     # Qdrant векторный поиск
│   ├── text_indexer.py       # Full-text search
│   └── graph_indexer.py      # Neo4j Knowledge Graph
│
├── api/                       # Unified API (TODO)
│   ├── query.py              # Поиск по библиотеке
│   └── stats.py              # Статистика
│
└── config/
    ├── domains.yaml          # Конфигурация доменов
    └── sources.yaml          # Внешние источники
```

---

## 🚀 Использование

### 1. Загрузка стандартов

```python
from knowledge_system.loader import StandardsLoader

loader = StandardsLoader()

# Загрузить ISO 22301
iso_data = await loader.load_iso_standard("iso-22301", version="2019")

print(iso_data['metadata']['title'])
# → "Business Continuity Management Systems - Requirements"

print(len(iso_data['clauses']))
# → 10

print(iso_data['guides'])
# → [{"name": "BSI Implementation Guide", "size_mb": 10.6}, ...]

# Загрузить все ISO стандарты
all_iso = await loader.load_all_iso_standards()
# → {"iso-22301": {...}, "iso-27001": {...}, ...}
```

### 2. Сбор кейсов

```python
from knowledge_system.loader import CaseCollector

collector = CaseCollector()

# Собрать кейс из завершенного workflow
case = await collector.collect_workflow_case(
    workflow_id="wf-12345",
    module="bia",
    outcome="success",
    organization_context={
        "industry": "healthcare",
        "size": "medium",
        "employees": 500
    },
    metrics={
        "duration_days": 14,
        "total_tasks": 8,
        "completion_rate": 1.0
    },
    decisions=[
        {"step": "rto_definition", "value": "4 hours", "rationale": "..."}
    ]
)

# → Сохраняется в:
#    1. PostgreSQL (workflow.workflow_cases)
#    2. data/cases/workflow_cases/bia/{case_id}.json
#    3. Vector DB (Qdrant collection: knowledge_cases)

# Импортировать кейс из маркетплейса
community_case = await collector.import_community_case(
    case_data={
        "title": "Healthcare BIA Template",
        "module": "bia",
        "organization_context": {...},
        "template": {...}
    },
    source="marketplace"
)

# → Сохраняется в: data/cases/community_cases/marketplace/{case_id}.json
```

### 3. Поиск похожих кейсов

```python
# Найти похожие кейсы
similar_cases = await collector.find_similar_cases(
    module="bia",
    organization_context={
        "industry": "healthcare",
        "size": "medium"
    },
    limit=5
)

for case in similar_cases:
    print(f"{case['case_id']}: {case['outcome']}")
    print(f"  Duration: {case['metrics']['duration_days']} days")
    print(f"  Industry: {case['organization_context']['industry']}")
```

### 4. Статистика

```python
# Статистика по кейсам
stats = await collector.get_case_stats()

print(stats)
# {
#   "total": 42,
#   "by_module": {"bia": 15, "risk": 12, "compliance": 10, "drp": 5},
#   "by_source": {
#     "workflow": 30,
#     "community_marketplace": 8,
#     "community_templates": 4
#   }
# }

# Список доступных стандартов
available = await loader.list_available_standards()

print(available)
# {
#   "iso": ["iso-22301", "iso-27001"],
#   "bci": ["gpg-2018"],
#   "who": ["who-framework"]
# }
```

---

## 📊 Организация данных

### Файловая структура

```
/Users/MD/AI-Platform-ISO/data/
├── knowledge/                           # Статические знания
│   ├── standards/
│   │   ├── iso/
│   │   │   ├── iso-22301/              ✅ Перемещено из корня
│   │   │   │   ├── BSI-ISO-22301-Implementation-Guide.pdf
│   │   │   │   ├── NQA-ISO-22301-Implementation-Guide.pdf
│   │   │   │   ├── ISO-22301-2019-Implementation-Guide.pdf
│   │   │   │   ├── standards/
│   │   │   │   │   └── clauses_breakdown.md
│   │   │   │   ├── iso_bci_platform_mapping.md
│   │   │   │   ├── metadata.json       ✅ Новое
│   │   │   │   └── README.md
│   │   │   ├── iso-27001/              (TODO)
│   │   │   ├── iso-27005/              (TODO)
│   │   │   └── iso-31000/              (TODO)
│   │   ├── bci/
│   │   │   └── gpg-2018/               (TODO)
│   │   ├── who/                        (TODO)
│   │   └── nist/                       (TODO)
│   │
│   ├── research/                        # Консалтинговые исследования
│   │   ├── deloitte/                   (TODO)
│   │   ├── mckinsey/                   (TODO)
│   │   ├── ey/                         (TODO)
│   │   └── pwc/                        (TODO)
│   │
│   └── regulatory/                      # Регуляторные требования
│       ├── gdpr/                       (TODO)
│       ├── hipaa/                      (TODO)
│       └── sox/                        (TODO)
│
├── cases/                               # Живая библиотека кейсов
│   ├── workflow_cases/
│   │   ├── bia/
│   │   ├── risk/
│   │   ├── compliance/
│   │   └── drp/
│   │
│   ├── community_cases/
│   │   ├── marketplace/
│   │   ├── templates/
│   │   └── best_practices/
│   │
│   └── simulation_cases/
│       └── bcm_incident/
│
├── external/                            # Автообновляемые источники
│   ├── iso_updates/                    (TODO)
│   ├── regulatory_changes/             (TODO)
│   └── threat_intelligence/            (TODO)
│
└── cache/                               # Кеш для производительности
    ├── embeddings/                      # Векторные представления
    ├── parsed/                          # Распарсенные документы
    └── indexed/                         # Индексы
```

---

## ⚙️ Конфигурация

### domains.yaml

Конфигурация доменов знаний:

```yaml
domains:
  standards:
    iso:
      standards:
        - id: iso-22301
          version: "2019"
          priority: high
          auto_update: true
```

См. `config/domains.yaml`

### sources.yaml

Внешние источники для автообновления:

```yaml
sources:
  iso_updates:
    type: rss
    url: https://www.iso.org/rss/updates.xml
    frequency: daily
    enabled: true
```

См. `config/sources.yaml`

---

## 🔗 Интеграция с платформой

### 1. AI Experts Knowledge

```python
# БЫЛО (старый код):
from ai_experts.knowledge.iso_loader import ISO22301Loader

loader = ISO22301Loader(
    library_path="/Users/MD/AI-Platform-ISO/ISO-22301-Library"  # ❌ Старый путь
)

# СТАЛО (обновлено):
loader = ISO22301Loader(
    library_path="/Users/MD/AI-Platform-ISO/data/knowledge/standards/iso/iso-22301"  # ✅ Новый путь
)

# ИЛИ использовать StandardsLoader напрямую:
from knowledge_system.loader import StandardsLoader

loader = StandardsLoader()
iso_data = await loader.load_iso_standard("iso-22301")
```

### 2. Workflow Intelligence

```python
# Интеграция с workflow_intelligence.case_library

from knowledge_system.loader import CaseCollector
from workflow_intelligence.case_library.repository import CaseRepository

# Создать collector с repository
repository = CaseRepository(db_session, vector_db_client)
collector = CaseCollector(repository=repository)

# При завершении workflow
await collector.collect_workflow_case(
    workflow_id=instance.id,
    module="bia",
    outcome="success",
    ...
)

# → Автоматически сохраняется в:
#   - PostgreSQL (через repository)
#   - File System (data/cases/workflow_cases/)
#   - Vector DB (через repository)
```

### 3. Community Marketplace

```python
# API endpoint для импорта кейсов

@app.post("/api/community/cases/import")
async def import_marketplace_case(case_data: Dict):
    collector = CaseCollector()

    result = await collector.import_community_case(
        case_data=case_data,
        source="marketplace"
    )

    return result
```

---

## 🎯 Производительность

### Кеширование (3 уровня)

```
1. Memory (Redis)
   └─ TTL: 1 hour
   └─ Use: Частые запросы

2. File System (parsed/)
   └─ TTL: До изменения файла (MD5 hash)
   └─ Use: Распарсенные PDF, JSON

3. Vector DB (Qdrant)
   └─ TTL: Permanent
   └─ Use: Семантический поиск (<10ms)
```

### Оптимизации

- **Hash-based caching** - MD5 файлов для инвалидации кеша
- **Batch loading** - загрузка нескольких стандартов одновременно
- **Vector indexing** - HNSW индекс для быстрого поиска
- **Deduplication** - автоматическое удаление дубликатов кейсов

---

## 🚧 Roadmap

### Phase 1: Foundation ✅ DONE

- [x] Directory structure (`data/`)
- [x] StandardsLoader implementation
- [x] CaseCollector implementation
- [x] Configuration files (domains.yaml, sources.yaml)
- [x] Integration with existing code (iso_loader.py updated)
- [x] Migration of ISO-22301-Library

### Phase 2: Auto-update (TODO)

- [ ] ISO update monitor
- [ ] Regulatory scrapers
- [ ] Temporal workflows for scheduling
- [ ] Notification system (email, Slack)

### Phase 3: Indexing (TODO)

- [ ] Qdrant vector indexer
- [ ] Neo4j Knowledge Graph updater
- [ ] Full-text search (Elasticsearch)

### Phase 4: Unified API (TODO)

- [ ] KnowledgeAPI implementation
- [ ] REST endpoints
- [ ] GraphQL support
- [ ] Caching layer

### Phase 5: Additional Standards (TODO)

- [ ] ISO 27001 (Information Security)
- [ ] ISO 27005 (Risk Management)
- [ ] ISO 31000 (Enterprise Risk)
- [ ] BCI GPG 2018
- [ ] WHO Framework
- [ ] NIST CSF

---

## 📝 Migration Guide

### Для разработчиков

Если вы использовали старый путь `ISO-22301-Library`:

**1. Обновите импорты:**

```python
# БЫЛО
loader = ISO22301Loader(library_path="/Users/MD/AI-Platform-ISO/ISO-22301-Library")

# СТАЛО
from knowledge_system.loader import StandardsLoader
loader = StandardsLoader()
data = await loader.load_iso_standard("iso-22301")
```

**2. Или просто обновите путь:**

```python
# Старый код продолжит работать с новым путем
loader = ISO22301Loader(
    library_path="/Users/MD/AI-Platform-ISO/data/knowledge/standards/iso/iso-22301"
)
```

### Для администраторов

**1. Проверьте, что миграция прошла успешно:**

```bash
# Проверить новое расположение
ls -la /Users/MD/AI-Platform-ISO/data/knowledge/standards/iso/iso-22301/

# Убедиться, что старой директории нет
ls /Users/MD/AI-Platform-ISO/ISO-22301-Library  # Should not exist
```

**2. Обновите переменные окружения (если используются):**

```bash
# .env
ISO_LIBRARY_PATH=/Users/MD/AI-Platform-ISO/data/knowledge/standards/iso/iso-22301
```

---

## 🧪 Тестирование

```python
# tests/test_standards_loader.py

import pytest
from knowledge_system.loader import StandardsLoader

@pytest.mark.asyncio
async def test_load_iso_22301():
    loader = StandardsLoader()

    data = await loader.load_iso_standard("iso-22301")

    assert data["standard"] == "iso-22301"
    assert data["metadata"]["title"] is not None
    assert len(data["guides"]) >= 3  # BSI, NQA, ISO guides
    assert "clauses" in data

@pytest.mark.asyncio
async def test_cache_works():
    loader = StandardsLoader(cache_enabled=True)

    # First load (from source)
    data1 = await loader.load_iso_standard("iso-22301")

    # Second load (from cache)
    data2 = await loader.load_iso_standard("iso-22301")

    assert data1 == data2

@pytest.mark.asyncio
async def test_list_standards():
    loader = StandardsLoader()

    available = await loader.list_available_standards()

    assert "iso" in available
    assert "iso-22301" in available["iso"]
```

```python
# tests/test_case_collector.py

import pytest
from knowledge_system.loader import CaseCollector

@pytest.mark.asyncio
async def test_collect_workflow_case():
    collector = CaseCollector()

    case = await collector.collect_workflow_case(
        workflow_id="test-wf-123",
        module="bia",
        outcome="success",
        organization_context={"industry": "healthcare", "size": "medium"},
        metrics={"duration_days": 14}
    )

    assert case["case_id"] is not None
    assert case["module"] == "bia"

@pytest.mark.asyncio
async def test_find_similar_cases():
    collector = CaseCollector()

    # First, collect a case
    await collector.collect_workflow_case(
        workflow_id="wf-1",
        module="bia",
        outcome="success",
        organization_context={"industry": "healthcare", "size": "medium"},
        metrics={}
    )

    # Then find similar
    similar = await collector.find_similar_cases(
        module="bia",
        organization_context={"industry": "healthcare", "size": "medium"},
        limit=5
    )

    assert len(similar) >= 1
```

Запуск:

```bash
cd intelligent-core/knowledge-system
pytest tests/ -v
```

---

## 📞 Support

**Вопросы:**
- Architecture: См. `/doc-project/KNOWLEDGE_LIBRARY_ARCHITECTURE.md`
- Issues: GitHub Issues
- Slack: #knowledge-system

**Документация:**
- [README.md](README.md) - Этот файл
- [config/domains.yaml](config/domains.yaml) - Конфигурация доменов
- [config/sources.yaml](config/sources.yaml) - Внешние источники
- [/doc-project/KNOWLEDGE_LIBRARY_ARCHITECTURE.md](/doc-project/KNOWLEDGE_LIBRARY_ARCHITECTURE.md) - Архитектура

---

**Создано MD & Claude • Октябрь 2025** 🚀
