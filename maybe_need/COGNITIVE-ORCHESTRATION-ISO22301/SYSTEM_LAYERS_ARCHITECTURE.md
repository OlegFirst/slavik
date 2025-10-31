# 🏗️ АРХИТЕКТУРА СЛОЕВ СИСТЕМЫ

## Структура "Живого организма" BCM Platform

```
┌─────────────────────────────────────────────────────────────┐
│                    🌐 EXTERNAL WORLD                         │
│                  (Users, External Systems)                   │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              🛡️ PROTECTION LAYER (Защитный слой)            │
│                        "Череп и кожа"                        │
├─────────────────────────────────────────────────────────────┤
│  • API Gateway (8080)     - Единая точка входа              │
│  • Auth Service (8003)    - Аутентификация/Авторизация      │
│  • Config Service (8004)  - Централизованная конфигурация   │
│  • Rate Limiter          - Защита от DDoS                  │
│  • Monitoring Stack      - Prometheus, Grafana, Loki        │
│  • Notification Service  - Внешние коммуникации            │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│               🧠 NUCLEUS (Ядро системы)                      │
│                    "Мозг и нервная система"                  │
├─────────────────────────────────────────────────────────────┤
│  • Orchestrator (8000)    - Единый мозг (AI + Scenarios)    │
│  • EventBus (8001)        - Нервные импульсы                │
│  • Service Registry (8002) - Память о сервисах              │
│  • Workflow Engine (8005) - Исполнение процессов            │
│  • BCM Integration Hub    - Координатор модулей             │
│  ┌───────────────────────────────────────────────────┐      │
│  │  Инфраструктура: PostgreSQL, Redis, RabbitMQ      │      │
│  └───────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│            📦 SERVICE LAYER (Сервисный слой)                │
│                      "Органы системы"                        │
├─────────────────────────────────────────────────────────────┤
│  Домены BCM:                                                │
│  • Document Processor     - Обработка документов            │
│  • Risk Management        - Управление рисками              │
│  • Incident Management    - Управление инцидентами          │
│  • Audit Service         - Аудит и контроль                │
│  • Training Service      - Обучение и тренинги             │
│  • BIA Service          - Анализ влияния на бизнес         │
│  • Recovery Planning     - Планирование восстановления      │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│           🔌 INTEGRATION LAYER (Интеграционный слой)        │
│                    "Связь с внешним миром"                   │
├─────────────────────────────────────────────────────────────┤
│  • Odoo Modules          - BCM модули Odoo                  │
│  • TheHive Integration   - Управление инцидентами           │
│  • Moodle Integration    - Система обучения                 │
│  • External APIs         - Внешние системы                  │
│  • IoT Sensors          - Датчики и устройства             │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Последовательность запуска:

### 1️⃣ **NUCLEUS** (./start-nucleus.sh)
```bash
# Ядро - мозг системы
- PostgreSQL, Redis, RabbitMQ
- EventBus, Service Registry
- Workflow Engine
- Orchestrator
- BCM Integration Hub
```

### 2️⃣ **PROTECTION** (./start-protection.sh)
```bash
# Защита - череп и кожа
- Auth Service
- Config Service
- API Gateway
- Monitoring Stack
- Notification Service
- Rate Limiter
```

### 3️⃣ **SERVICES** (./start-services.sh) - TODO
```bash
# Органы - бизнес-функции
- Document Processor
- Risk Management
- Incident Management
- Audit Service
- Training Service
- BIA Service
```

### 4️⃣ **INTEGRATIONS** (./start-integrations.sh) - TODO
```bash
# Интеграции - внешние связи
- Odoo Platform
- TheHive
- Moodle
- External APIs
```

## 🔄 Взаимодействие слоев:

```
External Request → API Gateway → Auth Check →
→ Route to Service → EventBus → Process →
→ Orchestrator Decision → Workflow Execution →
→ Service Action → Event Publication →
→ Notification → Response to User
```

## 🎯 Принципы архитектуры:

1. **Изоляция слоев** - каждый слой независим
2. **Единая точка входа** - все через API Gateway
3. **Event-driven** - общение через события
4. **Resilience** - каждый компонент может упасть и восстановиться
5. **Observability** - все метрики и логи собираются
6. **Security by Design** - безопасность на каждом уровне

## 🚀 Quick Start:

```bash
# Запуск полной системы
./start-nucleus.sh      # Ядро
./start-protection.sh   # Защита
./start-services.sh     # Сервисы (TODO)
./start-integrations.sh # Интеграции (TODO)

# Или одной командой (TODO):
./start-platform.sh
```

## 📊 Мониторинг:

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **API Gateway**: http://localhost:8080/metrics
- **Health Checks**: http://localhost:8080/health/all

## 🔐 Безопасность:

- Все запросы через API Gateway
- JWT токены для аутентификации
- Rate limiting на всех endpoints
- Encrypted communication между сервисами
- Audit logging всех действий