# 🗺️ КАРТА РАСПРЕДЕЛЕНИЯ КОМПОНЕНТОВ ПО СЛОЯМ

## Анализ компонентов из BCM-v1:

### 🧠 **1_NUCLEUS** (Ядро - мозг и нервная система)
```
backend/eventbus              → event-bus/           ✅ Уже есть
backend/orchestrator          → orchestrator/         ✅ Уже есть
backend/orchestrator_service  → orchestrator/         (объединить)
backend/bpmn_service          → workflow-engine/      ✅ Уже есть
services/ai_workflow_optimizer → ai-optimizer/        (AI оптимизация процессов)
services/process_mining_service → process-mining/     (Анализ процессов)
```

### 🛡️ **2_PROTECTION** (Защитный слой - череп)
```
integrations/gateway          → api-gateway/          (основной gateway)
integrations/nginx            → load-balancer/        (балансировка)
backend/auth_service          → auth-service/         ✅ Уже есть
services/unified_api_gateway  → api-gateway/          (объединить с gateway)
services/monitoring_service   → monitoring/           ✅ Уже есть
backend/notification_service  → notifications/        (объединить)
services/notification_service → notifications/        (объединить)
services/realtime_websocket   → websocket-gateway/    (real-time коммуникации)
```

### 📡 **3_CONTROL** (Управляющий слой - командный центр)
```
services/unified_control_center    → control-center/     (центр управления)
services/unified_database_gateway  → data-gateway/       (единый доступ к данным)
services/deployer                  → deployment-manager/  (управление развертыванием)
```

### 🔌 **4_INTEGRATIONS** (Интеграционный слой)
```
integrations/thehive         → thehive-connector/    (интеграция с TheHive)
backend/thehive_adapter      → thehive-connector/    (объединить)
integrations/lms             → lms-connector/        (система обучения)
backend/lms_adapter          → lms-connector/        (объединить)
integrations/governance      → governance-connector/ (GRC интеграция)
integrations/opengrc_oscal   → oscal-connector/      (OSCAL стандарт)
```

## 📊 НОВАЯ СТРУКТУРА С УЧЕТОМ ВСЕХ КОМПОНЕНТОВ:

```
COGNITIVE-ORCHESTRATION-ISO22301/
│
├── 1_NUCLEUS/                    # 🧠 ЯДРО
│   ├── orchestrator/             # Единый мозг (AI + Platform + Service)
│   ├── event-bus/                # Нервная система
│   ├── service-registry/         # Память о сервисах
│   ├── workflow-engine/          # BPMN процессы
│   ├── ai-optimizer/             # AI оптимизация workflow
│   ├── process-mining/           # Анализ и майнинг процессов
│   └── infrastructure/           # PostgreSQL, Redis, RabbitMQ
│
├── 2_PROTECTION/                 # 🛡️ ЗАЩИТА
│   ├── api-gateway/              # Объединенный Gateway (gateway + unified_api)
│   ├── load-balancer/            # Nginx балансировка
│   ├── auth-service/             # Аутентификация
│   ├── config-service/           # Конфигурация
│   ├── rate-limiter/             # DDoS защита
│   ├── monitoring/               # Prometheus, Grafana, Loki
│   ├── notifications/            # Объединенный notification service
│   └── websocket-gateway/        # WebSocket для real-time
│
├── 3_CONTROL/                    # 🎛️ УПРАВЛЕНИЕ
│   ├── control-center/           # Единый центр управления
│   ├── data-gateway/             # Универсальный доступ к данным
│   └── deployment-manager/       # Управление развертыванием
│
├── 4_SERVICES/                   # 📦 БИЗНЕС-СЕРВИСЫ
│   ├── document-processor/
│   ├── risk-management/
│   ├── incident-management/
│   └── ...
│
├── 5_INTEGRATIONS/              # 🔌 ВНЕШНИЕ ИНТЕГРАЦИИ
│   ├── thehive-connector/       # TheHive (объединенный)
│   ├── lms-connector/           # LMS/Moodle (объединенный)
│   ├── governance-connector/    # GRC системы
│   ├── oscal-connector/         # OpenGRC OSCAL
│   └── odoo-modules/            # Odoo BCM модули
│
└── 6_AI_CORE/                   # 🤖 AI КОМПОНЕНТЫ
    ├── models/
    ├── agents/
    └── training/
```

## 🔄 СВЯЗИ МЕЖДУ КОМПОНЕНТАМИ:

### Поток данных:
```
External Request
    ↓
[2_PROTECTION/load-balancer]
    ↓
[2_PROTECTION/api-gateway]
    ↓
[2_PROTECTION/auth-service]
    ↓
[1_NUCLEUS/orchestrator] ←→ [1_NUCLEUS/event-bus]
    ↓                            ↓
[1_NUCLEUS/workflow-engine]  [1_NUCLEUS/service-registry]
    ↓                            ↓
[1_NUCLEUS/ai-optimizer]     [All Services]
    ↓
[3_CONTROL/control-center] → Monitoring & Management
    ↓
[4_SERVICES/*] → Business Logic
    ↓
[5_INTEGRATIONS/*] → External Systems
```

### Event-Driven связи:
```
┌─────────────────────────────────────┐
│         EVENT BUS (Ядро)            │
├─────────────────────────────────────┤
│  Publishers:                        │
│  • Orchestrator                     │
│  • Workflow Engine                  │
│  • All Services                     │
│  • Control Center                   │
│                                     │
│  Subscribers:                       │
│  • Process Mining (анализ)          │
│  • AI Optimizer (оптимизация)       │
│  • Notifications (уведомления)      │
│  • WebSocket Gateway (real-time)    │
│  • Control Center (мониторинг)      │
└─────────────────────────────────────┘
```

### Data Flow:
```
[3_CONTROL/data-gateway]
    ↓
┌────────────────────┐
│   PostgreSQL       │ ← [1_NUCLEUS/orchestrator]
│   Redis            │ ← [2_PROTECTION/api-gateway]
│   RabbitMQ         │ ← [1_NUCLEUS/event-bus]
│   Elasticsearch    │ ← [2_PROTECTION/monitoring]
└────────────────────┘
```

## 🚀 ПОРЯДОК ЗАПУСКА:

1. **Infrastructure** (PostgreSQL, Redis, RabbitMQ)
2. **1_NUCLEUS** (Ядро системы)
3. **2_PROTECTION** (Защитный слой)
4. **3_CONTROL** (Управление)
5. **4_SERVICES** (Бизнес-логика)
6. **5_INTEGRATIONS** (Внешние системы)

## 🎯 КЛЮЧЕВЫЕ ОБЪЕДИНЕНИЯ:

1. **Orchestrator**: объединить `orchestrator` + `orchestrator_service`
2. **API Gateway**: объединить `gateway` + `unified_api_gateway`
3. **Notifications**: объединить `backend/notification_service` + `services/notification_service`
4. **TheHive**: объединить `thehive` + `thehive_adapter`
5. **LMS**: объединить `lms` + `lms_adapter`

## 💡 УНИКАЛЬНЫЕ КОМПОНЕНТЫ:

- **AI Workflow Optimizer** - оптимизирует процессы на лету
- **Process Mining** - анализирует паттерны использования
- **Unified Control Center** - единая панель управления
- **Unified Database Gateway** - абстракция для всех БД
- **Deployer** - автоматическое развертывание компонентов