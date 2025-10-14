# Service Catalog v2.0

**Status**: ✅ Integrated into Service Discovery v2.0
**Location**: `/infrastructure/runtime/service-catalog/`
**Schema Version**: 2.0
**Last Updated**: October 11, 2025

## Overview

Централизованный каталог всех сервисов AI Platform ISO 22301. Содержит статические шаблоны сервисов, которые комбинируются с runtime данными через Service Discovery v2.0.

## 📁 Files

- **`service-catalog.yaml`** - Основной каталог сервисов (27 сервисов)
- **`service-catalog.json`** - JSON версия каталога
- **`CATALOG_SCHEMA.md`** - 📋 **Полная официальная спецификация схемы**
- **`QUICK_REFERENCE.md`** - ⚡ **Быстрая справка для разработчиков**
- **`INFRASTRUCTURE_CATALOG.md`** - Документация инфраструктуры
- **`README.md`** - Этот файл

## 🚀 Быстрый старт

### Для разработчиков: Добавить новый сервис

1. **Прочитайте**: `QUICK_REFERENCE.md` (2 минуты)
2. **Скопируйте** шаблон из Quick Reference
3. **Заполните** обязательные поля
4. **Добавьте** в `service-catalog.yaml`
5. **Валидируйте** (см. ниже)

### Для архитекторов: Понять схему

Читайте `CATALOG_SCHEMA.md` - полная официальная спецификация со всеми разделами, правилами и примерами.

## 📊 Структура каталога

### Обязательные разделы

```yaml
metadata:                          # Метаданные каталога
  platform_name: string           # "AI-Platform-ISO"
  version: string                 # Semver (2.0.0)
  generated_at: datetime          # ISO 8601
  total_services: integer         # Автоподсчет

services:                          # Массив сервисов
  - name: string                  # ✅ REQUIRED
    type: string                  # ✅ REQUIRED
    business_process: string      # ✅ REQUIRED
    port: integer | null          # ✅ REQUIRED
    status: string                # ✅ REQUIRED
    path: string                  # ✅ REQUIRED
    kpis: array                   # ✅ REQUIRED (min 4)
    dependencies: array           # ✅ REQUIRED
    metrics_endpoint: string      # ✅ REQUIRED для HTTP
    health_endpoint: string       # ✅ REQUIRED для HTTP
    framework: string             # 📝 OPTIONAL
```

## 🏷️ Типы сервисов

| Тип | Количество | Примеры |
|-----|-----------|---------|
| `infrastructure/gateway` | 1 | api-gateway |
| `infrastructure/observability` | 2 | monitoring-backend, notification-service |
| `infrastructure/AI-office-infrastructure` | ~7 | mio-manager, orchestrator, analytics-specialist |
| `infrastructure/runtime` | ~4 | service-discovery, message-queue |
| `infrastructure/security` | ~3 | auth, secrets-manager |
| `intelligent-core` | 10 | ai-foundation, workflow_intelligence, predictive |
| `platform-services` | 12 | bia-service, compliance-service, risk-service |
| `interface` | 3 | admin-control-center, admin_panel, web-app |

**Полный список**: См. `CATALOG_SCHEMA.md` раздел 2

## 📈 KPIs

### Базовые (обязательные для HTTP)
```yaml
kpis:
  - request_latency_ms          # ✅
  - requests_per_second         # ✅
  - error_rate_percent          # ✅
  - availability_percent        # ✅
```

### Специализированные

- **AI Services**: `ai_decisions_total`, `ml_prediction_accuracy`, `knowledge_graph_size`
- **Workflow**: `workflows_executed`, `workflow_success_rate`, `avg_workflow_duration_sec`
- **Monitoring**: `coverage_percentage`, `alert_response_time`, `services_monitored`
- **UI**: `page_load_time_ms`, `time_to_interactive_ms`, `bundle_size_kb`

**Полный список**: См. `CATALOG_SCHEMA.md` раздел 4

## 🔌 Integration с Service Discovery v2.0

Service Catalog интегрирован в Service Discovery через `catalog_integration.py`:

```python
# Service Discovery автоматически загружает catalog
from infrastructure.runtime.service-discovery import CatalogIntegration

catalog = CatalogIntegration()
await catalog.load_catalog()  # Загружает service-catalog.yaml

# Получить unified view (catalog + runtime)
unified_services = await catalog.get_all_unified_services(registry)

# Найти missing services (в каталоге но не запущены)
missing = await catalog.get_missing_services(registry)

# Найти unknown services (запущены но не в каталоге)
unknown = await catalog.get_unknown_services(registry)
```

### API Endpoints

Service Discovery v2.0 предоставляет:

```http
GET /v2/catalog/services       # Все сервисы (unified view)
GET /v2/catalog/missing        # Missing services
GET /v2/catalog/unknown        # Unknown services
GET /v2/catalog/stats          # Статистика
```

**См. также**: `/infrastructure/runtime/service-discovery/README.md`

## 📚 Документация

### Для разработчиков
- **QUICK_REFERENCE.md** - Быстрая справка (3 мин)
- Checklist для нового сервиса
- Готовые шаблоны
- Частые ошибки

### Для архитекторов
- **CATALOG_SCHEMA.md** - Полная спецификация (15 мин)
- Все разделы схемы
- Правила валидации
- Расширения
- Версионирование

### Для DevOps
- **Service Discovery README** - Integration guide
- EventBus integration
- Prometheus metrics
- Health checks

## ✅ Валидация

### Автоматическая валидация

```python
from infrastructure.runtime.service-discovery import CatalogIntegration

catalog = CatalogIntegration()
await catalog.load_catalog()

# Валидация происходит автоматически при загрузке
# Проверяет:
# - Обязательные поля
# - Уникальность имен
# - Валидность типов
# - Формат endpoints
```

### Ручная проверка

Checklist:
1. ⬜ Все обязательные поля заполнены
2. ⬜ Тип из официального списка
3. ⬜ Бизнес-процесс из официального списка
4. ⬜ Минимум 4 базовых KPI
5. ⬜ Endpoints для HTTP сервисов
6. ⬜ Port в правильном диапазоне
7. ⬜ Имя уникально

## 🔄 Обновление каталога

### Автоматическая генерация

```bash
cd infrastructure/tools/analyzers
python3 discover_services.py
```

Сгенерирует новый `service-catalog.yaml` на основе сканирования директорий.

### Ручное обновление

1. Отредактируйте `service-catalog.yaml`
2. Обновите `metadata.version`
3. Обновите `metadata.generated_at`
4. Обновите `metadata.total_services`
5. Валидируйте (см. выше)

## 📊 Статистика (текущая)

- **Всего сервисов:** 27
- **С портами (HTTP):** 8
- **Intelligent Core:** 10
- **Platform Services:** 12
- **Infrastructure:** ~7
- **Interface:** 3

### По бизнес-процессам

| Процесс | Количество |
|---------|-----------|
| AI Intelligence & Decision Support | 4 |
| Workflow Orchestration & Automation | 3 |
| Business Continuity Planning | 2 |
| ISO 22301 Compliance Management | 1 |
| User Interface & Presentation | 3 |
| System Monitoring & Observability | 2 |
| Core Platform Services | 5 |
| *Остальные* | 7 |

## 🔗 Связанные ресурсы

- **Service Discovery v2.0**: `/infrastructure/runtime/service-discovery/`
- **MIO Manager**: `/infrastructure/AI-office-infrastructure/mio-manager/`
- **Archive**: `/_archive/runtime-deprecated-20251011/`
- **Migration Guide**: `/_archive/runtime-deprecated-20251011/MIGRATION_COMPLETE.md`

## 📝 Changelog

### v2.0.0 (October 11, 2025)
- ✅ Интеграция с Service Discovery v2.0
- ✅ Создана официальная спецификация схемы
- ✅ Добавлена быстрая справка
- ✅ Добавлен тип `infrastructure/AI-office-infrastructure`
- ✅ Расширены KPIs для monitoring сервисов
- ✅ Добавлена поддержка EventBus integration

### v1.0.0 (October 10, 2025)
- Первая версия каталога
- 27 сервисов
- Базовая структура

---

**Approved**: ✅ AI Platform Architecture Team
**Version**: 2.0.0
**Last Updated**: October 11, 2025
