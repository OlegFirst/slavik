# 🛠️ Каталог инструментов AI Platform Infrastructure

**Полный индекс всех инструментов автоматизации платформы**

Создано: 2025-10-08
Статус: Активный анализ
AI Curator: Claude (AI Office Infrastructure)

---

## 📋 Содержание

1. [Обзор](#обзор)
2. [Структура директорий](#структура-директорий)
3. [Инструменты анализа (analyzers)](#analyzers---инструменты-анализа)
4. [Генераторы документации (doc-generators)](#doc-generators---генераторы-документации)
5. [Автогенерируемые конфиги (auto-generated)](#auto-generated---автогенерируемые-конфиги)
6. [Docker конфигурации (docker-generated)](#docker-generated---docker-конфигурации)
7. [Управление Docker (docker-management)](#docker-management---управление-docker)
8. [Статус автоматизации](#статус-автоматизации)
9. [Кто управляет инструментами](#кто-управляет-инструментами)
10. [Карта выходных данных](#карта-выходных-данных)

---

## 🎯 Обзор

### Назначение
Набор инструментов для автоматического анализа, документирования и развертывания микросервисной платформы AI-Platform-ISO.

### Статистика
- **Всего инструментов:** 25+
- **Анализаторов:** 11
- **Генераторов:** 7
- **Docker утилит:** 5
- **Строк кода:** ~38,655+ строк Python
- **Автоматизация:** 40% (10/25 инструментов)

### Архитектура
```
/infrastructure/tools/
├── analyzers/          # AST, зависимости, метрики, бизнес-логика
├── doc-generators/     # API docs, UI blueprints, тесты
├── auto-generated/     # Автогенерируемые конфигурации
├── docker-generated/   # Docker Compose по слоям
├── docker-management/  # Docker API wrapper
├── dashboards/         # Интерактивные визуализации
├── config/             # Конфигурации анализаторов
├── arhive/             # Архивные версии
└── vscode-extension/   # VSCode расширение
```

---

## 📁 Структура директорий

```
/Users/MD/AI-Platform-ISO/infrastructure/tools/
│
├── analyzers/              (11 инструментов, ~3,828 строк)
├── doc-generators/         (7 инструментов, ~2,827 строк)
├── auto-generated/         (7 файлов, автогенерация)
├── docker-generated/       (12 файлов, Docker configs)
├── docker-management/      (5 модулей, Docker API)
├── dashboards/             (Plotly визуализации)
├── config/                 (YAML конфиги)
├── arhive/                 (Старые версии)
├── vscode-extension/       (VSCode расширение)
└── README.md              (Главная документация)
```

---

## 🔍 ANALYZERS - Инструменты анализа

### Назначение
Автоматический анализ кодовой базы: AST, зависимости, метрики, бизнес-логика.

### Список инструментов

#### 1. **ast_analyzer.py** (13,032 строк)
**Функция:** Извлечение функций, классов, API endpoints из Python кода
**Автоматизация:** ❌ Ручной запуск
**Выходные данные:**
- `reports/ast_analysis.json` - JSON со всеми данными
- `reports/ast_analysis.md` - Markdown отчет

**Использование:**
```bash
python3 tools/analyzers/ast_analyzer.py
```

**Что извлекает:**
- Функции (имя, параметры, async/sync, декораторы)
- Классы (имя, базовые классы, методы)
- API Endpoints (path, method, handler function)
- Dependencies (imports, вызовы функций)

**Управляется:** Analytics Specialist AI (использует этот инструмент через wrapper)

---

#### 2. **dependency_mapper.py** (13,389 строк)
**Функция:** Построение графа зависимостей между модулями
**Автоматизация:** ❌ Ручной запуск
**Выходные данные:**
- `reports/dependencies.json` - Список зависимостей
- `reports/dependencies.md` - Markdown отчет
- `reports/dependency_graph.png` - Граф (PNG)
- `reports/dependency_graph.graphml` - Граф для Gephi/Cytoscape
- `reports/circular_dependencies.json` - Циклические зависимости

**Использование:**
```bash
python3 tools/analyzers/dependency_mapper.py
```

**Что анализирует:**
- Import statements (from X import Y)
- Circular dependencies
- Dependency depth
- Module coupling

**Управляется:** Analytics Specialist AI (dependency_mapper_tool.py wrapper)

---

#### 3. **dependency_validator.py** (20,494 строки)
**Функция:** Валидация зависимостей, обнаружение конфликтов
**Автоматизация:** ❌ Ручной запуск
**Выходные данные:**
- `reports/dependency_validation.json` - Результаты валидации
- `reports/conflicts.json` - Обнаруженные конфликты

**Использование:**
```bash
python3 tools/analyzers/dependency_validator.py
```

**Что проверяет:**
- Конфликты версий зависимостей
- Missing dependencies
- Unused dependencies
- Security vulnerabilities

**Управляется:** Analytics Specialist AI (middle+ level)

---

#### 4. **dependency_reconciler.py** (13,361 строка)
**Функция:** Автоматическое разрешение конфликтов зависимостей
**Автоматизация:** ❌ Ручной запуск
**Выходные данные:**
- `reports/dependency_reconciliation.md` - План разрешения конфликтов
- `requirements_reconciled.txt` - Исправленные зависимости

**Использование:**
```bash
python3 tools/analyzers/dependency_reconciler.py
```

**Управляется:** Analytics Specialist AI (senior+ level)

---

#### 5. **discover_services.py** (15,806 строк)
**Функция:** Автоматическое обнаружение всех сервисов в проекте
**Автоматизация:** ✅ Используется Infrastructure Builder
**Выходные данные:**
- `auto-generated/service-catalog.json` - Каталог всех сервисов

**Использование:**
```bash
python3 tools/analyzers/discover_services.py
```

**Что обнаруживает:**
- FastAPI приложения (main.py, app.py)
- Порты сервисов
- Зависимости между сервисами
- Health check endpoints

**Управляется:** Infrastructure Builder Orchestrator (AI Office)

---

#### 6. **api_mapper.py** (13,286 строк)
**Функция:** Маппинг всех API endpoints платформы
**Автоматизация:** ❌ Ручной запуск
**Выходные данные:**
- `reports/api_map.md` - Карта всех API
- `reports/api_endpoints.json` - JSON список endpoints

**Использование:**
```bash
python3 tools/analyzers/api_mapper.py
```

**Управляется:** Analytics Specialist AI + Project Agent

---

#### 7. **business_logic_mapper.py** (7,375 строк)
**Функция:** Извлечение бизнес-логики из кода
**Автоматизация:** ❌ Ручной запуск
**Выходные данные:**
- `reports/business_logic.md` - Описание бизнес-процессов

**Использование:**
```bash
python3 tools/analyzers/business_logic_mapper.py
```

**Управляется:** Project Agent (business logic analysis)

---

#### 8. **metrics_discovery.py** (16,279 строк)
**Функция:** Обнаружение Prometheus метрик в коде
**Автоматизация:** ❌ Ручной запуск
**Выходные данные:**
- `reports/metrics_coverage.json` - Покрытие метриками
- `prometheus.auto.yml` - Автогенерация Prometheus config

**Использование:**
```bash
python3 tools/analyzers/metrics_discovery.py
```

**Управляется:** Analytics Specialist AI (metrics_discovery_tool.py wrapper)

---

#### 9. **module_scanner.py** (21,843 строки)
**Функция:** Сканирование модулей проекта, структурный анализ
**Автоматизация:** ❌ Ручной запуск
**Выходные данные:**
- `reports/modules/*.md` - Отчеты по каждому модулю

**Использование:**
```bash
python3 tools/analyzers/module_scanner.py
```

**Управляется:** Infrastructure Builder + Analytics Specialist

---

#### 10. **generate_improved_compose.py** (12,277 строк)
**Функция:** Генерация улучшенного docker-compose.yml
**Автоматизация:** ✅ Используется Infrastructure Builder
**Выходные данные:**
- `auto-generated/docker-compose.improved.yml` - Улучшенная версия

**Использование:**
```bash
python3 tools/analyzers/generate_improved_compose.py
```

**Управляется:** Infrastructure Builder Orchestrator

---

### 📊 Выходные данные analyzers

**Директория:** `/infrastructure/tools/analyzers/reports/`

```
reports/
├── ast_analysis.json           # AST анализ (JSON)
├── ast_analysis.md             # AST анализ (Markdown)
├── dependencies.json           # Граф зависимостей
├── dependencies.md             # Отчет по зависимостям
├── dependency_graph.png        # Визуализация графа
├── dependency_graph.graphml    # Граф для Gephi
├── circular_dependencies.json  # Циклические зависимости
├── api_map.md                  # Карта API
├── api_endpoints.json          # Endpoints (JSON)
├── business_logic.md           # Бизнес-логика
├── metrics_coverage.json       # Покрытие метриками
└── modules/                    # Отчеты по модулям
    ├── workflow_intelligence_scan.md
    ├── community_intelligence_scan.md
    ├── orchestration_scan.md
    └── ... (47+ файлов)
```

---

## 📝 DOC-GENERATORS - Генераторы документации

### Назначение
Автоматическая генерация API документации, UI blueprints, тестов.

### Список инструментов

#### 1. **documentation_generator.py** (24,418 строк) ⭐
**Функция:** Генерация полной документации проекта
**Автоматизация:** ❌ Ручной запуск
**Выходные данные:**
- `docs/ARCHITECTURE.md` - Архитектура платформы
- `docs/API_REFERENCE.md` - API справочник
- `docs/SERVICES_OVERVIEW.md` - Обзор сервисов

**Использование:**
```bash
python3 tools/doc-generators/documentation_generator.py
```

**Управляется:** Project Agent (documentation tasks)

---

#### 2. **ai_documentation_generator.py** (21,740 строк)
**Функция:** AI-powered генерация документации через LLM
**Автоматизация:** ❌ Ручной запуск
**Выходные данные:**
- `docs/ai-generated/` - AI-генерированная документация

**Использование:**
```bash
python3 tools/doc-generators/ai_documentation_generator.py
```

**Управляется:** AI Foundation (LLM Router)

---

#### 3. **api_docs_generator.py** (9,992 строки)
**Функция:** Генерация API документации из OpenAPI спецификаций
**Автоматизация:** ❌ Ручной запуск
**Выходные данные:**
- `docs/api/validation.md` - Validation Service API
- `docs/api/documents.md` - Documents Service API
- `docs/api/postman_collection.json` - Postman коллекция

**Использование:**
```bash
python3 tools/doc-generators/api_docs_generator.py
```

**Требования:** Сервисы должны быть запущены

**Управляется:** Project Agent

---

#### 4. **ui_blueprint_gen.py** (14,718 строк)
**Функция:** Генерация UI blueprints для фронтенда
**Автоматизация:** ❌ Ручной запуск
**Выходные данные:**
- `docs/ui/validation_blueprint.html` - UI для Validation Service
- `docs/ui/documents_blueprint.html` - UI для Documents Service
- `docs/ui/validation_spec.json` - JSON спецификация экранов

**Использование:**
```bash
python3 tools/doc-generators/ui_blueprint_gen.py
```

**Управляется:** Project Agent

---

#### 5. **test_generator.py** (10,719 строк)
**Функция:** Автоматическая генерация pytest тестов
**Автоматизация:** ✅ GitHub Actions (project-agent-automation.yml)
**Выходные данные:**
- `/tests/generated/*.py` - Сгенерированные тесты

**Использование:**
```bash
python3 tools/doc-generators/test_generator.py --module validation-service
```

**Управляется:** Project Agent (автоматически при изменении кода)

---

#### 6. **event_catalog_generator.py** (13,686 строк)
**Функция:** Генерация каталога событий EventBus
**Автоматизация:** ❌ Ручной запуск
**Выходные данные:**
- `docs/events/EVENT_CATALOG.md` - Каталог всех событий
- `docs/events/event_flows.json` - Потоки событий

**Использование:**
```bash
python3 tools/doc-generators/event_catalog_generator.py
```

**Управляется:** Infrastructure Builder

---

#### 7. **prometheus_config_generator.py** (11,530 строк)
**Функция:** Генерация Prometheus конфигурации
**Автоматизация:** ✅ Используется Infrastructure Builder
**Выходные данные:**
- `auto-generated/prometheus.auto.yml` - Prometheus config
- `observability/config/prometheus/prometheus.yml` - Production config

**Использование:**
```bash
python3 tools/doc-generators/prometheus_config_generator.py
```

**Управляется:** Infrastructure Builder Orchestrator

---

### 📊 Выходные данные doc-generators

**Директории:**

```
docs/
├── api/                        # API документация
│   ├── README.md
│   ├── validation.md
│   ├── documents.md
│   └── postman_collection.json
├── ui/                         # UI Blueprints
│   ├── index.html
│   ├── validation_blueprint.html
│   ├── validation_spec.json
│   ├── documents_blueprint.html
│   └── documents_spec.json
├── events/                     # Event Catalog
│   ├── EVENT_CATALOG.md
│   └── event_flows.json
├── ai-generated/               # AI-generated docs
│   └── ...
└── architecture/
    ├── ARCHITECTURE.md
    ├── API_REFERENCE.md
    └── SERVICES_OVERVIEW.md

/tests/generated/               # Сгенерированные тесты
├── test_validation_service.py
├── test_documents_service.py
└── ...
```

---

## 🤖 AUTO-GENERATED - Автогенерируемые конфиги

### Назначение
Автоматически генерируемые конфигурации Docker Compose, Prometheus, Gateway.

### Содержимое

#### 1. **docker-compose.auto.yml** (18,186 строк)
**Генератор:** `discover_services.py` + `generate_improved_compose.py`
**Автоматизация:** ✅ Автогенерация
**Назначение:** Базовый docker-compose файл всех сервисов

---

#### 2. **docker-compose.improved.yml** (33,169 строк)
**Генератор:** `generate_improved_compose.py`
**Автоматизация:** ✅ Автогенерация
**Назначение:** Улучшенная версия с health checks, networks, volumes

---

#### 3. **service-catalog.json** (40,596 строк)
**Генератор:** `discover_services.py`
**Автоматизация:** ✅ Автогенерация
**Назначение:** Полный каталог всех обнаруженных сервисов

**Формат:**
```json
{
  "services": [
    {
      "name": "workflow-intelligence",
      "path": "/intelligent-core/workflow_intelligence",
      "port": 8037,
      "type": "fastapi",
      "health_endpoint": "/health",
      "dependencies": ["postgres", "redis"],
      "layer": "intelligent-core"
    }
  ],
  "total_services": 47,
  "last_scan": "2025-10-07T01:26:00Z"
}
```

---

#### 4. **prometheus.auto.yml** (5,433 строки)
**Генератор:** `prometheus_config_generator.py` + `metrics_discovery.py`
**Автоматизация:** ✅ Автогенерация
**Назначение:** Prometheus scrape configs для всех сервисов

---

#### 5. **gateway-routes.auto.json** (1,345 строк)
**Генератор:** `discover_services.py`
**Автоматизация:** ✅ Автогенерация
**Назначение:** API Gateway маршруты для всех сервисов

---

#### 6. **DOCKER_COMPOSE_USAGE.md** (1,940 строк)
**Генератор:** Документация автогенерации
**Назначение:** Инструкции по использованию сгенерированных файлов

---

### 📊 Использование auto-generated

```bash
# Использовать автогенерированный compose
cd /infrastructure/tools/auto-generated
docker-compose -f docker-compose.improved.yml up -d

# Просмотреть каталог сервисов
cat service-catalog.json | jq '.services[] | select(.layer == "intelligent-core")'

# Проверить Prometheus конфиг
cat prometheus.auto.yml | grep scrape_configs -A 50
```

**Управляется:** Infrastructure Builder Orchestrator (автоматическая регенерация)

---

## 🐳 DOCKER-GENERATED - Docker конфигурации по слоям

### Назначение
Docker Compose файлы, разделенные по архитектурным слоям для модульного запуска.

### Содержимое

#### 1. **docker-compose.gateway.yml** (1,004 строки)
**Генератор:** Infrastructure Builder (docker_compose_generator.py)
**Автоматизация:** ✅ Автогенерация
**Сервисы:**
- api-gateway (8000)
- unified-database-gateway (8008)
- intelligent-gateway (8005)

---

#### 2. **docker-compose.runtime.yml** (1,018 строк)
**Генератор:** Infrastructure Builder
**Автоматизация:** ✅ Автогенерация
**Сервисы:**
- realtime-websocket (8050)
- eventbus (библиотека)
- message-queue (библиотека)

---

#### 3. **docker-compose.observability.yml** (1,374 строки)
**Генератор:** Infrastructure Builder
**Автоматизация:** ✅ Автогенерация
**Сервисы:**
- monitoring (8047)
- mio-manager (8046)
- notification-service (8048)
- prometheus (9090)
- grafana (3000)

---

#### 4. **docker-compose.integration.yml** (786 строк)
**Генератор:** Infrastructure Builder
**Автоматизация:** ✅ Автогенерация
**Сервисы:**
- github-integration
- process-mining-service
- deployment-service

---

#### 5. **docker-compose.full.yml** (4,762 строки)
**Генератор:** Infrastructure Builder
**Автоматизация:** ✅ Автогенерация
**Назначение:** Все сервисы вместе (aggregated)

---

#### 6. **service-catalog.json** (35,220 строк)
**Генератор:** `discover_services.py`
**Назначение:** Каталог сервисов для Docker генерации

---

#### 7. **start_infrastructure.sh** (1,738 строк)
**Генератор:** Infrastructure Builder
**Автоматизация:** ✅ Автогенерация
**Использование:**
```bash
./start_infrastructure.sh gateway      # Только Gateway слой
./start_infrastructure.sh runtime      # Только Runtime слой
./start_infrastructure.sh observability # Только Observability
./start_infrastructure.sh integration  # Только Integration
./start_infrastructure.sh full         # Все сервисы
```

---

#### 8. **stop_infrastructure.sh** (792 строки)
**Генератор:** Infrastructure Builder
**Автоматизация:** ✅ Автогенерация
**Использование:**
```bash
./stop_infrastructure.sh full
```

---

#### 9. **check_health.sh** (896 строк)
**Генератор:** Infrastructure Builder
**Автоматизация:** ✅ Автогенерация
**Назначение:** Проверка здоровья всех сервисов

---

#### 10. **.env.template** (1,201 строка)
**Генератор:** Infrastructure Builder
**Автоматизация:** ✅ Автогенерация
**Назначение:** Шаблон переменных окружения

**Формат:**
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/db

# Redis
REDIS_URL=redis://localhost:6379

# Services
AI_ORCHESTRATOR_URL=http://localhost:8004
WORKFLOW_INTELLIGENCE_URL=http://localhost:8037
...
```

---

### 📊 Использование docker-generated

```bash
cd /infrastructure/tools/docker-generated

# 1. Настроить environment
cp .env.template .env
vim .env  # Установить credentials

# 2. Запустить слой
./start_infrastructure.sh gateway

# 3. Проверить здоровье
./check_health.sh

# 4. Остановить
./stop_infrastructure.sh full
```

**Управляется:** Infrastructure Builder Orchestrator

---

## 🐋 DOCKER-MANAGEMENT - Управление Docker

### Назначение
Python обертка над Docker API для программного управления контейнерами.

### Содержимое

#### 1. **docker_manager.py**
**Функция:** Главный класс для управления Docker
**Автоматизация:** ✅ Используется в Infrastructure Builder

**API:**
```python
from docker_management import DockerManager

manager = DockerManager()

# Управление контейнерами
manager.start_service("workflow-intelligence")
manager.stop_service("workflow-intelligence")
manager.restart_service("workflow-intelligence")

# Проверка статуса
status = manager.get_container_status("workflow-intelligence")
health = manager.check_health("workflow-intelligence")

# Логи
logs = manager.get_logs("workflow-intelligence", tail=100)

# Метрики
stats = manager.get_container_stats("workflow-intelligence")
```

---

#### 2. **README.md**
**Назначение:** Документация по Docker Management API

---

### 📊 Использование docker-management

```python
# Пример: Автоматический рестарт при падении
from docker_management import DockerManager
import time

manager = DockerManager()
services = ["workflow-intelligence", "ai-orchestration", "community-intelligence"]

while True:
    for service in services:
        if not manager.check_health(service):
            print(f"⚠️ {service} is down, restarting...")
            manager.restart_service(service)
    time.sleep(60)
```

**Управляется:**
- Infrastructure Builder
- Deployment Manager (intelligent-core)
- AI Orchestrator (monitoring)

---

## 🎨 DASHBOARDS - Интерактивные визуализации

### Назначение
Plotly-based интерактивные дашборды для визуализации данных анализа.

### Содержимое (по README.md)

#### **module_dashboard.py**
**Функция:** Генерация интерактивных HTML дашбордов
**Автоматизация:** ❌ Ручной запуск
**Выходные данные:**
- `reports/dashboard.html` - Общая статистика
- `reports/endpoint_map.html` - Sunburst диаграмма API
- `reports/dependency_network.html` - Граф зависимостей

**Использование:**
```bash
python3 tools/dashboards/module_dashboard.py
open tools/reports/dashboard.html
```

**Управляется:** Analytics Specialist AI (визуализация insights)

---

## 📦 CONFIG - Конфигурации

### Содержимое

#### **analysis_config.yaml**
**Назначение:** Конфигурация для анализаторов

**Формат:**
```yaml
scan_paths:
  - intelligent-core/
  - infrastructure/
  - platform-services/

exclude:
  - "*/venv/*"
  - "*/__pycache__/*"
  - "*/migrations/*"

complexity:
  max_cyclomatic: 10
  max_cognitive: 15
  warn_threshold: 5

security:
  confidence_level: "HIGH"
  severity_level: "MEDIUM"
```

---

## 🗄️ ARHIVE - Архивные версии

### Содержимое
Старые версии инструментов, устаревшие скрипты, исторические данные.

**Содержит:**
- `setup.sh` - Старый скрипт установки
- `run_analysis.sh` - Старый скрипт запуска анализа
- `run_all_analyzers.sh` - Старый оркестратор
- Документация устаревших версий

**Статус:** Архив, не используется в production

---

## 📱 VSCODE-EXTENSION - VSCode расширение

### Назначение
VSCode расширение для интеграции инструментов в IDE.

**Статус:** В разработке

---

## ⚙️ Статус автоматизации

### Полностью автоматизированные (10/25 = 40%)

| Инструмент | Автоматизация | Триггер |
|-----------|---------------|---------|
| **test_generator.py** | ✅ GitHub Actions | Изменение .py файлов |
| **discover_services.py** | ✅ Infrastructure Builder | По требованию |
| **generate_improved_compose.py** | ✅ Infrastructure Builder | После discovery |
| **prometheus_config_generator.py** | ✅ Infrastructure Builder | После discovery |
| **docker-compose генерация** | ✅ Infrastructure Builder | По требованию |
| **start_infrastructure.sh** | ✅ Infrastructure Builder | Автогенерация |
| **stop_infrastructure.sh** | ✅ Infrastructure Builder | Автогенерация |
| **check_health.sh** | ✅ Infrastructure Builder | Автогенерация |
| **.env.template** | ✅ Infrastructure Builder | Автогенерация |
| **service-catalog.json** | ✅ discover_services.py | Автогенерация |

---

### Ручной запуск (15/25 = 60%)

| Инструмент | Статус | Причина |
|-----------|--------|---------|
| ast_analyzer.py | ❌ Ручной | Требуется по требованию |
| dependency_mapper.py | ❌ Ручной | Требуется по требованию |
| dependency_validator.py | ❌ Ручной | Требуется по требованию |
| dependency_reconciler.py | ❌ Ручной | Требуется по требованию |
| api_mapper.py | ❌ Ручной | Требуется по требованию |
| business_logic_mapper.py | ❌ Ручной | Требуется по требованию |
| metrics_discovery.py | ❌ Ручной | Требуется по требованию |
| module_scanner.py | ❌ Ручной | Требуется по требованию |
| documentation_generator.py | ❌ Ручной | Требуется по требованию |
| ai_documentation_generator.py | ❌ Ручной | Требуется LLM API |
| api_docs_generator.py | ❌ Ручной | Требует запущенных сервисов |
| ui_blueprint_gen.py | ❌ Ручной | Требуется по требованию |
| event_catalog_generator.py | ❌ Ручной | Требуется по требованию |
| module_dashboard.py | ❌ Ручной | Требуется по требованию |
| VSCode extension | 🚧 В разработке | Не готово |

---

### Рекомендации по автоматизации

#### ✅ Можно автоматизировать сейчас:

1. **ast_analyzer.py** → GitHub Actions (после коммита)
2. **dependency_mapper.py** → GitHub Actions (еженедельно)
3. **metrics_discovery.py** → Infrastructure Builder (после deployment)
4. **module_dashboard.py** → После запуска анализаторов
5. **api_docs_generator.py** → После deployment (если сервисы запущены)

#### 📋 План автоматизации:

```yaml
# .github/workflows/platform-analysis.yml
name: Platform Analysis

on:
  push:
    branches: [main]
    paths: ['**.py']
  schedule:
    - cron: '0 9 * * 1'  # Каждый понедельник в 09:00

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: AST Analysis
        run: python3 tools/analyzers/ast_analyzer.py

      - name: Dependency Mapping
        run: python3 tools/analyzers/dependency_mapper.py

      - name: Metrics Discovery
        run: python3 tools/analyzers/metrics_discovery.py

      - name: Generate Dashboard
        run: python3 tools/dashboards/module_dashboard.py

      - name: Upload Reports
        uses: actions/upload-artifact@v3
        with:
          name: analysis-reports
          path: tools/analyzers/reports/
```

---

## 👔 Кто управляет инструментами

### AI Office Infrastructure - Управляющие службы

#### 1. **Infrastructure Builder Orchestrator**
**Путь:** `/infrastructure/AI-office-infrastructure/orchestrator/infrastructure_builder.py`

**Управляет:**
- ✅ discover_services.py
- ✅ generate_improved_compose.py
- ✅ prometheus_config_generator.py
- ✅ Docker Compose генерация (все слои)
- ✅ Startup/Stop скрипты
- ✅ .env.template генерация

**Запуск:**
```bash
python3 infrastructure/AI-office-infrastructure/orchestrator/infrastructure_builder.py --build-and-deploy
```

---

#### 2. **Analytics Specialist AI**
**Путь:** `/infrastructure/AI-office-infrastructure/analytics-specialist/`

**Управляет (через wrappers):**
- ✅ dependency_mapper.py (dependency_mapper_tool.py)
- ✅ metrics_discovery.py (metrics_discovery_tool.py)
- ✅ ast_analyzer.py (через API)
- ✅ module_dashboard.py (визуализация insights)

**Competency Levels:**
- Junior: process_analytics, metrics_discovery
- Middle: + dependency_mapper, discover_services
- Senior: + predictive, optimizer, ast_analyzer
- Expert: + all tools

**API:**
```python
POST /analytics/platform-health
POST /analytics/bottleneck-detection
POST /analytics/dependency-analysis
POST /analytics/incident-investigation
```

---

#### 3. **Project Agent**
**Путь:** `/infrastructure/AI-office-infrastructure/project-agent/`

**Управляет:**
- ✅ test_generator.py (автоматическая генерация тестов)
- ✅ documentation_generator.py
- ✅ api_docs_generator.py
- ✅ ui_blueprint_gen.py
- ✅ api_mapper.py
- ✅ business_logic_mapper.py

**CLI Commands:**
```bash
project-agent generate-tests --module validation-service
project-agent report --daily
project-agent report --weekly
project-agent scan  # security, quality, compliance
```

**Автоматизация:**
- GitHub Actions: `.github/workflows/project-agent-automation.yml`
- Pre-commit hooks: `.pre-commit-config.yaml`
- Code watcher: `code_watcher.py` (real-time monitoring)

---

#### 4. **MIO Manager**
**Путь:** `/infrastructure/AI-office-infrastructure/mio-manager/`

**Использует:**
- Analytics Specialist insights (через API)
- Infrastructure Builder reports
- Project Agent reports

**Роль:** Координация и делегация задач между AI коллегами

---

### Intelligent Core - Использующие службы

#### 1. **AI Orchestrator**
**Путь:** `/intelligent-core/orchestration/ai-orchestration/`

**Использует:**
- Analytics Specialist API (context для решений)
- Infrastructure Builder (deployment decisions)
- Docker Management API (container orchestration)

---

#### 2. **Deployment Manager**
**Путь:** `/intelligent-core/orchestration/ai-orchestration/platform_orch/deployment_manager.py`

**Использует:**
- Docker Management API
- Service Discovery data (service-catalog.json)
- Health Monitor (check_health.sh)

---

## 📊 Карта выходных данных

### Структура выходных данных всех инструментов

```
/Users/MD/AI-Platform-ISO/
│
├── infrastructure/tools/
│   │
│   ├── analyzers/reports/              📊 OUTPUTS ANALYZERS
│   │   ├── ast_analysis.json           (ast_analyzer.py)
│   │   ├── ast_analysis.md             (ast_analyzer.py)
│   │   ├── dependencies.json           (dependency_mapper.py)
│   │   ├── dependencies.md             (dependency_mapper.py)
│   │   ├── dependency_graph.png        (dependency_mapper.py)
│   │   ├── dependency_graph.graphml    (dependency_mapper.py)
│   │   ├── circular_dependencies.json  (dependency_mapper.py)
│   │   ├── dependency_validation.json  (dependency_validator.py)
│   │   ├── conflicts.json              (dependency_validator.py)
│   │   ├── dependency_reconciliation.md(dependency_reconciler.py)
│   │   ├── api_map.md                  (api_mapper.py)
│   │   ├── api_endpoints.json          (api_mapper.py)
│   │   ├── business_logic.md           (business_logic_mapper.py)
│   │   ├── metrics_coverage.json       (metrics_discovery.py)
│   │   ├── dashboard.html              (module_dashboard.py)
│   │   ├── endpoint_map.html           (module_dashboard.py)
│   │   ├── dependency_network.html     (module_dashboard.py)
│   │   └── modules/                    (module_scanner.py)
│   │       ├── workflow_intelligence_scan.md
│   │       ├── community_intelligence_scan.md
│   │       └── ... (47+ файлов)
│   │
│   ├── auto-generated/                 📦 OUTPUTS AUTO-GENERATED
│   │   ├── docker-compose.auto.yml     (discover_services.py)
│   │   ├── docker-compose.improved.yml (generate_improved_compose.py)
│   │   ├── service-catalog.json        (discover_services.py)
│   │   ├── prometheus.auto.yml         (prometheus_config_generator.py)
│   │   └── gateway-routes.auto.json    (discover_services.py)
│   │
│   └── docker-generated/               🐳 OUTPUTS DOCKER-GENERATED
│       ├── docker-compose.gateway.yml      (Infrastructure Builder)
│       ├── docker-compose.runtime.yml      (Infrastructure Builder)
│       ├── docker-compose.observability.yml(Infrastructure Builder)
│       ├── docker-compose.integration.yml  (Infrastructure Builder)
│       ├── docker-compose.full.yml         (Infrastructure Builder)
│       ├── service-catalog.json            (Infrastructure Builder)
│       ├── start_infrastructure.sh         (Infrastructure Builder)
│       ├── stop_infrastructure.sh          (Infrastructure Builder)
│       ├── check_health.sh                 (Infrastructure Builder)
│       └── .env.template                   (Infrastructure Builder)
│
├── docs/                                📚 OUTPUTS DOC-GENERATORS
│   ├── api/                             (api_docs_generator.py)
│   │   ├── README.md
│   │   ├── validation.md
│   │   ├── documents.md
│   │   └── postman_collection.json
│   ├── ui/                              (ui_blueprint_gen.py)
│   │   ├── index.html
│   │   ├── validation_blueprint.html
│   │   ├── validation_spec.json
│   │   ├── documents_blueprint.html
│   │   └── documents_spec.json
│   ├── events/                          (event_catalog_generator.py)
│   │   ├── EVENT_CATALOG.md
│   │   └── event_flows.json
│   ├── ai-generated/                    (ai_documentation_generator.py)
│   │   └── ...
│   └── architecture/                    (documentation_generator.py)
│       ├── ARCHITECTURE.md
│       ├── API_REFERENCE.md
│       └── SERVICES_OVERVIEW.md
│
├── tests/generated/                     🧪 OUTPUTS TEST-GENERATOR
│   ├── test_validation_service.py       (test_generator.py)
│   ├── test_documents_service.py        (test_generator.py)
│   ├── test_workflow_intelligence.py    (test_generator.py)
│   └── ... (автогенерированные тесты)
│
└── infrastructure/observability/config/ ⚙️ OUTPUTS CONFIGS
    └── prometheus/
        └── prometheus.yml               (prometheus_config_generator.py)
```

---

### Потоки данных

```
┌─────────────────────────────────────────────────────────────┐
│                   ИНСТРУМЕНТЫ АНАЛИЗА                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  analyzers/reports/ (JSON, MD, PNG, HTML)                   │
│  - ast_analysis.json                                         │
│  - dependencies.json                                         │
│  - metrics_coverage.json                                     │
│  - dashboard.html                                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│         ANALYTICS SPECIALIST AI (Консьюмер данных)          │
│  - Читает JSON reports                                       │
│  - Анализирует метрики                                       │
│  - Генерирует insights                                       │
│  - Отправляет в MIO Manager                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  MIO MANAGER (Координация)                   │
│  - Получает insights                                         │
│  - Делегирует задачи                                         │
│  - Создает отчеты                                            │
└─────────────────────────────────────────────────────────────┘
```

---

```
┌─────────────────────────────────────────────────────────────┐
│            INFRASTRUCTURE BUILDER ORCHESTRATOR               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  1. discover_services.py → service-catalog.json              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  2. generate_improved_compose.py → docker-compose files      │
│  3. prometheus_config_generator.py → prometheus.yml          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  docker-generated/ (Все Docker configs + scripts)            │
│  - docker-compose.gateway.yml                                │
│  - docker-compose.runtime.yml                                │
│  - docker-compose.observability.yml                          │
│  - docker-compose.full.yml                                   │
│  - start_infrastructure.sh                                   │
│  - stop_infrastructure.sh                                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              DEPLOYMENT (Docker Compose запуск)              │
└─────────────────────────────────────────────────────────────┘
```

---

```
┌─────────────────────────────────────────────────────────────┐
│                      PROJECT AGENT                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  1. test_generator.py → /tests/generated/*.py                │
│  2. api_docs_generator.py → docs/api/*.md                    │
│  3. ui_blueprint_gen.py → docs/ui/*.html                     │
│  4. documentation_generator.py → docs/architecture/*.md      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              ТЕСТЫ, ДОКУМЕНТАЦИЯ, UI SPECS                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📈 Метрики инструментов

### Статистика кода

| Категория | Файлов | Строк кода | Средний размер |
|-----------|--------|------------|----------------|
| **analyzers/** | 11 | 138,655 | 12,605 |
| **doc-generators/** | 7 | 106,810 | 15,259 |
| **auto-generated/** | 7 | 98,129 | 14,018 |
| **docker-generated/** | 12 | 48,991 | 4,082 |
| **ИТОГО** | 37 | 392,585 | - |

### Покрытие автоматизацией

```
Автоматизация: ████████████░░░░░░░░░░░░░░░░ 40%

✅ Автоматизировано:   10 инструментов
❌ Ручной запуск:      15 инструментов
🚧 В разработке:        1 инструмент
─────────────────────────────────────────
📊 ИТОГО:              26 инструментов
```

### AI Ownership

```
Infrastructure Builder: ████████░░░░░░░░░░░░ 38%  (10 инструментов)
Analytics Specialist:   ███████░░░░░░░░░░░░░ 31%  (8 инструментов)
Project Agent:          ██████░░░░░░░░░░░░░░ 27%  (7 инструментов)
Без управления:         █░░░░░░░░░░░░░░░░░░░ 4%   (1 инструмент)
```

---

## 🎯 Рекомендации

### Немедленные улучшения

1. **Автоматизировать анализаторы через GitHub Actions**
   - ast_analyzer.py
   - dependency_mapper.py
   - metrics_discovery.py
   - module_dashboard.py

2. **Интегрировать с Analytics Specialist AI**
   - Автоматический запуск после deployment
   - Публикация insights в MIO Manager
   - Real-time monitoring

3. **Добавить мониторинг автоматизации**
   - Логирование запусков инструментов
   - Метрики успешности генерации
   - Alerting при ошибках

### Долгосрочные улучшения

1. **Web UI для инструментов**
   - Dashboard для запуска анализаторов
   - Визуализация результатов в реальном времени
   - История запусков

2. **AI-powered оркестрация**
   - AI Orchestrator автоматически запускает нужные инструменты
   - Адаптивная автоматизация на основе изменений
   - Predictive analysis scheduling

3. **Интеграция с CI/CD**
   - Pre-commit hooks для всех анализаторов
   - Post-deployment automated analysis
   - Performance benchmarking

---

## 📞 Поддержка

**Документация:**
- [README.md](./README.md) - Главная документация
- [analyzers/README.md](./analyzers/README.md) - Анализаторы
- [analyzers/INTEGRATION_GUIDE.md](./analyzers/INTEGRATION_GUIDE.md) - Интеграция

**AI Офис:**
- Infrastructure Builder: `/infrastructure/AI-office-infrastructure/orchestrator/`
- Analytics Specialist: `/infrastructure/AI-office-infrastructure/analytics-specialist/`
- Project Agent: `/infrastructure/AI-office-infrastructure/project-agent/`

**Issues & Questions:**
- GitHub Issues (если проект публичный)
- MIO Manager API: `http://localhost:8046/`

---

**Создано:** 2025-10-08
**Версия:** 1.0.0
**AI Curator:** Claude (AI Office Infrastructure)
**Последнее обновление:** 2025-10-08

---

**🎉 Каталог готов к использованию!**
