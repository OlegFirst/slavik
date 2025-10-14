# Service Catalog Schema - Официальная спецификация

**Version**: 2.0
**Date**: October 11, 2025
**Status**: ✅ Согласовано и зафиксировано

## 1. Структура каталога

### 1.1 Корневой уровень

```yaml
metadata:                          # Метаданные каталога
  platform_name: string           # Название платформы
  version: string                 # Версия каталога (semver)
  generated_at: datetime          # Дата генерации
  total_services: integer         # Общее количество сервисов

services:                          # Массив сервисов
  - name: string                  # Уникальное имя сервиса
    type: string                  # Тип сервиса (см. раздел 2)
    business_process: string      # Бизнес-процесс (см. раздел 3)
    port: integer | null          # Порт (null если не HTTP)
    status: string                # Статус конфигурации
    path: string                  # Путь к коду
    kpis: array[string]          # Ключевые метрики (см. раздел 4)
    dependencies: array[string]   # Зависимости (packages)
    metrics_endpoint: string | null   # Endpoint метрик Prometheus
    health_endpoint: string | null    # Endpoint health check
    framework: string | null      # Framework (для UI сервисов)
```

## 2. Типы сервисов (type)

### 2.1 Иерархия типов

```
infrastructure/              # Инфраструктурные сервисы
├── gateway/                # API Gateway & Routing
├── observability/          # Monitoring, Logging, Tracing
├── AI-office-infrastructure/  # AI Office (NEW)
├── runtime/                # Service Discovery, Message Queue
├── security/               # Auth, Secrets, API Gateway
└── integration/            # GitHub, MCP, External APIs

intelligent-core/           # Интеллектуальное ядро
├── ai-foundation/          # Базовые AI capabilities
├── orchestration/          # AI Orchestration
├── domain-expertise/       # Domain specialists
└── workflow_intelligence/  # Workflow Intelligence (Brain)

platform-services/          # Бизнес-сервисы
├── bcm/                    # Business Continuity Management
├── compliance/             # ISO 22301 Compliance
├── governance/             # Governance & Policy
└── documents/              # Document Management

interface/                  # UI & Frontend
├── admin/                  # Admin panels
└── user/                   # User-facing apps
```

### 2.2 Полный список типов

| Тип | Описание | Примеры |
|-----|----------|---------|
| `infrastructure/gateway` | API Gateway & Routing | api-gateway |
| `infrastructure/observability` | Monitoring & Observability | monitoring-backend, notification-service |
| `infrastructure/AI-office-infrastructure` | AI Office Components | mio-manager, orchestrator, analytics-specialist |
| `infrastructure/runtime` | Runtime services | service-discovery, message-queue, realtime-websocket |
| `infrastructure/security` | Security services | auth, secrets-manager, api-gateway |
| `infrastructure/integration` | Integrations | github-integration, mcp-server |
| `intelligent-core` | AI & Intelligence | ai-foundation, workflow_intelligence, predictive |
| `platform-services` | Business services | bia-service, compliance-service, risk-service |
| `interface` | UI & Frontend | admin-control-center, admin_panel, web-app |

## 3. Бизнес-процессы (business_process)

### 3.1 Категории бизнес-процессов

```yaml
# Infrastructure
- "API Gateway & Routing"
- "System Monitoring & Observability"
- "Service Discovery & Registry"
- "Message Queue & Event Bus"
- "Security & Authentication"
- "Integration & Connectivity"

# AI & Intelligence
- "AI Intelligence & Decision Support"
- "Workflow Orchestration & Automation"
- "Learning & Knowledge Management"
- "Predictive Analytics & Forecasting"
- "Event Intelligence & Analysis"

# Business Services
- "Business Continuity Planning"
- "ISO 22301 Compliance Management"
- "Risk Assessment & Management"
- "Incident Response Management"
- "Document Management"
- "Governance & Policy Management"
- "Data Validation & Quality"

# UI & Presentation
- "User Interface & Presentation"
- "Administration & Control"

# Generic (для новых/неопределенных)
- "Core Platform Services"
```

### 3.2 Mapping: Type → Business Process

| Type | Preferred Business Processes |
|------|------------------------------|
| `infrastructure/gateway` | API Gateway & Routing |
| `infrastructure/observability` | System Monitoring & Observability |
| `infrastructure/AI-office-infrastructure` | AI Office Management, Analytics & Reporting |
| `infrastructure/runtime` | Service Discovery & Registry, Message Queue & Event Bus |
| `intelligent-core` | AI Intelligence & Decision Support, Workflow Orchestration |
| `platform-services` | Business Continuity Planning, Compliance Management, Risk Assessment |
| `interface` | User Interface & Presentation |

## 4. KPIs (Key Performance Indicators)

### 4.1 Обязательные KPIs (для всех HTTP сервисов)

```yaml
kpis:
  - request_latency_ms           # Задержка запросов (мс)
  - requests_per_second          # Запросов в секунду
  - error_rate_percent           # % ошибок
  - availability_percent         # % доступности
```

### 4.2 Специализированные KPIs

#### AI & Intelligence Services
```yaml
  - ai_decisions_total           # Всего AI решений
  - ml_prediction_accuracy       # Точность ML прогнозов
  - knowledge_graph_size         # Размер графа знаний
```

#### Workflow Services
```yaml
  - workflows_executed           # Выполнено workflow
  - workflow_success_rate        # % успешных workflow
  - avg_workflow_duration_sec    # Средняя длительность
```

#### Monitoring Services
```yaml
  - metrics_collected_per_min    # Метрик в минуту
  - alert_response_time_sec      # Время реакции на алерт
  - dashboard_refresh_rate_sec   # Частота обновления дашборда
```

#### Compliance Services
```yaml
  - compliance_score_percent     # Балл соответствия
  - audit_items_tracked          # Отслеживаемых audit items
  - violations_detected          # Обнаружено нарушений
```

#### MIO Manager (Observability)
```yaml
  - coverage_percentage          # % покрытия мониторингом
  - alert_response_time          # Время реакции
  - services_monitored           # Сервисов под мониторингом
  - observations_published       # Опубликовано наблюдений
```

#### UI Services
```yaml
  - page_load_time_ms           # Время загрузки страницы
  - time_to_interactive_ms      # Время до интерактивности
  - bundle_size_kb              # Размер bundle
  - user_sessions_active        # Активных сессий
```

## 5. Endpoints

### 5.1 Стандартные endpoints

Все HTTP сервисы **ДОЛЖНЫ** предоставлять:

```yaml
metrics_endpoint: "http://localhost:{port}/metrics"   # Prometheus metrics
health_endpoint: "http://localhost:{port}/health"     # Health check
```

### 5.2 Health Check Response Format

```json
{
  "status": "healthy",           // healthy | unhealthy | degraded
  "service": "service-name",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "checks": {
    "database": "healthy",
    "redis": "healthy",
    "eventbus": "healthy"
  }
}
```

### 5.3 Metrics Format

Prometheus-совместимый формат:
```
# HELP request_latency_ms Request latency in milliseconds
# TYPE request_latency_ms histogram
request_latency_ms_bucket{le="100"} 95
request_latency_ms_bucket{le="500"} 98
request_latency_ms_count 100
request_latency_ms_sum 12500
```

## 6. Dependencies

### 6.1 Формат зависимостей

```yaml
dependencies:
  # Python packages
  - fastapi
  - uvicorn[standard]
  - pydantic>=2.0

  # Local packages (relative paths)
  - ../../../shared
  - ../../intelligent-core/workflow-intelligence

  # Local packages (file:// URLs)
  - workflow-intelligence @ file:///Users/MD/AI-Platform-ISO/intelligent-core/workflow-intelligence

  # NPM packages (для UI)
  - "@emotion/react"
  - "@mui/material"
```

### 6.2 Стандартные стеки

#### Python Backend Stack
```yaml
dependencies:
  - fastapi                      # Web framework
  - uvicorn[standard]           # ASGI server
  - pydantic                    # Data validation
  - pydantic-settings           # Settings management
  - sqlalchemy                  # ORM
  - asyncpg                     # PostgreSQL driver
  - redis                       # Redis client
  - httpx                       # HTTP client
  - python-multipart            # File uploads
  - prometheus-client           # Metrics
```

#### React Frontend Stack
```yaml
dependencies:
  - react
  - react-dom
  - typescript
  - "@mui/material"            # UI library
  - "@radix-ui/*"              # Headless UI
  - next                       # Framework (if Next.js)
```

## 7. Status Values

### 7.1 Возможные значения status

| Status | Описание |
|--------|----------|
| `configured` | Сервис сконфигурирован, готов к запуску |
| `active` | Сервис активно используется |
| `deprecated` | Устаревший, планируется замена |
| `archived` | Заархивирован, не используется |
| `planned` | Запланирован, но не реализован |

## 8. Валидация схемы

### 8.1 Обязательные поля

**Для каждого сервиса:**
```yaml
name: required                    # Уникальное имя
type: required                    # Тип из раздела 2
business_process: required        # Процесс из раздела 3
path: required                    # Путь к коду
status: required                  # Статус из раздела 7
```

**Для HTTP сервисов:**
```yaml
port: required                    # Порт
metrics_endpoint: required        # Prometheus endpoint
health_endpoint: required         # Health endpoint
kpis: required                    # Минимум 4 базовых KPI
```

**Для UI сервисов:**
```yaml
framework: recommended            # React, Next.js, Vue, etc.
```

### 8.2 Правила именования

#### Service Names
- **Format**: `kebab-case` или `snake_case`
- **Examples**: `mio-manager`, `workflow_intelligence`, `api-gateway`
- **Avoid**: CamelCase, spaces

#### Ports
- **Range**: 8000-8999
- **Reserved**:
  - 8000-8099: API Gateway & Core
  - 8100-8199: Infrastructure
  - 8200-8299: Platform Services
  - 8300-8399: Intelligent Core
  - 8400-8499: AI Office
  - 8500-8599: Runtime Services

## 9. Расширения схемы

### 9.1 Необязательные поля

```yaml
iso_clause: string                # ISO 22301 clause (deprecated, use tags)
orchestrator: string              # Orchestrator name (runtime, не каталог)
tags: array[string]              # Теги для группировки
  - "ai-powered"
  - "critical"
  - "iso-8.2.2"

environment: object              # Environment variables
  DATABASE_URL: "postgresql://..."
  REDIS_URL: "redis://..."

resources: object                # Resource requirements
  cpu: "500m"
  memory: "512Mi"

scaling: object                  # Scaling configuration
  min_replicas: 1
  max_replicas: 10
  target_cpu: 70
```

## 10. Примеры

### 10.1 Полный пример: Infrastructure Service

```yaml
- name: mio-manager
  type: infrastructure/AI-office-infrastructure
  business_process: "Monitoring & Observability Management"
  port: 8046
  status: active
  path: infrastructure/AI-office-infrastructure/mio-manager

  kpis:
    - request_latency_ms
    - requests_per_second
    - error_rate_percent
    - availability_percent
    - coverage_percentage
    - alert_response_time
    - services_monitored
    - observations_published

  dependencies:
    - fastapi
    - uvicorn[standard]
    - pydantic
    - redis
    - httpx
    - prometheus-client

  metrics_endpoint: http://localhost:8046/metrics
  health_endpoint: http://localhost:8046/health

  tags:
    - "critical"
    - "observability"
    - "ai-powered"
```

### 10.2 Полный пример: Intelligent Core Service

```yaml
- name: workflow_intelligence
  type: intelligent-core
  business_process: "Workflow Orchestration & Automation"
  port: 8037
  status: active
  path: intelligent-core/workflow_intelligence

  kpis:
    - request_latency_ms
    - requests_per_second
    - error_rate_percent
    - availability_percent
    - ai_decisions_total
    - ml_prediction_accuracy
    - knowledge_graph_size

  dependencies:
    - fastapi
    - pydantic
    - sqlalchemy
    - asyncpg
    - anthropic
    - httpx

  metrics_endpoint: http://localhost:8037/metrics
  health_endpoint: http://localhost:8037/health

  tags:
    - "brain"
    - "ai-powered"
    - "critical"
```

### 10.3 Полный пример: UI Service

```yaml
- name: admin-control-center
  type: interface
  business_process: "User Interface & Presentation"
  port: 5173
  status: active
  path: interface/admin-control-center
  framework: "React + Vite"

  kpis:
    - page_load_time_ms
    - time_to_interactive_ms
    - bundle_size_kb
    - user_sessions_active

  dependencies:
    - react
    - react-dom
    - "@mui/material"
    - "@radix-ui/react-dialog"
    - vite

  metrics_endpoint: null
  health_endpoint: null
```

## 11. Migration Guide

### 11.1 Добавление нового сервиса

1. **Определите тип** (раздел 2)
2. **Выберите бизнес-процесс** (раздел 3)
3. **Определите KPIs** (раздел 4)
4. **Добавьте endpoints** (если HTTP)
5. **Укажите зависимости** (раздел 6)
6. **Валидируйте** (раздел 8)

### 11.2 Обновление существующего сервиса

1. Обновите `version` в metadata
2. Обновите `generated_at`
3. Обновите `total_services`
4. Добавьте/обновите поля сервиса
5. Валидируйте схему

## 12. Инструменты

### 12.1 Валидация каталога

```python
from infrastructure.runtime.service-discovery import CatalogIntegration

catalog = CatalogIntegration()
await catalog.load_catalog()

# Check for missing required fields
# Check for invalid types
# Check for duplicate names
# Check port conflicts
```

### 12.2 Генерация каталога

```bash
cd infrastructure/tools/analyzers
python3 discover_services.py
```

## 13. Версионирование

**Format**: Semantic Versioning (semver)

```
1.0.0
│ │ │
│ │ └─ PATCH: Bug fixes, minor updates
│ └─── MINOR: New services, new fields (backward compatible)
└───── MAJOR: Breaking changes, schema changes
```

**Current Version**: `2.0.0`
**Date**: October 11, 2025

---

**Approved by**: AI Platform Architecture Team
**Status**: ✅ Официальная спецификация
**Last Updated**: October 11, 2025
