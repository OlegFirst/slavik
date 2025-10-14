# 📚 Индекс Документации: Каталог Сервисов

**Обновлено:** 2025-10-11
**Всего сервисов:** 47
**Версия каталога:** 3.0.0

---

## 🎯 Быстрая Навигация

### 📊 Главные Отчеты (Читать в порядке важности):

1. **[FINAL_CATALOG_INTEGRATION_REPORT.md](./FINAL_CATALOG_INTEGRATION_REPORT.md)** ⭐ **ГЛАВНЫЙ**
   - **20 KB** | Полная сводка интеграции
   - 47 сервисов, все категории
   - Grafana, Security, Monitoring
   - Проблемы и рекомендации
   - Quick Start инструкции

2. **[SERVICE_CATALOG_UPDATE_COMPLETE.md](./SERVICE_CATALOG_UPDATE_COMPLETE.md)**
   - **12 KB** | Обновление 13 сервисов
   - Добавлены: collective, ai_workflow_optimizer
   - Исправлен конфликт портов
   - SERVICE_INFO.yaml создано

3. **[SERVICE_CATALOG_INTEGRATION_COMPLETE.md](./SERVICE_CATALOG_INTEGRATION_COMPLETE.md)**
   - **16 KB** | Первичная интеграция
   - Service Discovery v2.0
   - Prometheus + Grafana
   - Генераторы каталога и документации

---

## 📁 Каталоги Сервисов

### Основные Каталоги:

| Файл | Размер | Сервисов | Описание |
|------|--------|----------|----------|
| **[infrastructure/SERVICE_CATALOG_DETAILED.yaml](./infrastructure/SERVICE_CATALOG_DETAILED.yaml)** | ~150 KB | 47 | Полный детальный каталог всех сервисов |
| **[infrastructure/runtime/service-catalog/service-catalog.yaml](./infrastructure/runtime/service-catalog/service-catalog.yaml)** | 126 KB | 13 | Компактный каталог (SERVICE_INFO.yaml) |
| **[UNIFIED_SERVICE_CATALOG.yaml](./UNIFIED_SERVICE_CATALOG.yaml)** | 126 KB | 13 | Root-level каталог (копия) |

### Резервные Копии:

- `infrastructure/SERVICE_CATALOG_DETAILED_backup.yaml` - Резервная копия (до merge)

---

## 📄 Документация по Категориям

### 🏗️ Infrastructure (19 сервисов)

**Отчеты:**
- `infrastructure/database/COMPLETE_IMPLEMENTATION_SUMMARY.md` - Database summary
- `infrastructure/database/INTEGRATION_COMPLETE_SUMMARY.md` - Integration details
- `infrastructure/observability/GRAFANA_QUICKSTART.md` - Grafana quick start

**Ключевые сервисы:**
- PostgreSQL (5432) - 29 schemas, Supabase
- Redis (6379) - Caching & pub/sub
- RabbitMQ (5672) - EventBus
- Service Discovery (8500) - Registry
- Grafana (3000) - Dashboards
- Prometheus (9090) - Metrics

### 🤖 AI Office (6 сервисов)

**Ключевые сервисы:**
- analytics-specialist (8009)
- orchestrator (8003)
- project-agent (8008)
- agent-router (8010)
- ai-event-manager (8016)
- mio-manager (8013)

### 🏢 Platform Services (10 сервисов)

**SERVICE_INFO.yaml файлы:**
- `platform-services/plans_service/SERVICE_INFO.yaml`
- `platform-services/documents-service/SERVICE_INFO.yaml`
- `platform-services/governance-service/SERVICE_INFO.yaml`
- `platform-services/compliance-service/SERVICE_INFO.yaml`
- `platform-services/risk-service/SERVICE_INFO.yaml`
- `platform-services/response-service/SERVICE_INFO.yaml`

**Остальные (в DETAILED каталоге):**
- planning_service (8011)
- bia_service (8012)
- learning_service (8021)
- validation_service (8022)

### 🧠 Intelligent Core (12 сервисов)

**SERVICE_INFO.yaml файлы:**
- `intelligent-core/workflow-engine/SERVICE_INFO.yaml` (8030)
- `intelligent-core/orchestration/ai-orchestration/SERVICE_INFO.yaml` (8002)
- `intelligent-core/event_intelligence/SERVICE_INFO.yaml` (8032)
- `intelligent-core/predictive/SERVICE_INFO.yaml` (8031)
- `intelligent-core/coordination-center/SERVICE_INFO.yaml` (8033, planned)
- `intelligent-core/collective/SERVICE_INFO.yaml` (8034) ✨ **NEW**
- `intelligent-core/ai_workflow_optimizer/SERVICE_INFO.yaml` (8038) ✨ **NEW**

**Остальные (в DETAILED каталоге):**
- workflow_intelligence (8037)
- ai-foundation (8040)
- expertise_center (library)
- community_intelligence (8030) ⚠️ **конфликт порта**
- system_bcm_service (8050)

---

## 🛠️ Инструменты и Скрипты

### Генерация Каталога:

| Скрипт | Назначение | Путь |
|--------|-----------|------|
| **generate_catalog.py** | Сканирует SERVICE_INFO.yaml, генерирует каталог | `infrastructure/runtime/service-catalog/` |
| **merge_catalogs.py** | Объединяет DETAILED + SERVICE_INFO | `infrastructure/runtime/service-catalog/` |
| **generate_docs.py** | Генерирует MD/HTML/JSON/Mermaid | `infrastructure/runtime/service-catalog/` |
| **quickstart.sh** | Автоматизация setup | `infrastructure/runtime/service-catalog/` |

### Использование:

```bash
# 1. Генерация каталога из SERVICE_INFO.yaml
python3 infrastructure/runtime/service-catalog/generate_catalog.py

# 2. Объединение с детальным каталогом
python3 infrastructure/runtime/service-catalog/merge_catalogs.py

# 3. Генерация документации
python3 infrastructure/runtime/service-catalog/generate_docs.py

# 4. Быстрый старт (все в одном)
./infrastructure/runtime/service-catalog/quickstart.sh
```

---

## 📊 Генерированная Документация

### Форматы Документации:

| Формат | Файл | Размер | Описание |
|--------|------|--------|----------|
| **Markdown** | `docs/service-catalog/SERVICE_CATALOG.md` | 15 KB | Полная документация |
| **HTML** | `docs/service-catalog/service-catalog.html` | 11 KB | Веб-интерфейс |
| **JSON** | `docs/service-catalog/service-catalog.json` | 183 KB | Программный доступ |
| **Mermaid** | `docs/service-catalog/architecture-diagram.md` | 1 KB | Диаграмма архитектуры |

### Просмотр:

```bash
# Markdown
cat docs/service-catalog/SERVICE_CATALOG.md

# HTML (откроется в браузере)
open docs/service-catalog/service-catalog.html

# JSON (программный доступ)
cat docs/service-catalog/service-catalog.json | jq
```

---

## 🔍 Service Discovery

### REST API Endpoints:

```bash
# Запустить Service Discovery
cd infrastructure/runtime/service-discovery
python3 main.py

# API endpoints (http://localhost:8500):
GET  /v2/catalog/services         # All unified services
GET  /v2/catalog/services/{name}  # Single service details
GET  /v2/catalog/stats             # Statistics
GET  /v2/catalog/missing           # Missing services
GET  /v2/catalog/unknown           # Unknown services
GET  /v2/catalog/healthy           # Healthy services only
```

### Документация:

- API Docs: `http://localhost:8500/docs` (Swagger UI)
- Health: `http://localhost:8500/health`
- Metrics: `http://localhost:8500/metrics` (Prometheus)

---

## 📈 Grafana & Monitoring

### Dashboards (3 готовых):

1. **Security & Data Management Dashboard**
   - Файл: `infrastructure/observability/grafana/provisioning/dashboards/security-dashboard.json`
   - Панелей: 12
   - Метрики: Vault, Events, Sessions, Archive

2. **Service Catalog Dashboard**
   - Панелей: 5
   - Метрики: Services, Coverage, Missing, Health

3. **PostgreSQL Dashboard**
   - Панелей: 8
   - Метрики: Connections, Queries, Schemas

### Quick Start:

```bash
# 1. Запустить Docker
open -a Docker

# 2. Запустить Grafana + Prometheus
cd infrastructure/observability
docker-compose -f docker-compose.grafana.yml up -d

# 3. Открыть Grafana
open http://localhost:3000
# Login: admin / admin

# 4. Найти дашборды
# Dashboards > Security & Data Management Dashboard
```

### Документация:

- `infrastructure/observability/GRAFANA_QUICKSTART.md` - Quick start guide
- Grafana UI: `http://localhost:3000`
- Prometheus: `http://localhost:9090`

---

## 🔐 Security & Archiving

### Vault Integration:

- **Service:** HashiCorp Vault (8200)
- **Secrets:** 4 хранится
- **Endpoints:** `/vault/*` (via db-intelligence)

### Archive Service:

- **Formats:** JSON, CSV + gzip
- **Tables:** 8+ партиционированных таблиц
- **Retention:** 15+ политик
- **Endpoints:** `/archive/*` (via db-intelligence)

### Документация:

- `infrastructure/database/COMPLETE_IMPLEMENTATION_SUMMARY.md`
- `infrastructure/database/INTEGRATION_COMPLETE_SUMMARY.md`

---

## ⚠️ Известные Проблемы

### 1. КРИТИЧЕСКИЙ: Конфликт портов (8030)

**Проблема:**
- `workflow-engine` (8030) - из SERVICE_INFO.yaml
- `community_intelligence` (8030) - из SERVICE_CATALOG_DETAILED.yaml

**Статус:** Требует проверки в main.py/config.py

**Решение:**
```bash
# Проверить реальный порт
grep -r "PORT.*8030" /Users/MD/AI-Platform-ISO/intelligent-core/

# Изменить один из сервисов на 8035 или 8036
```

### 2. Недостающие SERVICE_INFO.yaml

**34 сервиса** без SERVICE_INFO.yaml:
- Все описаны в SERVICE_CATALOG_DETAILED.yaml
- Требуется постепенное создание SERVICE_INFO.yaml

**Приоритет:**
- workflow_intelligence (8037)
- ai-foundation (8040)
- community_intelligence (8030)
- system_bcm_service (8050)

### 3. Версионирование

**Текущая версия:** 3.0.0
**Планируется:** 4.0.0 (после решения конфликта портов)

---

## 📋 Отчеты от Других Команд

### Infrastructure Reports:

- `infrastructure/CATALOG_DISCREPANCIES_REPORT.md` - Анализ несоответствий
- `infrastructure/PLATFORM_SERVICES_FULL_REPORT.md` - Platform services детали
- `infrastructure/PORT_CONFLICTS_CRITICAL.md` - Критические конфликты портов
- `infrastructure/FINAL_TRUTH_REPORT.md` - Источник истины о портах
- `infrastructure/QUICK_FIX_SUMMARY.md` - Краткая сводка исправлений
- `infrastructure/CATALOG_FIXES_REQUIRED.md` - План исправлений
- `infrastructure/CATALOG_UPDATE_FINAL_REPORT.md` - Финальный отчёт обновления

**Всего отчётов:** 20+ файлов

---

## 🎯 Рекомендации

### Немедленно (Критично):
- [ ] Решить конфликт портов 8030
- [ ] Обновить версию каталога до 4.0.0
- [ ] Запустить Grafana и проверить дашборды

### Краткосрочно (1-2 недели):
- [ ] Создать SERVICE_INFO.yaml для приоритетных сервисов (4-5)
- [ ] Автоматизировать обновление DETAILED каталога
- [ ] Настроить CI/CD для валидации

### Долгосрочно (1-3 месяца):
- [ ] Unified catalog format (один источник истины)
- [ ] Auto-discovery сервисов
- [ ] Service mesh integration
- [ ] OpenAPI spec generation

---

## 🚀 Quick Start (TL;DR)

```bash
# 1. Просмотр каталога
cat infrastructure/SERVICE_CATALOG_DETAILED.yaml
open docs/service-catalog/service-catalog.html

# 2. Service Discovery
cd infrastructure/runtime/service-discovery
python3 main.py
curl http://localhost:8500/v2/catalog/services

# 3. Grafana
cd infrastructure/observability
docker-compose -f docker-compose.grafana.yml up -d
open http://localhost:3000  # admin/admin

# 4. Новые сервисы
cd intelligent-core/collective && python3 main.py  # 8034
cd intelligent-core/ai_workflow_optimizer && python3 main.py  # 8038
```

---

## 📞 Контакты и Поддержка

### Команды:

- **Service Catalog Core Team** - SERVICE_INFO.yaml, генераторы, Service Discovery
- **Grafana & Security Team** - Dashboards, Vault, Retention, Archive

### Каналы:

- **Slack:** #intelligent-core, #platform-services
- **Documentation:** Все файлы в `/docs/service-catalog/`
- **Issues:** JIRA проекты Platform Services, Intelligent Core

---

## 📊 Метрики Успеха

### ✅ Достигнуто:

- **Сервисов задокументировано:** 47/47 (100%)
- **SERVICE_INFO.yaml создано:** 13/47 (28%)
- **Инструментов создано:** 4 (генераторы + quickstart)
- **Dashboards готовы:** 3 (Security, Catalog, PostgreSQL)
- **Форматов документации:** 4 (MD, HTML, JSON, Mermaid)
- **Отчётов создано:** 20+

### 🎯 Статус: **INTEGRATION COMPLETE** ✅

---

**Последнее обновление:** 2025-10-11
**Версия индекса:** 1.0.0
**Статус:** ✅ CURRENT
