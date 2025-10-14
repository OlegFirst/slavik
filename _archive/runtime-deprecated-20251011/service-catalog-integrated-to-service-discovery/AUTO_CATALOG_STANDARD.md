# Стандарт автоматической генерации Service Catalog

**Version**: 1.0.0
**Date**: October 11, 2025
**Status**: 🚧 Проект для обсуждения

---

## 📋 КОНЦЕПЦИЯ

### Проблема
Сейчас каталог `service-catalog.yaml` обновляется вручную. Разработчик создает новый сервис, но забывает добавить его в каталог или добавляет неполную информацию.

### Решение
Каждый сервис имеет локальный файл `SERVICE_INFO.yaml` в своей директории. Система автоматически сканирует проект, собирает все `SERVICE_INFO.yaml` и генерирует централизованный каталог.

### Принцип "Convention over Configuration"
1. **Разработчик создает сервис** → Добавляет `SERVICE_INFO.yaml` в корень сервиса
2. **Система сканирует** → Находит все `SERVICE_INFO.yaml` файлы
3. **Система генерирует** → Обновляет `service-catalog.yaml`
4. **Service Discovery читает** → Загружает актуальный каталог

---

## 📁 СТРУКТУРА ФАЙЛА `SERVICE_INFO.yaml`

### Расположение
Каждый сервис ДОЛЖЕН иметь файл в корне своей директории:

```
/infrastructure/AI-office-infrastructure/mio-manager/
├── SERVICE_INFO.yaml          # ← Обязательный файл
├── main.py
├── README.md
└── ...
```

### Полная схема `SERVICE_INFO.yaml`

```yaml
# ============================================
# РАЗДЕЛ 1: ОСНОВНАЯ ИНФОРМАЦИЯ (обязательно)
# ============================================
name: "mio-manager"                          # Уникальное имя (kebab-case)
display_name: "MIO Manager (EYES)"           # Человекочитаемое название
version: "2.1.0"                             # Версия сервиса (semver)
description: |                               # Описание функционала
  MIO Manager = EYES (Observatory) - observes platform state.
  Phase 2.1: Event-Driven Choreography architecture.
  Metrics Coverage Observer + Metrics Health Checker.

# ============================================
# РАЗДЕЛ 2: КЛАССИФИКАЦИЯ (обязательно)
# ============================================
type: "infrastructure/AI-office-infrastructure"    # Тип из CATALOG_SCHEMA.md
business_process: "Monitoring & Observability Management"  # Процесс из CATALOG_SCHEMA.md
status: "active"                             # active | configured | deprecated | planned

# ============================================
# РАЗДЕЛ 3: ТЕХНИЧЕСКИЕ ПАРАМЕТРЫ
# ============================================
runtime:
  language: "python"                         # python | typescript | javascript
  framework: "FastAPI"                       # FastAPI | Next.js | React | ...
  port: 8046                                 # Порт HTTP (null если не HTTP)
  protocol: "http"                           # http | grpc | websocket | cli

endpoints:
  health: "/health"                          # Health check endpoint
  metrics: "/metrics"                        # Prometheus metrics
  api_docs: "/docs"                          # OpenAPI docs (если есть)
  base_url: "http://localhost:8046"          # Base URL

# ============================================
# РАЗДЕЛ 4: ФУНКЦИОНАЛЬНОСТЬ (обязательно для разработчиков)
# ============================================
capabilities:                                # Что умеет делать сервис
  - "metrics_coverage_observation"           # Наблюдение за покрытием метриками
  - "metrics_health_checking"                # Проверка здоровья метрик
  - "service_discovery_event_handling"       # Обработка событий Service Discovery
  - "observation_publishing"                 # Публикация наблюдений в EventBus

features:                                    # Ключевые фичи
  - name: "Phase 2.1 EYES Observatory"
    description: "Event-Driven Choreography pattern - observes, doesn't command"
    since_version: "2.1.0"

  - name: "Metrics Coverage Observer"
    description: "Compares Service Discovery vs Prometheus targets every 5 min"
    since_version: "2.1.0"

  - name: "Metrics Health Checker"
    description: "Validates endpoints, scrape freshness, errors every 1 min"
    since_version: "2.1.0"

# ============================================
# РАЗДЕЛ 5: KPIs (Key Performance Indicators)
# ============================================
kpis:
  # Базовые KPIs (для всех HTTP сервисов)
  - name: "request_latency_ms"
    description: "Request latency in milliseconds"
    type: "histogram"

  - name: "requests_per_second"
    description: "Requests per second"
    type: "gauge"

  - name: "error_rate_percent"
    description: "Error rate percentage"
    type: "gauge"

  - name: "availability_percent"
    description: "Service availability percentage"
    type: "gauge"

  # Специализированные KPIs (для MIO Manager)
  - name: "coverage_percentage"
    description: "Percentage of services covered by monitoring"
    type: "gauge"

  - name: "alert_response_time"
    description: "Alert response time in seconds"
    type: "histogram"

  - name: "services_monitored"
    description: "Number of services under monitoring"
    type: "counter"

  - name: "observations_published"
    description: "Number of observations published to EventBus"
    type: "counter"

# ============================================
# РАЗДЕЛ 6: ЗАВИСИМОСТИ И ИНТЕГРАЦИИ
# ============================================
dependencies:
  # Внешние Python packages
  python_packages:
    - "fastapi>=0.104.0"
    - "uvicorn[standard]>=0.24.0"
    - "pydantic>=2.0.0"
    - "httpx>=0.25.0"
    - "redis>=5.0.0"
    - "prometheus-client>=0.18.0"

  # Внутренние сервисы (service-to-service)
  services:
    - name: "service-discovery"
      type: "required"
      version: ">=2.0"
      purpose: "Unified catalog API, event subscriptions"

    - name: "eventbus"
      type: "required"
      version: ">=1.0"
      purpose: "Event publishing and choreography"

    - name: "prometheus"
      type: "required"
      version: ">=2.40"
      purpose: "Metrics collection and validation"

    - name: "ai-event-manager"
      type: "optional"
      version: ">=1.0"
      purpose: "Receives observations for analysis"

    - name: "devops-agent"
      type: "optional"
      version: ">=2.0"
      purpose: "Receives observations for auto-fixes"

  # Инфраструктурные зависимости
  infrastructure:
    - name: "PostgreSQL"
      type: "optional"
      version: ">=15.0"
      purpose: "State storage"

    - name: "Redis"
      type: "required"
      version: ">=7.0"
      purpose: "EventBus backend, state caching"

integrations:
  # EventBus события
  eventbus:
    subscribes:                              # Подписывается на события
      - event: "platform.monitoring.service_registered"
        handler: "handle_service_registered"
        description: "Reacts to new service registration"

      - event: "platform.monitoring.service_deregistered"
        handler: "handle_service_deregistered"
        description: "Reacts to service deregistration"

    publishes:                               # Публикует события
      - event: "platform.mio.service_not_monitored_observed"
        priority: "high"
        description: "Service registered but not in Prometheus"

      - event: "platform.mio.metrics_endpoint_unreachable_observed"
        priority: "high"
        description: "Metrics endpoint is down"

      - event: "platform.mio.critical_service_failure_observed"
        priority: "critical"
        description: "Critical service failure detected"

  # REST API вызовы
  rest_api:
    - service: "service-discovery"
      endpoints:
        - "GET /v2/catalog/services"
        - "GET /v2/catalog/missing"

    - service: "prometheus"
      endpoints:
        - "GET /api/v1/targets"
        - "GET /api/v1/query"

# ============================================
# РАЗДЕЛ 7: ПРОБЛЕМНЫЕ МОМЕНТЫ
# ============================================
known_issues:
  - id: "ISSUE-001"
    severity: "medium"
    title: "Port conflict with db-intelligence"
    description: |
      MIO Manager uses port 8046, but db-intelligence also wants 8050.
      Need to coordinate port allocation.
    workaround: "Use port 8046 for MIO, 8050 for db-intelligence"
    status: "resolved"
    resolved_date: "2025-10-11"

  - id: "ISSUE-002"
    severity: "low"
    title: "Prometheus static config requires manual update"
    description: |
      When new services register, Prometheus config needs manual update.
      Phase 2.1 observes this and publishes event for DevOps Agent.
    workaround: "DevOps Agent will auto-fix in future"
    status: "in_progress"

limitations:
  - "Observation cycles are fixed (5 min coverage, 1 min health)"
  - "Cannot force-add services to Prometheus (by design - EYES pattern)"
  - "Requires Redis for EventBus backend"

# ============================================
# РАЗДЕЛ 8: DEPLOYMENT
# ============================================
deployment:
  startup_command: "uvicorn main:app --host 0.0.0.0 --port 8046"
  environment_variables:
    - name: "SERVICE_DISCOVERY_URL"
      required: true
      default: "http://localhost:8500"
      description: "Service Discovery v2.0 API URL"

    - name: "PROMETHEUS_URL"
      required: true
      default: "http://localhost:9090"
      description: "Prometheus API URL"

    - name: "EVENTBUS_REDIS_URL"
      required: true
      default: "redis://localhost:6379"
      description: "Redis URL for EventBus"

    - name: "LOG_LEVEL"
      required: false
      default: "INFO"
      description: "Logging level"

  health_check:
    endpoint: "/health"
    interval_seconds: 30
    timeout_seconds: 10
    healthy_threshold: 2
    unhealthy_threshold: 3

  resources:
    cpu: "500m"
    memory: "512Mi"
    disk: "1Gi"

  scaling:
    min_replicas: 1
    max_replicas: 3
    target_cpu_percent: 70

# ============================================
# РАЗДЕЛ 9: ДОКУМЕНТАЦИЯ
# ============================================
documentation:
  readme: "README.md"
  quick_start: "START_HERE.md"
  architecture: "QUICK_MONITORING_OVERVIEW.md"
  api_docs: "/docs"                          # OpenAPI/Swagger

  external_docs:
    - title: "Service Catalog Schema"
      url: "file://../../runtime/service-catalog/CATALOG_SCHEMA.md"

    - title: "Deployment Port Map"
      url: "file:///doc-project/DEPLOYMENT_PORT_MAP.md"

# ============================================
# РАЗДЕЛ 10: КОНТАКТЫ И OWNERSHIP
# ============================================
ownership:
  team: "AI Office Infrastructure Team"
  lead: "MIO Manager Team"
  contacts:
    - type: "documentation"
      value: "file://README.md"

    - type: "issues"
      value: "file://../../ISSUES.md"

# ============================================
# РАЗДЕЛ 11: МЕТАДАННЫЕ ФАЙЛА
# ============================================
meta:
  schema_version: "1.0.0"                    # Версия схемы SERVICE_INFO.yaml
  last_updated: "2025-10-11T02:00:00Z"
  auto_generated: false                      # Создан вручную
  validated: true                            # Прошел валидацию
```

---

## 🤖 АВТОМАТИЧЕСКАЯ ГЕНЕРАЦИЯ КАТАЛОГА

### Алгоритм сканирования

```python
# /infrastructure/tools/doc-generators/service_catalog_generator.py

import os
import yaml
from pathlib import Path
from typing import List, Dict

class ServiceCatalogGenerator:
    """Автоматическая генерация service-catalog.yaml из SERVICE_INFO.yaml файлов"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.services = []

    async def scan_project(self):
        """Сканирует проект и находит все SERVICE_INFO.yaml"""

        # Директории для сканирования
        scan_paths = [
            "infrastructure",
            "intelligent-core",
            "platform-services",
            "interface"
        ]

        for scan_path in scan_paths:
            full_path = self.project_root / scan_path
            if full_path.exists():
                await self._scan_directory(full_path)

        print(f"✅ Found {len(self.services)} services")

    async def _scan_directory(self, directory: Path):
        """Рекурсивно сканирует директорию"""

        # Проверяем наличие SERVICE_INFO.yaml в текущей директории
        service_info_path = directory / "SERVICE_INFO.yaml"

        if service_info_path.exists():
            try:
                with open(service_info_path, 'r', encoding='utf-8') as f:
                    service_info = yaml.safe_load(f)

                # Добавляем путь к сервису
                service_info['path'] = str(directory.relative_to(self.project_root))

                # Валидация
                if self._validate_service_info(service_info):
                    self.services.append(service_info)
                    print(f"  ✅ {service_info['name']}")
                else:
                    print(f"  ⚠️ {directory.name} - validation failed")

            except Exception as e:
                print(f"  ❌ {directory.name} - error: {e}")

        # Рекурсивно сканируем подпапки
        for subdir in directory.iterdir():
            if subdir.is_dir() and not subdir.name.startswith('.') and not subdir.name.startswith('_'):
                await self._scan_directory(subdir)

    def _validate_service_info(self, info: Dict) -> bool:
        """Валидация SERVICE_INFO.yaml"""

        required_fields = ['name', 'type', 'business_process', 'status']

        for field in required_fields:
            if field not in info:
                print(f"    ❌ Missing required field: {field}")
                return False

        # HTTP сервисы должны иметь port, endpoints
        if info.get('runtime', {}).get('port'):
            if 'endpoints' not in info:
                print(f"    ⚠️ HTTP service missing endpoints")

        return True

    async def generate_catalog(self, output_path: str):
        """Генерирует service-catalog.yaml"""

        # Сортируем по типу и имени
        self.services.sort(key=lambda s: (s['type'], s['name']))

        catalog = {
            'metadata': {
                'platform_name': 'AI-Platform-ISO',
                'version': '2.1.0',
                'generated_at': datetime.now().isoformat(),
                'total_services': len(self.services),
                'schema_version': '1.0.0',
                'auto_generated': True
            },
            'services': []
        }

        # Преобразуем SERVICE_INFO в формат каталога
        for service in self.services:
            catalog_entry = self._transform_to_catalog_format(service)
            catalog['services'].append(catalog_entry)

        # Сохраняем
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(catalog, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

        print(f"\n✅ Generated: {output_path}")
        print(f"   Services: {len(self.services)}")

    def _transform_to_catalog_format(self, service_info: Dict) -> Dict:
        """Преобразует SERVICE_INFO в формат service-catalog.yaml"""

        catalog_entry = {
            'name': service_info['name'],
            'type': service_info['type'],
            'business_process': service_info['business_process'],
            'status': service_info['status'],
            'path': service_info['path']
        }

        # Port
        if 'runtime' in service_info and 'port' in service_info['runtime']:
            catalog_entry['port'] = service_info['runtime']['port']

        # KPIs (extract names)
        if 'kpis' in service_info:
            catalog_entry['kpis'] = [kpi['name'] for kpi in service_info['kpis']]

        # Endpoints
        if 'endpoints' in service_info:
            base_url = service_info['endpoints'].get('base_url', f"http://localhost:{catalog_entry.get('port')}")
            catalog_entry['metrics_endpoint'] = base_url + service_info['endpoints'].get('metrics', '/metrics')
            catalog_entry['health_endpoint'] = base_url + service_info['endpoints'].get('health', '/health')

        # Dependencies (только package names)
        if 'dependencies' in service_info:
            if 'python_packages' in service_info['dependencies']:
                catalog_entry['dependencies'] = service_info['dependencies']['python_packages']

        # Documentation
        if 'documentation' in service_info:
            catalog_entry['documentation'] = service_info['documentation']['readme']

        return catalog_entry

# Usage
async def main():
    generator = ServiceCatalogGenerator("/Users/MD/AI-Platform-ISO")
    await generator.scan_project()
    await generator.generate_catalog(
        "/Users/MD/AI-Platform-ISO/infrastructure/runtime/service-catalog/service-catalog.yaml"
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

## 📊 ГДЕ ПУБЛИКУЕМ КАТАЛОГ

### 1. Централизованный файл (Primary)
```
/infrastructure/runtime/service-catalog/service-catalog.yaml
```
- Генерируется автоматически из всех SERVICE_INFO.yaml
- Используется Service Discovery v2.0
- Версионируется в Git

### 2. Web Dashboard (Secondary)
```
/infrastructure/observability/dashboards/service-catalog-dashboard.html
```
- Генерируется из service-catalog.yaml
- Интерактивная таблица с фильтрами
- Доступна через Grafana или отдельный веб-сервер

### 3. API Endpoint (Runtime)
```
GET /v2/catalog/services
GET /v2/catalog/services/{name}
GET /v2/catalog/stats
```
- Service Discovery предоставляет REST API
- Real-time данные (catalog + runtime status)

### 4. Documentation Website (Public)
```
/docs-website/src/data/service-catalog.json
```
- JSON версия для Next.js/React
- Автоматически синхронизируется из YAML

---

## 🔄 WORKFLOW АВТОГЕНЕРАЦИИ

### Вариант 1: Pre-commit Hook (Рекомендуется)

```bash
# .git/hooks/pre-commit

#!/bin/bash
# Auto-generate service-catalog.yaml before commit

echo "🔍 Checking for SERVICE_INFO.yaml changes..."

# Check if any SERVICE_INFO.yaml modified
if git diff --cached --name-only | grep -q "SERVICE_INFO.yaml"; then
    echo "✅ SERVICE_INFO.yaml changed, regenerating catalog..."

    # Run generator
    python3 infrastructure/tools/doc-generators/service_catalog_generator.py

    # Add generated catalog to commit
    git add infrastructure/runtime/service-catalog/service-catalog.yaml

    echo "✅ Catalog regenerated and added to commit"
else
    echo "ℹ️ No SERVICE_INFO.yaml changes, skipping catalog regeneration"
fi
```

### Вариант 2: GitHub Actions (CI/CD)

```yaml
# .github/workflows/update-service-catalog.yml

name: Update Service Catalog

on:
  push:
    paths:
      - '**/SERVICE_INFO.yaml'
  workflow_dispatch:

jobs:
  regenerate-catalog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install pyyaml

      - name: Regenerate catalog
        run: python3 infrastructure/tools/doc-generators/service_catalog_generator.py

      - name: Commit changes
        run: |
          git config user.name "Service Catalog Bot"
          git config user.email "bot@ai-platform.com"
          git add infrastructure/runtime/service-catalog/service-catalog.yaml
          git commit -m "chore: Auto-update service catalog [skip ci]"
          git push
```

### Вариант 3: Manual Command (Development)

```bash
# Скрипт для разработчиков
./scripts/update-catalog.sh

# Или напрямую
python3 infrastructure/tools/doc-generators/service_catalog_generator.py
```

---

## ✅ CHECKLIST ДЛЯ РАЗРАБОТЧИКА

Когда создаешь новый сервис:

```
☐ 1. Создал директорию сервиса
☐ 2. Создал SERVICE_INFO.yaml в корне сервиса
☐ 3. Заполнил все обязательные поля:
     ☐ name (уникальное)
     ☐ type (из CATALOG_SCHEMA.md)
     ☐ business_process
     ☐ status
     ☐ capabilities (что умеет)
     ☐ kpis (если HTTP)
     ☐ dependencies (все зависимости)
     ☐ integrations (EventBus, REST API)
☐ 4. Добавил endpoints (если HTTP):
     ☐ /health
     ☐ /metrics
☐ 5. Описал known_issues и limitations
☐ 6. Прописал deployment (команда запуска, env vars)
☐ 7. Запустил генератор каталога:
     python3 infrastructure/tools/doc-generators/service_catalog_generator.py
☐ 8. Проверил что service-catalog.yaml обновился
☐ 9. Закоммитил оба файла:
     - SERVICE_INFO.yaml
     - service-catalog.yaml
```

---

## 🎯 ПРЕИМУЩЕСТВА ПОДХОДА

### ✅ Для разработчиков
- Локальный файл в директории сервиса (близко к коду)
- Все данные о сервисе в одном месте
- Понятная структура (копируй-вставь шаблон)
- Автоматическая генерация каталога

### ✅ Для системы
- Актуальный каталог всегда синхронизирован с кодом
- Валидация при генерации
- Версионирование в Git
- API доступ через Service Discovery

### ✅ Для архитектуры
- Single Source of Truth (SERVICE_INFO.yaml в каждом сервисе)
- Децентрализованная информация, централизованная агрегация
- Расширяемость (новые поля добавляются в SERVICE_INFO.yaml)

---

## 📝 ДОПОЛНИТЕЛЬНЫЕ ПОЛЯ (МОИ ПРЕДЛОЖЕНИЯ)

Помимо твоих требований, я предлагаю добавить:

1. **Capabilities** - что умеет делать сервис (для поиска и фильтрации)
2. **Features** - ключевые фичи с версиями (changelog)
3. **Known Issues** - проблемные моменты с workarounds
4. **Limitations** - ограничения сервиса (важно знать заранее)
5. **EventBus Integration** - subscribes/publishes (для event-driven архитектуры)
6. **Deployment** - как запускать, env vars, health checks
7. **Ownership** - кто отвечает за сервис
8. **Documentation Links** - README, архитектура, API docs

---

## 🚀 ПЛАН ВНЕДРЕНИЯ

### Phase 1: Пилот (1 неделя)
1. Создать шаблон SERVICE_INFO.yaml
2. Написать service_catalog_generator.py
3. Создать SERVICE_INFO.yaml для 3-5 ключевых сервисов
4. Протестировать генерацию

### Phase 2: Rollout (2 недели)
1. Создать SERVICE_INFO.yaml для всех активных сервисов
2. Настроить pre-commit hook
3. Обновить документацию для разработчиков

### Phase 3: Automation (1 неделя)
1. Настроить GitHub Actions
2. Интегрировать с Service Discovery v2.0
3. Создать web dashboard

### Phase 4: Monitoring (ongoing)
1. Отслеживать актуальность каталога
2. Валидировать новые SERVICE_INFO.yaml
3. Улучшать схему по мере необходимости

---

## ❓ ВОПРОСЫ ДЛЯ ОБСУЖДЕНИЯ

1. **Формат файла**: `SERVICE_INFO.yaml` или `service.yaml`?
2. **Обязательные поля**: Согласен ли с моим списком или нужно сократить/расширить?
3. **Генерация**: Pre-commit hook или GitHub Actions или оба?
4. **Публикация**: Куда еще публиковать кроме service-catalog.yaml и API?
5. **Валидация**: Какие правила валидации добавить?
6. **Legacy сервисы**: Как поступить с сервисами без SERVICE_INFO.yaml?

---

**Статус**: 🚧 Черновик для обсуждения
**Автор**: AI Architecture Team
**Дата**: October 11, 2025
