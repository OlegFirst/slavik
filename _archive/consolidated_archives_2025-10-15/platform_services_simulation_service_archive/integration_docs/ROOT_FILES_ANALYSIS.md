# Root Files Analysis Report
**Date**: 2025-10-13
**Question**: "это от куда?" (where are these from?)

**Files in question**:
- `/platform-services/simulation/API.md`
- `/platform-services/simulation/__init__.py`
- `/platform-services/simulation/README.md`
- `/platform-services/simulation/KPI.yaml`

---

## 🔍 ANALYSIS RESULT

### Source: **СТАРАЯ ВЕРСИЯ v1.0 (Old Version v1.0)**

Эти файлы находятся в **КОРНЕВОЙ директории старого модуля** `/simulation/simulation/`:

```
/Users/MD/AI-Platform-ISO/platform-services/simulation/
├── API.md              ← АВТО-ГЕНЕРАЦИЯ (233 endpoints от старых модулей)
├── __init__.py         ← ПУСТОЙ ФАЙЛ (0 bytes)
├── README.md           ← Общее описание старого модуля
├── KPI.yaml            ← KPI метрики старого модуля
├── simulation/         ← СТАРЫЕ МОДУЛИ (v1.0)
│   ├── simulation2/
│   ├── scenario_orchestrator/
│   ├── bia_engine_O/
│   ├── exercise_simulators/
│   ├── engines/
│   ├── integrations/
│   ├── bia_engine/
│   ├── models/
│   ├── workers/
│   └── api/
└── simulation-service/ ← НОВЫЙ МОДУЛЬ (v2.0) ✅ ТУТ МЫ РАБОТАЕМ
    ├── api/
    ├── core/
    ├── engines/
    ├── integration/
    ├── storage/
    └── ...
```

---

## 📄 FILE BREAKDOWN

### 1. `API.md` (71,391 bytes)
**Тип**: Авто-генерированная API документация
**Дата**: 2025-10-07 05:07
**Содержание**: 233 endpoints из старых модулей

**Сгенерировано из**:
- main.py
- app.py
- simple_app.py
- bia.py
- scenarios.py
- predictions.py
- simulations.py
- organizations.py
- exercises.py
- bridge_service.py
- thehive_adapter.py
- sim_adapter.py
- И многие другие старые модули...

**Примеры endpoints**:
```
GET  /
GET  /health (16 разных файлов!)
POST /ai-generate
POST /ai-scenarios/generate/{twin_id}
POST /bia/analyze/{twin_id}
GET  /api/cases
POST /api/simulations/start
GET  /api/thehive/{config_id}/alerts
POST /api/v1/exercises/create
GET  /learning/dashboard
POST /monte-carlo
GET  /scenarios
POST /simulations
```

**Статус**: ❌ **УСТАРЕВШАЯ ДОКУМЕНТАЦИЯ**
- Описывает 233 endpoints из **старых разрозненных модулей**
- Много дублирующихся endpoint'ов (например, 16x `/health`)
- Не отражает новую архитектуру `simulation-service`

**Что делать**:
- ✅ Можно **удалить** - это автогенерация из старого кода
- Новая документация должна генерироваться из `simulation-service/`

---

### 2. `__init__.py` (0 bytes)
**Тип**: Пустой Python package marker
**Дата**: 2025-10-06 13:27
**Содержание**: ПУСТОЙ ФАЙЛ

**Назначение**: Маркирует директорию `/simulation/` как Python package

**Статус**: ✅ **НОРМАЛЬНО**
- Пустой `__init__.py` - стандартная практика
- Позволяет делать `from simulation import ...`

**Что делать**: ✅ **Оставить как есть**

---

### 3. `README.md` (2,482 bytes)
**Тип**: Общее описание модуля
**Дата**: 2025-10-08 20:50
**Содержание**: Overview старого simulation модуля

**Ключевые данные**:
```yaml
Type: Platform Service
Domain: Business Continuity Management
Status: Active
Version: 2.0.0

Metrics (СТАРЫЕ):
  Total Lines of Code: 44,465
  Python Files: 160
  Classes: 382
  Functions: 81
  API Endpoints: 168
  Dependencies: 138
```

**Интеграции упомянутые**:
- EventBus
- Workflow Intelligence
- AI Foundation
- PostgreSQL 14+
- Redis 7+
- RabbitMQ 3.12+

**Статус**: ⚠️ **ЧАСТИЧНО УСТАРЕВШИЙ**
- Метрики отражают **старую кодовую базу** (44,465 lines, 160 files, 168 endpoints)
- Новый `simulation-service` имеет другую структуру

**Что делать**:
- ⚠️ **Обновить** с метриками нового `simulation-service`
- Или **переместить** в `simulation-service/README.md`

---

### 4. `KPI.yaml` (1,134 bytes)
**Тип**: KPI метрики для мониторинга
**Дата**: 2025-10-09 21:23
**Содержание**: Prometheus/Grafana метрики

**Определенные KPI**:
```yaml
module_name: simulation
version: 1.0.0
description: '**Type**: Platform Service'
module_type: service
owner: platform-team

kpis:
  - request_count (> 1000/day)
  - response_time_p95 (< 500ms)
  - error_rate (< 1%)
  - availability (> 99.5%)

monitoring:
  prometheus_enabled: true
  grafana_dashboard: dashboards/simulation.json
  alert_rules: alerts/simulation.yaml
```

**Статус**: ✅ **АКТУАЛЬНО**
- KPI метрики универсальны для любого сервиса
- Применимы и к `simulation-service`
- Prometheus/Grafana интеграция

**Что делать**:
- ✅ **Переместить** в `simulation-service/KPI.yaml`
- Обновить `version: 2.0.0`

---

## 📊 SUMMARY TABLE

| Файл | Размер | Дата | Источник | Статус | Действие |
|------|--------|------|----------|--------|----------|
| `API.md` | 71 KB | Oct 7 | Авто-генерация из старых модулей | ❌ Устарел | УДАЛИТЬ или архивировать |
| `__init__.py` | 0 bytes | Oct 6 | Package marker | ✅ Норма | ОСТАВИТЬ |
| `README.md` | 2.4 KB | Oct 8 | Описание старого модуля | ⚠️ Частично устарел | ОБНОВИТЬ с новыми метриками |
| `KPI.yaml` | 1.1 KB | Oct 9 | KPI метрики | ✅ Актуально | ПЕРЕМЕСТИТЬ в simulation-service/ |

---

## 🎯 RECOMMENDED ACTIONS

### 1. API.md - УДАЛИТЬ ИЛИ АРХИВИРОВАТЬ
```bash
# Архивировать старую документацию
mkdir -p /Users/MD/AI-Platform-ISO/platform-services/simulation/_archive_v1/
mv /Users/MD/AI-Platform-ISO/platform-services/simulation/API.md \
   /Users/MD/AI-Platform-ISO/platform-services/simulation/_archive_v1/API_old_233_endpoints.md

# Или просто удалить
rm /Users/MD/AI-Platform-ISO/platform-services/simulation/API.md
```

**Обоснование**:
- Описывает 233 endpoints из старых разрозненных модулей
- Много дублей (16x `/health`)
- Не отражает новую архитектуру

### 2. README.md - ОБНОВИТЬ ИЛИ ПЕРЕМЕСТИТЬ
```bash
# Вариант 1: Обновить существующий README с новыми метриками
# Edit /platform-services/simulation/README.md

# Вариант 2: Создать новый в simulation-service/
cp /Users/MD/AI-Platform-ISO/platform-services/simulation/README.md \
   /Users/MD/AI-Platform-ISO/platform-services/simulation/simulation-service/README.md
# Затем обновить метрики
```

**Новые метрики для README**:
```yaml
Version: 2.0.0
Status: Active - Unified Architecture

Metrics (NEW):
  Total Lines of Code: ~12,000 (integrated from v1.0)
  Python Files: 45+ (unified structure)
  Simulation Engines: 7 (JaamSim, Monte Carlo, Scenario, What-If, BIA-CIW, BCM, Advanced)
  Integration Clients: 11 (TheHive, NICS, JaamSim, Community, Workflow, Predictive, etc.)
  API Routers: 6 (Bridge, Scenario Advanced, Simulation, Execution, Scenario, Library)
  API Endpoints: 31 (consolidated from 233)
  Database Models: 4 (Simulation, Scenario, Execution, Result)
```

### 3. KPI.yaml - ПЕРЕМЕСТИТЬ В НОВЫЙ СЕРВИС
```bash
# Переместить в simulation-service
mv /Users/MD/AI-Platform-ISO/platform-services/simulation/KPI.yaml \
   /Users/MD/AI-Platform-ISO/platform-services/simulation/simulation-service/KPI.yaml

# Обновить version в файле
sed -i '' 's/version: 1.0.0/version: 2.0.0/' \
   /Users/MD/AI-Platform-ISO/platform-services/simulation/simulation-service/KPI.yaml
```

### 4. __init__.py - ОСТАВИТЬ КАК ЕСТЬ
```bash
# Ничего не делать - пустой __init__.py это норма
```

---

## 🗂️ ИТОГОВАЯ СТРУКТУРА (После очистки)

```
/Users/MD/AI-Platform-ISO/platform-services/simulation/
├── __init__.py                  ← ОСТАВИТЬ (package marker)
├── README.md                    ← ОБНОВИТЬ (с новыми метриками)
├── _archive_v1/                 ← СОЗДАТЬ для старых файлов
│   └── API_old_233_endpoints.md ← ПЕРЕМЕСТИТЬ API.md сюда
├── simulation/                  ← СТАРЫЕ МОДУЛИ (можно архивировать)
│   └── [10 старых директорий]
└── simulation-service/          ← НОВЫЙ УНИФИЦИРОВАННЫЙ СЕРВИС ✅
    ├── KPI.yaml                 ← ПЕРЕМЕСТИТЬ сюда
    ├── README.md                ← СОЗДАТЬ новый или обновить
    ├── api/                     ← 6 routers, 31 endpoints
    ├── core/                    ← AI generation, flow management
    ├── engines/                 ← 7 simulation engines
    ├── integration/             ← 11 integration clients
    ├── storage/                 ← Database models
    └── main.py
```

---

## ✅ FINAL ANSWER

### **Вопрос**: "это от куда?"

### **Ответ**:

Эти 4 файла - **МЕТАДАННЫЕ СТАРОГО МОДУЛЯ v1.0**:

1. **API.md** (71 KB) - Авто-генерированная документация 233 endpoints из старых разрозненных модулей
   - **Источник**: Сгенерирована `tools/generators/documentation_generator.py` из `simulation/simulation/`
   - **Дата**: 2025-10-07 05:07
   - **Статус**: ❌ Устарела (описывает старую архитектуру)
   - **Действие**: Удалить или архивировать

2. **__init__.py** (0 bytes) - Пустой Python package marker
   - **Источник**: Стандартный Python файл
   - **Статус**: ✅ Нормально
   - **Действие**: Оставить

3. **README.md** (2.4 KB) - Общее описание simulation модуля
   - **Источник**: Ручная документация
   - **Метрики**: 44,465 lines, 160 files, 168 endpoints (старые)
   - **Статус**: ⚠️ Частично устарел
   - **Действие**: Обновить с новыми метриками

4. **KPI.yaml** (1.1 KB) - Prometheus/Grafana метрики
   - **Источник**: Конфигурация мониторинга
   - **Статус**: ✅ Актуально
   - **Действие**: Переместить в `simulation-service/`

---

**Рекомендация**:
- **Удалить** API.md (или архивировать)
- **Обновить** README.md с новыми метриками
- **Переместить** KPI.yaml в simulation-service/
- **Оставить** __init__.py

После очистки останется только актуальная документация для **нового унифицированного сервиса** ✅
