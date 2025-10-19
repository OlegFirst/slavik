# 📚 Platform Catalogs - Central Repository

**Создано**: 2025-10-12
**Цель**: Единое место для всех каталогов платформы

---

## 🎯 Структура

```
catalogs/
├── services/              # Каталоги сервисов
│   ├── SERVICE_CATALOG_DETAILED.yaml        # Главный каталог (45 сервисов)
│   └── SERVICE_CATALOG_SUMMARY.yaml         # Краткая версия
│
├── subsystems/            # Подсистемы (L2)
│   ├── SUBSYSTEMS_CATALOG.yaml              # Все подсистемы
│   ├── database_infrastructure.yaml         # PostgreSQL, Redis, Qdrant
│   ├── runtime_services.yaml                # EventBus, Service Discovery
│   ├── gateway_layer.yaml                   # API Gateway, Balancer
│   ├── security.yaml                        # Auth, Vault, Secrets
│   ├── ai_office.yaml                       # MIO, Analytics, Agents
│   ├── platform_services.yaml               # BIA, Risk, Plans, etc.
│   └── intelligent_core.yaml                # Workflow, Predictive, etc.
│
├── systems/               # Системы (L3)
│   ├── SYSTEMS_CATALOG.yaml                 # Все системы
│   ├── infrastructure_system.yaml           # База платформы
│   ├── ai_intelligence_system.yaml          # AI ядро
│   └── business_platform_system.yaml        # Бизнес-логика
│
├── workflows/             # Воркфлоу (YAML)
│   ├── WORKFLOWS_CATALOG.yaml               # Индекс всех воркфлоу
│   ├── infrastructure/                      # L1 инфраструктурные
│   ├── subsystem/                           # L2 подсистемные
│   ├── intersystem/                         # L3 межсистемные
│   └── user/                                # L4 пользовательские
│
└── scenarios/             # Сценарии (YAML)
    ├── SCENARIOS_CATALOG.yaml               # Индекс всех сценариев
    ├── level1-modules/                      # L1 модульные
    ├── level2-subsystems/                   # L2 подсистемные
    ├── level3-intersystem/                  # L3 межсистемные
    └── level4-user/                         # L4 пользовательские
```

---

## 📋 Каталоги

### 0. **NEW!** Platform Integration Infrastructure 🎭
**Статус**: ✅ VERIFIED & PRODUCTION READY
**Файл**: `/catalogs/PLATFORM_INTEGRATION_CATALOG.yaml`
**Дата**: 2025-10-19

**Graceful Choreography** - объединенная интеграция 4 архитектурных паттернов:
- ✅ Intelligent EventBus (1,800+ строк)
- ✅ Saga Pattern Engine (6,600+ строк)
- ✅ Self-Aware Services (5,700+ строк)
- ✅ CQRS Infrastructure (6,400+ строк)

**Тесты**: 9/9 PASSED (100%)
**Всего кода**: ~33,400 строк + документация

**Документация**:
- [INTEGRATION_COMPLETE.md](../INTEGRATION_COMPLETE.md)
- [INTEGRATION_VERIFICATION_COMPLETE.md](../INTEGRATION_VERIFICATION_COMPLETE.md)
- [Platform Integration Guide](../DOC/PLATFORM_INTEGRATION_GUIDE.md)

---

### 1. Services (Сервисы)
**Источник**: `/infrastructure/SERVICE_CATALOG_DETAILED.yaml`
**Копия здесь**: `/catalogs/services/SERVICE_CATALOG_DETAILED.yaml`

**45 сервисов в 10 категориях**:
- database_infrastructure (PostgreSQL, Redis, Qdrant)
- runtime_services (EventBus, Service Discovery, Message Queue)
- gateway_layer (API Gateway, Balancer)
- observability (Prometheus, Grafana)
- security (Auth, Vault, Secrets Manager)
- ai_office (MIO Manager, Analytics, Agents)
- platform_services (BIA, Risk, Plans, Document, etc.)
- intelligent_core (Workflow, Predictive, Community, etc.)
- interface_layer (Admin Panel, Control Center)
- shared_libraries (Common utilities)

---

### 2. Subsystems (Подсистемы)
**Уровень**: L2
**Файл**: `/catalogs/subsystems/SUBSYSTEMS_CATALOG.yaml`

**8 подсистем**:
1. **Database Infrastructure** - хранилище данных
2. **Runtime Services** - runtime компоненты
3. **Gateway Layer** - точка входа
4. **Security** - безопасность
5. **AI Office** - AI коллеги
6. **Platform Services** - бизнес-логика BCM
7. **Intelligent Core** - AI интеллект
8. **Interface Layer** - UI/UX

---

### 3. Systems (Системы)
**Уровень**: L3
**Файл**: `/catalogs/systems/SYSTEMS_CATALOG.yaml`

**3 системы**:
1. **Infrastructure System** - база всей платформы
2. **AI Intelligence System** - AI ядро
3. **Business Platform System** - BCM бизнес-процессы

---

### 4. Workflows (Воркфлоу)
**Формат**: YAML
**Хранение**: `/catalogs/workflows/` + PostgreSQL + Qdrant

**Типы воркфлоу**:
- Infrastructure workflows (L1)
- Subsystem workflows (L2)
- Inter-system workflows (L3)
- User workflows (L4)

**Пример**:
```yaml
workflow:
  meta:
    id: "workflow-database-backup"
    name: "Database Backup Workflow"
    level: 1
    subsystem: "database_infrastructure"

  steps:
    - name: "Check database health"
      service: "postgresql"
      action: "health_check"

    - name: "Create backup"
      service: "postgresql"
      action: "pg_dump"
      params:
        format: "custom"

    - name: "Upload to S3"
      service: "storage"
      action: "upload"
```

---

### 5. Scenarios (Сценарии)
**Формат**: YAML
**Хранение**: `/catalogs/scenarios/` + PostgreSQL + Qdrant

**4 уровня**:
- L1: Module scenarios (45 сценариев - по одному на сервис)
- L2: Subsystem scenarios (8 сценариев - по одному на подсистему)
- L3: Inter-system scenarios (интеграции между системами)
- L4: User scenarios (пользовательские E2E workflows)

---

## 🔄 Процесс работы

### Генерация каталогов:

```bash
# 1. Services Catalog (уже есть)
cp /infrastructure/SERVICE_CATALOG_DETAILED.yaml /catalogs/services/

# 2. Generate Subsystems Catalog
python3 /catalogs/scripts/generate_subsystems_catalog.py

# 3. Generate Systems Catalog
python3 /catalogs/scripts/generate_systems_catalog.py

# 4. Generate Workflows
python3 /catalogs/scripts/generate_workflows_from_services.py

# 5. Generate Scenarios
python3 /catalogs/scripts/generate_scenarios_from_subsystems.py
```

### Использование:

```python
# Load catalogs
from catalogs.loader import CatalogLoader

loader = CatalogLoader()

# Services
services = await loader.load_services()

# Subsystems
subsystems = await loader.load_subsystems()

# Workflows
workflows = await loader.load_workflows(level=2)

# Scenarios
scenarios = await loader.load_scenarios(level="L2")
```

---

## 💾 Хранение

### Triple Storage:

1. **File System** (`/catalogs/`) - Source of truth (YAML files)
2. **PostgreSQL** - Persistence, queries, relationships
3. **Qdrant** - Semantic search, RAG

### Синхронизация:

```python
# Auto-sync script
python3 /catalogs/scripts/sync_catalogs.py

# Sync workflow:
# 1. Read YAML from /catalogs/
# 2. Validate YAML
# 3. Save to PostgreSQL
# 4. Index in Qdrant
# 5. Register in Service Discovery
```

---

## 🎯 Преимущества

✅ **Единое место** - все каталоги в одной директории
✅ **Версионирование** - Git контроль всех YAML
✅ **Семантический поиск** - Qdrant RAG
✅ **Быстрый доступ** - PostgreSQL queries
✅ **Source of Truth** - YAML файлы
✅ **Auto-generation** - из Service Catalog

---

## 📝 Следующие шаги

1. ✅ Создать структуру `/catalogs/`
2. ⏳ Скопировать SERVICE_CATALOG_DETAILED.yaml
3. ⏳ Создать SUBSYSTEMS_CATALOG.yaml
4. ⏳ Создать SYSTEMS_CATALOG.yaml
5. ⏳ Генерировать workflows
6. ⏳ Генерировать scenarios

---

**Статус**: ✅ Структура создана
**Следующее**: Генерация каталогов подсистем и систем
