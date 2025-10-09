# 📚 Knowledge Library Architecture

**Дата:** 2025-10-06
**Статус:** Proposal

---

## 🎯 Цель

Создать централизованную, живую библиотеку знаний с:
- **Доменной организацией** (ISO, BCI, WHO, Cases, etc.)
- **Автообновлением** из внешних источников
- **Интеграцией** с Case Library (маркетплейс кейсов)
- **Производительностью** (векторный поиск, кеширование)

---

## 🏗️ Предлагаемая архитектура

```
/Users/MD/AI-Platform-ISO/
├── data/                          # 🆕 Централизованное хранилище данных
│   ├── knowledge/                 # Статические знания
│   │   ├── standards/            # Стандарты и фреймворки
│   │   │   ├── iso/
│   │   │   │   ├── iso-22301/
│   │   │   │   │   ├── clauses/
│   │   │   │   │   ├── guides/
│   │   │   │   │   │   ├── BSI-ISO-22301-Implementation-Guide.pdf
│   │   │   │   │   │   ├── NQA-ISO-22301-Implementation-Guide.pdf
│   │   │   │   │   │   └── ISO-22301-2019-Implementation-Guide.pdf
│   │   │   │   │   ├── mappings/
│   │   │   │   │   │   └── iso_bci_platform_mapping.md
│   │   │   │   │   └── metadata.json
│   │   │   │   ├── iso-27001/
│   │   │   │   ├── iso-27005/
│   │   │   │   └── iso-31000/
│   │   │   ├── bci/              # BCI Good Practice Guidelines
│   │   │   │   └── gpg-2018/
│   │   │   ├── who/              # WHO Framework
│   │   │   └── nist/             # NIST frameworks
│   │   │
│   │   ├── research/             # Исследования консалтинговых компаний
│   │   │   ├── deloitte/
│   │   │   ├── mckinsey/
│   │   │   ├── ey/
│   │   │   └── pwc/
│   │   │
│   │   └── regulatory/           # Регуляторные требования
│   │       ├── gdpr/
│   │       ├── hipaa/
│   │       └── sox/
│   │
│   ├── cases/                     # 🔄 Живая библиотека кейсов
│   │   ├── workflow_cases/       # Case Library (из workflow_intelligence)
│   │   │   ├── bia/
│   │   │   ├── risk/
│   │   │   ├── compliance/
│   │   │   └── drp/
│   │   │
│   │   ├── community_cases/      # Кейсы из Community (маркетплейс)
│   │   │   ├── templates/
│   │   │   ├── best_practices/
│   │   │   └── lessons_learned/
│   │   │
│   │   └── simulation_cases/     # Результаты симуляций
│   │       └── scenarios/
│   │
│   ├── external/                  # 🌐 Автообновляемые источники
│   │   ├── iso_updates/          # Парсинг официальных обновлений
│   │   ├── regulatory_changes/   # Изменения в законодательстве
│   │   └── threat_intelligence/  # Threat feeds
│   │
│   └── cache/                     # Кеш для производительности
│       ├── embeddings/           # Векторные представления
│       ├── parsed/               # Распарсенные документы
│       └── indexed/              # Индексы для поиска
│
├── intelligent-core/
│   └── knowledge-system/          # 🆕 Система управления знаниями
│       ├── loader/               # Загрузчики
│       │   ├── standards_loader.py
│       │   ├── case_loader.py
│       │   └── external_loader.py
│       │
│       ├── updater/              # Автообновление
│       │   ├── iso_monitor.py    # Мониторинг обновлений ISO
│       │   ├── regulatory_scraper.py
│       │   └── scheduler.py      # Периодические обновления
│       │
│       ├── indexer/              # Индексация
│       │   ├── vector_indexer.py # Qdrant/Weaviate
│       │   ├── text_indexer.py   # Full-text search
│       │   └── graph_indexer.py  # Neo4j Knowledge Graph
│       │
│       ├── api/                  # Unified API
│       │   ├── query.py          # Поиск по библиотеке
│       │   ├── update.py         # Обновление контента
│       │   └── stats.py          # Статистика использования
│       │
│       └── config/
│           ├── domains.yaml      # Конфигурация доменов
│           └── sources.yaml      # Внешние источники
```

---

## 🔄 Компоненты системы

### 1. Standards Loader (Статические знания)

```python
# intelligent-core/knowledge-system/loader/standards_loader.py

from pathlib import Path
from typing import Dict, List
import hashlib

class StandardsLoader:
    """
    Загрузка стандартов в Knowledge Graph с версионированием
    """

    def __init__(self, data_path: Path = Path("/Users/MD/AI-Platform-ISO/data")):
        self.standards_path = data_path / "knowledge" / "standards"
        self.cache_path = data_path / "cache" / "parsed"

    async def load_iso_standard(
        self,
        standard: str,  # "iso-22301"
        version: str = "2019"
    ) -> Dict:
        """
        Загрузить ISO стандарт

        Features:
        - Версионирование
        - Кеширование распарсенных данных
        - Автоматическая индексация в Vector DB
        - Обновление Knowledge Graph
        """

        standard_path = self.standards_path / "iso" / standard

        # Проверка кеша (по hash файлов)
        cache_key = self._get_cache_key(standard_path)
        cached = await self._get_from_cache(cache_key)
        if cached:
            return cached

        # Парсинг
        clauses = await self._parse_clauses(standard_path / "clauses")
        guides = await self._parse_guides(standard_path / "guides")
        mappings = await self._parse_mappings(standard_path / "mappings")

        data = {
            "standard": standard,
            "version": version,
            "clauses": clauses,
            "guides": guides,
            "mappings": mappings,
            "metadata": await self._load_metadata(standard_path)
        }

        # Кеш
        await self._save_to_cache(cache_key, data)

        # Индексация
        await self._index_in_vector_db(data)
        await self._update_knowledge_graph(data)

        return data

    def _get_cache_key(self, path: Path) -> str:
        """MD5 hash всех файлов для кеша"""
        hasher = hashlib.md5()
        for file in sorted(path.rglob("*")):
            if file.is_file():
                hasher.update(file.read_bytes())
        return hasher.hexdigest()
```

### 2. Case Collector (Живая библиотека)

```python
# intelligent-core/knowledge-system/loader/case_loader.py

class CaseCollector:
    """
    Сбор кейсов из разных источников в единую библиотеку
    """

    def __init__(self):
        self.cases_path = Path("/Users/MD/AI-Platform-ISO/data/cases")
        self.workflow_cases = self.cases_path / "workflow_cases"
        self.community_cases = self.cases_path / "community_cases"

    async def collect_workflow_case(
        self,
        workflow_id: str,
        module: str,
        outcome: str,
        **kwargs
    ):
        """
        Сохранить кейс из workflow в файловую систему + PostgreSQL

        Flow:
        1. Сохранить в PostgreSQL (workflow_cases таблица)
        2. Сохранить в data/cases/workflow_cases/{module}/{case_id}.json
        3. Индексировать в Vector DB (для поиска похожих)
        4. Обновить статистику
        """

        # PostgreSQL (через workflow_intelligence.case_library.repository)
        case = await self.repository.save_case(workflow_id, module, outcome, **kwargs)

        # Файловая система (для долгосрочного хранения)
        case_file = self.workflow_cases / module / f"{case.id}.json"
        case_file.parent.mkdir(parents=True, exist_ok=True)
        case_file.write_text(case.json(indent=2))

        # Vector DB (для семантического поиска)
        await self.indexer.index_case(case)

        return case

    async def import_community_case(
        self,
        case_data: Dict,
        source: str = "marketplace"
    ):
        """
        Импорт кейса из Community Marketplace

        Sources:
        - marketplace (user-submitted)
        - templates (pre-built)
        - best_practices (curated)
        """

        case_file = self.community_cases / source / f"{case_data['id']}.json"
        case_file.parent.mkdir(parents=True, exist_ok=True)
        case_file.write_text(json.dumps(case_data, indent=2))

        # Индексация
        await self.indexer.index_case(case_data)
```

### 3. External Updater (Автообновление)

```python
# intelligent-core/knowledge-system/updater/iso_monitor.py

import aiohttp
from datetime import datetime, timedelta

class ISOUpdateMonitor:
    """
    Мониторинг обновлений ISO стандартов

    Sources:
    - ISO.org RSS feeds
    - Scraping ISO pages
    - Email notifications (если есть подписка)
    """

    SOURCES = {
        "iso_rss": "https://www.iso.org/rss",
        "iso_amendments": "https://www.iso.org/standard/amendments",
    }

    async def check_for_updates(self, standard: str = "iso-22301"):
        """
        Проверка обновлений раз в сутки

        Returns:
            List[Update] - список найденных обновлений
        """

        updates = []

        # RSS feed
        async with aiohttp.ClientSession() as session:
            async with session.get(self.SOURCES["iso_rss"]) as resp:
                feed = await resp.text()
                updates.extend(self._parse_rss(feed, standard))

        # Сравнение с текущей версией
        current_version = await self._get_current_version(standard)
        new_updates = [u for u in updates if u.version > current_version]

        if new_updates:
            # Уведомление
            await self._notify_admins(new_updates)

            # Сохранение метаданных
            await self._save_update_metadata(new_updates)

        return new_updates

    async def download_update(self, update: Dict):
        """
        Скачать обновление и интегрировать

        Note: ISO стандарты платные, нужна подписка или ручная загрузка
        """

        # Для бесплатных источников (guides, whitepapers)
        if update["type"] == "guide":
            await self._download_guide(update["url"])

        # Для ISO стандартов - ручная загрузка
        else:
            logger.info(f"Manual download required: {update['title']}")
            # Создать задачу для admin
            await self._create_admin_task(
                title=f"Download {update['title']}",
                url=update["url"]
            )
```

### 4. Knowledge Query API

```python
# intelligent-core/knowledge-system/api/query.py

from typing import List, Optional
from pydantic import BaseModel

class KnowledgeQuery(BaseModel):
    query: str
    domain: Optional[str] = None  # "iso", "bci", "cases"
    filters: Optional[Dict] = None
    limit: int = 10

class KnowledgeAPI:
    """
    Unified API для поиска по всей библиотеке знаний
    """

    async def search(self, query: KnowledgeQuery) -> List[KnowledgeItem]:
        """
        Поиск по всем источникам

        Uses:
        - Vector DB (semantic search)
        - Full-text search (exact matches)
        - Knowledge Graph (relationships)
        """

        results = []

        # Vector search (семантический поиск)
        if self.vector_db:
            vector_results = await self.vector_db.search(
                query=query.query,
                collection=query.domain,
                limit=query.limit
            )
            results.extend(vector_results)

        # Knowledge Graph (связи)
        if self.knowledge_graph:
            graph_results = await self.knowledge_graph.find_related(
                query=query.query,
                domain=query.domain
            )
            results.extend(graph_results)

        # Ranking (hybrid)
        ranked = self._rank_results(results, query.query)

        return ranked[:query.limit]

    async def get_standard(self, standard: str, version: str = "latest"):
        """Получить конкретный стандарт"""
        return await self.standards_loader.load_iso_standard(standard, version)

    async def find_similar_cases(
        self,
        industry: str,
        module: str,
        **filters
    ):
        """Найти похожие кейсы"""
        return await self.case_collector.find_similar(industry, module, **filters)
```

---

## 📊 Производительность

### Уровни кеширования

```
Level 1: Memory Cache (Redis)
  └─ TTL: 1 hour
  └─ Use: Частые запросы (standards, популярные кейсы)

Level 2: Parsed Cache (File System)
  └─ TTL: До изменения файла (MD5 hash)
  └─ Use: Распарсенные PDF, JSON

Level 3: Vector DB (Qdrant)
  └─ TTL: Permanent
  └─ Use: Семантический поиск

Level 4: Source Files (File System)
  └─ TTL: Permanent
  └─ Use: Оригинальные PDF, MD
```

### Оптимизация доступа

**1. Доменная организация** - быстрый доступ по пути:
```
data/knowledge/standards/iso/iso-22301/  # O(1) file access
```

**2. Индексы** - Vector DB + Full-text:
```python
# Vector search: O(log n) с HNSW индексом
results = await qdrant.search(embedding, top_k=10)  # ~5ms

# Full-text: O(log n) с inverted index
results = await elasticsearch.search(query)  # ~10ms
```

**3. Batch loading** - загрузка пачками:
```python
# Вместо 100 запросов
for standard in standards:
    await load_standard(standard)  # ❌ Медленно

# Один запрос
await load_standards_batch(standards)  # ✅ Быстро
```

---

## 🔄 Автообновление

### Периодические задачи (Celery/Temporal)

```python
# intelligent-core/knowledge-system/updater/scheduler.py

from temporal import workflow

@workflow.defn
class KnowledgeUpdateWorkflow:
    """
    Периодическое обновление библиотеки
    """

    @workflow.run
    async def run(self):
        # Ежедневно: Проверка ISO обновлений
        await workflow.execute_activity(
            check_iso_updates,
            schedule_to_close_timeout=timedelta(hours=1)
        )

        # Еженедельно: Regulatory changes
        if datetime.now().weekday() == 0:  # Monday
            await workflow.execute_activity(
                check_regulatory_updates,
                schedule_to_close_timeout=timedelta(hours=2)
            )

        # Ежемесячно: Консалтинговые исследования
        if datetime.now().day == 1:
            await workflow.execute_activity(
                scrape_consulting_research,
                schedule_to_close_timeout=timedelta(hours=4)
            )

# Запуск
workflow_client.start_workflow(
    KnowledgeUpdateWorkflow.run,
    id="knowledge-update",
    cron_schedule="0 2 * * *"  # Каждый день в 2:00
)
```

### Источники для автообновления

```yaml
# intelligent-core/knowledge-system/config/sources.yaml

sources:
  iso_updates:
    type: rss
    url: https://www.iso.org/rss
    frequency: daily
    filters:
      - iso-22301
      - iso-27001
      - iso-31000

  regulatory:
    gdpr:
      type: scraper
      url: https://gdpr.eu/updates
      frequency: weekly

    hipaa:
      type: api
      url: https://www.hhs.gov/hipaa/api/updates
      frequency: weekly

  threat_intelligence:
    mitre_attack:
      type: api
      url: https://attack.mitre.org/api
      frequency: daily

    cve_feed:
      type: rss
      url: https://nvd.nist.gov/feeds/rss
      frequency: hourly

  consulting_research:
    deloitte:
      type: scraper
      url: https://www2.deloitte.com/us/en/pages/risk/solutions/business-continuity-management.html
      frequency: monthly

    mckinsey:
      type: scraper
      url: https://www.mckinsey.com/capabilities/risk-and-resilience/how-we-help-clients
      frequency: monthly
```

---

## 🔗 Интеграция с существующими системами

### 1. Workflow Intelligence

```python
# Текущий код (workflow_intelligence/case_library/repository.py)
# использует InMemoryStorageAdapter

# ПОСЛЕ миграции:
from knowledge_system.loader.case_loader import CaseCollector

case_collector = CaseCollector()
await case_collector.collect_workflow_case(
    workflow_id=instance_id,
    module="bia",
    outcome="success",
    ...
)
# → Сохраняется в:
#   1. PostgreSQL (workflow.workflow_cases)
#   2. File System (data/cases/workflow_cases/bia/{id}.json)
#   3. Vector DB (для поиска)
```

### 2. AI Experts Knowledge

```python
# Текущий код (ai_experts/knowledge/iso_loader.py)
# хардкодит путь: /Users/MD/AI-Platform-ISO/ISO-22301-Library

# ПОСЛЕ миграции:
from knowledge_system.loader.standards_loader import StandardsLoader

loader = StandardsLoader()
iso_22301 = await loader.load_iso_standard("iso-22301", version="2019")
# → Читает из: data/knowledge/standards/iso/iso-22301/
```

### 3. Community Marketplace

```python
# Новый эндпоинт для импорта кейсов из маркетплейса

@app.post("/api/community/cases/import")
async def import_case(case_data: Dict):
    """
    Импорт кейса из Community Marketplace
    """
    collector = CaseCollector()
    await collector.import_community_case(
        case_data=case_data,
        source="marketplace"
    )

    return {"status": "imported", "case_id": case_data["id"]}
```

---

## 📦 План миграции

### Phase 1: Структура (1 день)

```bash
# 1. Создать структуру
mkdir -p data/knowledge/standards/{iso,bci,who,nist}
mkdir -p data/knowledge/research/{deloitte,mckinsey,ey,pwc}
mkdir -p data/knowledge/regulatory/{gdpr,hipaa,sox}
mkdir -p data/cases/{workflow_cases,community_cases,simulation_cases}
mkdir -p data/external/{iso_updates,regulatory_changes,threat_intelligence}
mkdir -p data/cache/{embeddings,parsed,indexed}

# 2. Переместить ISO-22301-Library
mv ISO-22301-Library data/knowledge/standards/iso/iso-22301

# 3. Создать metadata
cat > data/knowledge/standards/iso/iso-22301/metadata.json <<EOF
{
  "standard": "iso-22301",
  "title": "Business Continuity Management Systems",
  "version": "2019",
  "amendment": "2024",
  "last_updated": "2024-01-15",
  "sources": {
    "official": "https://www.iso.org/standard/75106.html",
    "guides": ["BSI", "NQA", "ISO"]
  }
}
EOF
```

### Phase 2: Knowledge System (3 дня)

```bash
# 1. Создать модуль
mkdir -p intelligent-core/knowledge-system/{loader,updater,indexer,api,config}

# 2. Реализовать компоненты
# - standards_loader.py
# - case_loader.py
# - iso_monitor.py
# - vector_indexer.py
# - query.py

# 3. Конфигурация
# - domains.yaml
# - sources.yaml
```

### Phase 3: Интеграция (2 дня)

```python
# 1. Обновить iso_loader.py
- library_path: str = "/Users/MD/AI-Platform-ISO/ISO-22301-Library"
+ library_path: str = "/Users/MD/AI-Platform-ISO/data/knowledge/standards/iso/iso-22301"

# 2. Обновить workflow_intelligence
+ from knowledge_system.loader.case_loader import CaseCollector

# 3. Добавить API endpoints
+ from knowledge_system.api import KnowledgeAPI
```

### Phase 4: Автообновление (2 дня)

```python
# 1. Настроить Temporal workflows
# 2. Добавить scrapers для источников
# 3. Настроить уведомления
# 4. Тестирование
```

---

## ✅ Преимущества решения

| До | После |
|----|-------|
| ISO-22301 в корне проекта | Доменная организация data/knowledge/standards/iso/ |
| Хардкод путей в коде | Конфигурация через domains.yaml |
| Кейсы только в памяти | Персистентность: PostgreSQL + File System + Vector DB |
| Нет автообновления | Автоматический мониторинг ISO/Regulatory changes |
| Дублирование кейсов | Единая библиотека: workflow + community + simulation |
| Медленный поиск | Vector DB + кеширование = <10ms |
| Статическая библиотека | Живая, самообновляющаяся система |

---

## 🎯 Метрики успеха

- **Query latency:** <10ms (p95) для cached queries
- **Update frequency:** Ежедневная проверка обновлений
- **Storage efficiency:** Deduplication кейсов (hash-based)
- **Search relevance:** >0.8 precision@10 (векторный поиск)
- **Coverage:** 100% ISO 22301, 80% BCI GPG, 60% WHO Framework

---

## 📞 Следующие шаги

1. **Approve architecture** - подтвердить предложенную структуру
2. **Create structure** - создать директории data/
3. **Migrate ISO-22301** - переместить библиотеку
4. **Build Knowledge System** - реализовать модуль
5. **Integrate** - подключить к существующим системам
6. **Setup auto-update** - настроить Temporal workflows

Готов начать реализацию?
