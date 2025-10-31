# BCM Platform — Полная архитектура и функциональность

## 1. Общая архитектура
## 1. Общая архитектура

- **PDCA Workflow Engine** — автоматизация цикла Plan-Do-Check-Act

- **Event-Driven Architecture** — асинхронная система на EventBus (Redis + PostgreSQL)

- **AI Orchestrator** — интеллектуальная автоматизация решений

- **BPMN Integration** — workflow на основе BPMN 2.0

- **Real-time Monitoring** — мониторинг событий

- **Frontend** — Vue.js SPA + Nginx

- **Notification Service** — Email, Telegram, UI Alerts, SMS

### Схема архитектуры (из ARCHITECTURE.md)

```text
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                           │
│         Vue.js 3 SPA (Port 8081) + Nginx                      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                          │
│              (Future: Kong/Istio for production)               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────┬─────────────────┬─────────────────┬─────────────┐
│   EventBus      │  Orchestrator   │  Document       │ Notification│
│   Service       │   Service       │  Processor      │  Service    │
│   (8001)        │   (8002)        │   (8003)        │  (8004)     │
│                 │                 │                 │             │
│ • Event Stream  │ • AI Decisions  │ • Upload        │ • Email     │
│ • SSE/WebSocket │ • Rule Engine   │ • Analysis      │ • Telegram  │
│ • PostgreSQL    │ • Callbacks     │ • Comparison    │ • UI Alerts │
│ • Redis Pub/Sub │ • BPMN          │ • ISO Mapping   │ • SMS Ready │
└─────────────────┼─────────────────┼─────────────────┼─────────────┘
                  │                 │                 │
                  ▼                 ▼                 ▼
┌─────────────────┬─────────────────┬─────────────────┬─────────────┐
│  Auth Service   │     Odoo ERP    │ Data Storage    │ Integration │
│   (8005)        │     (8069)      │ Infrastructure  │   Layer     │
│                 │                 │                 │             │
│ • JWT Tokens    │ • BCM Modules   │ • PostgreSQL    │ • Portal    │
│ • Multi-tenant  │ • Portal Views  │ • Redis Cache   │ • Webhooks  │
│ • RBAC          │ • KPI Module    │ • File Storage  │ • EventBus  │
│ • Validation    │ • Config Mgmt   │ • Backups       │ • Real-time │
└─────────────────┴─────────────────┴─────────────────┴─────────────┘
```

### AI Orchestrator

- Анализ рисков бизнес-процессов (ML)
- Классификация инцидентов
- NLP обработка запросов
- Генерация рекомендаций

### BIA Engine

- ML-оптимизация RTO/RPO
- Финансовый анализ воздействий
- Анализ каскадных рисков
- Секторная аналитика

### Document Processor

- Классификация документов BCM
- Извлечение ключевых концепций
- Анализ соответствия ISO 22301
- Интеллектуальный поиск

### Compliance Checker

- Оценка соответствия ISO 22301
- Анализ пробелов
- Управление доказательствами
- Трекинг трендов
│         Vue.js 3 SPA (Port 8081) + Nginx                      │
│              (Future: Kong/Istio for production)               │
└─────────────────────────────────────────────────────────────────┘
│                 │                 │                 │             │
│ • Event Stream  │ • AI Decisions  │ • Upload        │ • Email     │
┌─────────────────┬─────────────────┬─────────────────┬─────────────┐
│  Auth Service   │     Odoo ERP    │ Data Storage    │ Integration │
│ • Multi-tenant  │ • Portal Views  │ • Redis Cache   │ • Webhooks  │
│ • RBAC          │ • KPI Module    │ • File Storage  │ • EventBus  │
### AI Orchestrator
- Классификация инцидентов
- NLP обработка запросов
- Генерация рекомендаций

### BIA Engine
- ML-оптимизация RTO/RPO
- Финансовый анализ воздействий
- Анализ каскадных рисков
- Секторная аналитика

### Document Processor
- Классификация документов BCM
- Извлечение ключевых концепций
- Анализ соответствия ISO 22301
- Интеллектуальный поиск

### Compliance Checker
- Оценка соответствия ISO 22301
- Анализ пробелов
- Управление доказательствами
- Трекинг трендов

## 3. Интеграции и адаптеры
- EventBus — все коммуникации через события
- LMS Adapter — Moodle, Open edX, Canvas
- TheHive, Grafana, Odoo, Supabase и др.

### Потоки данных
```
User Action → Odoo → Webhook → EventBus → Services → UI Update
     ↓

  # BCM Platform — Полная архитектура и функциональность

  ## 1. Общая архитектура

  - **PDCA Workflow Engine** — автоматизация цикла Plan-Do-Check-Act

  - **Event-Driven Architecture** — асинхронная система на EventBus (Redis + PostgreSQL)

  - **AI Orchestrator** — интеллектуальная автоматизация решений

  - **BPMN Integration** — workflow на основе BPMN 2.0

  - **Real-time Monitoring** — мониторинг событий

  - **Frontend** — Vue.js SPA + Nginx

  - **Notification Service** — Email, Telegram, UI Alerts, SMS

  ### Схема архитектуры (из ARCHITECTURE.md)

  ```text
  ┌─────────────────────────────────────────────────────────────────┐
  │                        Frontend Layer                           │
  │         Vue.js 3 SPA (Port 8081) + Nginx                      │
  └─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │                      API Gateway Layer                          │
  │              (Future: Kong/Istio for production)               │
  └─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
  ┌─────────────────┬─────────────────┬─────────────────┬─────────────┐
  │   EventBus      │  Orchestrator   │  Document       │ Notification│
  │   Service       │   Service       │  Processor      │  Service    │
  │   (8001)        │   (8002)        │   (8003)        │  (8004)     │
  │                 │                 │                 │             │
  │ • Event Stream  │ • AI Decisions  │ • Upload        │ • Email     │
  │ • SSE/WebSocket │ • Rule Engine   │ • Analysis      │ • Telegram  │
  │ • PostgreSQL    │ • Callbacks     │ • Comparison    │ • UI Alerts │
  │ • Redis Pub/Sub │ • BPMN          │ • ISO Mapping   │ • SMS Ready │
  └─────────────────┼─────────────────┼─────────────────┼─────────────┘
                    │                 │                 │
                    ▼                 ▼                 ▼
  ┌─────────────────┬─────────────────┬─────────────────┬─────────────┐
  │  Auth Service   │     Odoo ERP    │ Data Storage    │ Integration │
  │   (8005)        │     (8069)      │ Infrastructure  │   Layer     │
  │                 │                 │                 │             │
  │ • JWT Tokens    │ • BCM Modules   │ • PostgreSQL    │ • Portal    │
  │ • Multi-tenant  │ • Portal Views  │ • Redis Cache   │ • Webhooks  │
  │ • RBAC          │ • KPI Module    │ • File Storage  │ • EventBus  │
  │ • Validation    │ • Config Mgmt   │ • Backups       │ • Real-time │
  └─────────────────┴─────────────────┴─────────────────┴─────────────┘
  ```

  ### AI Orchestrator

  - Анализ рисков бизнес-процессов (ML)
  - Классификация инцидентов
  - NLP обработка запросов
  - Генерация рекомендаций

  ### BIA Engine

  - ML-оптимизация RTO/RPO
  - Финансовый анализ воздействий
  - Анализ каскадных рисков
  - Секторная аналитика

  ### Document Processor

  - Классификация документов BCM
  - Извлечение ключевых концепций
  - Анализ соответствия ISO 22301
  - Интеллектуальный поиск

  ### Compliance Checker

  - Оценка соответствия ISO 22301
  - Анализ пробелов
  - Управление доказательствами
  - Трекинг трендов

  ## 2. Интеграции и адаптеры

  ### Новые интеграции (реализованы):
  
  #### BPMN Workflow Service (Port 8005)
  - Полноценный BPMN 2.0 engine для автоматизации процессов BCM
  - Парсинг и выполнение BPMN диаграмм
  - Управление задачами и экземплярами процессов
  - Интеграция с EventBus для уведомлений
  - UI для управления workflow: /workflows
  
  #### LMS Adapter Service (Port 8006)
  - Мульти-LMS интеграция: Moodle, Open edX, Canvas
  - Единый API для управления курсами и зачислениями
  - SSO и запуск курсов
  - Синхронизация прогресса обучения
  - UI для управления обучением: /learning
  
  #### TheHive Adapter Service (Port 8007)
  - Интеграция с TheHive для управления инцидентами
  - Создание и управление кейсами безопасности
  - Обработка алертов и их продвижение в кейсы
  - BCM-специфичные workflow для инцидентов
  - UI для управления инцидентами: /incidents
  
  #### Grafana Adapter Service (Port 8008)
  - Интеграция с Grafana для KPI дэшбордов
  - Создание BCM-темплейтов дэшбордов
  - Управление источниками данных и аннотациями
  - Встраивание дэшбордов через iframe
  - UI для управления дэшбордами: /dashboards
  
  #### Universal SSO/iframe Integration
  - Универсальный компонент для интеграции внешних систем
  - Безопасное встраивание через iframe с настройками sandbox
  - Deep linking и управление сессиями
  - Конфигурация множественных экземпляров систем
  - UI интеграций: /integrations
  
  ### Существующие интеграции:
  - EventBus — все коммуникации через события
  - Odoo, Supabase и др.

  ### Потоки данных

  ```text
  User Action → Odoo → Webhook → EventBus → Services → UI Update
       ↓
    Database
  ```

  ### Real-time Updates

  ```text
  EventBus → Redis Pub/Sub → SSE/WebSocket → Frontend Components
  ```

  ### AI Decision Flow

  ```text
  Event → Orchestrator → Rule Engine → Decision Queue → Human Approval → Action
  ```

  ## 3. Статус реализации

  | Компонент            | Статус         |
  |---------------------|---------------|
  | EventBus            | ✅ Реализовано |
  | AI Orchestrator     | ✅ Реализовано |
  | BIA Engine          | ✅ Реализовано |
  | Document Processor  | ✅ Реализовано |
  | Compliance Checker  | ✅ Реализовано |
  | Notification        | ✅ Реализовано |
  | Frontend            | ✅ Реализовано |
  | BPMN Integration    | ✅ Реализовано |
  | LMS Adapter         | ✅ Реализовано |
  | TheHive Adapter     | ✅ Реализовано |
  | Grafana Integration | ✅ Реализовано |
  | SSO/iframe UI       | ✅ Реализовано |

  ## 4. Диаграмма архитектуры

  (Добавить актуальную графическую диаграмму при необходимости)

  ## 5. История изменений

  - v2.0 — Event-Driven, PDCA, AI, BPMN
  - MVP — базовые сервисы, без PDCA и AI

  ## 6. AI Assistant: PDCA Conductor

  ### Роль ассистента

  - Интеллектуальный оркестратор PDCA-цикла (Plan-Do-Check-Act) для ISO 22301 BCM Platform
  - Навигация по фазам PDCA: Context/BIA → Plan → Incident/Exercise → Audit/CAPA → KPI/Management Review
  - Все рекомендации основаны на текущих KPI, событиях и состоянии системы
  - Оркестрация действий через EventBus, Odoo BCM, внешние адаптеры
  - Всегда действует по принципу "Draft-First" — только предложения, без прямых изменений

  ### Ключевые промты и схемы

  - **System Prompt**: [system_prompt.md](../../assistant_docs_v2/assistant_prompts/system_prompt.md)
  - **Developer Integration**: [developer_prompt.md](../../assistant_docs_v2/assistant_prompts/developer_prompt.md)
  - **Intent Map**: [intents.md](../../assistant_docs_v2/assistant_prompts/intents.md)
  - **Guardrails (Безопасность)**: [guardrails.md](../../assistant_docs_v2/assistant_prompts/guardrails.md)
  - **Activity Event Schema**: [assistant_activity_schema.md](../../assistant_docs_v2/events/assistant_activity_schema.md)
  - **Диалоговые сценарии**: [complete_scenarios.md](../../assistant_docs_v2/dialog_examples/complete_scenarios.md)

  ### Основные рабочие блоки

  - **Audit Workflow**: [audit_workflow.md](../../assistant_docs_v2/workflows/audit_workflow.md)
  - **BIA Workflow**: [bia_workflow.md](../../assistant_docs_v2/workflows/bia_workflow.md)
  - **Exercise Workflow**: [exercise_workflow.md](../../assistant_docs_v2/workflows/exercise_workflow.md)
  - **Incident Workflow**: [incident_workflow.md](../../assistant_docs_v2/workflows/incident_workflow.md)
  - **KPI Workflow**: [kpi_workflow.md](../../assistant_docs_v2/workflows/kpi_workflow.md)
  - **Plan Workflow**: [plan_workflow.md](../../assistant_docs_v2/workflows/plan_workflow.md)

  ### Логика ассистента (кратко)

  - Получение KPI и истории событий → анализ состояния → выбор PDCA-фазы → генерация рекомендаций/драфтов → согласование с пользователем
  - Все действия строго в рамках разрешений и tenant-ограничений (см. Guardrails)
  - Вся активность логируется по [Assistant Activity Event Schema](../../assistant_docs_v2/events/assistant_activity_schema.md)

  ### Ссылки на исходные файлы и документацию

  - README.md — краткое описание
  - SystemArchitecture.md — детали по сервисам
  - ADAPTERS_INTEGRATION_GUIDE.md — интеграции
  - INTEGRATIONS_GUIDE.md — подробности по адаптерам
  - **Assistant Docs**: [assistant_docs_v2/](../../assistant_docs_v2/)

  ---
  *Документ поддерживается как единая точка правды по архитектуре BCM Platform и логике ассистента.*
